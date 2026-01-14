"""MemorySystem aggregator implementation.

Combines all three memory components with parallel async queries
and graceful degradation when components are missing.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from cognitive_core.protocols.memory import MemoryQueryResult

if TYPE_CHECKING:
    from cognitive_core.core.types import CodeConcept, Experience, Strategy, Task, Trajectory
    from cognitive_core.protocols.memory import ConceptLibrary, ExperienceMemory, StrategyBank

logger = logging.getLogger(__name__)


class MemorySystemImpl:
    """Aggregator for all memory types.

    Provides a unified interface for querying and storing across
    all three memory types. Each component is optional for ablation studies.

    Example:
        ```python
        # Full system
        memory = MemorySystemImpl(
            experience=exp_memory,
            concepts=concept_lib,
            strategies=strategy_bank,
        )

        # Experience-only ablation
        memory = MemorySystemImpl(experience=exp_memory)

        # Query all components
        results = memory.query(task, k=5)
        ```
    """

    def __init__(
        self,
        experience: ExperienceMemory | None = None,
        concepts: ConceptLibrary | None = None,
        strategies: StrategyBank | None = None,
    ) -> None:
        """Initialize MemorySystemImpl.

        Args:
            experience: Optional ExperienceMemory component.
            concepts: Optional ConceptLibrary component.
            strategies: Optional StrategyBank component.
        """
        self._experience = experience
        self._concepts = concepts
        self._strategies = strategies

    @property
    def experience_memory(self) -> ExperienceMemory | None:
        """Experience memory component (if available)."""
        return self._experience

    @property
    def concept_library(self) -> ConceptLibrary | None:
        """Concept library component (if available)."""
        return self._concepts

    @property
    def strategy_bank(self) -> StrategyBank | None:
        """Strategy bank component (if available)."""
        return self._strategies

    def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
        """Query all available memory components.

        Queries all available components in parallel using asyncio.gather.
        Missing components return empty results (graceful degradation).
        Errors in one component don't affect others.

        Args:
            task: The task to query for.
            k: Number of results per component.

        Returns:
            Combined results from all components.
        """
        # Run async query internally
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already in async context, create task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self._query_async(task, k)
                )
                return future.result()
        else:
            return asyncio.run(self._query_async(task, k))

    async def _query_async(self, task: Task, k: int) -> MemoryQueryResult:
        """Internal async query implementation.

        Args:
            task: The task to query for.
            k: Number of results per component.

        Returns:
            Combined results from all components.
        """
        experiences: list[Experience] = []
        concepts: list[CodeConcept] = []
        strategies: list[Strategy] = []

        # Build list of coroutines for available components
        tasks: list[asyncio.Task[Any]] = []
        task_types: list[str] = []

        if self._experience is not None:
            tasks.append(
                asyncio.create_task(self._query_experience(task, k))
            )
            task_types.append("experience")

        if self._concepts is not None:
            tasks.append(
                asyncio.create_task(self._query_concepts(task, k))
            )
            task_types.append("concepts")

        if self._strategies is not None:
            tasks.append(
                asyncio.create_task(self._query_strategies(task, k))
            )
            task_types.append("strategies")

        if not tasks:
            return MemoryQueryResult()

        # Execute in parallel, allowing individual failures
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, handling exceptions per component
        for i, result in enumerate(results):
            task_type = task_types[i]

            if isinstance(result, Exception):
                logger.warning(
                    f"Error querying {task_type}: {result}",
                    exc_info=result,
                )
                continue

            if task_type == "experience":
                experiences = result
            elif task_type == "concepts":
                concepts = result
            elif task_type == "strategies":
                strategies = result

        return MemoryQueryResult(
            experiences=experiences,
            concepts=concepts,
            strategies=strategies,
        )

    async def _query_experience(self, task: Task, k: int) -> list[Experience]:
        """Query experience memory.

        ExperienceMemory.search is sync, so wrap in executor.

        Args:
            task: The task to query for.
            k: Number of results.

        Returns:
            List of experiences.
        """
        if self._experience is None:
            return []

        # ExperienceMemory.search is sync, run in thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._experience.search,
            task,
            k,
        )

    async def _query_concepts(self, task: Task, k: int) -> list[CodeConcept]:
        """Query concept library.

        ConceptLibrary.search is async.

        Args:
            task: The task to query for.
            k: Number of results.

        Returns:
            List of concepts.
        """
        if self._concepts is None:
            return []

        # ConceptLibrary.search is async
        return await self._concepts.search(task.description, k=k)

    async def _query_strategies(self, task: Task, k: int) -> list[Strategy]:
        """Query strategy bank.

        StrategyBank.read is async.

        Args:
            task: The task to query for.
            k: Number of results.

        Returns:
            List of strategies.
        """
        if self._strategies is None:
            return []

        # StrategyBank.read is async
        return await self._strategies.read(task, k=k)

    def store(self, trajectory: Trajectory) -> dict[str, Any]:
        """Store in all available components.

        - ExperienceMemory: Always stores (success and failure)
        - ConceptLibrary: Skip (compression is batch operation)
        - StrategyBank: Only write if trajectory.outcome.success

        Args:
            trajectory: The trajectory to store.

        Returns:
            Dict with IDs from each component that stored it.
        """
        result: dict[str, Any] = {}

        # ExperienceMemory always stores (success and failure)
        if self._experience is not None:
            try:
                exp_id = self._experience.store(trajectory)
                result["experience_id"] = exp_id
            except Exception as e:
                logger.warning(f"Error storing in experience memory: {e}")

        # StrategyBank only writes on success
        if self._strategies is not None and trajectory.outcome.success:
            try:
                # StrategyBank.write is async, run it
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop is not None:
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self._strategies.write(trajectory),
                        )
                        strategy = future.result()
                else:
                    strategy = asyncio.run(self._strategies.write(trajectory))

                if strategy is not None:
                    result["strategy_id"] = strategy.id
            except Exception as e:
                logger.warning(f"Error storing in strategy bank: {e}")

        # ConceptLibrary: Skip (compression is batch operation)
        # Concepts are extracted via compress() which is called separately

        return result
