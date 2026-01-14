"""Unit tests for ATLASSolver orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from cognitive_core.core.types import (
    Candidate,
    Outcome,
    RoutingDecision,
    Step,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.solver import ATLASSolver


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_memory() -> MagicMock:
    """Create mock MemorySystem."""
    memory = MagicMock()
    memory.query.return_value = MagicMock(
        experiences=[],
        concepts=[],
        strategies=[],
        is_empty=MagicMock(return_value=True),
    )
    memory.store.return_value = {"experience_id": "exp-123"}
    return memory


@pytest.fixture
def mock_executor() -> MagicMock:
    """Create mock TaskExecutor."""
    executor = MagicMock()
    executor.execute = AsyncMock(
        return_value=Trajectory(
            task=Task(
                id="test-task",
                domain="test",
                description="Test task",
                verification=VerificationSpec(method="test"),
            ),
            steps=[
                Step(
                    thought="Testing",
                    action="test_action()",
                    observation="Success",
                )
            ],
            outcome=Outcome(success=True, partial_score=1.0),
            agent_id="test-agent",
            timestamp=datetime.now(timezone.utc),
        )
    )
    return executor


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create mock SimpleLLM."""
    llm = MagicMock()
    llm.generate.return_value = "Adapted solution"
    return llm


@pytest.fixture
def mock_router() -> MagicMock:
    """Create mock TaskRouter."""
    router = MagicMock()
    router.route.return_value = RoutingDecision(
        strategy="direct",
        context=None,
        confidence=0.5,
        budget=5,
    )
    return router


@pytest.fixture
def mock_search() -> MagicMock:
    """Create mock SearchEngine."""
    search = MagicMock()
    search.name = "mock"
    search.search.return_value = [
        Candidate(
            solution="test solution",
            confidence=0.8,
            reasoning="Test reasoning",
            source="test",
            fitness=1.0,
        )
    ]
    return search


@pytest.fixture
def sample_task() -> Task:
    """Create sample task for testing."""
    return Task(
        id="task-001",
        domain="test",
        description="A test task",
        verification=VerificationSpec(method="test"),
    )


@pytest.fixture
def solver(
    mock_memory: MagicMock,
    mock_executor: MagicMock,
    mock_llm: MagicMock,
    mock_router: MagicMock,
    mock_search: MagicMock,
) -> ATLASSolver:
    """Create ATLASSolver with mocked dependencies."""
    return ATLASSolver(
        memory=mock_memory,
        executor=mock_executor,
        llm=mock_llm,
        router=mock_router,
        search=mock_search,
    )


# =============================================================================
# Initialization Tests
# =============================================================================


class TestATLASSolverInit:
    """Tests for ATLASSolver initialization."""

    def test_init_with_all_components(
        self,
        mock_memory: MagicMock,
        mock_executor: MagicMock,
        mock_llm: MagicMock,
        mock_router: MagicMock,
        mock_search: MagicMock,
    ) -> None:
        """Initialize with all components provided."""
        solver = ATLASSolver(
            memory=mock_memory,
            executor=mock_executor,
            llm=mock_llm,
            router=mock_router,
            search=mock_search,
        )

        assert solver.memory is mock_memory
        assert solver.router is mock_router
        assert solver.search is mock_search

    def test_init_with_defaults(
        self,
        mock_memory: MagicMock,
        mock_executor: MagicMock,
    ) -> None:
        """Initialize with default router and search."""
        solver = ATLASSolver(
            memory=mock_memory,
            executor=mock_executor,
        )

        assert solver.memory is mock_memory
        # Router and search should be created
        assert solver.router is not None
        assert solver.search is not None

    def test_init_creates_basic_task_router(
        self,
        mock_memory: MagicMock,
        mock_executor: MagicMock,
    ) -> None:
        """Default router is BasicTaskRouter."""
        from cognitive_core.search import BasicTaskRouter

        solver = ATLASSolver(
            memory=mock_memory,
            executor=mock_executor,
        )

        assert isinstance(solver.router, BasicTaskRouter)

    def test_init_creates_direct_solver(
        self,
        mock_memory: MagicMock,
        mock_executor: MagicMock,
    ) -> None:
        """Default search is DirectSolver."""
        from cognitive_core.search import DirectSolver

        solver = ATLASSolver(
            memory=mock_memory,
            executor=mock_executor,
        )

        assert isinstance(solver.search, DirectSolver)


