"""DirectSolver for ATLAS (Phase 4).

DirectSolver retrieves similar experiences from memory, adapts solutions
using SimpleLLM, and verifies results via the environment.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from cognitive_core.core.types import Candidate, Outcome, Trajectory

if TYPE_CHECKING:
    from cognitive_core.core.types import Experience, RoutingDecision, Task
    from cognitive_core.execution.executor import TaskExecutor
    from cognitive_core.llm.simple import SimpleLLM
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem

logger = logging.getLogger("cognitive_core.search.direct")


class DirectSolver:
    """Direct solver for high-confidence memory matches.

    DirectSolver implements the SearchEngine protocol. It:
    1. Retrieves similar experiences from memory (via routing.context)
    2. Adapts solutions using SimpleLLM (if provided)
    3. Verifies results via the environment
    4. Falls back to pure TaskExecutor generation when memory is empty

    Example:
        ```python
        solver = DirectSolver(memory=memory, executor=executor, llm=llm)
        candidates = solver.search(task, routing, env)
        best = max(candidates, key=lambda c: c.fitness or 0)
        ```
    """

    def __init__(
        self,
        memory: MemorySystem,
        executor: TaskExecutor,
        llm: SimpleLLM | None = None,
    ) -> None:
        """Initialize DirectSolver.

        Args:
            memory: Memory system for querying similar experiences.
            executor: TaskExecutor for running tasks via ACP agents.
            llm: Optional SimpleLLM for solution adaptation. If not provided,
                retrieved solutions are used directly without adaptation.
        """
        self._memory = memory
        self._executor = executor
        self._llm = llm

    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Search for candidate solutions.

        Algorithm:
        1. Get experiences from routing.context (or query memory if empty)
        2. For each experience (by similarity):
           a. Create adaptation prompt
           b. Adapt solution using LLM (or use directly if no LLM)
           c. Verify via env.verify()
           d. If success, return candidate
        3. If no experiences, fall back to TaskExecutor execution
        4. Return best partial result(s)

        Args:
            task: The task to solve.
            routing: Routing decision with strategy and context.
            env: Environment for verification.

        Returns:
            List of candidate solutions, potentially ranked by fitness.
        """
        logger.info(
            "DirectSolver.search started",
            extra={"task_id": task.id, "strategy": routing.strategy},
        )

        # Get experiences from routing context or query memory
        experiences = self._get_experiences(task, routing)

        # Empty memory fallback - pure generation via TaskExecutor
        if not experiences:
            logger.info(
                "No similar experiences found, falling back to TaskExecutor",
                extra={"task_id": task.id},
            )
            return self._generate_without_experience(task, env)

        # Try each experience in order of similarity
        candidates: list[Candidate] = []

        for i, experience in enumerate(experiences):
            logger.debug(
                "Trying experience",
                extra={
                    "task_id": task.id,
                    "experience_id": experience.id,
                    "index": i,
                    "success": experience.success,
                },
            )

            # Adapt the solution
            adapted_solution = self._adapt_solution(task, experience)

            # Verify via environment
            outcome = env.verify(adapted_solution)

            # Create candidate
            candidate = Candidate(
                solution=adapted_solution,
                confidence=0.8 if experience.success else 0.5,
                reasoning=f"Adapted from experience {experience.id}",
                source="adapted",
                fitness=outcome.partial_score,
            )
            candidates.append(candidate)

            # If successful, return immediately (per direct solver semantics)
            if outcome.success:
                logger.info(
                    "Found successful candidate",
                    extra={
                        "task_id": task.id,
                        "experience_id": experience.id,
                        "fitness": outcome.partial_score,
                    },
                )
                return [candidate]

        # No success - return best partial result(s)
        if candidates:
            # Sort by fitness descending
            candidates.sort(key=lambda c: c.fitness or 0.0, reverse=True)
            logger.info(
                "Returning best partial candidates",
                extra={
                    "task_id": task.id,
                    "count": len(candidates),
                    "best_fitness": candidates[0].fitness,
                },
            )
            return candidates

        # This shouldn't happen since we have experiences, but handle gracefully
        logger.warning(
            "No candidates generated despite having experiences",
            extra={"task_id": task.id},
        )
        return self._generate_without_experience(task, env)

    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine a candidate based on feedback.

        Creates an adapted version of the candidate's solution using the
        feedback. If LLM is available, uses it for refinement. Otherwise,
        returns the candidate unchanged.

        Args:
            candidate: The candidate to refine.
            feedback: Feedback from verification or LLM.
            task: The original task.

        Returns:
            Refined candidate.
        """
        logger.info(
            "Refining candidate",
            extra={"task_id": task.id, "source": candidate.source},
        )

        if self._llm is None:
            # Without LLM, we can't refine - return as-is
            logger.debug("No LLM available for refinement")
            return candidate

        # Create refinement prompt
        refinement_prompt = f"""
