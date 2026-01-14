"""Tests for DirectSolver."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cognitive_core.core.types import (
    Candidate,
    Experience,
    Outcome,
    RoutingDecision,
    Step,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem
from cognitive_core.protocols.search import SearchEngine
from cognitive_core.search.direct import DirectSolver


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
        verification=VerificationSpec(method="exact_match"),
    )


def make_experience(
    exp_id: str = "exp-1",
    task_input: str = "Similar task input",
    solution_output: str = "Solution output",
    success: bool = True,
) -> Experience:
    """Create a test experience with all required fields."""
    return Experience(
        id=exp_id,
        task_input=task_input,
        solution_output=solution_output,
        feedback="Test feedback",
        success=success,
        trajectory_id="traj-1",
        timestamp=datetime.now(timezone.utc),
    )


def make_trajectory(
    task: Task,
    success: bool = True,
    steps: list[Step] | None = None,
    partial_score: float = 1.0,
) -> Trajectory:
    """Create a test trajectory."""
    if steps is None:
        steps = [
            Step(
                thought="Thinking...",
                action="test_action",
                observation="test observation result",
            )
        ]
    return Trajectory(
        task=task,
        steps=steps,
        outcome=Outcome(success=success, partial_score=partial_score),
        agent_id="test-agent",
    )


def make_routing_decision(
    experiences: list[Experience] | None = None,
    strategy: str = "direct",
    confidence: float = 0.8,
    budget: int = 5,
) -> RoutingDecision:
    """Create a routing decision with optional context."""
    context = MemoryQueryResult(experiences=experiences) if experiences else None
    return RoutingDecision(
        strategy=strategy,
        context=context,
        confidence=confidence,
        budget=budget,
    )


def make_mock_memory(
    experiences: list[Experience] | None = None,
) -> MagicMock:
    """Create a mock memory system."""
    mock = MagicMock(spec=MemorySystem)
    result = MemoryQueryResult(experiences=experiences)
    mock.query = MagicMock(return_value=result)
    return mock


def make_mock_executor(
    trajectory: Trajectory | None = None,
) -> MagicMock:
    """Create a mock TaskExecutor."""
    mock = MagicMock()
    if trajectory is None:
        task = make_task()
        trajectory = make_trajectory(task)

    # Make execute return an awaitable
    mock.execute = AsyncMock(return_value=trajectory)
    return mock


def make_mock_llm(
    response: str = "Adapted solution",
) -> MagicMock:
    """Create a mock SimpleLLM."""
    mock = MagicMock()
    mock.generate = MagicMock(return_value=response)
    return mock


def make_mock_environment(
    success: bool = True,
    partial_score: float = 1.0,
) -> MagicMock:
    """Create a mock environment."""
    mock = MagicMock()
    outcome = Outcome(success=success, partial_score=partial_score)
    mock.verify = MagicMock(return_value=outcome)
    return mock


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestDirectSolverProtocol:
    """Tests for DirectSolver protocol compliance."""

    def test_implements_search_engine_protocol(self) -> None:
        """DirectSolver implements SearchEngine protocol."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor)
        assert isinstance(solver, SearchEngine)

    def test_has_search_method(self) -> None:
        """Has search method."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor)
        assert hasattr(solver, "search")
        assert callable(solver.search)

    def test_has_refine_method(self) -> None:
        """Has refine method."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor)
        assert hasattr(solver, "refine")
        assert callable(solver.refine)

    def test_has_name_property(self) -> None:
        """Has name property."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor)
        assert hasattr(solver, "name")
        assert solver.name == "direct"


# =============================================================================
# Search Method Tests
# =============================================================================


class TestDirectSolverSearch:
    """Tests for search method."""

    def test_search_returns_list_of_candidates(self) -> None:
        """Search returns a list of Candidates."""
        memory = make_mock_memory(experiences=[make_experience()])
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=[make_experience()])

        result = solver.search(task, routing, env)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(c, Candidate) for c in result)

    def test_search_uses_experiences_from_routing_context(self) -> None:
        """Search uses experiences from routing.context."""
        experiences = [make_experience()]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # Memory should not be queried since context has experiences
        memory.query.assert_not_called()

    def test_search_queries_memory_when_context_empty(self) -> None:
        """Search queries memory when routing.context is empty."""
        experiences = [make_experience()]
        memory = make_mock_memory(experiences=experiences)
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision()  # No experiences in context

        solver.search(task, routing, env)

        memory.query.assert_called_once_with(task)

    def test_search_verifies_adapted_solutions(self) -> None:
        """Search verifies adapted solutions via environment."""
        experiences = [make_experience()]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # Environment verify should be called
        env.verify.assert_called()

    def test_search_returns_immediately_on_success(self) -> None:
        """Search returns immediately when verification succeeds."""
        experiences = [
            make_experience("exp-1", solution_output="solution1"),
            make_experience("exp-2", solution_output="solution2"),
        ]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment(success=True)
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        # Should return after first successful verification
        assert len(result) == 1
        assert env.verify.call_count == 1

    def test_search_tries_all_experiences_on_failure(self) -> None:
        """Search tries all experiences when none succeed."""
        experiences = [
            make_experience("exp-1", solution_output="solution1"),
            make_experience("exp-2", solution_output="solution2"),
            make_experience("exp-3", solution_output="solution3"),
        ]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment(success=False, partial_score=0.5)
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        # Should try all experiences
        assert env.verify.call_count == 3
        # Should return all candidates
        assert len(result) == 3

    def test_search_returns_candidates_sorted_by_fitness(self) -> None:
        """Search returns candidates sorted by fitness when all fail."""
        experiences = [
            make_experience("exp-1"),
            make_experience("exp-2"),
        ]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = MagicMock()
        # First returns low score, second returns high score
        env.verify = MagicMock(
            side_effect=[
                Outcome(success=False, partial_score=0.3),
                Outcome(success=False, partial_score=0.8),
            ]
        )
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        # Should be sorted by fitness descending
        assert result[0].fitness == 0.8
        assert result[1].fitness == 0.3


# =============================================================================
# Empty Memory Fallback Tests
# =============================================================================


class TestDirectSolverEmptyMemoryFallback:
    """Tests for empty memory fallback to TaskExecutor."""

    def test_falls_back_to_executor_when_no_experiences(self) -> None:
        """Falls back to TaskExecutor when memory is empty."""
        memory = make_mock_memory(experiences=[])
        task = make_task()
        trajectory = make_trajectory(task, success=True, partial_score=0.8)
        executor = make_mock_executor(trajectory)
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        routing = make_routing_decision(experiences=[])

        with patch("asyncio.run", return_value=trajectory):
            result = solver.search(task, routing, env)

        assert len(result) == 1
        assert result[0].source == "generated"
        assert result[0].confidence == 0.5

    def test_fallback_includes_trajectory_in_candidate(self) -> None:
        """Fallback includes trajectory in candidate."""
        memory = make_mock_memory(experiences=[])
        task = make_task()
        trajectory = make_trajectory(task, success=True, partial_score=0.9)
        executor = make_mock_executor(trajectory)
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        routing = make_routing_decision(experiences=[])

        with patch("asyncio.run", return_value=trajectory):
            result = solver.search(task, routing, env)

        assert result[0].trajectory == trajectory

    def test_fallback_extracts_solution_from_trajectory(self) -> None:
        """Fallback extracts solution from trajectory steps."""
        memory = make_mock_memory(experiences=[])
        task = make_task()
        steps = [
            Step(thought="Step 1", action="action1", observation="obs1"),
            Step(thought="Step 2", action="action2", observation="final_solution"),
        ]
        trajectory = make_trajectory(task, success=True, steps=steps)
        executor = make_mock_executor(trajectory)
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        routing = make_routing_decision(experiences=[])

        with patch("asyncio.run", return_value=trajectory):
            result = solver.search(task, routing, env)

        assert result[0].solution == "final_solution"

    def test_fallback_reasoning_indicates_no_experience(self) -> None:
        """Fallback candidate reasoning indicates no similar experience."""
        memory = make_mock_memory(experiences=[])
        task = make_task()
        trajectory = make_trajectory(task)
        executor = make_mock_executor(trajectory)
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        routing = make_routing_decision(experiences=[])

        with patch("asyncio.run", return_value=trajectory):
            result = solver.search(task, routing, env)

        assert "without similar experience" in result[0].reasoning.lower()

    def test_fallback_handles_executor_failure(self) -> None:
        """Fallback handles TaskExecutor failure gracefully."""
        memory = make_mock_memory(experiences=[])
        task = make_task()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        routing = make_routing_decision(experiences=[])

        with patch("asyncio.run", side_effect=RuntimeError("Executor failed")):
            result = solver.search(task, routing, env)

        assert len(result) == 1
        assert result[0].confidence == 0.0
        assert "failed" in result[0].reasoning.lower()


# =============================================================================
# Solution Adaptation Tests
# =============================================================================


class TestDirectSolverAdaptation:
    """Tests for solution adaptation with LLM."""

    def test_adapts_solution_with_llm_when_provided(self) -> None:
        """Adapts solution using LLM when provided."""
        experiences = [make_experience(solution_output="original solution")]
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm(response="adapted solution")
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # LLM should be called for adaptation
        llm.generate.assert_called_once()
        # Verify should receive adapted solution
        env.verify.assert_called_with("adapted solution")

    def test_adaptation_prompt_includes_task_and_experience(self) -> None:
        """Adaptation prompt includes task description and experience."""
        experiences = [make_experience(
            task_input="Original task",
            solution_output="Original solution",
        )]
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task(description="New task description")
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # Check the prompt contains expected content
        call_args = llm.generate.call_args[0][0]
        assert "Original task" in call_args
        assert "Original solution" in call_args
        assert "New task description" in call_args

    def test_uses_solution_directly_when_no_llm(self) -> None:
        """Uses solution directly when no LLM provided."""
        experiences = [make_experience(solution_output="direct solution")]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor, llm=None)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # Verify should receive original solution
        env.verify.assert_called_with("direct solution")

    def test_falls_back_to_original_on_llm_error(self) -> None:
        """Falls back to original solution when LLM fails."""
        experiences = [make_experience(solution_output="original solution")]
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=Exception("LLM error"))
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        solver.search(task, routing, env)

        # Should fall back to original solution
        env.verify.assert_called_with("original solution")


# =============================================================================
# Refine Method Tests
# =============================================================================


class TestDirectSolverRefine:
    """Tests for refine method."""

    def test_refine_returns_candidate(self) -> None:
        """Refine returns a Candidate."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm(response="refined solution")
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Test",
            source="adapted",
        )

        result = solver.refine(candidate, "feedback", task)

        assert isinstance(result, Candidate)

    def test_refine_uses_llm_for_refinement(self) -> None:
        """Refine uses LLM to generate refined solution."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm(response="refined solution")
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Test",
            source="adapted",
        )

        result = solver.refine(candidate, "feedback", task)

        llm.generate.assert_called_once()
        assert result.solution == "refined solution"

    def test_refine_includes_feedback_in_prompt(self) -> None:
        """Refine includes feedback in the refinement prompt."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm()
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="adapted",
        )

        solver.refine(candidate, "This is my feedback", task)

        call_args = llm.generate.call_args[0][0]
        assert "This is my feedback" in call_args

    def test_refine_returns_original_when_no_llm(self) -> None:
        """Refine returns original candidate when no LLM provided."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor, llm=None)
        task = make_task()
        candidate = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Test",
            source="adapted",
        )

        result = solver.refine(candidate, "feedback", task)

        assert result == candidate

    def test_refine_reduces_confidence(self) -> None:
        """Refined candidate has slightly lower confidence."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = make_mock_llm()
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=1.0,
            reasoning="Test",
            source="adapted",
        )

        result = solver.refine(candidate, "feedback", task)

        assert result.confidence < candidate.confidence

    def test_refine_handles_llm_error(self) -> None:
        """Refine handles LLM error gracefully."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=Exception("LLM error"))
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="adapted",
        )

        result = solver.refine(candidate, "feedback", task)

        # Should return original candidate on error
        assert result == candidate


# =============================================================================
# Candidate Properties Tests
# =============================================================================


class TestDirectSolverCandidateProperties:
    """Tests for candidate properties."""

    def test_adapted_candidate_has_correct_source(self) -> None:
        """Adapted candidates have source='adapted'."""
        experiences = [make_experience()]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        assert result[0].source == "adapted"

    def test_candidate_includes_experience_id_in_reasoning(self) -> None:
        """Candidate reasoning includes experience ID."""
        experiences = [make_experience("exp-xyz")]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment()
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        assert "exp-xyz" in result[0].reasoning

    def test_candidate_fitness_from_verification(self) -> None:
        """Candidate fitness comes from verification outcome."""
        experiences = [make_experience()]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment(success=True, partial_score=0.95)
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        assert result[0].fitness == 0.95

    def test_successful_experience_has_higher_confidence(self) -> None:
        """Candidates from successful experiences have higher confidence."""
        success_exp = make_experience("exp-success", success=True)
        fail_exp = make_experience("exp-fail", success=False)
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = make_mock_environment(success=False)
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()

        # Test with successful experience
        routing1 = make_routing_decision(experiences=[success_exp])
        result1 = solver.search(task, routing1, env)
        success_confidence = result1[0].confidence

        # Test with failed experience
        routing2 = make_routing_decision(experiences=[fail_exp])
        result2 = solver.search(task, routing2, env)
        fail_confidence = result2[0].confidence

        assert success_confidence > fail_confidence


# =============================================================================
# Integration Tests
# =============================================================================


class TestDirectSolverIntegration:
    """Integration tests for DirectSolver."""

    def test_full_search_flow_with_successful_adaptation(self) -> None:
        """Full search flow with successful adaptation."""
        experiences = [make_experience(solution_output="adapted this")]
        memory = make_mock_memory(experiences=experiences)
        executor = make_mock_executor()
        llm = make_mock_llm(response="perfectly adapted solution")
        env = make_mock_environment(success=True, partial_score=1.0)
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task(description="Solve this problem")
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        # Should return single successful candidate
        assert len(result) == 1
        assert result[0].source == "adapted"
        assert result[0].fitness == 1.0
        assert result[0].solution == "perfectly adapted solution"

    def test_search_then_refine_flow(self) -> None:
        """Search followed by refinement flow."""
        experiences = [make_experience()]
        memory = make_mock_memory(experiences=experiences)
        executor = make_mock_executor()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=["initial", "refined"])
        env = make_mock_environment(success=False, partial_score=0.5)
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        # Search first
        candidates = solver.search(task, routing, env)
        assert len(candidates) > 0

        # Then refine
        refined = solver.refine(candidates[0], "Try a different approach", task)
        assert refined.solution == "refined"
        assert refined.source == "adapted"

    def test_multiple_experiences_with_mixed_results(self) -> None:
        """Multiple experiences with mixed verification results."""
        experiences = [
            make_experience("exp-1", solution_output="sol1"),
            make_experience("exp-2", solution_output="sol2"),
            make_experience("exp-3", solution_output="sol3"),
        ]
        memory = make_mock_memory()
        executor = make_mock_executor()
        env = MagicMock()
        # All fail with different scores
        env.verify = MagicMock(
            side_effect=[
                Outcome(success=False, partial_score=0.2),
                Outcome(success=False, partial_score=0.8),
                Outcome(success=False, partial_score=0.5),
            ]
        )
        solver = DirectSolver(memory=memory, executor=executor)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        result = solver.search(task, routing, env)

        # Should have all candidates sorted by fitness
        assert len(result) == 3
        assert result[0].fitness == 0.8  # Best first
        assert result[1].fitness == 0.5
        assert result[2].fitness == 0.2

    def test_name_property(self) -> None:
        """Name property returns 'direct'."""
        memory = make_mock_memory()
        executor = make_mock_executor()
        solver = DirectSolver(memory=memory, executor=executor)

        assert solver.name == "direct"
