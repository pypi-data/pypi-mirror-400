"""ATLASSolver: Top-level orchestrator for the ATLAS system.

Combines memory, routing, search, and verification into a complete solving pipeline.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cognitive_core.core.types import Candidate, Outcome, Step, Trajectory
from cognitive_core.environments import PassthroughEnvironment, create_environment
from cognitive_core.search import BasicTaskRouter, DirectSolver

if TYPE_CHECKING:
    from cognitive_core.core.types import RoutingDecision, Task
    from cognitive_core.execution.executor import TaskExecutor
    from cognitive_core.llm.simple import SimpleLLM
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemorySystem
    from cognitive_core.protocols.search import SearchEngine, TaskRouter

logger = logging.getLogger("cognitive_core.solver")


class ATLASSolver:
    """Top-level solver combining all ATLAS components.

    ATLASSolver orchestrates the complete task-solving pipeline:
    1. Routes the task to determine search strategy
    2. Searches for candidate solutions
    3. Selects the best candidate
    4. Stores the result trajectory in memory
    5. Returns the trajectory

    Example:
        ```python
        # Create with all components
        solver = ATLASSolver(
            memory=memory_system,
            executor=task_executor,
            llm=simple_llm,
        )

        # Solve a task
        trajectory = solver.solve(task)

        # Or with custom environment
        trajectory = solver.solve(task, env=arc_environment)
        ```

    Attributes:
        memory: Memory system for storing and retrieving experiences
        router: Task router for deciding search strategy
        search: Search engine for finding solutions
    """

    def __init__(
        self,
        memory: MemorySystem,
        executor: TaskExecutor,
        llm: SimpleLLM | None = None,
        router: TaskRouter | None = None,
        search: SearchEngine | None = None,
    ) -> None:
        """Initialize ATLASSolver.

        Args:
            memory: Memory system for querying and storing trajectories.
            executor: TaskExecutor for running tasks via ACP agents.
            llm: Optional SimpleLLM for solution adaptation. Lazy-initialized
                if not provided.
            router: Optional TaskRouter for routing decisions. Defaults to
                BasicTaskRouter.
            search: Optional SearchEngine for solution search. Defaults to
                DirectSolver.
        """
        self._memory = memory
        self._executor = executor
        self._llm = llm
        self._router = router or BasicTaskRouter()
        self._search = search or DirectSolver(memory, executor, llm)

    @property
    def memory(self) -> MemorySystem:
        """Memory system used by this solver."""
        return self._memory

    @property
    def router(self) -> TaskRouter:
        """Task router used by this solver."""
        return self._router

    @property
    def search(self) -> SearchEngine:
        """Search engine used by this solver."""
        return self._search

    def solve(
        self,
        task: Task,
        env: Environment | None = None,
    ) -> Trajectory:
        """Solve a task and return the trajectory.

        Pipeline:
        1. Create environment if not provided
        2. Reset environment with task
        3. Route task to determine strategy
        4. Search for candidates
        5. Select best candidate
        6. Build trajectory from result
        7. Store trajectory in memory
        8. Return trajectory

        Args:
            task: The task to solve.
            env: Optional environment for execution. If not provided,
                creates appropriate environment based on task domain.

        Returns:
            Trajectory recording the solving attempt.

        Raises:
            ValueError: If no candidates are generated.
        """
        logger.info(
            "ATLASSolver.solve started",
            extra={"task_id": task.id, "domain": task.domain},
        )

        # Create or use provided environment
        if env is None:
            env = create_environment(task)
            logger.debug(
                "Created environment",
                extra={"type": type(env).__name__},
            )

        # Reset environment with task
        env.reset(task)
        logger.debug("Environment reset with task")

        # Route to determine strategy
        routing = self._router.route(task, self._memory)
        logger.info(
            "Task routed",
            extra={
                "strategy": routing.strategy,
                "confidence": routing.confidence,
                "budget": routing.budget,
            },
        )

        # Search for candidates
        candidates = self._search.search(task, routing, env)
        logger.info(
            "Search completed",
            extra={"num_candidates": len(candidates)},
        )

        # Select best candidate
        best = self._select_best(candidates)
        logger.info(
            "Best candidate selected",
            extra={
                "fitness": best.fitness,
                "source": best.source,
                "confidence": best.confidence,
            },
        )

        # Build trajectory
        trajectory = self._build_trajectory(task, best, routing)
        logger.info(
            "Trajectory built",
            extra={
                "success": trajectory.outcome.success,
                "partial_score": trajectory.outcome.partial_score,
            },
        )

        # Store in memory
        store_result = self._memory.store(trajectory)
        logger.info(
            "Trajectory stored",
            extra={"store_result": store_result},
        )

        return trajectory

    def solve_batch(
        self,
        tasks: list[Task],
        envs: list[Environment] | None = None,
    ) -> list[Trajectory]:
        """Solve multiple tasks.

        Processes tasks sequentially. For parallel execution, use external
        parallelization.

        Args:
            tasks: List of tasks to solve.
            envs: Optional list of environments, one per task. If not
                provided, environments are created based on task domains.

        Returns:
            List of trajectories, one per task.

        Raises:
            ValueError: If envs is provided but has different length than tasks.
        """
        if envs is not None and len(envs) != len(tasks):
            raise ValueError(
                f"Number of environments ({len(envs)}) must match "
                f"number of tasks ({len(tasks)})"
            )

        logger.info(
            "ATLASSolver.solve_batch started",
            extra={"num_tasks": len(tasks)},
        )

        trajectories: list[Trajectory] = []

        for i, task in enumerate(tasks):
            env = envs[i] if envs else None
            try:
                trajectory = self.solve(task, env)
                trajectories.append(trajectory)
            except Exception as e:
                logger.error(
                    "Task solve failed",
                    extra={"task_id": task.id, "error": str(e)},
                )
                # Create failure trajectory
                trajectory = Trajectory(
                    task=task,
                    steps=[],
                    outcome=Outcome(
                        success=False,
                        partial_score=0.0,
                        error_info=str(e),
                    ),
                    agent_id="atlas-solver",
                    timestamp=datetime.now(timezone.utc),
                )
                trajectories.append(trajectory)

        logger.info(
            "ATLASSolver.solve_batch completed",
            extra={
                "num_tasks": len(tasks),
                "num_success": sum(1 for t in trajectories if t.outcome.success),
            },
        )

        return trajectories

    @classmethod
    def create_default(
        cls,
        memory: MemorySystem | None = None,
        executor: TaskExecutor | None = None,
    ) -> ATLASSolver:
        """Create solver with default configuration.

        Creates a minimal ATLASSolver with optional memory and executor.
        Uses empty MemorySystemImpl and mock executor if not provided.

        Args:
            memory: Optional memory system. If not provided, creates empty
                MemorySystemImpl.
            executor: Optional task executor. If not provided, creates a
                mock executor.

        Returns:
            Configured ATLASSolver instance.

        Example:
            ```python
            # Simple solver with defaults
            solver = ATLASSolver.create_default()

            # Solver with custom memory
            solver = ATLASSolver.create_default(memory=my_memory)
            ```
        """
        from cognitive_core.memory.system import MemorySystemImpl

        if memory is None:
            memory = MemorySystemImpl()
            logger.debug("Created empty MemorySystemImpl")

        if executor is None:
            # Create a mock executor
            executor = _create_mock_executor()
            logger.debug("Created mock TaskExecutor")

        return cls(memory=memory, executor=executor)

    def _select_best(self, candidates: list[Candidate]) -> Candidate:
        """Select best candidate by fitness/success.

        Selection criteria:
        1. Prefer successful candidates (from trajectory outcome)
        2. Among successful, select highest fitness
        3. If no successful, select highest partial fitness

        Args:
            candidates: List of candidates to select from.

        Returns:
            The best candidate.

        Raises:
            ValueError: If no candidates are provided.
        """
        if not candidates:
            raise ValueError("No candidates generated")

        # Check for successful candidates via trajectory
        successful = [
            c for c in candidates
            if c.trajectory is not None and c.trajectory.outcome.success
        ]

        if successful:
            logger.debug(
                "Found successful candidates",
                extra={"count": len(successful)},
            )
            return max(successful, key=lambda c: c.fitness or 0.0)

        # Check for successful candidates via fitness = 1.0 as proxy
        high_fitness = [c for c in candidates if (c.fitness or 0.0) >= 1.0]
        if high_fitness:
            logger.debug(
                "Found high-fitness candidates",
                extra={"count": len(high_fitness)},
            )
            return max(high_fitness, key=lambda c: c.fitness or 0.0)

        # No success - return best partial
        logger.debug("No successful candidates, returning best partial")
        return max(candidates, key=lambda c: c.fitness or 0.0)

    def _build_trajectory(
        self,
        task: Task,
        candidate: Candidate,
        routing: RoutingDecision,
    ) -> Trajectory:
        """Build trajectory from a candidate.

        If candidate has a trajectory attached, uses that. Otherwise,
        builds a new trajectory from the candidate's solution.

        Args:
            task: The original task.
            candidate: The selected candidate.
            routing: The routing decision used.

        Returns:
            Trajectory recording the solving attempt.
        """
        # If candidate has trajectory, use it
        if candidate.trajectory is not None:
            return candidate.trajectory

        # Build trajectory from candidate
        success = (candidate.fitness or 0.0) >= 1.0

        steps = [
            Step(
                thought=f"Routing strategy: {routing.strategy}, confidence: {routing.confidence}",
                action=f"search({candidate.source})",
                observation=f"Solution: {str(candidate.solution)[:200]}...",
            )
        ]

        return Trajectory(
            task=task,
            steps=steps,
            outcome=Outcome(
                success=success,
                partial_score=candidate.fitness,
                verification_details={
                    "source": candidate.source,
                    "confidence": candidate.confidence,
                    "reasoning": candidate.reasoning,
                },
            ),
            agent_id="atlas-solver",
            timestamp=datetime.now(timezone.utc),
            metadata={
                "routing_strategy": routing.strategy,
                "routing_confidence": routing.confidence,
                "candidate_source": candidate.source,
            },
        )


def _create_mock_executor() -> Any:
    """Create a mock TaskExecutor for default configuration.

    Returns a mock that raises NotImplementedError when execute() is called,
    indicating that a real executor should be provided for actual task solving.

    Returns:
        Mock TaskExecutor instance.
    """
    from unittest.mock import MagicMock

    mock = MagicMock()

    async def mock_execute(task: Any, env: Any) -> None:
        raise NotImplementedError(
            "Default mock executor cannot execute tasks. "
            "Provide a real TaskExecutor to ATLASSolver for task solving."
        )

    mock.execute = mock_execute
    return mock
