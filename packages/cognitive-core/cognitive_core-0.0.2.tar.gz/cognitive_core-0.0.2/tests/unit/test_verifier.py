"""Tests for Verifier implementations."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from cognitive_core.core.types import Candidate, Outcome, Task, VerificationSpec
from cognitive_core.protocols.search import Verifier
from cognitive_core.search.verifier import ExactMatchVerifier, SimpleVerifier


# =============================================================================
# Test Fixtures
# =============================================================================


def make_task(
    task_id: str = "test-1",
    description: str = "Test task",
    expected: Any = None,
) -> Task:
    """Create a test task with all required fields."""
    config = {"expected": expected} if expected is not None else {}
    return Task(
        id=task_id,
        description=description,
        domain="test",
        verification=VerificationSpec(method="exact_match", config=config),
    )


def make_candidate(
    solution: Any = "test_solution",
    confidence: float = 0.8,
    fitness: float | None = None,
) -> Candidate:
    """Create a test candidate with all required fields."""
    return Candidate(
        solution=solution,
        confidence=confidence,
        reasoning="Test reasoning",
        source="generated",
        fitness=fitness,
    )


def make_mock_environment(outcome: Outcome | None = None) -> MagicMock:
    """Create a mock environment that returns the given outcome."""
    env = MagicMock()
    if outcome is None:
        outcome = Outcome(success=True, partial_score=1.0)
    env.verify = MagicMock(return_value=outcome)
    return env


# =============================================================================
# SimpleVerifier Tests
# =============================================================================


class TestSimpleVerifierProtocol:
    """Tests for SimpleVerifier protocol compliance."""

    def test_implements_verifier_protocol(self) -> None:
        """SimpleVerifier implements Verifier protocol."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        assert isinstance(verifier, Verifier)

    def test_has_verify_method(self) -> None:
        """Has verify method."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        assert hasattr(verifier, "verify")
        assert callable(verifier.verify)

    def test_has_rank_method(self) -> None:
        """Has rank method."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        assert hasattr(verifier, "rank")
        assert callable(verifier.rank)

    def test_has_batch_verify_method(self) -> None:
        """Has batch_verify method."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        assert hasattr(verifier, "batch_verify")
        assert callable(verifier.batch_verify)

    def test_has_supports_partial_scoring_property(self) -> None:
        """Has supports_partial_scoring property."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        assert hasattr(verifier, "supports_partial_scoring")


class TestSimpleVerifierVerify:
    """Tests for SimpleVerifier.verify()."""

    def test_verify_delegates_to_environment(self) -> None:
        """Verify delegates to environment.verify()."""
        outcome = Outcome(success=True, partial_score=0.95)
        env = make_mock_environment(outcome)
        verifier = SimpleVerifier(env)
        task = make_task()
        candidate = make_candidate(solution="my_solution")

        result = verifier.verify(task, candidate)

        assert result == outcome
        env.verify.assert_called_once_with("my_solution")

    def test_verify_returns_environment_success(self) -> None:
        """Verify returns success from environment."""
        outcome = Outcome(success=True, partial_score=1.0)
        env = make_mock_environment(outcome)
        verifier = SimpleVerifier(env)
        task = make_task()
        candidate = make_candidate()

        result = verifier.verify(task, candidate)

        assert result.success is True

    def test_verify_returns_environment_failure(self) -> None:
        """Verify returns failure from environment."""
        outcome = Outcome(success=False, partial_score=0.0, error_info="Failed")
        env = make_mock_environment(outcome)
        verifier = SimpleVerifier(env)
        task = make_task()
        candidate = make_candidate()

        result = verifier.verify(task, candidate)

        assert result.success is False
        assert result.error_info == "Failed"

    def test_verify_passes_solution_not_candidate(self) -> None:
        """Verify passes candidate.solution to environment, not the whole candidate."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        task = make_task()
        solution_data = {"grid": [[1, 2], [3, 4]]}
        candidate = make_candidate(solution=solution_data)

        verifier.verify(task, candidate)

        env.verify.assert_called_once_with(solution_data)


class TestSimpleVerifierRank:
    """Tests for SimpleVerifier.rank()."""

    def test_rank_returns_candidates_with_fitness(self) -> None:
        """Rank returns candidates with their fitness scores."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        task = make_task()
        candidates = [
            make_candidate(solution="a", fitness=0.5),
            make_candidate(solution="b", fitness=0.8),
            make_candidate(solution="c", fitness=0.3),
        ]

        result = verifier.rank(task, candidates)

        assert len(result) == 3
        # Should be sorted by fitness descending
        assert result[0][0].solution == "b"
        assert result[0][1] == 0.8
        assert result[1][0].solution == "a"
        assert result[1][1] == 0.5
        assert result[2][0].solution == "c"
        assert result[2][1] == 0.3

    def test_rank_handles_none_fitness(self) -> None:
        """Rank treats None fitness as 0.0."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        task = make_task()
        candidates = [
            make_candidate(solution="a", fitness=None),
            make_candidate(solution="b", fitness=0.5),
        ]

        result = verifier.rank(task, candidates)

        assert result[0][0].solution == "b"
        assert result[0][1] == 0.5
        assert result[1][0].solution == "a"
        assert result[1][1] == 0.0

    def test_rank_empty_list(self) -> None:
        """Rank handles empty candidate list."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        task = make_task()

        result = verifier.rank(task, [])

        assert result == []