Given a solution attempt and feedback:

Original Task: {task.description}

Attempted Solution: {candidate.solution}

Feedback: {feedback}

Please provide an improved solution that addresses the feedback:
"""

        try:
            refined_solution = self._llm.generate(refinement_prompt)

            return Candidate(
                solution=refined_solution,
                confidence=candidate.confidence * 0.9,  # Slightly lower confidence
                reasoning=f"Refined based on feedback: {feedback[:100]}",
                source="adapted",
                fitness=None,  # Will be set after verification
                parent_ids=[candidate.solution if isinstance(candidate.solution, str) else str(id(candidate))],
            )
        except Exception as e:
            logger.warning(
                "LLM refinement failed",
                extra={"error": str(e)},
            )
            return candidate

    @property
    def name(self) -> str:
        """Name of this search method."""
        return "direct"

    def _get_experiences(
        self,
        task: Task,
        routing: RoutingDecision,
    ) -> list[Experience]:
        """Get experiences from routing context or query memory.

        Args:
            task: The task to find experiences for.
            routing: Routing decision that may contain context.

        Returns:
            List of similar experiences.
        """
        # First check routing context
        if routing.context is not None:
            context: MemoryQueryResult = routing.context
            if context.experiences:
                logger.debug(
                    "Using experiences from routing context",
                    extra={"count": len(context.experiences)},
                )
                return context.experiences

        # Fall back to querying memory directly
        logger.debug("Querying memory for experiences")
        result = self._memory.query(task)
        return result.experiences

    def _adapt_solution(
        self,
        task: Task,
        experience: Experience,
    ) -> Any:
        """Adapt a solution from an experience to the current task.

        If LLM is provided, uses it to adapt the solution. Otherwise,
        returns the solution directly.

        Args:
            task: The current task.
            experience: The experience with solution to adapt.

        Returns:
            Adapted solution.
        """
        if self._llm is None:
            # No LLM - use solution directly
            logger.debug("No LLM, using solution directly")
            return experience.solution_output

        # Create adaptation prompt
        adaptation_prompt = f"""
Given a similar solved task:
Task: {experience.task_input}
Solution: {experience.solution_output}

Adapt this solution for the new task:
Task: {task.description}

Return the adapted solution:
"""

        try:
            adapted = self._llm.generate(adaptation_prompt)
            logger.debug(
                "Solution adapted via LLM",
                extra={"original_length": len(str(experience.solution_output))},
            )
            return adapted
        except Exception as e:
            logger.warning(
                "LLM adaptation failed, using original solution",
                extra={"error": str(e)},
            )
            return experience.solution_output

    def _generate_without_experience(
        self,
        task: Task,
        env: Environment,
    ) -> list[Candidate]:
        """Generate solution without similar experiences.

        Falls back to TaskExecutor for pure generation.

        Args:
            task: The task to solve.
            env: Environment for verification.

        Returns:
            List with single generated candidate.
        """
        logger.info(
            "Generating without experience via TaskExecutor",
            extra={"task_id": task.id},
        )

        try:
            # Import asyncio for running async executor
            import asyncio

            # Run executor (which is async) in sync context
            try:
                loop = asyncio.get_running_loop()
                # Already in async context - create task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    trajectory = loop.run_in_executor(
                        pool, lambda: asyncio.run(self._executor.execute(task, env))
                    )
                    # This won't work well - fall back to simpler approach
                    raise RuntimeError("Nested async not supported")
            except RuntimeError:
                # No running loop - safe to use asyncio.run
                trajectory = asyncio.run(self._executor.execute(task, env))

            # Extract solution from trajectory
            solution = self._extract_solution(trajectory)

            return [
                Candidate(
                    solution=solution,
                    confidence=0.5,  # Lower confidence for pure generation
                    reasoning="Generated without similar experience",
                    source="generated",
                    fitness=trajectory.outcome.partial_score,
                    trajectory=trajectory,
                )
            ]

        except Exception as e:
            logger.error(
                "TaskExecutor execution failed",
                extra={"task_id": task.id, "error": str(e)},
            )
            # Return empty candidate on failure
            return [
                Candidate(
                    solution=None,
                    confidence=0.0,
                    reasoning=f"Generation failed: {e}",
                    source="generated",
                    fitness=0.0,
                )
            ]

    def _extract_solution(self, trajectory: Trajectory) -> Any:
        """Extract solution from a trajectory.

        Returns the last non-empty observation from the trajectory steps.

        Args:
            trajectory: The trajectory to extract from.

        Returns:
            The extracted solution.
        """
        if not trajectory.steps:
            return None

        # Return the last non-empty observation
        for step in reversed(trajectory.steps):
            if step.observation:
                return step.observation

        return None
