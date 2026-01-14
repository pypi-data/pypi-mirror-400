"""Vector storage abstraction for memory implementations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    import chromadb


@dataclass
class QueryResult:
    """Result from a vector store query.

    Attributes:
        ids: List of document IDs matching the query.
        distances: List of distances/scores for each result.
        metadatas: List of metadata dictionaries for each result.
        documents: List of document content strings.
    """

    ids: list[str]
    distances: list[float]
    metadatas: list[dict[str, Any]]
    documents: list[str]


@runtime_checkable
class VectorStore(Protocol):
    """Abstract vector storage - allows swapping ChromaDB for other backends.

    This protocol defines the interface for vector storage implementations,
    enabling experimentation with different backends (ChromaDB, Pinecone, etc.)
    without changing the memory implementation code.
    """

    async def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Add items to the store.

        Args:
            ids: Unique identifiers for each item.
            embeddings: Vector embeddings for each item.
            metadatas: Metadata dictionaries for each item.
            documents: Document content strings for each item.
        """
        ...

    async def query(
        self,
        embedding: list[float],
        k: int,
        where: dict[str, Any] | None = None,
    ) -> QueryResult:
        """Query for similar items.

        Args:
            embedding: Query vector to find similar items.
            k: Number of results to return.
            where: Optional metadata filter (ChromaDB-style where clause).

        Returns:
            QueryResult containing matching items sorted by similarity.
        """
        ...

    async def delete(self, ids: list[str]) -> None:
        """Delete items by ID.

        Args:
            ids: List of item IDs to delete.
        """
        ...

    async def get(self, ids: list[str]) -> list[dict[str, Any]]:
        """Get items by ID.

        Args:
            ids: List of item IDs to retrieve.

        Returns:
            List of item dictionaries with id, embedding, metadata, and document.
        """
        ...

    async def count(self) -> int:
        """Return number of items in store.

        Returns:
            Total count of items in the store.
        """
        ...


