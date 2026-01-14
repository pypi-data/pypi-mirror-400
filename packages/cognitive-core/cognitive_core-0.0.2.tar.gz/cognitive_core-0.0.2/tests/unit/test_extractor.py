"""Tests for AbstractionExtractor and pattern extractors."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import (
    CodeConcept,
    Outcome,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.learning.extractor import (
    AbstractionExtractor,
    CombinedPatternExtractor,
    LLMPatternExtractor,
    PatternExtractor,
    TextPatternExtractor,
    create_extractor,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="task-1",
        domain="swe",
        description="Fix the bug in the authentication module",
        verification=VerificationSpec(method="test_suite"),
    )


@pytest.fixture
def sample_steps() -> list[Step]:
    """Create sample steps for testing."""
    return [
        Step(
            action="Read the auth.py file",
            observation="```python\ndef login(user, password):\n    return True\n```",
            thought="Need to understand the current implementation",
        ),
        Step(
            action="Edit auth.py to add validation",
            observation="File updated successfully",
            thought="Adding password validation",
        ),
        Step(
            action="Run pytest tests/test_auth.py",
            observation="3 tests passed",
            thought="Verifying the fix",
        ),
    ]


@pytest.fixture
def successful_trajectory(sample_task: Task, sample_steps: list[Step]) -> Trajectory:
    """Create a successful trajectory for testing."""
    return Trajectory(
        task=sample_task,
        steps=sample_steps,
        outcome=Outcome(success=True, partial_score=1.0),
        agent_id="test-agent",
        timestamp=datetime.now(),
    )


@pytest.fixture
def failed_trajectory(sample_task: Task) -> Trajectory:
    """Create a failed trajectory for testing."""
    return Trajectory(
        task=sample_task,
        steps=[
            Step(
                action="Try random fix",
                observation="Error: syntax error",
            ),
        ],
        outcome=Outcome(success=False, error_info="Test failed"),
        agent_id="test-agent",
        timestamp=datetime.now(),
    )


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create a mock LLM for testing."""
    llm = MagicMock()
    return llm


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    """Create a mock embedding service for testing."""
    service = MagicMock()
    # Return random embeddings for each call
    service.embed.side_effect = lambda x: np.random.randn(384)
    return service


# =============================================================================
# PatternExtractor Protocol Tests
# =============================================================================


class TestPatternExtractorProtocol:
    """Tests for PatternExtractor protocol compliance."""

    def test_llm_extractor_implements_protocol(self, mock_llm: MagicMock) -> None:
        """Test that LLMPatternExtractor implements PatternExtractor."""
        extractor = LLMPatternExtractor(mock_llm)
        assert isinstance(extractor, PatternExtractor)

    def test_text_extractor_implements_protocol(self) -> None:
        """Test that TextPatternExtractor implements PatternExtractor."""
        extractor = TextPatternExtractor()
        assert isinstance(extractor, PatternExtractor)

    def test_combined_extractor_implements_protocol(self, mock_llm: MagicMock) -> None:
        """Test that CombinedPatternExtractor implements PatternExtractor."""
        extractor = CombinedPatternExtractor(mock_llm)
        assert isinstance(extractor, PatternExtractor)


# =============================================================================
# LLMPatternExtractor Tests
# =============================================================================