class TestSimpleVerifierBatchVerify:
    """Tests for SimpleVerifier.batch_verify()."""

    def test_batch_verify_all_candidates(self) -> None:
        """Batch verify calls verify for each candidate."""
        outcome = Outcome(success=True, partial_score=1.0)
        env = make_mock_environment(outcome)
        verifier = SimpleVerifier(env)
        task = make_task()
        candidates = [
            make_candidate(solution="a"),
            make_candidate(solution="b"),
            make_candidate(solution="c"),
        ]

        results = verifier.batch_verify(task, candidates)

        assert len(results) == 3
        assert all(r.success for r in results)
        assert env.verify.call_count == 3

    def test_batch_verify_preserves_order(self) -> None:
        """Batch verify returns results in same order as candidates."""
        env = MagicMock()
        outcomes = [
            Outcome(success=True, partial_score=1.0),
            Outcome(success=False, partial_score=0.0),
            Outcome(success=True, partial_score=0.5),
        ]
        env.verify = MagicMock(side_effect=outcomes)
        verifier = SimpleVerifier(env)
        task = make_task()
        candidates = [
            make_candidate(solution="a"),
            make_candidate(solution="b"),
            make_candidate(solution="c"),
        ]

        results = verifier.batch_verify(task, candidates)

        assert results[0].success is True
        assert results[0].partial_score == 1.0
        assert results[1].success is False
        assert results[2].partial_score == 0.5

    def test_batch_verify_empty_list(self) -> None:
        """Batch verify handles empty candidate list."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)
        task = make_task()

        results = verifier.batch_verify(task, [])

        assert results == []


class TestSimpleVerifierProperties:
    """Tests for SimpleVerifier properties."""

    def test_supports_partial_scoring_is_true(self) -> None:
        """supports_partial_scoring returns True."""
        env = make_mock_environment()
        verifier = SimpleVerifier(env)

        assert verifier.supports_partial_scoring is True


# =============================================================================
# ExactMatchVerifier Tests
# =============================================================================


class TestExactMatchVerifierProtocol:
    """Tests for ExactMatchVerifier protocol compliance."""

    def test_implements_verifier_protocol(self) -> None:
        """ExactMatchVerifier implements Verifier protocol."""
        verifier = ExactMatchVerifier()
        assert isinstance(verifier, Verifier)

    def test_has_verify_method(self) -> None:
        """Has verify method."""
        verifier = ExactMatchVerifier()
        assert hasattr(verifier, "verify")
        assert callable(verifier.verify)

    def test_has_rank_method(self) -> None:
        """Has rank method."""
        verifier = ExactMatchVerifier()
        assert hasattr(verifier, "rank")
        assert callable(verifier.rank)

    def test_has_batch_verify_method(self) -> None:
        """Has batch_verify method."""
        verifier = ExactMatchVerifier()
        assert hasattr(verifier, "batch_verify")
        assert callable(verifier.batch_verify)

    def test_has_supports_partial_scoring_property(self) -> None:
        """Has supports_partial_scoring property."""
        verifier = ExactMatchVerifier()
        assert hasattr(verifier, "supports_partial_scoring")


class TestExactMatchVerifierVerify:
    """Tests for ExactMatchVerifier.verify()."""

    def test_verify_exact_string_match_success(self) -> None:
        """Verify returns success when string matches exactly."""
        verifier = ExactMatchVerifier()
        task = make_task(expected="hello world")
        candidate = make_candidate(solution="hello world")

        result = verifier.verify(task, candidate)

        assert result.success is True
        assert result.partial_score == 1.0

    def test_verify_exact_string_match_failure(self) -> None:
        """Verify returns failure when string doesn't match."""
        verifier = ExactMatchVerifier()
        task = make_task(expected="hello world")
        candidate = make_candidate(solution="goodbye world")

        result = verifier.verify(task, candidate)

        assert result.success is False
        assert result.partial_score == 0.0

    def test_verify_exact_int_match_success(self) -> None:
        """Verify returns success when int matches exactly."""
        verifier = ExactMatchVerifier()
        task = make_task(expected=42)
        candidate = make_candidate(solution=42)

        result = verifier.verify(task, candidate)

        assert result.success is True

    def test_verify_exact_list_match_success(self) -> None:
        """Verify returns success when list matches exactly."""
        verifier = ExactMatchVerifier()
        expected_list = [1, 2, 3]
        task = make_task(expected=expected_list)
        candidate = make_candidate(solution=[1, 2, 3])

        result = verifier.verify(task, candidate)

        assert result.success is True

    def test_verify_exact_dict_match_success(self) -> None:
        """Verify returns success when dict matches exactly."""
        verifier = ExactMatchVerifier()
        expected_dict = {"a": 1, "b": 2}
        task = make_task(expected=expected_dict)
        candidate = make_candidate(solution={"a": 1, "b": 2})

        result = verifier.verify(task, candidate)

        assert result.success is True

    def test_verify_no_expected_value_matches_none(self) -> None:
        """Verify matches None when no expected value provided."""
        verifier = ExactMatchVerifier()
        task = make_task()  # No expected value
        candidate = make_candidate(solution=None)

        result = verifier.verify(task, candidate)

        assert result.success is True

    def test_verify_no_expected_value_fails_for_non_none(self) -> None:
        """Verify fails when no expected value but candidate has solution."""
        verifier = ExactMatchVerifier()
        task = make_task()  # No expected value
        candidate = make_candidate(solution="something")

        result = verifier.verify(task, candidate)

        assert result.success is False

    def test_verify_case_sensitive(self) -> None:
        """Verify is case sensitive for strings."""
        verifier = ExactMatchVerifier()
        task = make_task(expected="Hello")
        candidate = make_candidate(solution="hello")

        result = verifier.verify(task, candidate)

        assert result.success is False

    def test_verify_type_sensitive(self) -> None:
        """Verify distinguishes between types."""
        verifier = ExactMatchVerifier()
        task = make_task(expected=42)
        candidate = make_candidate(solution="42")

        result = verifier.verify(task, candidate)

        assert result.success is False


