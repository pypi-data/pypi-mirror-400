"""Tests for HindsightLearner (SAGE-style learning)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import (
    AnalysisResult,
    Experience,
    Outcome,
    Step,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.learning.hindsight import HindsightLearner


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def verification_spec() -> VerificationSpec:
    """Create a test verification spec."""
    return VerificationSpec(method="exact_match", config={})


@pytest.fixture
def successful_task(verification_spec: VerificationSpec) -> Task:
    """Create a successful test task."""
    return Task(
        id="task-success-001",
        domain="test",
        description="Implement a sorting algorithm",
        verification=verification_spec,
    )


@pytest.fixture
def failed_task(verification_spec: VerificationSpec) -> Task:
    """Create a failed test task."""
    return Task(
        id="task-fail-001",
        domain="test",
        description="Fix the broken authentication",
        verification=verification_spec,
    )


@pytest.fixture
def successful_trajectory(successful_task: Task) -> Trajectory:
    """Create a successful test trajectory."""
    return Trajectory(
        task=successful_task,
        steps=[
            Step(
                thought="I need to implement quicksort",
                action="def quicksort(arr): ...",
                observation="Function defined",
            ),
            Step(
                thought="Add base case",
                action="if len(arr) <= 1: return arr",
                observation="Base case added",
            ),
            Step(
                thought="Add partition logic",
                action="pivot = arr[0]; less = [x for x in arr[1:] if x <= pivot]",
                observation="Partition implemented",
            ),
        ],
        outcome=Outcome(success=True, partial_score=1.0),
        agent_id="test-agent",
    )


@pytest.fixture
def failed_trajectory(failed_task: Task) -> Trajectory:
    """Create a failed test trajectory."""
    return Trajectory(
        task=failed_task,
        steps=[
            Step(
                thought="Check the auth module",
                action="open auth.py",
                observation="File opened",
            ),
            Step(
                thought="Try to fix the token validation",
                action="token = request.headers['auth']",
                observation="KeyError: 'auth'",
            ),
        ],
        outcome=Outcome(
            success=False,
            error_info="KeyError: 'auth' header not found",
        ),
        agent_id="test-agent",
    )


@pytest.fixture
def success_analysis() -> AnalysisResult:
    """Create analysis result for successful trajectory."""
    return AnalysisResult(
        success=True,
        key_steps=[0, 2],
        step_attribution=[0.3, 0.2, 0.5],
        error_patterns=[],
        abstractable=True,
        training_examples=[],
    )


@pytest.fixture
def failure_analysis() -> AnalysisResult:
    """Create analysis result for failed trajectory."""
    return AnalysisResult(
        success=False,
        key_steps=[1],
        step_attribution=[0.4, 0.6],
        error_patterns=[{"name": "key_error", "signature": "KeyError"}],
        abstractable=True,
        training_examples=[],
    )


@pytest.fixture
def mock_llm() -> Mock:
    """Create a mock LLM."""
    llm = Mock()
    llm.generate = Mock(
        return_value='{"corrected_solution": "Use request.headers.get(\'Authorization\')", '
        '"reasoning": "Should use get() with default to avoid KeyError", '
        '"key_insight": "Always use safe dict access"}'
    )
    return llm


@pytest.fixture
def mock_memory() -> Mock:
    """Create a mock memory system."""
    memory = Mock()
    mock_exp_memory = Mock()
    mock_exp_memory.prune = Mock(return_value=5)
    memory.experience_memory = mock_exp_memory
    return memory


# =============================================================================
# Test HindsightLearner Initialization
# =============================================================================


class TestHindsightLearnerInit:
    """Tests for HindsightLearner initialization."""

    def test_init_defaults(self) -> None:
        """Test initialization with defaults."""
        learner = HindsightLearner()

        assert learner._llm is None
        assert learner._memory is None
        assert learner._config is not None
        assert learner._accumulated == []
        assert learner._last_batch_time is None

    def test_init_with_llm(self, mock_llm: Mock) -> None:
        """Test initialization with LLM."""
        learner = HindsightLearner(llm=mock_llm)

        assert learner._llm is mock_llm

    def test_init_with_memory(self, mock_memory: Mock) -> None:
        """Test initialization with memory system."""
        learner = HindsightLearner(memory=mock_memory)

        assert learner._memory is mock_memory

    def test_init_with_config(self) -> None:
        """Test initialization with custom config."""
        config = LearningConfig(min_trajectories=10, min_success_rate=0.8)
        learner = HindsightLearner(config=config)

        assert learner._config.min_trajectories == 10
        assert learner._config.min_success_rate == 0.8


# =============================================================================
# Test learn_from_trajectory
# =============================================================================


class TestLearnFromTrajectory:
    """Tests for learn_from_trajectory method."""

    def test_learn_from_successful_trajectory(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test learning from a successful trajectory."""
        learner = HindsightLearner()
        experiences = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )

        # Should have at least the main experience
        assert len(experiences) >= 1

        # First experience should be the full trajectory
        main_exp = experiences[0]
        assert main_exp.success is True
        assert main_exp.trajectory_id == successful_trajectory.task.id
        assert main_exp.metadata.get("source") == "success"
        assert main_exp.metadata.get("type") == "full_trajectory"

    def test_learn_from_failed_trajectory(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
    ) -> None:
        """Test learning from a failed trajectory."""
        learner = HindsightLearner()
        experiences = learner.learn_from_trajectory(
            failed_trajectory, failure_analysis
        )

        # Should have at least the failure experience
        assert len(experiences) >= 1

        # First experience should be the negative example
        failure_exp = experiences[0]
        assert failure_exp.success is False
        assert failure_exp.trajectory_id == failed_trajectory.task.id
        assert failure_exp.metadata.get("source") == "failure"
        assert failure_exp.metadata.get("type") == "negative_example"

    def test_learn_from_failure_with_llm(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
        mock_llm: Mock,
    ) -> None:
        """Test learning from failure generates hindsight examples with LLM."""
        learner = HindsightLearner(llm=mock_llm)
        experiences = learner.learn_from_trajectory(
            failed_trajectory, failure_analysis
        )

        # Should have failure example + hindsight corrected example
        assert len(experiences) >= 2

        # Check that LLM was called
        mock_llm.generate.assert_called_once()

        # Find the hindsight example
        hindsight_exp = next(
            (e for e in experiences if e.metadata.get("source") == "hindsight"), None
        )
        assert hindsight_exp is not None
        assert hindsight_exp.success is True
        assert hindsight_exp.metadata.get("type") == "corrected"
        assert hindsight_exp.metadata.get("generated") is True