# =============================================================================
# Solve Tests
# =============================================================================


class TestATLASSolverSolve:
    """Tests for ATLASSolver.solve()."""

    def test_solve_returns_trajectory(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Solve returns a Trajectory."""
        trajectory = solver.solve(sample_task)

        assert isinstance(trajectory, Trajectory)
        assert trajectory.task == sample_task

    def test_solve_calls_router(
        self,
        solver: ATLASSolver,
        sample_task: Task,
        mock_router: MagicMock,
        mock_memory: MagicMock,
    ) -> None:
        """Solve calls router.route()."""
        solver.solve(sample_task)

        mock_router.route.assert_called_once_with(sample_task, mock_memory)

    def test_solve_calls_search(
        self,
        solver: ATLASSolver,
        sample_task: Task,
        mock_search: MagicMock,
    ) -> None:
        """Solve calls search.search()."""
        solver.solve(sample_task)

        mock_search.search.assert_called_once()
        call_args = mock_search.search.call_args
        assert call_args[0][0] == sample_task

    def test_solve_stores_trajectory(
        self,
        solver: ATLASSolver,
        sample_task: Task,
        mock_memory: MagicMock,
    ) -> None:
        """Solve stores trajectory in memory."""
        solver.solve(sample_task)

        mock_memory.store.assert_called_once()
        stored = mock_memory.store.call_args[0][0]
        assert isinstance(stored, Trajectory)

    def test_solve_with_custom_environment(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Solve uses provided environment."""
        mock_env = MagicMock()
        mock_env.reset.return_value = sample_task.description
        mock_env.verify.return_value = Outcome(success=True, partial_score=1.0)

        trajectory = solver.solve(sample_task, env=mock_env)

        mock_env.reset.assert_called_once_with(sample_task)
        assert isinstance(trajectory, Trajectory)

    def test_solve_creates_environment_if_none(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Solve creates environment based on task domain."""
        with patch("cognitive_core.solver.create_environment") as mock_create:
            mock_env = MagicMock()
            mock_env.reset.return_value = sample_task.description
            mock_create.return_value = mock_env

            solver.solve(sample_task)

            mock_create.assert_called_once_with(sample_task)

    def test_solve_raises_on_no_candidates(
        self,
        solver: ATLASSolver,
        sample_task: Task,
        mock_search: MagicMock,
    ) -> None:
        """Solve raises ValueError if no candidates."""
        mock_search.search.return_value = []

        with pytest.raises(ValueError, match="No candidates"):
            solver.solve(sample_task)


# =============================================================================
# Candidate Selection Tests
# =============================================================================


class TestCandidateSelection:
    """Tests for candidate selection logic."""

    def test_select_best_prefers_successful(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Selection prefers successful candidates."""
        successful = Candidate(
            solution="success",
            confidence=0.8,
            reasoning="Successful",
            source="test",
            fitness=0.8,
            trajectory=Trajectory(
                task=Task(
                    id="t",
                    domain="test",
                    description="T",
                    verification=VerificationSpec(method="test"),
                ),
                steps=[],
                outcome=Outcome(success=True, partial_score=0.8),
                agent_id="test",
                timestamp=datetime.now(timezone.utc),
            ),
        )
        partial = Candidate(
            solution="partial",
            confidence=0.9,
            reasoning="Partial",
            source="test",
            fitness=0.9,  # Higher fitness but not successful
        )

        best = solver._select_best([partial, successful])

        assert best.solution == "success"

    def test_select_best_uses_fitness_among_successful(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Selection uses fitness among successful candidates."""
        task = Task(
            id="t",
            domain="test",
            description="T",
            verification=VerificationSpec(method="test"),
        )

        lower = Candidate(
            solution="lower",
            confidence=0.8,
            reasoning="Lower fitness",
            source="test",
            fitness=0.7,
            trajectory=Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=True, partial_score=0.7),
                agent_id="test",
                timestamp=datetime.now(timezone.utc),
            ),
        )
        higher = Candidate(
            solution="higher",
            confidence=0.8,
            reasoning="Higher fitness",
            source="test",
            fitness=0.9,
            trajectory=Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=True, partial_score=0.9),
                agent_id="test",
                timestamp=datetime.now(timezone.utc),
            ),
        )

        best = solver._select_best([lower, higher])

        assert best.solution == "higher"

    def test_select_best_returns_best_partial_on_no_success(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Selection returns best partial if no successful candidates."""
        lower = Candidate(
            solution="lower",
            confidence=0.8,
            reasoning="Lower",
            source="test",
            fitness=0.3,
        )
        higher = Candidate(
            solution="higher",
            confidence=0.8,
            reasoning="Higher",
            source="test",
            fitness=0.7,
        )

        best = solver._select_best([lower, higher])

        assert best.solution == "higher"

    def test_select_best_handles_none_fitness(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Selection handles candidates with None fitness."""
        none_fitness = Candidate(
            solution="none",
            confidence=0.8,
            reasoning="None fitness",
            source="test",
            fitness=None,
        )
        has_fitness = Candidate(
            solution="has",
            confidence=0.8,
            reasoning="Has fitness",
            source="test",
            fitness=0.5,
        )

        best = solver._select_best([none_fitness, has_fitness])

        assert best.solution == "has"


# =============================================================================
# Batch Solve Tests
# =============================================================================


class TestATLASSolverBatch:
    """Tests for ATLASSolver.solve_batch()."""

    def test_solve_batch_returns_trajectories(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Batch solve returns list of trajectories."""
        tasks = [
            Task(
                id=f"task-{i}",
                domain="test",
                description=f"Task {i}",
                verification=VerificationSpec(method="test"),
            )
            for i in range(3)
        ]

        trajectories = solver.solve_batch(tasks)

        assert len(trajectories) == 3
        assert all(isinstance(t, Trajectory) for t in trajectories)

    def test_solve_batch_with_environments(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Batch solve uses provided environments."""
        tasks = [
            Task(
                id=f"task-{i}",
                domain="test",
                description=f"Task {i}",
                verification=VerificationSpec(method="test"),
            )
            for i in range(2)
        ]
        envs = [MagicMock(), MagicMock()]
        for env in envs:
            env.reset.return_value = "reset"
            env.verify.return_value = Outcome(success=True)

        trajectories = solver.solve_batch(tasks, envs)

        assert len(trajectories) == 2
        envs[0].reset.assert_called_once_with(tasks[0])
        envs[1].reset.assert_called_once_with(tasks[1])

    def test_solve_batch_validates_env_length(
        self,
        solver: ATLASSolver,
    ) -> None:
        """Batch solve raises if env count doesn't match tasks."""
        tasks = [
            Task(
                id=f"task-{i}",
                domain="test",
                description=f"Task {i}",
                verification=VerificationSpec(method="test"),
            )
            for i in range(3)
        ]
        envs = [MagicMock()]  # Only 1 env for 3 tasks

        with pytest.raises(ValueError, match="Number of environments"):
            solver.solve_batch(tasks, envs)

    def test_solve_batch_handles_failures(
        self,
        solver: ATLASSolver,
        mock_search: MagicMock,
    ) -> None:
        """Batch solve handles individual task failures gracefully."""
        tasks = [
            Task(
                id=f"task-{i}",
                domain="test",
                description=f"Task {i}",
                verification=VerificationSpec(method="test"),
            )
            for i in range(3)
        ]

        # Second task will fail
        def search_side_effect(task, routing, env):
            if task.id == "task-1":
                return []  # Will raise ValueError
            return [
                Candidate(
                    solution="ok",
                    confidence=0.8,
                    reasoning="ok",
                    source="test",
                    fitness=1.0,
                )
            ]

        mock_search.search.side_effect = search_side_effect

        trajectories = solver.solve_batch(tasks)

        # Should have 3 trajectories even with one failure
        assert len(trajectories) == 3
        # Failed task should have failure trajectory
        assert trajectories[1].outcome.success is False


# =============================================================================
# Factory Method Tests
# =============================================================================


class TestATLASSolverFactory:
    """Tests for ATLASSolver.create_default()."""

    def test_create_default_with_no_args(self) -> None:
        """Create default solver without arguments."""
        solver = ATLASSolver.create_default()

        assert solver.memory is not None
        assert solver.router is not None
        assert solver.search is not None

    def test_create_default_with_memory(
        self,
        mock_memory: MagicMock,
    ) -> None:
        """Create default solver with custom memory."""
        solver = ATLASSolver.create_default(memory=mock_memory)

        assert solver.memory is mock_memory

    def test_create_default_with_executor(
        self,
        mock_executor: MagicMock,
    ) -> None:
        """Create default solver with custom executor."""
        solver = ATLASSolver.create_default(executor=mock_executor)

        assert solver._executor is mock_executor

    def test_create_default_mock_executor_raises(self) -> None:
        """Default mock executor raises NotImplementedError."""
        solver = ATLASSolver.create_default()

        # The mock executor should raise when called
        with pytest.raises(NotImplementedError, match="Default mock executor"):
            import asyncio
            asyncio.run(solver._executor.execute(None, None))


# =============================================================================
# Trajectory Building Tests
# =============================================================================


class TestTrajectoryBuilding:
    """Tests for trajectory building from candidates."""

    def test_build_trajectory_uses_candidate_trajectory(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Build uses existing trajectory from candidate."""
        existing = Trajectory(
            task=sample_task,
            steps=[Step(thought="T", action="A", observation="O")],
            outcome=Outcome(success=True, partial_score=1.0),
            agent_id="test",
            timestamp=datetime.now(timezone.utc),
        )
        candidate = Candidate(
            solution="sol",
            confidence=0.9,
            reasoning="R",
            source="test",
            fitness=1.0,
            trajectory=existing,
        )
        routing = RoutingDecision(
            strategy="direct",
            confidence=0.8,
            budget=5,
        )

        result = solver._build_trajectory(sample_task, candidate, routing)

        assert result is existing

    def test_build_trajectory_creates_new_if_none(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Build creates new trajectory if candidate has none."""
        candidate = Candidate(
            solution="my solution",
            confidence=0.9,
            reasoning="My reasoning",
            source="test",
            fitness=0.8,
        )
        routing = RoutingDecision(
            strategy="direct",
            confidence=0.7,
            budget=5,
        )

        result = solver._build_trajectory(sample_task, candidate, routing)

        assert result.task == sample_task
        assert len(result.steps) == 1
        assert result.outcome.partial_score == 0.8
        assert result.metadata["routing_strategy"] == "direct"

    def test_build_trajectory_success_from_fitness(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Build determines success from fitness >= 1.0."""
        candidate = Candidate(
            solution="sol",
            confidence=0.9,
            reasoning="R",
            source="test",
            fitness=1.0,
        )
        routing = RoutingDecision(strategy="direct", confidence=0.8, budget=5)

        result = solver._build_trajectory(sample_task, candidate, routing)

        assert result.outcome.success is True

    def test_build_trajectory_failure_from_low_fitness(
        self,
        solver: ATLASSolver,
        sample_task: Task,
    ) -> None:
        """Build determines failure from fitness < 1.0."""
        candidate = Candidate(
            solution="sol",
            confidence=0.9,
            reasoning="R",
            source="test",
            fitness=0.5,
        )
        routing = RoutingDecision(strategy="direct", confidence=0.8, budget=5)

        result = solver._build_trajectory(sample_task, candidate, routing)

        assert result.outcome.success is False


# =============================================================================
# Properties Tests
# =============================================================================


class TestATLASSolverProperties:
    """Tests for ATLASSolver properties."""

    def test_memory_property(
        self,
        solver: ATLASSolver,
        mock_memory: MagicMock,
    ) -> None:
        """Memory property returns memory system."""
        assert solver.memory is mock_memory

    def test_router_property(
        self,
        solver: ATLASSolver,
        mock_router: MagicMock,
    ) -> None:
        """Router property returns task router."""
        assert solver.router is mock_router

    def test_search_property(
        self,
        solver: ATLASSolver,
        mock_search: MagicMock,
    ) -> None:
        """Search property returns search engine."""
        assert solver.search is mock_search
