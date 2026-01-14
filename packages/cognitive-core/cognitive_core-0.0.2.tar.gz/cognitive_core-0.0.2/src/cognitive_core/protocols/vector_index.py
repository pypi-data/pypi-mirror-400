"""Vector index protocol for ATLAS.

Provides vector storage and similarity search.
Implementations can use ChromaDB, FAISS, or in-memory storage.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class VectorIndex(Protocol):
    """Vector storage and similarity search.

    Provides the storage layer for memory systems. Can be backed by
    ChromaDB (recommended), FAISS, or a simple in-memory implementation.

    Example:
        ```python
        index = ChromaDBIndex(collection_name="experiences")
        index.add("exp-1", embedding, {"task": "fix bug"})
        results = index.search(query_embedding, k=5)
        ```
    """

    def add(
        self,
        id: str,
        vector: np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a vector with metadata.

        Args:
            id: Unique identifier for this vector
            vector: The embedding vector (1-dimensional)
            metadata: Optional metadata for filtering
        """
        ...

    def add_batch(
        self,
        ids: list[str],
        vectors: np.ndarray,
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add multiple vectors efficiently.

        Args:
            ids: List of unique identifiers
            vectors: 2D array of shape (n, dimension)
            metadatas: Optional list of metadata dicts
        """
        ...

    def search(
        self,
        vector: np.ndarray,
        k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find k nearest neighbors.

        Args:
            vector: Query vector
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (id, score, metadata) tuples, sorted by similarity
        """
        ...

    def get(self, id: str) -> tuple[np.ndarray, dict[str, Any]] | None:
        """Get a vector by ID.

        Args:
            id: Vector identifier

        Returns:
            (vector, metadata) tuple, or None if not found
        """
        ...

    def delete(self, id: str) -> bool:
        """Remove a vector by ID.

        Args:
            id: Vector identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def __len__(self) -> int:
        """Number of vectors stored.

        Returns:
            Total count of vectors in the index
        """
        ...

    def clear(self) -> None:
        """Remove all vectors from the index."""
        ...
