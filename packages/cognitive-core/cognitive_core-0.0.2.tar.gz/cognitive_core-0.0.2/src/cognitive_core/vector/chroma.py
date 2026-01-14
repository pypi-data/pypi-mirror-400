"""ChromaDB vector index implementation.

Provides persistent vector storage with similarity search.
Data is stored in project-local .atlas/chroma/ directory.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    import chromadb
    from chromadb import Collection

from cognitive_core.config import StorageConfig

logger = logging.getLogger("cognitive_core.storage")


class ChromaIndex:
    """ChromaDB-backed vector index.

    Implements the VectorIndex protocol with persistent storage
    in the project-local .atlas/chroma/ directory.

    Example:
        ```python
        index = ChromaIndex("experiences")
        index.add("exp-1", embedding, {"task": "fix bug"})
        results = index.search(query_embedding, k=5)
        ```
    """

    def __init__(
        self,
        collection_name: str,
        config: StorageConfig | None = None,
    ) -> None:
        """Initialize ChromaDB index.

        Args:
            collection_name: Name for the ChromaDB collection.
            config: Storage configuration. Uses defaults if not provided.
        """
        self._config = config or StorageConfig()
        self._base_collection_name = collection_name
        self._collection_name = self._prefixed_name(collection_name)
        self._client: chromadb.ClientAPI | None = None
        self._collection: Collection | None = None

    def _prefixed_name(self, name: str) -> str:
        """Apply collection prefix if configured."""
        prefix = self._config.chroma_collection_prefix
        return f"{prefix}{name}" if prefix else name

    def _get_client(self) -> chromadb.ClientAPI:
        """Lazy initialize ChromaDB client.

        Returns:
            ChromaDB persistent client.

        Raises:
            ImportError: If chromadb is not installed.
        """
        if self._client is None:
            try:
                import chromadb
            except ImportError as e:
                raise ImportError(
                    "chromadb is required for vector storage. "
                    "Install with: pip install chromadb"
                ) from e

            persist_dir = self._config.base_path / "chroma"
            persist_dir.mkdir(parents=True, exist_ok=True)

            logger.info(
                "Initializing ChromaDB",
                extra={"path": str(persist_dir)},
            )
            self._client = chromadb.PersistentClient(path=str(persist_dir))

        return self._client

    def _get_collection(self) -> Collection:
        """Get or create the ChromaDB collection.

        Returns:
            ChromaDB collection configured with the appropriate distance metric.
        """
        if self._collection is None:
            # Map our metric names to ChromaDB's
            space_map = {
                "cosine": "cosine",
                "l2": "l2",
                "ip": "ip",
            }
            space = space_map.get(self._config.distance_metric, "cosine")

            self._collection = self._get_client().get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": space},
            )
            logger.debug(
                "Collection ready",
                extra={
                    "name": self._collection_name,
                    "space": space,
                },
            )

        return self._collection

    def add(
        self,
        id: str,
        vector: np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a vector with metadata.

        Args:
            id: Unique identifier for this vector.
            vector: The embedding vector (1-dimensional).
            metadata: Optional metadata for filtering.
        """
        collection = self._get_collection()
        # ChromaDB 1.4+ requires non-empty metadata
        meta = metadata if metadata else {"_placeholder": True}
        collection.add(
            ids=[id],
            embeddings=[vector.tolist()],
            metadatas=[meta],
        )
        logger.debug("Added vector", extra={"id": id})

    def add_batch(
        self,
        ids: list[str],
        vectors: np.ndarray,
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add multiple vectors efficiently.

        Args:
            ids: List of unique identifiers.
            vectors: 2D array of shape (n, dimension).
            metadatas: Optional list of metadata dicts.
        """
        if len(ids) == 0:
            return

        collection = self._get_collection()
        # ChromaDB 1.4+ requires non-empty metadata
        metas = metadatas if metadatas else [{"_placeholder": True} for _ in ids]
        # Ensure each metadata dict is non-empty
        metas = [m if m else {"_placeholder": True} for m in metas]
        collection.add(
            ids=ids,
            embeddings=vectors.tolist(),
            metadatas=metas,
        )
        logger.debug("Added batch", extra={"count": len(ids)})

    def search(
        self,
        vector: np.ndarray,
        k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find k nearest neighbors.

        Args:
            vector: Query vector.
            k: Number of results to return.
            filter: Optional metadata filter (ChromaDB where clause).

        Returns:
            List of (id, score, metadata) tuples, sorted by similarity.
            Score interpretation depends on distance metric:
            - cosine: higher is more similar (similarity score)
            - l2: lower is more similar (distance)
        """
        collection = self._get_collection()

        # Handle empty collection
        if collection.count() == 0:
            return []

        # Adjust k if collection has fewer items
        actual_k = min(k, collection.count())

        results = collection.query(
            query_embeddings=[vector.tolist()],
            n_results=actual_k,
            where=filter,
            include=["metadatas", "distances"],
        )

        # Extract results
        output: list[tuple[str, float, dict[str, Any]]] = []

        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            distances = results["distances"][0] if results["distances"] else [0.0] * len(ids)
            metadatas = results["metadatas"][0] if results["metadatas"] else [{} for _ in ids]

            # Convert distance to similarity score for cosine
            # ChromaDB returns distance, we want similarity for cosine
            for id_, dist, meta in zip(ids, distances, metadatas):
                if self._config.distance_metric == "cosine":
                    # Cosine distance to similarity: sim = 1 - dist
                    score = 1.0 - dist
                else:
                    # For L2/IP, keep as distance (lower is better)
                    score = dist
                output.append((id_, score, meta or {}))

        return output

    def get(self, id: str) -> tuple[np.ndarray, dict[str, Any]] | None:
        """Get a vector by ID.

        Args:
            id: Vector identifier.

        Returns:
            (vector, metadata) tuple, or None if not found.
        """
        collection = self._get_collection()

        try:
            results = collection.get(
                ids=[id],
                include=["embeddings", "metadatas"],
            )

            if results["ids"]:
                embedding = np.array(results["embeddings"][0])
                metadata = results["metadatas"][0] if results["metadatas"] else {}
                return embedding, metadata

        except Exception:
            pass

        return None

    def delete(self, id: str) -> bool:
        """Remove a vector by ID.

        Args:
            id: Vector identifier.

        Returns:
            True if deleted, False if not found.
        """
        collection = self._get_collection()

        # Check if exists first
        existing = collection.get(ids=[id])
        if not existing["ids"]:
            return False

        collection.delete(ids=[id])
        logger.debug("Deleted vector", extra={"id": id})
        return True

    def update(
        self,
        id: str,
        vector: np.ndarray | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update a vector and/or its metadata.

        Args:
            id: Vector identifier.
            vector: New embedding vector (optional).
            metadata: New metadata (optional).

        Returns:
            True if updated, False if not found.
        """
        collection = self._get_collection()

        # Check if exists
        existing = collection.get(ids=[id])
        if not existing["ids"]:
            return False

        update_kwargs: dict[str, Any] = {"ids": [id]}
        if vector is not None:
            update_kwargs["embeddings"] = [vector.tolist()]
        if metadata is not None:
            update_kwargs["metadatas"] = [metadata]

        collection.update(**update_kwargs)
        return True

    def __len__(self) -> int:
        """Number of vectors stored."""
        return self._get_collection().count()

    def clear(self) -> None:
        """Remove all vectors from the index."""
        # Delete and recreate collection
        client = self._get_client()
        try:
            client.delete_collection(self._collection_name)
        except ValueError:
            pass  # Collection doesn't exist

        self._collection = None
        # Recreate empty collection
        self._get_collection()
        logger.info("Cleared collection", extra={"name": self._collection_name})

    @property
    def collection_name(self) -> str:
        """The full collection name (with prefix if any)."""
        return self._collection_name
