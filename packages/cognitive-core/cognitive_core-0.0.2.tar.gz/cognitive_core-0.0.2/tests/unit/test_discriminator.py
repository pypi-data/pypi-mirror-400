"""Tests for Discriminator value estimation."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cognitive_core.core.types import Candidate, Outcome, Task, Trajectory, VerificationSpec
from cognitive_core.search.discriminator import Discriminator


# =============================================================================
# Test Fixtures
# =============================================================================


def make_task(
    task_id: str = "test-1",
    description: str = "Test task description",
) -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        description=description,
        domain="test",
        verification=VerificationSpec(method="exact_match", config={}),
    )


def make_candidate(
    solution: Any = "test_solution",
    confidence: float = 0.8,
    reasoning: str = "Test reasoning",
) -> Candidate:
    """Create a test candidate with all required fields."""
    return Candidate(
        solution=solution,
        confidence=confidence,
        reasoning=reasoning,
        source="generated",
    )


def make_mock_llm(response: str = "0.8") -> MagicMock:
    """Create a mock SimpleLLM that returns the given response."""
    llm = MagicMock()
    llm.generate = MagicMock(return_value=response)
    return llm


def make_mock_executor(
    outcome: Outcome | None = None,
) -> MagicMock:
    """Create a mock TaskExecutor that returns a trajectory with the given outcome."""
    executor = MagicMock()
    if outcome is None:
        outcome = Outcome(success=True, partial_score=1.0)

    trajectory = MagicMock(spec=Trajectory)
    trajectory.outcome = outcome

    executor.execute = AsyncMock(return_value=trajectory)
    return executor


def make_mock_environment() -> MagicMock:
    """Create a mock Environment."""
    env = MagicMock()
    return env


# =============================================================================
# Discriminator.estimate() Tests
# =============================================================================


class TestDiscriminatorEstimate:
    """Tests for Discriminator.estimate()."""

    def test_estimate_returns_valid_score(self) -> None:
        """estimate() returns a score between 0.0 and 1.0."""
        llm = make_mock_llm("0.75")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert 0.0 <= score <= 1.0
        assert score == 0.75

    def test_estimate_clamps_high_values(self) -> None:
        """estimate() clamps values above 1.0."""
        llm = make_mock_llm("1.5")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert score == 1.0

    def test_estimate_clamps_low_values(self) -> None:
        """estimate() clamps values below 0.0."""
        llm = make_mock_llm("-0.5")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert score == 0.0

    def test_estimate_handles_malformed_response(self) -> None:
        """estimate() returns 0.5 for malformed LLM responses."""
        llm = make_mock_llm("This is not a number")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert score == 0.5

    def test_estimate_handles_exception(self) -> None:
        """estimate() returns 0.5 when LLM raises exception."""
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=RuntimeError("API error"))
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert score == 0.5

    def test_estimate_strips_whitespace(self) -> None:
        """estimate() strips whitespace from response."""
        llm = make_mock_llm("  0.85  \n")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        score = discriminator.estimate(task, candidate)

        assert score == 0.85

    def test_estimate_calls_llm_with_task_and_candidate_info(self) -> None:
        """estimate() includes task and candidate in prompt."""
        llm = make_mock_llm("0.7")
        discriminator = Discriminator(llm=llm)
        task = make_task(description="Solve the puzzle")
        candidate = make_candidate(solution="my solution", reasoning="my reasoning")

        discriminator.estimate(task, candidate)

        call_args = llm.generate.call_args
        prompt = call_args[0][0]
        assert "Solve the puzzle" in prompt
        assert "my solution" in prompt
        assert "my reasoning" in prompt

    def test_estimate_uses_zero_temperature(self) -> None:
        """estimate() uses temperature=0.0 for deterministic results."""
        llm = make_mock_llm("0.7")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidate = make_candidate()

        discriminator.estimate(task, candidate)

        call_args = llm.generate.call_args
        assert call_args.kwargs.get("temperature") == 0.0


# =============================================================================
# Discriminator.should_rollout() Tests
# =============================================================================


class TestDiscriminatorShouldRollout:
    """Tests for Discriminator.should_rollout()."""

    def test_should_rollout_above_threshold(self) -> None:
        """should_rollout() returns True when score >= threshold."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        assert discriminator.should_rollout(0.8, threshold=0.7) is True
        assert discriminator.should_rollout(0.7, threshold=0.7) is True

    def test_should_rollout_below_threshold(self) -> None:
        """should_rollout() returns False when score < threshold."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        assert discriminator.should_rollout(0.6, threshold=0.7) is False
        assert discriminator.should_rollout(0.0, threshold=0.7) is False

    def test_should_rollout_default_threshold(self) -> None:
        """should_rollout() uses default threshold of 0.7."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        assert discriminator.should_rollout(0.7) is True
        assert discriminator.should_rollout(0.69) is False

    def test_should_rollout_custom_threshold(self) -> None:
        """should_rollout() respects custom threshold."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        assert discriminator.should_rollout(0.5, threshold=0.5) is True
        assert discriminator.should_rollout(0.5, threshold=0.6) is False


# =============================================================================
# Discriminator.batch_estimate() Tests
# =============================================================================


class TestDiscriminatorBatchEstimate:
    """Tests for Discriminator.batch_estimate()."""

    def test_batch_estimate_empty_list(self) -> None:
        """batch_estimate() returns empty list for empty input."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)
        task = make_task()

        scores = discriminator.batch_estimate(task, [])

        assert scores == []

    def test_batch_estimate_single_candidate(self) -> None:
        """batch_estimate() calls individual estimate for <= 3 candidates."""
        llm = make_mock_llm("0.8")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate()]

        scores = discriminator.batch_estimate(task, candidates)

        assert len(scores) == 1
        assert scores[0] == 0.8

    def test_batch_estimate_three_candidates(self) -> None:
        """batch_estimate() uses individual estimates for exactly 3 candidates."""
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=["0.8", "0.6", "0.9"])
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate(), make_candidate(), make_candidate()]

        scores = discriminator.batch_estimate(task, candidates)

        assert len(scores) == 3
        assert scores == [0.8, 0.6, 0.9]

    def test_batch_estimate_multiple_candidates(self) -> None:
        """batch_estimate() uses batch prompt for > 3 candidates."""
        llm = make_mock_llm("1: 0.8, 2: 0.6, 3: 0.9, 4: 0.5")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate() for _ in range(4)]

        scores = discriminator.batch_estimate(task, candidates)

        assert len(scores) == 4
        assert scores == [0.8, 0.6, 0.9, 0.5]

    def test_batch_estimate_handles_partial_response(self) -> None:
        """batch_estimate() defaults to 0.5 for missing scores."""
        llm = make_mock_llm("1: 0.8, 3: 0.9")  # Missing 2 and 4
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate() for _ in range(4)]

        scores = discriminator.batch_estimate(task, candidates)

        assert len(scores) == 4
        assert scores[0] == 0.8
        assert scores[1] == 0.5  # Default
        assert scores[2] == 0.9
        assert scores[3] == 0.5  # Default

    def test_batch_estimate_falls_back_on_error(self) -> None:
        """batch_estimate() returns 0.5 for all on error."""
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=RuntimeError("API error"))
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate() for _ in range(4)]

        scores = discriminator.batch_estimate(task, candidates)

        assert len(scores) == 4
        assert all(s == 0.5 for s in scores)

    def test_batch_estimate_clamps_scores(self) -> None:
        """batch_estimate() clamps scores to valid range."""
        llm = make_mock_llm("1: 1.5, 2: -0.5, 3: 0.7, 4: 0.8")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate() for _ in range(4)]

        scores = discriminator.batch_estimate(task, candidates)

        assert scores[0] == 1.0  # Clamped from 1.5
        assert scores[1] == 0.0  # Clamped from -0.5
        assert scores[2] == 0.7
        assert scores[3] == 0.8