# =============================================================================
# Test _learn_from_success
# =============================================================================


class TestLearnFromSuccess:
    """Tests for _learn_from_success method."""

    def test_extracts_main_experience(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test extraction of main experience from success."""
        learner = HindsightLearner()
        experiences = learner._learn_from_success(
            successful_trajectory, success_analysis
        )

        main_exp = experiences[0]
        assert main_exp.task_input == successful_trajectory.task.description
        assert "quicksort" in main_exp.solution_output.lower() or main_exp.solution_output

    def test_extracts_key_step_experiences(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test extraction of key step experiences."""
        learner = HindsightLearner()
        experiences = learner._learn_from_success(
            successful_trajectory, success_analysis
        )

        # Find key step experiences
        key_step_exps = [
            e for e in experiences if e.metadata.get("type") == "key_step"
        ]

        # Should have experiences for high-attribution key steps
        # Step 0 has attribution 0.3 (>= threshold), step 2 has 0.5
        assert len(key_step_exps) >= 1

        for exp in key_step_exps:
            assert exp.success is True
            assert "step_index" in exp.metadata
            assert "attribution" in exp.metadata

    def test_generates_alternatives_with_llm(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test alternative generation with LLM."""
        mock_llm = Mock()
        mock_llm.generate = Mock(
            return_value='{"alternative_solution": "Use merge sort instead", '
            '"reasoning": "Also O(n log n) but stable"}'
        )

        learner = HindsightLearner(llm=mock_llm)
        experiences = learner._learn_from_success(
            successful_trajectory, success_analysis
        )

        # Find alternative experiences
        alt_exps = [
            e for e in experiences if e.metadata.get("type") == "alternative"
        ]

        assert len(alt_exps) >= 1
        assert alt_exps[0].metadata.get("generated") is True


# =============================================================================
# Test _learn_from_failure
# =============================================================================


class TestLearnFromFailure:
    """Tests for _learn_from_failure method."""

    def test_creates_negative_example(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
    ) -> None:
        """Test creation of negative example from failure."""
        learner = HindsightLearner()
        experiences = learner._learn_from_failure(
            failed_trajectory, failure_analysis
        )

        failure_exp = experiences[0]
        assert failure_exp.success is False
        assert failure_exp.feedback == "KeyError: 'auth' header not found"
        assert "error_patterns" in failure_exp.metadata

    def test_generates_corrected_examples_with_llm(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
        mock_llm: Mock,
    ) -> None:
        """Test hindsight correction with LLM."""
        learner = HindsightLearner(llm=mock_llm)
        experiences = learner._learn_from_failure(
            failed_trajectory, failure_analysis
        )

        # Should have both failure and corrected
        assert len(experiences) >= 2

        corrected = next(
            (e for e in experiences if e.metadata.get("type") == "corrected"), None
        )
        assert corrected is not None
        assert corrected.success is True
        assert "get()" in corrected.solution_output or "Authorization" in corrected.solution_output


# =============================================================================
# Test _convert_to_experiences
# =============================================================================


class TestConvertToExperiences:
    """Tests for _convert_to_experiences method."""

    def test_converts_examples_to_experiences(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test conversion of example dicts to Experience objects."""
        learner = HindsightLearner()

        examples = [
            {
                "solution": "Use binary search for faster lookups",
                "reasoning": "Reduces time complexity to O(log n)",
                "key_insight": "Sorted data enables binary search",
            }
        ]

        experiences = learner._convert_to_experiences(successful_trajectory, examples)

        assert len(experiences) == 1
        exp = experiences[0]
        assert exp.solution_output == "Use binary search for faster lookups"
        assert "O(log n)" in exp.feedback
        assert exp.metadata.get("source") == "hindsight"
        assert exp.metadata.get("key_insight") == "Sorted data enables binary search"

    def test_skips_empty_solutions(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that empty solutions are skipped."""
        learner = HindsightLearner()

        examples = [
            {"solution": "", "reasoning": "Empty"},
            {"solution": "Valid solution", "reasoning": "Good"},
        ]

        experiences = learner._convert_to_experiences(successful_trajectory, examples)

        assert len(experiences) == 1
        assert experiences[0].solution_output == "Valid solution"

    def test_produces_valid_experience_objects(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that produced experiences are valid Experience objects."""
        learner = HindsightLearner()

        examples = [{"solution": "Test solution", "reasoning": "Test reasoning"}]

        experiences = learner._convert_to_experiences(successful_trajectory, examples)

        exp = experiences[0]
        assert isinstance(exp, Experience)
        assert exp.id.startswith("exp-")
        assert exp.trajectory_id == successful_trajectory.task.id
        assert exp.timestamp is not None
        assert exp.embedding is None  # Will be computed by memory system


# =============================================================================
# Test update_memory
# =============================================================================


class TestUpdateMemory:
    """Tests for update_memory method."""

    def test_logs_warning_without_memory(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test that warning is logged when no memory system."""
        learner = HindsightLearner()
        experiences = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )

        # Should not raise, just log warning
        with patch("cognitive_core.learning.hindsight.logger") as mock_logger:
            learner.update_memory(experiences)
            mock_logger.warning.assert_called()

    def test_stores_experiences_with_memory(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
        mock_memory: Mock,
    ) -> None:
        """Test storing experiences with memory system."""
        learner = HindsightLearner(memory=mock_memory)
        experiences = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )

        with patch("cognitive_core.learning.hindsight.logger") as mock_logger:
            learner.update_memory(experiences)
            # Should log info for each experience
            assert mock_logger.info.call_count == len(experiences)


# =============================================================================
# Test Accumulation and Batch Learning
# =============================================================================


class TestAccumulation:
    """Tests for trajectory accumulation."""

    def test_accumulate_adds_trajectory(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test accumulate adds trajectory to list."""
        learner = HindsightLearner()
        learner.accumulate(successful_trajectory)

        assert learner.accumulated_count == 1
        assert successful_trajectory in learner.get_accumulated()

    def test_should_finetune_always_false(self) -> None:
        """Test should_finetune always returns False (SAGE-style)."""
        learner = HindsightLearner()
        assert learner.should_finetune() is False

    def test_should_run_batch_respects_min_trajectories(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test should_run_batch respects min_trajectories threshold."""
        config = LearningConfig(min_trajectories=3)
        learner = HindsightLearner(config=config)

        # Not enough trajectories
        learner.accumulate(successful_trajectory)
        learner.accumulate(successful_trajectory)
        assert learner.should_run_batch() is False

        # Now enough
        learner.accumulate(successful_trajectory)
        assert learner.should_run_batch() is True

    def test_should_run_batch_respects_time_trigger(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test should_run_batch respects time trigger."""
        config = LearningConfig(min_trajectories=1, min_hours_since_last=1.0)
        learner = HindsightLearner(config=config)

        learner.accumulate(successful_trajectory)

        # No previous batch, should run
        assert learner.should_run_batch() is True

        # Simulate previous batch just ran
        learner._last_batch_time = datetime.now(timezone.utc)
        assert learner.should_run_batch() is False

        # Simulate previous batch was long ago
        learner._last_batch_time = datetime.now(timezone.utc) - timedelta(hours=2)
        assert learner.should_run_batch() is True

    def test_should_run_batch_respects_quality_trigger(
        self,
        successful_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test should_run_batch respects quality trigger."""
        config = LearningConfig(min_trajectories=2, min_success_rate=0.6)
        learner = HindsightLearner(config=config)

        # Add one success, one failure (50% rate < 60% threshold)
        learner.accumulate(successful_trajectory)
        learner.accumulate(failed_trajectory)
        assert learner.should_run_batch() is False

        # Add another success (66% rate > 60% threshold)
        learner.accumulate(successful_trajectory)
        assert learner.should_run_batch() is True

    def test_clear_accumulated_resets_state(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test clear_accumulated resets state correctly."""
        learner = HindsightLearner()
        learner.accumulate(successful_trajectory)
        learner.accumulate(successful_trajectory)

        assert learner.accumulated_count == 2

        learner.clear_accumulated()

        assert learner.accumulated_count == 0
        assert learner._last_batch_time is not None


# =============================================================================
# Test prepare_training_data
# =============================================================================


class TestPrepareTrainingData:
    """Tests for prepare_training_data method."""

    def test_formats_successful_trajectories(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test formatting of successful trajectories."""
        learner = HindsightLearner()
        learner.accumulate(successful_trajectory)

        data = learner.prepare_training_data()

        assert "sampling" in data
        assert "refinement" in data
        assert "error" in data

        # Should have sampling data from success
        assert len(data["sampling"]) >= 1
        assert data["sampling"][0]["weight"] == 2.0

        # Should have refinement data for key steps
        assert len(data["refinement"]) >= 1
        assert data["refinement"][0]["weight"] == 1.5

    def test_formats_failed_trajectories(
        self,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test formatting of failed trajectories."""
        learner = HindsightLearner()
        learner.accumulate(failed_trajectory)

        data = learner.prepare_training_data()

        # Should have error data from failure
        assert len(data["error"]) >= 1
        assert data["error"][0]["weight"] == 1.0
        assert "[ERROR]" in data["error"][0]["output"]

    def test_uses_provided_trajectories(
        self,
        successful_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test using provided trajectories instead of accumulated."""
        learner = HindsightLearner()

        # Accumulate one trajectory
        learner.accumulate(successful_trajectory)

        # But provide different trajectories
        data = learner.prepare_training_data(trajectories=[failed_trajectory])

        # Should only have error data (from provided failed trajectory)
        assert len(data["sampling"]) == 0
        assert len(data["error"]) >= 1


# =============================================================================
# Test prune_low_value_experiences
# =============================================================================


class TestPruneLowValueExperiences:
    """Tests for prune_low_value_experiences method."""

    def test_returns_zero_without_memory(self) -> None:
        """Test returns 0 when no memory system."""
        learner = HindsightLearner()
        result = learner.prune_low_value_experiences()
        assert result == 0

    def test_calls_memory_prune(self, mock_memory: Mock) -> None:
        """Test calls memory system prune method."""
        learner = HindsightLearner(memory=mock_memory)
        result = learner.prune_low_value_experiences(threshold=0.5)

        mock_memory.experience_memory.prune.assert_called_once_with(
            {"min_success_rate": 0.5}
        )
        assert result == 5  # Mock returns 5

    def test_default_threshold(self, mock_memory: Mock) -> None:
        """Test default threshold value."""
        learner = HindsightLearner(memory=mock_memory)
        learner.prune_low_value_experiences()

        # Default threshold is 0.3
        mock_memory.experience_memory.prune.assert_called_once_with(
            {"min_success_rate": 0.3}
        )


# =============================================================================
# Test Helper Methods
# =============================================================================


class TestHelperMethods:
    """Tests for helper methods."""

    def test_extract_full_solution(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test _extract_full_solution."""
        learner = HindsightLearner()
        solution = learner._extract_full_solution(successful_trajectory)

        # Should contain all actions
        assert "quicksort" in solution.lower() or solution
        assert len(solution) > 0

    def test_extract_full_solution_empty_steps(
        self,
        verification_spec: VerificationSpec,
    ) -> None:
        """Test _extract_full_solution with empty steps."""
        task = Task(
            id="empty-task",
            domain="test",
            description="Empty task",
            verification=verification_spec,
        )
        trajectory = Trajectory(
            task=task,
            steps=[],
            outcome=Outcome(success=False),
            agent_id="test",
        )

        learner = HindsightLearner()
        solution = learner._extract_full_solution(trajectory)

        assert solution == ""

    def test_build_step_context(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test _build_step_context."""
        learner = HindsightLearner()

        # Context up to step 1 (should include step 0)
        context = learner._build_step_context(successful_trajectory, 1)

        assert "Task:" in context
        assert successful_trajectory.task.description in context
        assert "Action 1:" in context

    def test_format_steps_for_prompt(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test _format_steps_for_prompt."""
        learner = HindsightLearner()
        formatted = learner._format_steps_for_prompt(successful_trajectory)

        assert "Step 1" in formatted
        assert "thought:" in formatted.lower()
        assert "action:" in formatted.lower()

    def test_is_key_step_first_last(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test _is_key_step identifies first and last steps."""
        learner = HindsightLearner()

        # First step is always key
        assert learner._is_key_step(successful_trajectory, 0) is True

        # Last step is always key
        last_idx = len(successful_trajectory.steps) - 1
        assert learner._is_key_step(successful_trajectory, last_idx) is True

    def test_is_key_step_out_of_bounds(
        self,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test _is_key_step with out of bounds index."""
        learner = HindsightLearner()
        assert learner._is_key_step(successful_trajectory, 100) is False


# =============================================================================
# Test Experience ID Generation
# =============================================================================


class TestExperienceIdGeneration:
    """Tests for experience ID generation."""

    def test_generates_unique_ids(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test that unique experience IDs are generated."""
        learner = HindsightLearner()

        experiences1 = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )
        experiences2 = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )

        all_ids = [e.id for e in experiences1 + experiences2]

        # All IDs should be unique
        assert len(all_ids) == len(set(all_ids))

    def test_id_format(
        self,
        successful_trajectory: Trajectory,
        success_analysis: AnalysisResult,
    ) -> None:
        """Test experience ID format."""
        learner = HindsightLearner()
        experiences = learner.learn_from_trajectory(
            successful_trajectory, success_analysis
        )

        for exp in experiences:
            assert exp.id.startswith("exp-")
            assert len(exp.id) == 16  # "exp-" + 12 hex chars


# =============================================================================
# Test LLM Error Handling
# =============================================================================


class TestLLMErrorHandling:
    """Tests for LLM error handling."""

    def test_handles_llm_json_parse_error(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
    ) -> None:
        """Test graceful handling of LLM JSON parse errors."""
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value="Not valid JSON at all")

        learner = HindsightLearner(llm=mock_llm)
        experiences = learner._learn_from_failure(
            failed_trajectory, failure_analysis
        )

        # Should still have the failure experience
        assert len(experiences) >= 1
        assert experiences[0].success is False

    def test_handles_llm_exception(
        self,
        failed_trajectory: Trajectory,
        failure_analysis: AnalysisResult,
    ) -> None:
        """Test graceful handling of LLM exceptions."""
        mock_llm = Mock()
        mock_llm.generate = Mock(side_effect=Exception("API Error"))

        learner = HindsightLearner(llm=mock_llm)

        # Should not raise
        experiences = learner._learn_from_failure(
            failed_trajectory, failure_analysis
        )

        # Should still have the failure experience
        assert len(experiences) >= 1