class TestExactMatchVerifierRank:
    """Tests for ExactMatchVerifier.rank()."""

    def test_rank_returns_candidates_with_fitness(self) -> None:
        """Rank returns candidates with their fitness scores."""
        verifier = ExactMatchVerifier()
        task = make_task()
        candidates = [
            make_candidate(solution="a", fitness=0.7),
            make_candidate(solution="b", fitness=0.9),
        ]

        result = verifier.rank(task, candidates)

        assert len(result) == 2
        assert result[0][0].solution == "b"
        assert result[0][1] == 0.9

    def test_rank_handles_none_fitness(self) -> None:
        """Rank treats None fitness as 0.0."""
        verifier = ExactMatchVerifier()
        task = make_task()
        candidates = [
            make_candidate(solution="a", fitness=None),
            make_candidate(solution="b", fitness=0.5),
        ]

        result = verifier.rank(task, candidates)

        assert result[0][1] == 0.5
        assert result[1][1] == 0.0


class TestExactMatchVerifierBatchVerify:
    """Tests for ExactMatchVerifier.batch_verify()."""

    def test_batch_verify_multiple_candidates(self) -> None:
        """Batch verify checks all candidates against expected."""
        verifier = ExactMatchVerifier()
        task = make_task(expected="correct")
        candidates = [
            make_candidate(solution="correct"),
            make_candidate(solution="wrong"),
            make_candidate(solution="correct"),
        ]

        results = verifier.batch_verify(task, candidates)

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    def test_batch_verify_empty_list(self) -> None:
        """Batch verify handles empty candidate list."""
        verifier = ExactMatchVerifier()
        task = make_task()

        results = verifier.batch_verify(task, [])

        assert results == []


class TestExactMatchVerifierProperties:
    """Tests for ExactMatchVerifier properties."""

    def test_supports_partial_scoring_is_true(self) -> None:
        """supports_partial_scoring returns True."""
        verifier = ExactMatchVerifier()

        assert verifier.supports_partial_scoring is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestVerifierIntegration:
    """Integration tests for verifier usage patterns."""

    def test_simple_verifier_best_of_k_selection(self) -> None:
        """SimpleVerifier can be used for best-of-k selection."""
        # Create environment that returns different scores
        env = MagicMock()
        outcomes = [
            Outcome(success=True, partial_score=0.7),
            Outcome(success=True, partial_score=0.9),
            Outcome(success=False, partial_score=0.3),
        ]
        env.verify = MagicMock(side_effect=outcomes)

        verifier = SimpleVerifier(env)
        task = make_task()
        candidates = [
            make_candidate(solution="a"),
            make_candidate(solution="b"),
            make_candidate(solution="c"),
        ]

        # Batch verify all candidates
        results = verifier.batch_verify(task, candidates)

        # Select best candidate
        best_idx = max(
            range(len(results)),
            key=lambda i: results[i].partial_score or 0.0,
        )

        assert best_idx == 1  # Solution "b" has highest score

    def test_exact_match_verifier_for_simple_tasks(self) -> None:
        """ExactMatchVerifier works for simple equality tasks."""
        verifier = ExactMatchVerifier()

        # Simulate a simple math task
        task = make_task(expected=10)  # 5 + 5 = 10
        correct = make_candidate(solution=10)
        wrong = make_candidate(solution=11)

        correct_result = verifier.verify(task, correct)
        wrong_result = verifier.verify(task, wrong)

        assert correct_result.success is True
        assert wrong_result.success is False

    def test_verifiers_work_with_complex_solutions(self) -> None:
        """Verifiers handle complex solution types."""
        # ARC-style grid solution
        grid = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]

        verifier = ExactMatchVerifier()
        task = make_task(expected=grid)
        candidate = make_candidate(solution=[[1, 0, 1], [0, 1, 0], [1, 0, 1]])

        result = verifier.verify(task, candidate)

        assert result.success is True