# =============================================================================
# Discriminator.estimate_with_rollout() Tests
# =============================================================================


class TestDiscriminatorEstimateWithRollout:
    """Tests for Discriminator.estimate_with_rollout()."""

    @pytest.mark.asyncio
    async def test_estimate_with_rollout_uses_executor(self) -> None:
        """estimate_with_rollout() uses executor when available."""
        llm = make_mock_llm()
        outcome = Outcome(success=True, partial_score=1.0)
        executor = make_mock_executor(outcome)
        discriminator = Discriminator(llm=llm, executor=executor)
        task = make_task()
        candidate = make_candidate()
        env = make_mock_environment()

        score = await discriminator.estimate_with_rollout(task, candidate, env)

        assert score == 1.0
        executor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_estimate_with_rollout_returns_partial_score(self) -> None:
        """estimate_with_rollout() returns partial_score on non-success."""
        llm = make_mock_llm()
        outcome = Outcome(success=False, partial_score=0.6)
        executor = make_mock_executor(outcome)
        discriminator = Discriminator(llm=llm, executor=executor)
        task = make_task()
        candidate = make_candidate()
        env = make_mock_environment()

        score = await discriminator.estimate_with_rollout(task, candidate, env)

        assert score == 0.6

    @pytest.mark.asyncio
    async def test_estimate_with_rollout_no_partial_score(self) -> None:
        """estimate_with_rollout() returns 0.0 when no partial_score."""
        llm = make_mock_llm()
        outcome = Outcome(success=False, partial_score=None)
        executor = make_mock_executor(outcome)
        discriminator = Discriminator(llm=llm, executor=executor)
        task = make_task()
        candidate = make_candidate()
        env = make_mock_environment()

        score = await discriminator.estimate_with_rollout(task, candidate, env)

        assert score == 0.0

    @pytest.mark.asyncio
    async def test_estimate_with_rollout_fallback_to_llm(self) -> None:
        """estimate_with_rollout() falls back to LLM when no executor."""
        llm = make_mock_llm("0.75")
        discriminator = Discriminator(llm=llm, executor=None)
        task = make_task()
        candidate = make_candidate()
        env = make_mock_environment()

        score = await discriminator.estimate_with_rollout(task, candidate, env)

        assert score == 0.75
        llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_estimate_with_rollout_handles_exception(self) -> None:
        """estimate_with_rollout() returns 0.0 on executor error."""
        llm = make_mock_llm()
        executor = MagicMock()
        executor.execute = AsyncMock(side_effect=RuntimeError("Execution failed"))
        discriminator = Discriminator(llm=llm, executor=executor)
        task = make_task()
        candidate = make_candidate()
        env = make_mock_environment()

        score = await discriminator.estimate_with_rollout(task, candidate, env)

        assert score == 0.0


