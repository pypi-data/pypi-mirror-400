"""ConceptLibrary implementation backed by ChromaDB."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from cognitive_core.core.types import CodeConcept, Trajectory
    from cognitive_core.memory.storage import VectorStore
    from cognitive_core.memory.strategies.concepts import (
        CompositionStrategy,
        CompressionStrategy,
        PrimitiveLoader,
    )
    from cognitive_core.protocols.embeddings import EmbeddingProvider


class ChromaConceptLibrary:
    """ConceptLibrary implementation backed by ChromaDB.

    Stores and retrieves code concepts at different abstraction levels:
    - Primitives: Domain-specific base operations (loaded at init, in-memory only)
    - Learned: Extracted from trajectories via compression (stored in vector store)
    - Composed: Combinations of existing concepts (stored in vector store)

    Example:
        ```python
        library = ChromaConceptLibrary(
            embedder=embedder,
            vector_store=vector_store,
            primitive_loader=arc_primitives,
        )
        concept_id = await library.add(learned_concept)
        relevant = await library.search("rotate grid 90 degrees", k=5)
        composed = await library.compose([concept1.id, concept2.id])
        ```
    """

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        primitive_loader: PrimitiveLoader | None = None,
        composition_strategy: CompositionStrategy | None = None,
        compression_strategy: CompressionStrategy | None = None,
    ) -> None:
        """Initialize ChromaConceptLibrary.

        Args:
            embedder: Provider for text embeddings.
            vector_store: Vector store for concept storage.
            primitive_loader: Optional loader for domain-specific primitives.
            composition_strategy: Optional strategy for composing concepts.
            compression_strategy: Optional strategy for extracting concepts from trajectories.
        """
        self._embedder = embedder
        self._vector_store = vector_store
        self._composition_strategy = composition_strategy
        self._compression_strategy = compression_strategy

        # Load primitives into memory (not stored in vector store)
        self._primitives: dict[str, CodeConcept] = {}
        if primitive_loader is not None:
            self._primitives = primitive_loader.load()

    async def add(self, concept: CodeConcept) -> str:
        """Add a concept to the library.

        Uses concept.id if provided, else generates UUID.
        Embeds f"{concept.name}: {concept.description}" and stores
        in vector store with metadata.

        Args:
            concept: The concept to add.

        Returns:
            Unique concept ID.
        """
        from cognitive_core.core.types import CodeConcept

        # Use provided ID or generate new one
        concept_id = concept.id if concept.id else uuid.uuid4().hex

        # Embed name + description
        embed_text = f"{concept.name}: {concept.description}"
        embedding = self._embedder.encode(embed_text)

        # Prepare metadata
        metadata = {
            "name": concept.name,
            "description": concept.description,
            "code": concept.code,
            "signature": concept.signature,
            "examples": json.dumps(concept.examples),
            "usage_count": concept.usage_count,
            "success_rate": concept.success_rate,
            "source": concept.source,
        }

        # Store in vector store
        await self._vector_store.add(
            ids=[concept_id],
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
            documents=[embed_text],
        )

        return concept_id

    async def search(self, query: str, k: int = 5) -> list[CodeConcept]:
        """Find relevant concepts by semantic similarity.

        Searches both learned concepts in vector store and primitives in memory.
        Returns combined results sorted by similarity.

        Args:
            query: Natural language description of what's needed.
            k: Number of concepts to return.

        Returns:
            List of relevant concepts, sorted by similarity.
        """
        from cognitive_core.core.types import CodeConcept

        results: list[tuple[float, CodeConcept]] = []

        # Search primitives by matching query against name/description
        query_lower = query.lower()
        query_embedding = self._embedder.encode(query)

        for concept in self._primitives.values():
            # Compute similarity using embedding if available
            embed_text = f"{concept.name}: {concept.description}"
            primitive_embedding = self._embedder.encode(embed_text)

            # Cosine similarity
            similarity = float(
                np.dot(query_embedding, primitive_embedding)
                / (np.linalg.norm(query_embedding) * np.linalg.norm(primitive_embedding) + 1e-8)
            )
            # Convert similarity to distance (lower is better for sorting)
            distance = 1.0 - similarity
            results.append((distance, concept))

        # Search vector store for learned concepts
        query_result = await self._vector_store.query(
            embedding=query_embedding.tolist(),
            k=k,
        )

        # Reconstruct CodeConcept objects from results
        for i, concept_id in enumerate(query_result.ids):
            metadata = query_result.metadatas[i]
            distance = query_result.distances[i]

            concept = CodeConcept(
                id=concept_id,
                name=metadata.get("name", ""),
                description=metadata.get("description", ""),
                code=metadata.get("code", ""),
                signature=metadata.get("signature", ""),
                examples=json.loads(metadata.get("examples", "[]")),
                usage_count=int(metadata.get("usage_count", 0)),
                success_rate=float(metadata.get("success_rate", 0.0)),
                source=metadata.get("source", "learned"),
            )
            results.append((distance, concept))

        # Sort by distance (ascending) and return top k
        results.sort(key=lambda x: x[0])
        return [concept for _, concept in results[:k]]

    async def get(self, concept_id: str) -> CodeConcept | None:
        """Get a concept by ID.

        Checks primitives first (in-memory), then vector store.

        Args:
            concept_id: The concept ID.

        Returns:
            The concept, or None if not found.
        """
        from cognitive_core.core.types import CodeConcept

        # Check primitives first
        if concept_id in self._primitives:
            return self._primitives[concept_id]

        # Check vector store
        items = await self._vector_store.get(ids=[concept_id])
        if not items:
            return None

        item = items[0]
        metadata = item.get("metadata", {})

        return CodeConcept(
            id=concept_id,
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            code=metadata.get("code", ""),
            signature=metadata.get("signature", ""),
            examples=json.loads(metadata.get("examples", "[]")),
            usage_count=int(metadata.get("usage_count", 0)),
            success_rate=float(metadata.get("success_rate", 0.0)),
            source=metadata.get("source", "learned"),
        )

    async def compose(self, concept_ids: list[str]) -> CodeConcept | None:
        """Compose multiple concepts into one.

        Delegates to composition_strategy if available.

        Args:
            concept_ids: IDs of concepts to compose.

        Returns:
            New composed concept, or None if strategy is None or composition fails.
        """
        if self._composition_strategy is None:
            return None

        # Get all concepts by IDs
        concepts = []
        for concept_id in concept_ids:
            concept = await self.get(concept_id)
            if concept is not None:
                concepts.append(concept)

        if not concepts:
            return None

        # Delegate to composition strategy
        return await self._composition_strategy.compose(concepts)

    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """Extract new concepts via compression.

        Filters to successful trajectories only, then delegates to
        compression_strategy if available.

        Args:
            trajectories: Trajectories to extract patterns from.

        Returns:
            List of newly extracted concepts.
        """
        if self._compression_strategy is None:
            return []

        # Filter to successful trajectories only
        successful = [t for t in trajectories if t.outcome.success]

        if not successful:
            return []

        # Delegate to compression strategy
        extracted = await self._compression_strategy.compress(successful)

        # Add extracted concepts to library
        for concept in extracted:
            await self.add(concept)

        return extracted

    async def update_stats(self, concept_id: str, success: bool) -> None:
        """Update usage statistics for a concept.

        Increments usage_count and updates success_rate using simple average.

        Args:
            concept_id: The concept ID.
            success: Whether usage was successful.
        """
        # Primitives are in-memory - we could update them but they're frozen
        # So we only update learned concepts in vector store
        if concept_id in self._primitives:
            # Primitives are immutable (frozen=True), skip stats update
            return

        # Get current stats from vector store
        items = await self._vector_store.get(ids=[concept_id])
        if not items:
            return

        item = items[0]
        metadata = item.get("metadata", {})

        # Calculate new stats
        old_usage_count = int(metadata.get("usage_count", 0))
        old_success_rate = float(metadata.get("success_rate", 0.0))

        new_usage_count = old_usage_count + 1
        # Simple average: new_rate = (old_rate * old_count + success) / new_count
        new_success_rate = (old_success_rate * old_usage_count + (1.0 if success else 0.0)) / new_usage_count

        # Update metadata
        metadata["usage_count"] = new_usage_count
        metadata["success_rate"] = new_success_rate

        # Delete and re-add with updated metadata
        # (ChromaDB doesn't support metadata update, so we delete and re-add)
        embedding = item.get("embedding", [])
        document = item.get("document", "")

        await self._vector_store.delete(ids=[concept_id])
        await self._vector_store.add(
            ids=[concept_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document],
        )

    async def __len__(self) -> int:
        """Return number of concepts in the library.

        Returns:
            Count of primitives + learned concepts.
        """
        learned_count = await self._vector_store.count()
        return len(self._primitives) + learned_count
