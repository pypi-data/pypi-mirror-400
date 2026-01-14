"""Tests for MemorySystemImpl aggregator."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cognitive_core.core.types import (
    CodeConcept,
    Experience,
    Outcome,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.memory.system import MemorySystemImpl
from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem


def make_task(task_id: str = "test-1", description: str = "Test task") -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        description=description,
        domain="test",
        verification=VerificationSpec(method="exact_match"),
    )


def make_experience(
    exp_id: str = "exp-1",
    success: bool = True,
) -> Experience:
    """Create a test experience with all required fields."""
    return Experience(
        id=exp_id,
        task_input="Test input",
        solution_output="Test output",
        feedback="Test feedback",
        success=success,
        trajectory_id="traj-1",
        timestamp=datetime.now(timezone.utc),
    )


def make_concept(concept_id: str = "concept-1") -> CodeConcept:
    """Create a test concept with all required fields."""
    return CodeConcept(
        id=concept_id,
        name="Test Concept",
        description="Test description",
        code="def test(): pass",
        signature="() -> None",
    )


def make_strategy(strategy_id: str = "strategy-1") -> Strategy:
    """Create a test strategy with all required fields."""
    return Strategy(
        id=strategy_id,
        situation="When X happens",
        suggestion="Do Y",
    )


def make_trajectory(success: bool = True) -> Trajectory:
    """Create a test trajectory with all required fields."""
    return Trajectory(
        task=make_task(),
        steps=[
            Step(
                action="Test action",
                observation="Test observation",
                thought="Test thought",
            )
        ],
        outcome=Outcome(
            success=success,
            error_info=None if success else "Test error",
        ),
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
    )


class TestMemorySystemImplProtocol:
    """Tests for protocol compliance."""

    def test_implements_protocol(self) -> None:
        """MemorySystemImpl implements MemorySystem protocol."""
        system = MemorySystemImpl()
        assert isinstance(system, MemorySystem)

    def test_has_experience_memory_property(self) -> None:
        """Has experience_memory property."""
        system = MemorySystemImpl()
        assert hasattr(system, "experience_memory")
        assert system.experience_memory is None

    def test_has_concept_library_property(self) -> None:
        """Has concept_library property."""
        system = MemorySystemImpl()
        assert hasattr(system, "concept_library")
        assert system.concept_library is None

    def test_has_strategy_bank_property(self) -> None:
        """Has strategy_bank property."""
        system = MemorySystemImpl()
        assert hasattr(system, "strategy_bank")
        assert system.strategy_bank is None

    def test_has_query_method(self) -> None:
        """Has query method."""
        system = MemorySystemImpl()
        assert hasattr(system, "query")
        assert callable(system.query)

    def test_has_store_method(self) -> None:
        """Has store method."""
        system = MemorySystemImpl()
        assert hasattr(system, "store")
        assert callable(system.store)


class TestMemorySystemImplInit:
    """Tests for initialization."""

    def test_init_with_no_components(self) -> None:
        """Can initialize with no components."""
        system = MemorySystemImpl()
        assert system.experience_memory is None
        assert system.concept_library is None
        assert system.strategy_bank is None

    def test_init_with_experience_only(self) -> None:
        """Can initialize with experience memory only."""
        mock_exp = MagicMock()
        system = MemorySystemImpl(experience=mock_exp)
        assert system.experience_memory is mock_exp
        assert system.concept_library is None
        assert system.strategy_bank is None

    def test_init_with_concepts_only(self) -> None:
        """Can initialize with concept library only."""
        mock_concepts = MagicMock()
        system = MemorySystemImpl(concepts=mock_concepts)
        assert system.experience_memory is None
        assert system.concept_library is mock_concepts
        assert system.strategy_bank is None

    def test_init_with_strategies_only(self) -> None:
        """Can initialize with strategy bank only."""
        mock_strategies = MagicMock()
        system = MemorySystemImpl(strategies=mock_strategies)
        assert system.experience_memory is None
        assert system.concept_library is None
        assert system.strategy_bank is mock_strategies

    def test_init_with_all_components(self) -> None:
        """Can initialize with all components."""
        mock_exp = MagicMock()
        mock_concepts = MagicMock()
        mock_strategies = MagicMock()

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
            strategies=mock_strategies,
        )

        assert system.experience_memory is mock_exp
        assert system.concept_library is mock_concepts
        assert system.strategy_bank is mock_strategies


class TestMemorySystemImplQuery:
    """Tests for query method."""

    def test_query_with_no_components_returns_empty_result(self) -> None:
        """Query with no components returns empty result."""
        system = MemorySystemImpl()
        task = make_task()

        result = system.query(task, k=5)

        assert isinstance(result, MemoryQueryResult)
        assert result.is_empty()
        assert result.experiences == []
        assert result.concepts == []
        assert result.strategies == []

    def test_query_with_experience_memory(self) -> None:
        """Query returns experiences from experience memory."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        system = MemorySystemImpl(experience=mock_exp)
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == experiences
        mock_exp.search.assert_called_once_with(task, 5)

    def test_query_with_concept_library(self) -> None:
        """Query returns concepts from concept library."""
        mock_concepts = MagicMock()
        concepts = [make_concept()]
        mock_concepts.search = AsyncMock(return_value=concepts)

        system = MemorySystemImpl(concepts=mock_concepts)
        task = make_task()

        result = system.query(task, k=5)

        assert result.concepts == concepts
        mock_concepts.search.assert_called_once_with(task.description, k=5)

    def test_query_with_strategy_bank(self) -> None:
        """Query returns strategies from strategy bank."""
        mock_strategies = MagicMock()
        strategies = [make_strategy()]
        mock_strategies.read = AsyncMock(return_value=strategies)

        system = MemorySystemImpl(strategies=mock_strategies)
        task = make_task()

        result = system.query(task, k=5)

        assert result.strategies == strategies
        mock_strategies.read.assert_called_once_with(task, k=5)

    def test_query_with_all_components(self) -> None:
        """Query returns results from all components."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        mock_concepts = MagicMock()
        concepts = [make_concept()]
        mock_concepts.search = AsyncMock(return_value=concepts)

        mock_strategies = MagicMock()
        strategies = [make_strategy()]
        mock_strategies.read = AsyncMock(return_value=strategies)

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
            strategies=mock_strategies,
        )
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == experiences
        assert result.concepts == concepts
        assert result.strategies == strategies
        assert not result.is_empty()

    def test_query_respects_k_parameter(self) -> None:
        """Query passes k parameter to all components."""
        mock_exp = MagicMock()
        mock_exp.search = MagicMock(return_value=[])

        mock_concepts = MagicMock()
        mock_concepts.search = AsyncMock(return_value=[])

        mock_strategies = MagicMock()
        mock_strategies.read = AsyncMock(return_value=[])

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
            strategies=mock_strategies,
        )
        task = make_task()

        system.query(task, k=10)

        mock_exp.search.assert_called_once_with(task, 10)
        mock_concepts.search.assert_called_once_with(task.description, k=10)
        mock_strategies.read.assert_called_once_with(task, k=10)

    def test_query_default_k_is_5(self) -> None:
        """Query uses k=5 by default."""
        mock_exp = MagicMock()
        mock_exp.search = MagicMock(return_value=[])

        system = MemorySystemImpl(experience=mock_exp)
        task = make_task()

        system.query(task)

        mock_exp.search.assert_called_once_with(task, 5)


class TestMemorySystemImplErrorHandling:
    """Tests for error handling."""

    def test_query_handles_experience_error(self) -> None:
        """Query continues when experience memory raises error."""
        mock_exp = MagicMock()
        mock_exp.search = MagicMock(side_effect=RuntimeError("Test error"))

        mock_concepts = MagicMock()
        concepts = [make_concept()]
        mock_concepts.search = AsyncMock(return_value=concepts)

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
        )
        task = make_task()

        result = system.query(task, k=5)

        # Experience failed but concepts succeeded
        assert result.experiences == []
        assert result.concepts == concepts

    def test_query_handles_concepts_error(self) -> None:
        """Query continues when concept library raises error."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        mock_concepts = MagicMock()
        mock_concepts.search = AsyncMock(side_effect=RuntimeError("Test error"))

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
        )
        task = make_task()

        result = system.query(task, k=5)

        # Concepts failed but experiences succeeded
        assert result.experiences == experiences
        assert result.concepts == []

    def test_query_handles_strategies_error(self) -> None:
        """Query continues when strategy bank raises error."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        mock_strategies = MagicMock()
        mock_strategies.read = AsyncMock(side_effect=RuntimeError("Test error"))

        system = MemorySystemImpl(
            experience=mock_exp,
            strategies=mock_strategies,
        )
        task = make_task()

        result = system.query(task, k=5)

        # Strategies failed but experiences succeeded
        assert result.experiences == experiences
        assert result.strategies == []

    def test_query_handles_all_errors(self) -> None:
        """Query returns empty result when all components fail."""
        mock_exp = MagicMock()
        mock_exp.search = MagicMock(side_effect=RuntimeError("Exp error"))

        mock_concepts = MagicMock()
        mock_concepts.search = AsyncMock(side_effect=RuntimeError("Concepts error"))

        mock_strategies = MagicMock()
        mock_strategies.read = AsyncMock(side_effect=RuntimeError("Strategies error"))

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
            strategies=mock_strategies,
        )
        task = make_task()

        result = system.query(task, k=5)

        assert result.is_empty()


class TestMemorySystemImplStore:
    """Tests for store method."""

    def test_store_with_no_components(self) -> None:
        """Store with no components returns empty dict."""
        system = MemorySystemImpl()
        trajectory = make_trajectory()

        result = system.store(trajectory)

        assert result == {}

    def test_store_success_trajectory_in_experience_memory(self) -> None:
        """Store stores successful trajectory in experience memory."""
        mock_exp = MagicMock()
        mock_exp.store = MagicMock(return_value="exp-id-1")

        system = MemorySystemImpl(experience=mock_exp)
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        assert result["experience_id"] == "exp-id-1"
        mock_exp.store.assert_called_once_with(trajectory)

    def test_store_failure_trajectory_in_experience_memory(self) -> None:
        """Store stores failed trajectory in experience memory."""
        mock_exp = MagicMock()
        mock_exp.store = MagicMock(return_value="exp-id-2")

        system = MemorySystemImpl(experience=mock_exp)
        trajectory = make_trajectory(success=False)

        result = system.store(trajectory)

        assert result["experience_id"] == "exp-id-2"
        mock_exp.store.assert_called_once_with(trajectory)

    def test_store_success_trajectory_in_strategy_bank(self) -> None:
        """Store writes successful trajectory to strategy bank."""
        mock_strategies = MagicMock()
        strategy = make_strategy()
        mock_strategies.write = AsyncMock(return_value=strategy)

        system = MemorySystemImpl(strategies=mock_strategies)
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        assert result["strategy_id"] == "strategy-1"
        mock_strategies.write.assert_called_once_with(trajectory)

    def test_store_failure_trajectory_not_in_strategy_bank(self) -> None:
        """Store does not write failed trajectory to strategy bank."""
        mock_strategies = MagicMock()
        mock_strategies.write = AsyncMock(return_value=None)

        system = MemorySystemImpl(strategies=mock_strategies)
        trajectory = make_trajectory(success=False)

        result = system.store(trajectory)

        assert "strategy_id" not in result
        mock_strategies.write.assert_not_called()

    def test_store_strategy_returns_none(self) -> None:
        """Store handles strategy bank returning None."""
        mock_strategies = MagicMock()
        mock_strategies.write = AsyncMock(return_value=None)

        system = MemorySystemImpl(strategies=mock_strategies)
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        # No strategy_id when write returns None
        assert "strategy_id" not in result

    def test_store_with_all_components_success(self) -> None:
        """Store to all components with successful trajectory."""
        mock_exp = MagicMock()
        mock_exp.store = MagicMock(return_value="exp-id")

        mock_strategies = MagicMock()
        strategy = make_strategy(strategy_id="strategy-id")
        mock_strategies.write = AsyncMock(return_value=strategy)

        # ConceptLibrary should not be called (compression is batch)
        mock_concepts = MagicMock()
        mock_concepts.add = AsyncMock()

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
            strategies=mock_strategies,
        )
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        assert result["experience_id"] == "exp-id"
        assert result["strategy_id"] == "strategy-id"
        # ConceptLibrary.add should not be called
        mock_concepts.add.assert_not_called()

    def test_store_handles_experience_error(self) -> None:
        """Store continues when experience memory raises error."""
        mock_exp = MagicMock()
        mock_exp.store = MagicMock(side_effect=RuntimeError("Test error"))

        mock_strategies = MagicMock()
        strategy = make_strategy(strategy_id="strategy-id")
        mock_strategies.write = AsyncMock(return_value=strategy)

        system = MemorySystemImpl(
            experience=mock_exp,
            strategies=mock_strategies,
        )
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        # Experience failed but strategy succeeded
        assert "experience_id" not in result
        assert result["strategy_id"] == "strategy-id"

    def test_store_handles_strategy_error(self) -> None:
        """Store continues when strategy bank raises error."""
        mock_exp = MagicMock()
        mock_exp.store = MagicMock(return_value="exp-id")

        mock_strategies = MagicMock()
        mock_strategies.write = AsyncMock(side_effect=RuntimeError("Test error"))

        system = MemorySystemImpl(
            experience=mock_exp,
            strategies=mock_strategies,
        )
        trajectory = make_trajectory(success=True)

        result = system.store(trajectory)

        # Strategy failed but experience succeeded
        assert result["experience_id"] == "exp-id"
        assert "strategy_id" not in result


class TestMemorySystemImplAblation:
    """Tests for ablation study configurations."""

    def test_experience_only_ablation(self) -> None:
        """Test experience-only ablation configuration."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        system = MemorySystemImpl(experience=mock_exp)
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == experiences
        assert result.concepts == []
        assert result.strategies == []

    def test_concepts_only_ablation(self) -> None:
        """Test concepts-only ablation configuration."""
        mock_concepts = MagicMock()
        concepts = [make_concept()]
        mock_concepts.search = AsyncMock(return_value=concepts)

        system = MemorySystemImpl(concepts=mock_concepts)
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == []
        assert result.concepts == concepts
        assert result.strategies == []

    def test_strategies_only_ablation(self) -> None:
        """Test strategies-only ablation configuration."""
        mock_strategies = MagicMock()
        strategies = [make_strategy()]
        mock_strategies.read = AsyncMock(return_value=strategies)

        system = MemorySystemImpl(strategies=mock_strategies)
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == []
        assert result.concepts == []
        assert result.strategies == strategies

    def test_experience_concepts_ablation(self) -> None:
        """Test experience+concepts ablation (no strategies)."""
        mock_exp = MagicMock()
        experiences = [make_experience()]
        mock_exp.search = MagicMock(return_value=experiences)

        mock_concepts = MagicMock()
        concepts = [make_concept()]
        mock_concepts.search = AsyncMock(return_value=concepts)

        system = MemorySystemImpl(
            experience=mock_exp,
            concepts=mock_concepts,
        )
        task = make_task()

        result = system.query(task, k=5)

        assert result.experiences == experiences
        assert result.concepts == concepts
        assert result.strategies == []
