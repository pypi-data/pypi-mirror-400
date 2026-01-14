"""ChromaDB-backed experience memory implementation."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Coroutine, TypeVar

import numpy as np

from cognitive_core.core.types import Experience
from cognitive_core.memory.storage import VectorStore
from cognitive_core.memory.strategies.experience import (
    ExperienceExtractor,
    PassthroughRefineStrategy,
    RefineStrategy,
    SimpleExperienceExtractor,
)

if TYPE_CHECKING:
    from cognitive_core.core.types import Task, Trajectory
    from cognitive_core.protocols.embeddings import EmbeddingProvider

T = TypeVar("T")


def _run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run async code from sync context, handling missing event loops.

    This handles the case where we're running in a thread without an event loop
    (e.g., when called from asyncio.run_in_executor).

    Args:
        coro: Coroutine to run.

    Returns:
        Result of the coroutine.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # We're in an async context, can't use run_until_complete
        # Create a new event loop in a nested way (not recommended but works)
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
    else:
        # No running loop, safe to create one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in this thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)


class ChromaExperienceMemory:
    """ExperienceMemory implementation backed by ChromaDB.

    Implements the ExperienceMemory protocol from cognitive_core.protocols.memory for
    task-level retrieval of similar past experiences using ReMem-style search.

    Key features:
    - Store trajectories as experiences with embeddings
    - Search for similar experiences via embedding similarity
    - Configurable extraction and refinement strategies
    - Prune low-quality or old experiences

    Example:
        ```python
        memory = ChromaExperienceMemory(
            embedder=embedder,
            vector_store=vector_store,
        )
        exp_id = memory.store(trajectory)
        similar = memory.search(new_task, k=4)  # Default k=4 from ReMem
        ```
    """

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        extractor: ExperienceExtractor = SimpleExperienceExtractor(),
        refine_strategy: RefineStrategy = PassthroughRefineStrategy(),
    ) -> None:
        """Initialize ChromaExperienceMemory.

        Args:
            embedder: Provider for generating text embeddings.
            vector_store: Vector store for storing and querying experiences.
            extractor: Strategy for extracting embedding text from trajectories.
            refine_strategy: Strategy for refining retrieved experiences.
        """
        self._embedder = embedder
        self._vector_store = vector_store
        self._extractor = extractor
        self._refine_strategy = refine_strategy

    def store(self, trajectory: Trajectory) -> str:
        """Store a trajectory as an experience.

        Extracts relevant information from the trajectory and stores it
        with an embedding for later retrieval.

        Args:
            trajectory: The trajectory to store.

        Returns:
            Unique experience ID.
        """
        # Generate UUID for experience_id
        experience_id = uuid.uuid4().hex

        # Extract embedding text via extractor
        embedding_text = self._extractor.extract(trajectory)

        # Embed the text
        embedding = self._embedder.encode(embedding_text)

        # Create Experience from trajectory fields
        experience = Experience(
            id=experience_id,
            task_input=trajectory.task.description,
            solution_output=self._extract_solution(trajectory),
            feedback=self._extract_feedback(trajectory),
            success=trajectory.outcome.success,
            embedding=embedding,
            trajectory_id=trajectory.task.id,
            timestamp=trajectory.timestamp,
            metadata=trajectory.metadata.copy() if trajectory.metadata else {},
        )

        # Prepare metadata for vector store
        metadata = {
            "success": experience.success,
            "timestamp": experience.timestamp.isoformat(),
            "task_id": trajectory.task.id,
            "task_input": experience.task_input,
            "solution_output": experience.solution_output,
            "feedback": experience.feedback,
            "trajectory_id": experience.trajectory_id,
        }

        # Store in vector store (run async in sync context)
        _run_async(
            self._vector_store.add(
                ids=[experience_id],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
                documents=[embedding_text],
            )
        )

        return experience_id

    def search(self, task: Task, k: int = 4) -> list[Experience]:
        """Find similar experiences via embedding similarity.

        Default k=4 is from the ReMem paper.

        Args:
            task: The task to find similar experiences for.
            k: Number of experiences to return.

        Returns:
            List of similar experiences, sorted by similarity.
        """
        # Embed task description
        query_embedding = self._embedder.encode(task.description)

        # Query vector store for top-k similar
        result = _run_async(
            self._vector_store.query(
                embedding=query_embedding.tolist(),
                k=k,
            )
        )

        # Reconstruct Experience objects from results
        experiences: list[Experience] = []
        for i, exp_id in enumerate(result.ids):
            metadata = result.metadatas[i] if i < len(result.metadatas) else {}
            experiences.append(self._reconstruct_experience(exp_id, metadata))

        return experiences

    def get(self, experience_id: str) -> Experience | None:
        """Get an experience by ID.

        Args:
            experience_id: The experience ID.

        Returns:
            The experience, or None if not found.
        """
        items = _run_async(
            self._vector_store.get(ids=[experience_id])
        )

        if not items:
            return None

        item = items[0]
        metadata = item.get("metadata", {})
        embedding = item.get("embedding")

        return self._reconstruct_experience(
            experience_id,
            metadata,
            embedding=np.array(embedding) if embedding is not None else None,
        )

    def refine(self, experiences: list[Experience]) -> list[Experience]:
        """ReMem-style refinement: exploit useful, prune noise, reorganize.

        Args:
            experiences: Experiences to refine.

        Returns:
            Refined list of experiences.
        """
        # Delegate to refine_strategy (which is async)
        return _run_async(
            self._refine_strategy.refine(experiences)
        )

    def prune(self, criteria: dict[str, Any]) -> int:
        """Remove low-value experiences.

        Supported criteria:
        - min_success_rate: Minimum success rate to keep (not used for individual
          experiences, but can filter by success=True/False)
        - max_age_days: Maximum age in days

        Args:
            criteria: Pruning criteria.

        Returns:
            Number of experiences removed.
        """
        ids_to_remove: list[str] = []

        # Get all experiences to evaluate
        count = _run_async(self._vector_store.count())
        if count == 0:
            return 0

        # Query all items by using a dummy embedding and large k
        # This is a workaround since VectorStore doesn't have a list_all method
        dummy_embedding = [0.0] * self._embedder.dimension

        result = _run_async(
            self._vector_store.query(
                embedding=dummy_embedding,
                k=count,
            )
        )

        now = datetime.now(timezone.utc)

        for i, exp_id in enumerate(result.ids):
            metadata = result.metadatas[i] if i < len(result.metadatas) else {}
            should_remove = False

            # Check max_age_days criteria
            if "max_age_days" in criteria:
                max_age_days = criteria["max_age_days"]
                timestamp_str = metadata.get("timestamp")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        # Ensure timestamp is timezone-aware for comparison
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=timezone.utc)
                        age = now - timestamp
                        if age > timedelta(days=max_age_days):
                            should_remove = True
                    except (ValueError, TypeError):
                        pass

            # Check min_success_rate criteria (filter failures if threshold > 0)
            if "min_success_rate" in criteria and not should_remove:
                min_success_rate = criteria["min_success_rate"]
                success = metadata.get("success", True)
                # If min_success_rate > 0, remove failures
                if min_success_rate > 0 and not success:
                    should_remove = True

            if should_remove:
                ids_to_remove.append(exp_id)

        # Delete matching experiences
        if ids_to_remove:
            _run_async(
                self._vector_store.delete(ids=ids_to_remove)
            )

        return len(ids_to_remove)

    def __len__(self) -> int:
        """Number of stored experiences."""
        return _run_async(self._vector_store.count())

    def _extract_solution(self, trajectory: Trajectory) -> str:
        """Extract solution output from trajectory steps.

        Args:
            trajectory: The trajectory to extract from.

        Returns:
            Solution output string.
        """
        if not trajectory.steps:
            return ""

        # Use the last action as the solution
        return trajectory.steps[-1].action

    def _extract_feedback(self, trajectory: Trajectory) -> str:
        """Extract feedback from trajectory outcome.

        Args:
            trajectory: The trajectory to extract from.

        Returns:
            Feedback string.
        """
        if trajectory.outcome.success:
            return "Success"
        return trajectory.outcome.error_info or "Failed"

    def _reconstruct_experience(
        self,
        experience_id: str,
        metadata: dict[str, Any],
        embedding: np.ndarray | None = None,
    ) -> Experience:
        """Reconstruct an Experience object from stored metadata.

        Args:
            experience_id: The experience ID.
            metadata: Stored metadata dictionary.
            embedding: Optional embedding array.

        Returns:
            Reconstructed Experience object.
        """
        # Parse timestamp
        timestamp_str = metadata.get("timestamp")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)

        return Experience(
            id=experience_id,
            task_input=metadata.get("task_input", ""),
            solution_output=metadata.get("solution_output", ""),
            feedback=metadata.get("feedback", ""),
            success=metadata.get("success", False),
            embedding=embedding,
            trajectory_id=metadata.get("trajectory_id", ""),
            timestamp=timestamp,
            metadata={
                k: v
                for k, v in metadata.items()
                if k
                not in {
                    "success",
                    "timestamp",
                    "task_id",
                    "task_input",
                    "solution_output",
                    "feedback",
                    "trajectory_id",
                }
            },
        )
