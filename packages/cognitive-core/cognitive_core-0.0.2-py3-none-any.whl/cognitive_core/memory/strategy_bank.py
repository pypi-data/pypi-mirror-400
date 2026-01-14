"""ChromaStrategyBank implementation for StrategyBank protocol.

Stores abstract reasoning patterns (ArcMemo-style) backed by ChromaDB.
Key insight from ArcMemo: concept-level beats instance-level at ALL compute scales.
"""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

import numpy as np

from cognitive_core.memory.strategies.strategy_bank import EMASuccessUpdater

if TYPE_CHECKING:
    from cognitive_core.core.types import Strategy, Task, Trajectory
    from cognitive_core.memory.storage import VectorStore
    from cognitive_core.memory.strategies.strategy_bank import StrategyAbstractor, SuccessRateUpdater
    from cognitive_core.protocols.embeddings import EmbeddingProvider


class ChromaStrategyBank:
    """StrategyBank implementation backed by ChromaDB.

    Stores high-level strategies that describe when and how to approach problems.

    Example:
        ```python
        bank = ChromaStrategyBank(
            embedder=embedder,
            vector_store=vector_store,
            abstractor=abstractor,
        )
        strategy = await bank.write(successful_trajectory)
        applicable = await bank.read(new_task, k=5)
        await bank.update_stats(strategy.id, success=True)
        ```
    """

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        abstractor: StrategyAbstractor,
        success_updater: SuccessRateUpdater | None = None,
    ) -> None:
        """Initialize ChromaStrategyBank.

        Args:
            embedder: Provider for text embeddings.
            vector_store: Vector storage backend for strategies.
            abstractor: Strategy abstractor for extracting strategies from trajectories.
            success_updater: Strategy for updating success rates.
                Defaults to EMASuccessUpdater.
        """
        self._embedder = embedder
        self._vector_store = vector_store
        self._abstractor = abstractor
        self._success_updater = success_updater or EMASuccessUpdater()

    async def write(self, trajectory: Trajectory) -> Strategy | None:
        """Abstract a trajectory into a strategy.

        Only processes successful trajectories. Uses the abstractor to extract
        a high-level strategy from the trajectory.

        Args:
            trajectory: The trajectory to abstract.

        Returns:
            New strategy, or None if trajectory failed or not abstractable.
        """
        # Only process successful trajectories
        if not trajectory.outcome.success:
            return None

        # Delegate to abstractor
        strategy = await self._abstractor.abstract(trajectory)
        if strategy is None:
            return None

        # Generate UUID for strategy if not set
        strategy_id = strategy.id if strategy.id else uuid.uuid4().hex

        # Embed the situation field (describes WHEN to apply)
        embedding = self._embedder.encode(strategy.situation)

        # Prepare metadata
        metadata = {
            "usage_count": strategy.usage_count,
            "success_rate": strategy.success_rate,
            "source_task_id": trajectory.task.id,
            "suggestion": strategy.suggestion,
            "parameters": json.dumps(strategy.parameters),
        }

        # Store in vector store
        await self._vector_store.add(
            ids=[strategy_id],
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
            documents=[strategy.situation],
        )

        # Return strategy with updated id and embedding
        from cognitive_core.core.types import Strategy as StrategyType

        return StrategyType(
            id=strategy_id,
            situation=strategy.situation,
            suggestion=strategy.suggestion,
            parameters=strategy.parameters,
            usage_count=strategy.usage_count,
            success_rate=strategy.success_rate,
            embedding=embedding,
        )

    async def read(self, task: Task, k: int = 5) -> list[Strategy]:
        """Find applicable strategies for a task.

        Embeds the task description and queries for similar strategies,
        then sorts by a combination of distance and success rate.

        Args:
            task: The task to find strategies for.
            k: Number of strategies to return.

        Returns:
            List of applicable strategies, sorted by relevance.
        """
        from cognitive_core.core.types import Strategy as StrategyType

        # Embed task description
        query_embedding = self._embedder.encode(task.description)

        # Query vector store for top-k similar
        results = await self._vector_store.query(
            embedding=query_embedding.tolist(),
            k=k,
        )

        if not results.ids:
            return []

        # Reconstruct Strategy objects from results
        strategies: list[tuple[float, Strategy]] = []
        for i, strategy_id in enumerate(results.ids):
            metadata = results.metadatas[i]
            document = results.documents[i]
            distance = results.distances[i]

            # Parse parameters from JSON
            parameters = json.loads(metadata.get("parameters", "[]"))

            strategy = StrategyType(
                id=strategy_id,
                situation=document,
                suggestion=metadata.get("suggestion", ""),
                parameters=parameters,
                usage_count=int(metadata.get("usage_count", 0)),
                success_rate=float(metadata.get("success_rate", 0.5)),
                embedding=None,  # Don't include embedding in results
            )

            # Calculate combined score (lower is better)
            # Normalize distance (usually 0-2 for cosine) and invert success rate
            # Higher success rate should give lower score
            combined_score = distance - strategy.success_rate

            strategies.append((combined_score, strategy))

        # Sort by combined score (lower is better)
        strategies.sort(key=lambda x: x[0])

        return [s for _, s in strategies]

    async def get(self, strategy_id: str) -> Strategy | None:
        """Get a strategy by ID.

        Args:
            strategy_id: The strategy ID.

        Returns:
            The strategy, or None if not found.
        """
        from cognitive_core.core.types import Strategy as StrategyType

        items = await self._vector_store.get(ids=[strategy_id])

        if not items:
            return None

        item = items[0]
        metadata = item.get("metadata", {})
        document = item.get("document", "")
        embedding = item.get("embedding")

        # Parse parameters from JSON
        parameters = json.loads(metadata.get("parameters", "[]"))

        # Convert embedding if present
        embedding_array = None
        if embedding is not None:
            embedding_array = np.array(embedding)

        return StrategyType(
            id=strategy_id,
            situation=document,
            suggestion=metadata.get("suggestion", ""),
            parameters=parameters,
            usage_count=int(metadata.get("usage_count", 0)),
            success_rate=float(metadata.get("success_rate", 0.5)),
            embedding=embedding_array,
        )

    async def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update usage statistics for a strategy.

        Uses the configured success updater to calculate new statistics,
        then updates the stored metadata.

        Args:
            strategy_id: The strategy ID.
            success: Whether application was successful.
        """
        # Get current strategy
        items = await self._vector_store.get(ids=[strategy_id])

        if not items:
            return  # Strategy not found, nothing to update

        item = items[0]
        metadata = item.get("metadata", {})
        embedding = item.get("embedding", [])
        document = item.get("document", "")

        # Get current stats
        current_rate = float(metadata.get("success_rate", 0.5))
        current_count = int(metadata.get("usage_count", 0))

        # Delegate to success updater
        new_rate, new_count = self._success_updater.update(
            current_rate=current_rate,
            current_count=current_count,
            success=success,
        )

        # Update metadata
        new_metadata = dict(metadata)
        new_metadata["success_rate"] = new_rate
        new_metadata["usage_count"] = new_count

        # VectorStore doesn't have update, so delete and re-add
        await self._vector_store.delete(ids=[strategy_id])
        await self._vector_store.add(
            ids=[strategy_id],
            embeddings=[embedding],
            metadatas=[new_metadata],
            documents=[document],
        )

    def __len__(self) -> int:
        """Return number of strategies in the bank.

        Note: This is a synchronous method that uses asyncio.run internally.
        For async code, use await vector_store.count() directly.
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(self._vector_store.count())

        # If there's a running loop, we need a different approach
        # Create a new thread to run the coroutine
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self._vector_store.count())
            return future.result()
