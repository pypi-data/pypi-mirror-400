"""Simple LLM adapter for ATLAS.

Lightweight LLM wrapper for simple prompt-based operations.
Used by DirectSolver for solution adaptation and simple text transformations.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger("cognitive_core.llm")


class SimpleLLMError(Exception):
    """Base exception for SimpleLLM errors."""

    pass


class SimpleLLM:
    """Lightweight LLM for simple prompt operations.

    Implements the LLM protocol with Anthropic as the backend.
    Designed for simple, stateless operations like text generation
    and JSON extraction.

    Example:
        ```python
        llm = SimpleLLM(model="claude-sonnet-4-20250514")
        response = llm.generate("What is 2 + 2?")
        data = llm.extract_json("Return {\"result\": 4}")
        ```
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> None:
        """Initialize SimpleLLM.

        Args:
            model: Anthropic model identifier.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 for deterministic).
        """
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._client: Any = None  # Lazy loaded

    def _get_client(self) -> Any:
        """Lazy load the Anthropic client.

        Returns:
            Anthropic client instance.

        Raises:
            SimpleLLMError: If anthropic is not installed or API key is missing.
        """
        if self._client is None:
            try:
                import anthropic
            except ImportError as e:
                raise SimpleLLMError(
                    "anthropic package is required for SimpleLLM. "
                    "Install with: pip install anthropic"
                ) from e

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise SimpleLLMError(
                    "ANTHROPIC_API_KEY environment variable is required"
                )

            self._client = anthropic.Anthropic(api_key=api_key)
            logger.info(
                "Initialized Anthropic client",
                extra={"model": self._model},
            )

        return self._client

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            stop: Stop sequences (mapped to stop_sequences).
            **kwargs: Additional arguments passed to the API.

        Returns:
            Generated text.

        Raises:
            SimpleLLMError: If API call fails.
        """
        client = self._get_client()

        temp = temperature if temperature is not None else self._temperature
        tokens = max_tokens if max_tokens is not None else self._max_tokens

        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=tokens,
                temperature=temp,
                messages=[{"role": "user", "content": prompt}],
                stop_sequences=stop,
                **kwargs,
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""

        except Exception as e:
            logger.error(
                "LLM generation failed",
                extra={"error": str(e), "model": self._model},
            )
            raise SimpleLLMError(f"Generation failed: {e}") from e

    async def agenerate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Async version of generate.

        Args:
            prompt: The input prompt.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            stop: Stop sequences.
            **kwargs: Additional arguments passed to the API.

        Returns:
            Generated text.

        Raises:
            SimpleLLMError: If API call fails.
        """
        # For simplicity, use sync client in thread pool
        # A full async implementation would use anthropic.AsyncAnthropic
        import asyncio

        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                **kwargs,
            ),
        )

    def extract_json(
        self,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate and parse JSON response.

        Instructs the model to return valid JSON and parses the response.

        Args:
            prompt: The input prompt describing what JSON to generate.
            schema: Optional JSON schema hint for the model.

        Returns:
            Parsed JSON as a dictionary.

        Raises:
            SimpleLLMError: If generation or parsing fails.
        """
        # Build JSON instruction
        json_instruction = (
            "You must respond with valid JSON only. "
            "Do not include any text before or after the JSON. "
            "Do not wrap the JSON in markdown code blocks."
        )

        if schema:
            json_instruction += f"\n\nExpected schema: {json.dumps(schema)}"

        full_prompt = f"{json_instruction}\n\n{prompt}"

        response = self.generate(full_prompt, temperature=0.0)

        # Try to extract JSON from response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response (handle markdown code blocks)
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object or array
            json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", response)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            logger.error(
                "Failed to parse JSON response",
                extra={"response": response[:200]},
            )
            raise SimpleLLMError(
                f"Failed to parse JSON from response: {response[:100]}..."
            )

    @property
    def model_id(self) -> str:
        """Model identifier.

        Returns:
            String identifying the model.
        """
        return self._model