class ChromaVectorStore:
    """ChromaDB-backed vector store implementation.

    Wraps ChromaDB collection operations with async compatibility using
    asyncio.to_thread for non-blocking execution.

    Example:
        ```python
        store = ChromaVectorStore(
            collection_name="atlas_experiences",
            persist_directory=".atlas/chroma"
        )
        await store.add(
            ids=["exp-1"],
            embeddings=[[0.1, 0.2, ...]],
            metadatas=[{"task": "fix bug"}],
            documents=["Fix the login bug"]
        )
        results = await store.query(query_embedding, k=5)
        ```
    """

    def __init__(
        self,
        collection_name: str | None = None,
        persist_directory: str | None = None,
        collection: chromadb.Collection | None = None,
    ) -> None:
        """Initialize ChromaDB vector store.

        Either provide a collection directly, or provide collection_name
        to create/get a collection. If persist_directory is provided,
        uses persistent storage; otherwise uses ephemeral in-memory storage.

        Args:
            collection_name: Name for the ChromaDB collection.
            persist_directory: Directory for persistent storage (optional).
            collection: Existing ChromaDB collection to use (optional).

        Raises:
            ValueError: If neither collection nor collection_name is provided.
        """
        if collection is not None:
            self._collection = collection
            self._client: chromadb.ClientAPI | None = None
        elif collection_name is not None:
            self._collection_name = collection_name
            self._persist_directory = persist_directory
            self._client = None
            self._collection = None
        else:
            raise ValueError("Either collection or collection_name must be provided")

    def _get_collection(self) -> chromadb.Collection:
        """Lazy initialize and return the ChromaDB collection.

        Returns:
            ChromaDB collection.

        Raises:
            ImportError: If chromadb is not installed.
        """
        if self._collection is None:
            try:
                import chromadb
            except ImportError as e:
                raise ImportError(
                    "chromadb is required for vector storage. "
                    "Install with: pip install chromadb"
                ) from e

            if self._persist_directory:
                from pathlib import Path

                persist_path = Path(self._persist_directory)
                persist_path.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(path=str(persist_path))
            else:
                self._client = chromadb.Client()

            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )

        return self._collection

    async def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Add items to the store.

        Args:
            ids: Unique identifiers for each item.
            embeddings: Vector embeddings for each item.
            metadatas: Metadata dictionaries for each item.
            documents: Document content strings for each item.
        """
        if not ids:
            return

        # Ensure metadatas are not empty (ChromaDB requirement)
        safe_metadatas = [
            m if m else {"_placeholder": True} for m in metadatas
        ]

        def _add() -> None:
            collection = self._get_collection()
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=safe_metadatas,
                documents=documents,
            )

        await asyncio.to_thread(_add)

    async def query(
        self,
        embedding: list[float],
        k: int,
        where: dict[str, Any] | None = None,
    ) -> QueryResult:
        """Query for similar items.

        Args:
            embedding: Query vector to find similar items.
            k: Number of results to return.
            where: Optional metadata filter (ChromaDB-style where clause).

        Returns:
            QueryResult containing matching items sorted by similarity.
        """

        def _query() -> QueryResult:
            collection = self._get_collection()

            # Handle empty collection
            item_count = collection.count()
            if item_count == 0:
                return QueryResult(ids=[], distances=[], metadatas=[], documents=[])

            # Adjust k if collection has fewer items
            actual_k = min(k, item_count)

            query_kwargs: dict[str, Any] = {
                "query_embeddings": [embedding],
                "n_results": actual_k,
                "include": ["metadatas", "distances", "documents"],
            }
            if where:
                query_kwargs["where"] = where

            results = collection.query(**query_kwargs)

            # Extract results - ChromaDB returns nested lists
            if results["ids"] and results["ids"][0]:
                ids = results["ids"][0]
                distances = results["distances"][0] if results.get("distances") else []
                metadatas = results["metadatas"][0] if results.get("metadatas") else []
                documents = results["documents"][0] if results.get("documents") else []

                # Ensure all lists have same length
                length = len(ids)
                if len(distances) < length:
                    distances = distances + [0.0] * (length - len(distances))
                if len(metadatas) < length:
                    metadatas = metadatas + [{}] * (length - len(metadatas))
                if len(documents) < length:
                    documents = documents + [""] * (length - len(documents))

                return QueryResult(
                    ids=ids,
                    distances=distances,
                    metadatas=metadatas,
                    documents=documents,
                )

            return QueryResult(ids=[], distances=[], metadatas=[], documents=[])

        return await asyncio.to_thread(_query)

    async def delete(self, ids: list[str]) -> None:
        """Delete items by ID.

        Args:
            ids: List of item IDs to delete.
        """
        if not ids:
            return

        def _delete() -> None:
            collection = self._get_collection()
            collection.delete(ids=ids)

        await asyncio.to_thread(_delete)

    async def get(self, ids: list[str]) -> list[dict[str, Any]]:
        """Get items by ID.

        Args:
            ids: List of item IDs to retrieve.

        Returns:
            List of item dictionaries with id, embedding, metadata, and document.
        """
        if not ids:
            return []

        def _get() -> list[dict[str, Any]]:
            collection = self._get_collection()
            results = collection.get(
                ids=ids,
                include=["embeddings", "metadatas", "documents"],
            )

            items: list[dict[str, Any]] = []
            if results["ids"]:
                embeddings = results.get("embeddings")
                metadatas = results.get("metadatas")
                documents = results.get("documents")

                for i, item_id in enumerate(results["ids"]):
                    item: dict[str, Any] = {"id": item_id}
                    if embeddings is not None and i < len(embeddings):
                        item["embedding"] = embeddings[i]
                    if metadatas is not None and i < len(metadatas):
                        item["metadata"] = metadatas[i]
                    if documents is not None and i < len(documents):
                        item["document"] = documents[i]
                    items.append(item)

            return items

        return await asyncio.to_thread(_get)

    async def count(self) -> int:
        """Return number of items in store.

        Returns:
            Total count of items in the store.
        """

        def _count() -> int:
            collection = self._get_collection()
            return collection.count()

        return await asyncio.to_thread(_count)