# =============================================================================
# Discriminator._parse_batch_scores() Tests
# =============================================================================


class TestDiscriminatorParseBatchScores:
    """Tests for Discriminator._parse_batch_scores()."""

    def test_parse_standard_format(self) -> None:
        """Parse standard format: '1: 0.8, 2: 0.6, 3: 0.9'."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        scores = discriminator._parse_batch_scores("1: 0.8, 2: 0.6, 3: 0.9", 3)

        assert scores == [0.8, 0.6, 0.9]

    def test_parse_with_newlines(self) -> None:
        """Parse format with newlines."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        response = "1: 0.8\n2: 0.6\n3: 0.9"
        scores = discriminator._parse_batch_scores(response, 3)

        assert scores == [0.8, 0.6, 0.9]

    def test_parse_missing_indices(self) -> None:
        """Default to 0.5 for missing indices."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        scores = discriminator._parse_batch_scores("1: 0.8, 3: 0.9", 4)

        assert scores == [0.8, 0.5, 0.9, 0.5]

    def test_parse_out_of_range_index(self) -> None:
        """Ignore out-of-range indices."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        scores = discriminator._parse_batch_scores("1: 0.8, 5: 0.9", 2)

        assert scores == [0.8, 0.5]

    def test_parse_invalid_score(self) -> None:
        """Handle invalid score strings gracefully."""
        llm = make_mock_llm()
        discriminator = Discriminator(llm=llm)

        scores = discriminator._parse_batch_scores("1: 0.8, 2: abc, 3: 0.9", 3)

        assert scores[0] == 0.8
        assert scores[1] == 0.5  # Default (invalid score skipped)
        assert scores[2] == 0.9


# =============================================================================
# Integration Tests
# =============================================================================


class TestDiscriminatorIntegration:
    """Integration tests for Discriminator usage patterns."""

    def test_hybrid_estimation_workflow(self) -> None:
        """Test typical hybrid estimation workflow."""
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=["0.5", "0.8", "0.3"])
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [
            make_candidate(solution="low quality"),
            make_candidate(solution="high quality"),
            make_candidate(solution="very low quality"),
        ]

        # Step 1: Quick estimates
        scores = [discriminator.estimate(task, c) for c in candidates]

        # Step 2: Filter promising candidates
        promising = [
            (c, s) for c, s in zip(candidates, scores)
            if discriminator.should_rollout(s)
        ]

        assert len(promising) == 1
        assert promising[0][1] == 0.8

    def test_batch_then_rollout_pattern(self) -> None:
        """Test batch estimate followed by selective rollouts."""
        llm = make_mock_llm("1: 0.4, 2: 0.8, 3: 0.3, 4: 0.75")
        discriminator = Discriminator(llm=llm)
        task = make_task()
        candidates = [make_candidate() for _ in range(4)]

        # Batch estimate all
        scores = discriminator.batch_estimate(task, candidates)

        # Find candidates warranting rollout
        rollout_indices = [
            i for i, s in enumerate(scores)
            if discriminator.should_rollout(s)
        ]

        assert rollout_indices == [1, 3]  # 0.8 and 0.75 >= 0.7

    def test_discriminator_without_executor(self) -> None:
        """Discriminator works without executor (LLM only)."""
        llm = make_mock_llm("0.65")
        discriminator = Discriminator(llm=llm)

        assert discriminator._executor is None

        task = make_task()
        candidate = make_candidate()
        score = discriminator.estimate(task, candidate)

        assert score == 0.65
