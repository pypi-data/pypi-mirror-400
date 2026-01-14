"""Tests for SimpleLLM adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cognitive_core.llm.simple import SimpleLLM, SimpleLLMError


class TestSimpleLLMInit:
    """Tests for SimpleLLM initialization."""

    def test_default_values(self) -> None:
        """Test initialization with default values."""
        llm = SimpleLLM()

        assert llm._model == "claude-sonnet-4-20250514"
        assert llm._max_tokens == 4096
        assert llm._temperature == 0.0
        assert llm._client is None

    def test_custom_values(self) -> None:
        """Test initialization with custom values."""
        llm = SimpleLLM(
            model="claude-3-opus-20240229",
            max_tokens=2048,
            temperature=0.7,
        )

        assert llm._model == "claude-3-opus-20240229"
        assert llm._max_tokens == 2048
        assert llm._temperature == 0.7

    def test_model_id_property(self) -> None:
        """Test model_id property returns the model."""
        llm = SimpleLLM(model="test-model")

        assert llm.model_id == "test-model"


class TestSimpleLLMClient:
    """Tests for SimpleLLM client initialization."""

    def test_lazy_loading(self) -> None:
        """Test that client is not loaded until first use."""
        llm = SimpleLLM()

        assert llm._client is None

    def test_missing_api_key_raises_error(self) -> None:
        """Test that missing API key raises SimpleLLMError."""
        llm = SimpleLLM()

        mock_anthropic = MagicMock()

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}, clear=True):
            with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
                with pytest.raises(SimpleLLMError, match="ANTHROPIC_API_KEY"):
                    llm._get_client()

    def test_client_initialization_with_api_key(self) -> None:
        """Test that client initializes with valid API key."""
        llm = SimpleLLM()

        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
                client = llm._get_client()

        assert client is mock_client
        mock_anthropic.Anthropic.assert_called_once_with(api_key="test-key")

    def test_client_cached_after_first_call(self) -> None:
        """Test that client is cached after first initialization."""
        llm = SimpleLLM()

        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
                client1 = llm._get_client()
                client2 = llm._get_client()

        assert client1 is client2
        # Should only be called once
        assert mock_anthropic.Anthropic.call_count == 1


class TestSimpleLLMGenerate:
    """Tests for SimpleLLM.generate method."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Anthropic client."""
        client = MagicMock()
        response = MagicMock()
        response.content = [MagicMock(text="Generated response")]
        client.messages.create.return_value = response
        return client

    @pytest.fixture
    def llm_with_mock_client(self, mock_client: MagicMock) -> SimpleLLM:
        """Create SimpleLLM with a mock client."""
        llm = SimpleLLM()
        llm._client = mock_client
        return llm

    def test_generate_basic(self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock) -> None:
        """Test basic text generation."""
        result = llm_with_mock_client.generate("Hello")

        assert result == "Generated response"
        mock_client.messages.create.assert_called_once()

    def test_generate_uses_default_parameters(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that generate uses default parameters."""
        llm_with_mock_client.generate("Hello")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["max_tokens"] == 4096
        assert call_kwargs["temperature"] == 0.0
        assert call_kwargs["messages"] == [{"role": "user", "content": "Hello"}]

    def test_generate_override_temperature(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that temperature can be overridden."""
        llm_with_mock_client.generate("Hello", temperature=0.5)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5

    def test_generate_override_max_tokens(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that max_tokens can be overridden."""
        llm_with_mock_client.generate("Hello", max_tokens=1024)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 1024

    def test_generate_with_stop_sequences(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that stop sequences are passed correctly."""
        llm_with_mock_client.generate("Hello", stop=["END", "STOP"])

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["stop_sequences"] == ["END", "STOP"]

    def test_generate_empty_response(self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock) -> None:
        """Test handling of empty response."""
        mock_client.messages.create.return_value.content = []

        result = llm_with_mock_client.generate("Hello")

        assert result == ""

    def test_generate_api_error(self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock) -> None:
        """Test that API errors are wrapped in SimpleLLMError."""
        mock_client.messages.create.side_effect = Exception("API Error")

        with pytest.raises(SimpleLLMError, match="Generation failed"):
            llm_with_mock_client.generate("Hello")


class TestSimpleLLMExtractJson:
    """Tests for SimpleLLM.extract_json method."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Anthropic client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def llm_with_mock_client(self, mock_client: MagicMock) -> SimpleLLM:
        """Create SimpleLLM with a mock client."""
        llm = SimpleLLM()
        llm._client = mock_client
        return llm

    def test_extract_json_valid(self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock) -> None:
        """Test extraction of valid JSON."""
        response = MagicMock()
        response.content = [MagicMock(text='{"key": "value", "number": 42}')]
        mock_client.messages.create.return_value = response

        result = llm_with_mock_client.extract_json("Return some JSON")

        assert result == {"key": "value", "number": 42}

    def test_extract_json_with_markdown_code_block(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test extraction of JSON wrapped in markdown code block."""
        response = MagicMock()
        response.content = [MagicMock(text='```json\n{"key": "value"}\n```')]
        mock_client.messages.create.return_value = response

        result = llm_with_mock_client.extract_json("Return some JSON")

        assert result == {"key": "value"}

    def test_extract_json_with_surrounding_text(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test extraction of JSON with surrounding text."""
        response = MagicMock()
        response.content = [MagicMock(text='Here is the JSON: {"result": true}')]
        mock_client.messages.create.return_value = response

        result = llm_with_mock_client.extract_json("Return some JSON")

        assert result == {"result": True}

    def test_extract_json_with_schema(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that schema is included in prompt."""
        response = MagicMock()
        response.content = [MagicMock(text='{"name": "test"}')]
        mock_client.messages.create.return_value = response

        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        llm_with_mock_client.extract_json("Return some JSON", schema=schema)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        prompt = call_kwargs["messages"][0]["content"]
        assert "Expected schema" in prompt

    def test_extract_json_invalid_raises_error(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that invalid JSON raises SimpleLLMError."""
        response = MagicMock()
        response.content = [MagicMock(text="This is not JSON at all")]
        mock_client.messages.create.return_value = response

        with pytest.raises(SimpleLLMError, match="Failed to parse JSON"):
            llm_with_mock_client.extract_json("Return some JSON")

    def test_extract_json_uses_zero_temperature(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test that extract_json always uses temperature 0."""
        response = MagicMock()
        response.content = [MagicMock(text='{"key": "value"}')]
        mock_client.messages.create.return_value = response

        # Even if SimpleLLM was initialized with non-zero temperature
        llm_with_mock_client._temperature = 0.7
        llm_with_mock_client.extract_json("Return some JSON")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.0

    def test_extract_json_array(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test extraction of JSON array."""
        response = MagicMock()
        response.content = [MagicMock(text='[1, 2, 3, "four"]')]
        mock_client.messages.create.return_value = response

        result = llm_with_mock_client.extract_json("Return an array")

        assert result == [1, 2, 3, "four"]


class TestSimpleLLMAgenerate:
    """Tests for SimpleLLM.agenerate async method."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Anthropic client."""
        client = MagicMock()
        response = MagicMock()
        response.content = [MagicMock(text="Async response")]
        client.messages.create.return_value = response
        return client

    @pytest.fixture
    def llm_with_mock_client(self, mock_client: MagicMock) -> SimpleLLM:
        """Create SimpleLLM with a mock client."""
        llm = SimpleLLM()
        llm._client = mock_client
        return llm

    @pytest.mark.asyncio
    async def test_agenerate_basic(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test basic async text generation."""
        result = await llm_with_mock_client.agenerate("Hello")

        assert result == "Async response"
        mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_agenerate_with_parameters(
        self, llm_with_mock_client: SimpleLLM, mock_client: MagicMock
    ) -> None:
        """Test async generation with parameters."""
        await llm_with_mock_client.agenerate(
            "Hello",
            temperature=0.5,
            max_tokens=1024,
            stop=["END"],
        )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 1024
        assert call_kwargs["stop_sequences"] == ["END"]


class TestSimpleLLMProtocolCompliance:
    """Tests for LLM protocol compliance."""

    def test_implements_generate(self) -> None:
        """Test that SimpleLLM has generate method."""
        llm = SimpleLLM()

        assert hasattr(llm, "generate")
        assert callable(llm.generate)

    def test_implements_agenerate(self) -> None:
        """Test that SimpleLLM has agenerate method."""
        llm = SimpleLLM()

        assert hasattr(llm, "agenerate")
        assert callable(llm.agenerate)

    def test_implements_model_id(self) -> None:
        """Test that SimpleLLM has model_id property."""
        llm = SimpleLLM()

        assert hasattr(llm, "model_id")
        assert isinstance(llm.model_id, str)

    def test_conforms_to_llm_protocol(self) -> None:
        """Test that SimpleLLM conforms to LLM protocol."""
        from cognitive_core.protocols.llm import LLM

        llm = SimpleLLM()

        # Runtime checkable protocol
        assert isinstance(llm, LLM)