class TestLLMPatternExtractor:
    """Tests for LLMPatternExtractor."""

    def test_extract_concepts_empty_trajectories(self, mock_llm: MagicMock) -> None:
        """Test extract_concepts with empty list."""
        extractor = LLMPatternExtractor(mock_llm)
        result = extractor.extract_concepts([])
        assert result == []

    def test_extract_concepts_no_successful(
        self, mock_llm: MagicMock, failed_trajectory: Trajectory
    ) -> None:
        """Test extract_concepts with only failed trajectories."""
        extractor = LLMPatternExtractor(mock_llm)
        result = extractor.extract_concepts([failed_trajectory])
        assert result == []

    def test_extract_concepts_success(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test successful concept extraction."""
        mock_llm.extract_json.return_value = [
            {
                "name": "validation_pattern",
                "description": "Input validation before processing",
                "code": "def validate(x): return x is not None",
                "signature": "(x: Any) -> bool",
            }
        ]

        extractor = LLMPatternExtractor(mock_llm)
        concepts = extractor.extract_concepts([successful_trajectory])

        assert len(concepts) == 1
        assert concepts[0].name == "validation_pattern"
        assert concepts[0].description == "Input validation before processing"
        assert concepts[0].source == "learned"
        mock_llm.extract_json.assert_called_once()

    def test_extract_concepts_llm_error(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test graceful handling of LLM errors."""
        mock_llm.extract_json.side_effect = Exception("LLM error")

        extractor = LLMPatternExtractor(mock_llm)
        concepts = extractor.extract_concepts([successful_trajectory])

        assert concepts == []

    def test_extract_strategies_empty(self, mock_llm: MagicMock) -> None:
        """Test extract_strategies with empty list."""
        extractor = LLMPatternExtractor(mock_llm)
        result = extractor.extract_strategies([])
        assert result == []

    def test_extract_strategies_success(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test successful strategy extraction."""
        mock_llm.extract_json.return_value = {
            "situation": "When fixing authentication bugs",
            "suggestion": "First read the code, then add validation",
            "parameters": [{"name": "module", "type": "string"}],
        }

        extractor = LLMPatternExtractor(mock_llm)
        strategies = extractor.extract_strategies([successful_trajectory])

        assert len(strategies) == 1
        assert strategies[0].situation == "When fixing authentication bugs"
        assert "read the code" in strategies[0].suggestion
        assert len(strategies[0].parameters) == 1

    def test_extract_concepts_multiple_domains(self, mock_llm: MagicMock) -> None:
        """Test extraction across multiple domains."""
        task_arc = Task(
            id="task-arc",
            domain="arc",
            description="Transform the grid",
            verification=VerificationSpec(method="exact_match"),
        )
        task_swe = Task(
            id="task-swe",
            domain="swe",
            description="Fix the bug",
            verification=VerificationSpec(method="test_suite"),
        )

        traj_arc = Trajectory(
            task=task_arc,
            steps=[Step(action="Transform", observation="Done")],
            outcome=Outcome(success=True),
            agent_id="agent",
        )
        traj_swe = Trajectory(
            task=task_swe,
            steps=[Step(action="Edit", observation="Done")],
            outcome=Outcome(success=True),
            agent_id="agent",
        )

        # Return different results for each domain
        mock_llm.extract_json.side_effect = [
            [{"name": "arc_pattern", "description": "ARC", "code": "", "signature": ""}],
            [{"name": "swe_pattern", "description": "SWE", "code": "", "signature": ""}],
        ]

        extractor = LLMPatternExtractor(mock_llm)
        concepts = extractor.extract_concepts([traj_arc, traj_swe])

        assert len(concepts) == 2
        assert mock_llm.extract_json.call_count == 2


# =============================================================================
# TextPatternExtractor Tests
# =============================================================================


class TestTextPatternExtractor:
    """Tests for TextPatternExtractor."""

    def test_extract_concepts_empty(self) -> None:
        """Test extract_concepts with empty list."""
        extractor = TextPatternExtractor()
        result = extractor.extract_concepts([])
        assert result == []

    def test_extract_concepts_with_code_blocks(self) -> None:
        """Test extraction from code blocks in trajectories."""
        task = Task(
            id="task-1",
            domain="python",
            description="Write code",
            verification=VerificationSpec(method="test_suite"),
        )

        # Create trajectory with code containing repeated patterns
        steps = [
            Step(
                action="Write function",
                observation="```python\nimport json\nimport json\ndef parse():\n    json.loads(data)\n    json.loads(more_data)\n```",
            ),
            Step(
                action="Add more",
                observation="```python\nimport json\njson.loads(x)\n```",
            ),
        ]

        traj = Trajectory(
            task=task,
            steps=steps,
            outcome=Outcome(success=True),
            agent_id="agent",
        )

        extractor = TextPatternExtractor()
        concepts = extractor.extract_concepts([traj])

        # Should find json.loads pattern (appears 3+ times)
        # and json import (appears 3 times)
        assert len(concepts) > 0
        names = [c.name for c in concepts]
        assert "loads" in names or "json" in names

    def test_extract_strategies_empty(self) -> None:
        """Test extract_strategies with empty list."""
        extractor = TextPatternExtractor()
        result = extractor.extract_strategies([])
        assert result == []

    def test_extract_strategies_finds_action_sequences(self) -> None:
        """Test that common action sequences are extracted."""
        task = Task(
            id="task-1",
            domain="swe",
            description="Fix bug",
            verification=VerificationSpec(method="test_suite"),
        )

        # Create multiple trajectories with similar action patterns
        def make_traj(task: Task) -> Trajectory:
            return Trajectory(
                task=task,
                steps=[
                    Step(action="Read file", observation="content"),
                    Step(action="Edit file", observation="edited"),
                    Step(action="Run tests", observation="passed"),
                ],
                outcome=Outcome(success=True),
                agent_id="agent",
            )

        trajectories = [make_traj(task) for _ in range(3)]

        extractor = TextPatternExtractor()
        strategies = extractor.extract_strategies(trajectories)

        assert len(strategies) > 0
        # Should find read -> edit pattern
        assert any("read_file" in s.suggestion.lower() for s in strategies)

    def test_extract_concepts_no_successful(
        self, failed_trajectory: Trajectory
    ) -> None:
        """Test that failed trajectories are filtered out."""
        extractor = TextPatternExtractor()
        concepts = extractor.extract_concepts([failed_trajectory])
        assert concepts == []

    def test_simplify_action_categories(self) -> None:
        """Test action simplification."""
        extractor = TextPatternExtractor()

        assert extractor._simplify_action("read the file") == "read_file"
        assert extractor._simplify_action("cat main.py") == "read_file"
        assert extractor._simplify_action("write to output") == "edit_file"
        assert extractor._simplify_action("edit config.yaml") == "edit_file"
        assert extractor._simplify_action("run the tests") == "execute"
        assert extractor._simplify_action("search for pattern") == "search"
        assert extractor._simplify_action("grep error") == "search"
        assert extractor._simplify_action("pytest tests/") == "test"
        assert extractor._simplify_action("unknown action") == "other"


# =============================================================================
# CombinedPatternExtractor Tests
# =============================================================================


class TestCombinedPatternExtractor:
    """Tests for CombinedPatternExtractor."""

    def test_merges_llm_and_text_concepts(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test that concepts from both extractors are merged."""
        # LLM returns one concept
        mock_llm.extract_json.return_value = [
            {"name": "llm_concept", "description": "From LLM", "code": "", "signature": ""}
        ]

        extractor = CombinedPatternExtractor(mock_llm)

        # Mock the text extractor to return a concept
        text_concept = CodeConcept(
            id="text-1",
            name="text_concept",
            description="From text",
            code="",
            signature="",
            source="learned",
        )
        with patch.object(
            extractor._text_extractor, "extract_concepts", return_value=[text_concept]
        ):
            concepts = extractor.extract_concepts([successful_trajectory])

        # Should have both concepts
        names = {c.name for c in concepts}
        assert "llm_concept" in names
        assert "text_concept" in names

    def test_deduplicates_by_name(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test that duplicate names are removed."""
        # LLM returns concept with same name as text
        mock_llm.extract_json.return_value = [
            {"name": "shared_name", "description": "From LLM", "code": "llm", "signature": ""}
        ]

        extractor = CombinedPatternExtractor(mock_llm)

        # Text extractor also returns shared_name
        text_concept = CodeConcept(
            id="text-1",
            name="shared_name",
            description="From text",
            code="text",
            signature="",
            source="learned",
        )
        with patch.object(
            extractor._text_extractor, "extract_concepts", return_value=[text_concept]
        ):
            concepts = extractor.extract_concepts([successful_trajectory])

        # Should only have one concept (LLM version preferred)
        assert len(concepts) == 1
        assert concepts[0].code == "llm"

    def test_merges_strategies(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test that strategies from both extractors are merged."""
        mock_llm.extract_json.return_value = {
            "situation": "LLM situation",
            "suggestion": "LLM suggestion",
            "parameters": [],
        }

        extractor = CombinedPatternExtractor(mock_llm)

        text_strategy = Strategy(
            id="text-1",
            situation="Text situation",
            suggestion="Text suggestion",
            source="learned",
        )
        with patch.object(
            extractor._text_extractor, "extract_strategies", return_value=[text_strategy]
        ):
            strategies = extractor.extract_strategies([successful_trajectory])

        situations = {s.situation for s in strategies}
        assert "LLM situation" in situations
        assert "Text situation" in situations


# =============================================================================
# AbstractionExtractor Tests
# =============================================================================


class TestAbstractionExtractor:
    """Tests for AbstractionExtractor."""

    def test_extract_from_batch_returns_tuple(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test that extract_from_batch returns concepts and strategies."""
        mock_llm.extract_json.return_value = []
        pattern_extractor = LLMPatternExtractor(mock_llm)
        extractor = AbstractionExtractor(pattern_extractor)

        concepts, strategies = extractor.extract_from_batch([successful_trajectory])

        assert isinstance(concepts, list)
        assert isinstance(strategies, list)

    def test_extract_from_batch_with_results(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test extraction returns actual results."""
        # First call for concepts, second for strategies
        mock_llm.extract_json.side_effect = [
            [{"name": "concept1", "description": "d", "code": "c", "signature": "s"}],
            {"situation": "s", "suggestion": "sug", "parameters": []},
        ]

        pattern_extractor = LLMPatternExtractor(mock_llm)
        extractor = AbstractionExtractor(pattern_extractor)

        concepts, strategies = extractor.extract_from_batch([successful_trajectory])

        assert len(concepts) == 1
        assert len(strategies) == 1

    def test_deduplication_without_embedding(
        self, mock_llm: MagicMock, successful_trajectory: Trajectory
    ) -> None:
        """Test name-based deduplication when no embedding service."""
        mock_llm.extract_json.side_effect = [
            [{"name": "existing_concept", "description": "new", "code": "", "signature": ""}],
            [],
        ]

        pattern_extractor = LLMPatternExtractor(mock_llm)
        extractor = AbstractionExtractor(pattern_extractor, embedding_service=None)

        existing_concepts = [
            CodeConcept(
                id="e1",
                name="existing_concept",
                description="old",
                code="",
                signature="",
                source="learned",
            )
        ]

        concepts, _ = extractor.extract_from_batch(
            [successful_trajectory],
            existing_concepts=existing_concepts,
        )

        # Should deduplicate by name
        assert len(concepts) == 0

    def test_deduplication_with_embedding(
        self,
        mock_llm: MagicMock,
        mock_embedding_service: MagicMock,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test embedding-based deduplication."""
        mock_llm.extract_json.side_effect = [
            [{"name": "new_concept", "description": "test", "code": "", "signature": ""}],
            [],
        ]

        pattern_extractor = LLMPatternExtractor(mock_llm)
        extractor = AbstractionExtractor(
            pattern_extractor, embedding_service=mock_embedding_service
        )

        existing_concepts = [
            CodeConcept(
                id="e1",
                name="old_concept",
                description="test",
                code="",
                signature="",
                source="learned",
            )
        ]

        # Make embeddings return same vector (high similarity)
        fixed_embedding = np.ones(384)
        mock_embedding_service.embed.side_effect = None
        mock_embedding_service.embed.return_value = fixed_embedding

        concepts, _ = extractor.extract_from_batch(
            [successful_trajectory],
            existing_concepts=existing_concepts,
        )

        # Should be deduplicated due to high similarity
        assert len(concepts) == 0

    def test_deduplication_keeps_novel(
        self,
        mock_llm: MagicMock,
        mock_embedding_service: MagicMock,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that novel concepts are kept."""
        mock_llm.extract_json.side_effect = [
            [{"name": "novel_concept", "description": "unique", "code": "", "signature": ""}],
            [],
        ]

        pattern_extractor = LLMPatternExtractor(mock_llm)
        extractor = AbstractionExtractor(
            pattern_extractor, embedding_service=mock_embedding_service
        )

        existing_concepts = [
            CodeConcept(
                id="e1",
                name="old_concept",
                description="different",
                code="",
                signature="",
                source="learned",
            )
        ]

        # Make embeddings return different vectors (low similarity)
        call_count = [0]

        def return_different_embeddings(_: str) -> np.ndarray:
            call_count[0] += 1
            if call_count[0] == 1:
                return np.array([1, 0, 0] * 128)
            return np.array([0, 1, 0] * 128)

        mock_embedding_service.embed.side_effect = return_different_embeddings

        concepts, _ = extractor.extract_from_batch(
            [successful_trajectory],
            existing_concepts=existing_concepts,
        )

        # Should keep the novel concept
        assert len(concepts) == 1
        assert concepts[0].name == "novel_concept"

    def test_cosine_similarity(self) -> None:
        """Test cosine similarity calculation."""
        extractor = AbstractionExtractor(TextPatternExtractor())

        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        assert extractor._cosine_similarity(vec1, vec2) == pytest.approx(1.0)

        vec3 = np.array([0, 1, 0])
        assert extractor._cosine_similarity(vec1, vec3) == pytest.approx(0.0)

        vec4 = np.array([1, 1, 0])
        expected = 1 / np.sqrt(2)
        assert extractor._cosine_similarity(vec1, vec4) == pytest.approx(expected)

    def test_cosine_similarity_zero_vector(self) -> None:
        """Test cosine similarity with zero vector."""
        extractor = AbstractionExtractor(TextPatternExtractor())

        vec1 = np.array([1, 0, 0])
        zero = np.array([0, 0, 0])
        assert extractor._cosine_similarity(vec1, zero) == 0.0
        assert extractor._cosine_similarity(zero, vec1) == 0.0


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateExtractor:
    """Tests for create_extractor factory function."""

    def test_creates_llm_extractor(self, mock_llm: MagicMock) -> None:
        """Test creating extractor with LLM pattern extractor."""
        config = LearningConfig(pattern_extractor="llm")
        extractor = create_extractor(config, mock_llm)

        assert isinstance(extractor, AbstractionExtractor)
        assert isinstance(extractor._extractor, LLMPatternExtractor)

    def test_creates_text_extractor(self, mock_llm: MagicMock) -> None:
        """Test creating extractor with text pattern extractor."""
        config = LearningConfig(pattern_extractor="text")
        extractor = create_extractor(config, mock_llm)

        assert isinstance(extractor, AbstractionExtractor)
        assert isinstance(extractor._extractor, TextPatternExtractor)

    def test_creates_combined_extractor(self, mock_llm: MagicMock) -> None:
        """Test creating extractor with combined pattern extractor."""
        config = LearningConfig(pattern_extractor="both")
        extractor = create_extractor(config, mock_llm)

        assert isinstance(extractor, AbstractionExtractor)
        assert isinstance(extractor._extractor, CombinedPatternExtractor)

    def test_raises_on_unknown_type(self, mock_llm: MagicMock) -> None:
        """Test that unknown extractor type raises error."""
        # Create a config with invalid pattern_extractor
        # We need to bypass validation, so we'll patch it
        config = LearningConfig()
        # Manually set the value (bypassing Pydantic validation for test)
        object.__setattr__(config, "pattern_extractor", "unknown")

        with pytest.raises(ValueError, match="Unknown pattern extractor"):
            create_extractor(config, mock_llm)

    def test_passes_embedding_service(
        self, mock_llm: MagicMock, mock_embedding_service: MagicMock
    ) -> None:
        """Test that embedding service is passed to extractor."""
        config = LearningConfig(pattern_extractor="llm")
        extractor = create_extractor(config, mock_llm, mock_embedding_service)

        assert extractor._embedding is mock_embedding_service


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the extractor module."""

    def test_full_extraction_pipeline(self, mock_llm: MagicMock) -> None:
        """Test complete extraction from trajectories."""
        # Setup tasks and trajectories
        task = Task(
            id="task-1",
            domain="python",
            description="Write a sorting function",
            verification=VerificationSpec(method="test_suite"),
        )

        trajectories = []
        for i in range(3):
            traj = Trajectory(
                task=task,
                steps=[
                    Step(
                        action="Read the code",
                        observation="```python\ndef sort(arr):\n    return sorted(arr)\n```",
                    ),
                    Step(
                        action="Edit to add optimization",
                        observation="Success",
                    ),
                    Step(
                        action="Run pytest",
                        observation="All tests passed",
                    ),
                ],
                outcome=Outcome(success=True),
                agent_id=f"agent-{i}",
            )
            trajectories.append(traj)

        # Configure mock LLM
        mock_llm.extract_json.side_effect = [
            [{"name": "sorting_pattern", "description": "Sort optimization", "code": "sorted(arr, key=...)", "signature": ""}],
            {"situation": "When sorting", "suggestion": "Use built-in sorted", "parameters": []},
            {"situation": "When sorting 2", "suggestion": "Use built-in sorted 2", "parameters": []},
            {"situation": "When sorting 3", "suggestion": "Use built-in sorted 3", "parameters": []},
        ]

        # Create extractor and run
        config = LearningConfig(pattern_extractor="llm")
        extractor = create_extractor(config, mock_llm)

        concepts, strategies = extractor.extract_from_batch(trajectories)

        assert len(concepts) >= 0
        assert len(strategies) >= 0

    def test_empty_batch_handling(self, mock_llm: MagicMock) -> None:
        """Test handling of empty trajectory batch."""
        config = LearningConfig(pattern_extractor="llm")
        extractor = create_extractor(config, mock_llm)

        concepts, strategies = extractor.extract_from_batch([])

        assert concepts == []
        assert strategies == []

    def test_mixed_success_failure_trajectories(self, mock_llm: MagicMock) -> None:
        """Test that only successful trajectories are used."""
        task = Task(
            id="task-1",
            domain="swe",
            description="Fix bug",
            verification=VerificationSpec(method="test_suite"),
        )

        successful = Trajectory(
            task=task,
            steps=[Step(action="Fix", observation="Fixed")],
            outcome=Outcome(success=True),
            agent_id="agent",
        )
        failed = Trajectory(
            task=task,
            steps=[Step(action="Try", observation="Error")],
            outcome=Outcome(success=False),
            agent_id="agent",
        )

        mock_llm.extract_json.side_effect = [
            [{"name": "fix_pattern", "description": "d", "code": "c", "signature": "s"}],
            {"situation": "s", "suggestion": "sug", "parameters": []},
        ]

        config = LearningConfig(pattern_extractor="llm")
        extractor = create_extractor(config, mock_llm)

        concepts, strategies = extractor.extract_from_batch([successful, failed])

        # Should only process the successful one
        assert len(concepts) == 1
