"""Tests for ChromaConceptLibrary implementation."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from cognitive_core.core.types import CodeConcept, Outcome, Step, Task, Trajectory, VerificationSpec
from cognitive_core.memory.concepts import ChromaConceptLibrary
from cognitive_core.memory.storage import QueryResult


class MockEmbeddingProvider:
    """Mock embedding provider for testing."""

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    def encode(self, text: str) -> np.ndarray:
        """Return deterministic embedding based on text hash."""
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(self._dimension).astype(np.float32)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Return embeddings for multiple texts."""
        return np.array([self.encode(t) for t in texts])

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return "mock-embedding-model"


class MockVectorStore:
    """Mock vector store for testing."""

    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    async def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        for i, item_id in enumerate(ids):
            self._items[item_id] = {
                "id": item_id,
                "embedding": embeddings[i],
                "metadata": metadatas[i],
                "document": documents[i],
            }

    async def query(
        self,
        embedding: list[float],
        k: int,
        where: dict[str, Any] | None = None,
    ) -> QueryResult:
        if not self._items:
            return QueryResult(ids=[], distances=[], metadatas=[], documents=[])

        # Calculate distances using cosine similarity
        query_vec = np.array(embedding)
        results = []

        for item_id, item in self._items.items():
            item_vec = np.array(item["embedding"])
            # Cosine distance
            similarity = np.dot(query_vec, item_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(item_vec) + 1e-8
            )
            distance = 1.0 - similarity
            results.append((distance, item_id, item))

        # Sort by distance
        results.sort(key=lambda x: x[0])
        results = results[:k]

        return QueryResult(
            ids=[r[1] for r in results],
            distances=[r[0] for r in results],
            metadatas=[r[2]["metadata"] for r in results],
            documents=[r[2]["document"] for r in results],
        )

    async def delete(self, ids: list[str]) -> None:
        for item_id in ids:
            self._items.pop(item_id, None)

    async def get(self, ids: list[str]) -> list[dict[str, Any]]:
        return [self._items[item_id] for item_id in ids if item_id in self._items]

    async def count(self) -> int:
        return len(self._items)


class MockPrimitiveLoader:
    """Mock primitive loader for testing."""

    def __init__(self, primitives: dict[str, CodeConcept] | None = None) -> None:
        self._primitives = primitives or {}

    def load(self) -> dict[str, CodeConcept]:
        return self._primitives


class MockCompositionStrategy:
    """Mock composition strategy for testing."""

    def __init__(self, return_value: CodeConcept | None = None) -> None:
        self._return_value = return_value
        self.compose_called = False
        self.compose_args: list[CodeConcept] | None = None

    async def compose(self, concepts: list[CodeConcept]) -> CodeConcept | None:
        self.compose_called = True
        self.compose_args = concepts
        return self._return_value


class MockCompressionStrategy:
    """Mock compression strategy for testing."""

    def __init__(self, return_value: list[CodeConcept] | None = None) -> None:
        self._return_value = return_value or []
        self.compress_called = False
        self.compress_args: list[Trajectory] | None = None

    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        self.compress_called = True
        self.compress_args = trajectories
        return self._return_value


def create_concept(
    id: str = "",
    name: str = "test_concept",
    description: str = "A test concept",
    code: str = "def test(): pass",
    signature: str = "() -> None",
    source: str = "learned",
) -> CodeConcept:
    """Helper to create test concepts."""
    return CodeConcept(
        id=id,
        name=name,
        description=description,
        code=code,
        signature=signature,
        examples=[("input", "output")],
        usage_count=0,
        success_rate=0.0,
        source=source,
    )


def create_trajectory(success: bool = True) -> Trajectory:
    """Helper to create test trajectories."""
    return Trajectory(
        task=Task(
            id="task-1",
            domain="test",
            description="Test task",
            verification=VerificationSpec(method="exact_match"),
        ),
        steps=[
            Step(
                action="test_action",
                observation="test_observation",
            )
        ],
        outcome=Outcome(success=success),
        agent_id="test-agent",
    )


class TestChromaConceptLibraryAdd:
    """Tests for add() method."""

    @pytest.fixture
    def library(self) -> ChromaConceptLibrary:
        """Create a library for testing."""
        return ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

    @pytest.mark.asyncio
    async def test_add_stores_concept_and_returns_id(self, library: ChromaConceptLibrary) -> None:
        """Test that add stores concept and returns ID."""
        concept = create_concept(id="test-id-123")

        result_id = await library.add(concept)

        assert result_id == "test-id-123"

        # Verify concept is stored
        retrieved = await library.get("test-id-123")
        assert retrieved is not None
        assert retrieved.name == concept.name

    @pytest.mark.asyncio
    async def test_add_generates_uuid_if_no_id(self, library: ChromaConceptLibrary) -> None:
        """Test that add generates UUID if concept has no ID."""
        concept = create_concept(id="")

        result_id = await library.add(concept)

        assert result_id != ""
        assert len(result_id) == 32  # UUID hex format

    @pytest.mark.asyncio
    async def test_add_stores_metadata_correctly(self, library: ChromaConceptLibrary) -> None:
        """Test that add stores all metadata correctly."""
        concept = create_concept(
            id="meta-test",
            name="meta_name",
            description="meta description",
            code="def meta(): pass",
            signature="() -> str",
            source="composed",
        )

        await library.add(concept)
        retrieved = await library.get("meta-test")

        assert retrieved is not None
        assert retrieved.name == "meta_name"
        assert retrieved.description == "meta description"
        assert retrieved.code == "def meta(): pass"
        assert retrieved.signature == "() -> str"
        assert retrieved.source == "composed"


class TestChromaConceptLibrarySearch:
    """Tests for search() method."""

    @pytest.fixture
    def library(self) -> ChromaConceptLibrary:
        """Create a library for testing."""
        return ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

    @pytest.mark.asyncio
    async def test_search_returns_relevant_concepts(self, library: ChromaConceptLibrary) -> None:
        """Test that search returns relevant concepts."""
        # Add some concepts
        await library.add(create_concept(id="c1", name="rotate", description="rotate grid"))
        await library.add(create_concept(id="c2", name="flip", description="flip grid"))

        results = await library.search("rotate grid 90 degrees", k=5)

        assert len(results) > 0
        # Results should include our concepts
        result_ids = [c.id for c in results]
        assert "c1" in result_ids or "c2" in result_ids

    @pytest.mark.asyncio
    async def test_search_includes_primitives(self) -> None:
        """Test that search includes primitives in results."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive_op", description="a primitive", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        # Add a learned concept
        await library.add(create_concept(id="learned-1", name="learned_op", description="a learned concept"))

        results = await library.search("primitive", k=5)

        # Should include both primitive and learned
        result_ids = [c.id for c in results]
        assert "prim-1" in result_ids

    @pytest.mark.asyncio
    async def test_search_returns_empty_for_empty_library(self, library: ChromaConceptLibrary) -> None:
        """Test that search returns empty list for empty library."""
        results = await library.search("anything", k=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_search_respects_k_limit(self, library: ChromaConceptLibrary) -> None:
        """Test that search respects k limit."""
        # Add many concepts
        for i in range(10):
            await library.add(create_concept(id=f"c{i}", name=f"concept_{i}", description=f"description {i}"))

        results = await library.search("concept", k=3)

        assert len(results) == 3


class TestChromaConceptLibraryGet:
    """Tests for get() method."""

    @pytest.fixture
    def library(self) -> ChromaConceptLibrary:
        """Create a library for testing."""
        return ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

    @pytest.mark.asyncio
    async def test_get_retrieves_stored_concept(self, library: ChromaConceptLibrary) -> None:
        """Test that get retrieves stored concept."""
        concept = create_concept(id="stored-1", name="stored_concept")
        await library.add(concept)

        retrieved = await library.get("stored-1")

        assert retrieved is not None
        assert retrieved.id == "stored-1"
        assert retrieved.name == "stored_concept"

    @pytest.mark.asyncio
    async def test_get_returns_primitives(self) -> None:
        """Test that get returns primitives."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive_op", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        retrieved = await library.get("prim-1")

        assert retrieved is not None
        assert retrieved.id == "prim-1"
        assert retrieved.source == "primitive"

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_id(self, library: ChromaConceptLibrary) -> None:
        """Test that get returns None for missing ID."""
        retrieved = await library.get("nonexistent")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_checks_primitives_first(self) -> None:
        """Test that get checks primitives before vector store."""
        primitives = {
            "shared-id": create_concept(id="shared-id", name="primitive_version", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        # Add learned concept with same ID (shouldn't happen in practice)
        await library.add(create_concept(id="shared-id", name="learned_version", source="learned"))

        # Should return primitive
        retrieved = await library.get("shared-id")

        assert retrieved is not None
        assert retrieved.source == "primitive"


class TestChromaConceptLibraryCompose:
    """Tests for compose() method."""

    @pytest.mark.asyncio
    async def test_compose_delegates_to_strategy(self) -> None:
        """Test that compose delegates to composition strategy."""
        composed_concept = create_concept(id="composed-1", name="composed", source="composed")
        strategy = MockCompositionStrategy(return_value=composed_concept)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            composition_strategy=strategy,
        )

        # Add concepts to compose
        await library.add(create_concept(id="c1", name="concept1"))
        await library.add(create_concept(id="c2", name="concept2"))

        result = await library.compose(["c1", "c2"])

        assert strategy.compose_called
        assert len(strategy.compose_args) == 2
        assert result == composed_concept

    @pytest.mark.asyncio
    async def test_compose_returns_none_when_no_strategy(self) -> None:
        """Test that compose returns None when no strategy."""
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

        await library.add(create_concept(id="c1", name="concept1"))

        result = await library.compose(["c1"])

        assert result is None

    @pytest.mark.asyncio
    async def test_compose_returns_none_for_empty_ids(self) -> None:
        """Test that compose returns None for empty concept IDs."""
        strategy = MockCompositionStrategy()

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            composition_strategy=strategy,
        )

        result = await library.compose([])

        assert result is None

    @pytest.mark.asyncio
    async def test_compose_returns_none_for_nonexistent_ids(self) -> None:
        """Test that compose returns None when IDs don't exist."""
        strategy = MockCompositionStrategy()

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            composition_strategy=strategy,
        )

        result = await library.compose(["nonexistent-1", "nonexistent-2"])

        assert result is None


class TestChromaConceptLibraryCompress:
    """Tests for compress() method."""

    @pytest.mark.asyncio
    async def test_compress_delegates_to_strategy(self) -> None:
        """Test that compress delegates to compression strategy."""
        extracted = [create_concept(id="extracted-1", name="extracted")]
        strategy = MockCompressionStrategy(return_value=extracted)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            compression_strategy=strategy,
        )

        trajectories = [create_trajectory(success=True)]
        result = await library.compress(trajectories)

        assert strategy.compress_called
        assert len(strategy.compress_args) == 1
        assert result == extracted

    @pytest.mark.asyncio
    async def test_compress_filters_to_successful_only(self) -> None:
        """Test that compress filters to successful trajectories only."""
        strategy = MockCompressionStrategy(return_value=[])

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            compression_strategy=strategy,
        )

        trajectories = [
            create_trajectory(success=True),
            create_trajectory(success=False),
            create_trajectory(success=True),
        ]

        await library.compress(trajectories)

        assert strategy.compress_called
        # Should only pass successful trajectories
        assert len(strategy.compress_args) == 2
        assert all(t.outcome.success for t in strategy.compress_args)

    @pytest.mark.asyncio
    async def test_compress_returns_empty_when_no_strategy(self) -> None:
        """Test that compress returns empty list when no strategy."""
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

        trajectories = [create_trajectory(success=True)]
        result = await library.compress(trajectories)

        assert result == []

    @pytest.mark.asyncio
    async def test_compress_returns_empty_for_all_failures(self) -> None:
        """Test that compress returns empty for all failed trajectories."""
        strategy = MockCompressionStrategy()

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            compression_strategy=strategy,
        )

        trajectories = [create_trajectory(success=False), create_trajectory(success=False)]
        result = await library.compress(trajectories)

        assert result == []
        # Strategy should not be called if no successful trajectories
        assert not strategy.compress_called

    @pytest.mark.asyncio
    async def test_compress_adds_extracted_concepts(self) -> None:
        """Test that compress adds extracted concepts to library."""
        extracted = [create_concept(id="extracted-1", name="extracted")]
        strategy = MockCompressionStrategy(return_value=extracted)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            compression_strategy=strategy,
        )

        trajectories = [create_trajectory(success=True)]
        await library.compress(trajectories)

        # Verify concept was added
        retrieved = await library.get("extracted-1")
        assert retrieved is not None
        assert retrieved.name == "extracted"


class TestChromaConceptLibraryUpdateStats:
    """Tests for update_stats() method."""

    @pytest.fixture
    def library(self) -> ChromaConceptLibrary:
        """Create a library for testing."""
        return ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

    @pytest.mark.asyncio
    async def test_update_stats_increments_usage(self, library: ChromaConceptLibrary) -> None:
        """Test that update_stats increments usage_count."""
        await library.add(create_concept(id="stats-1", name="stats_concept"))

        await library.update_stats("stats-1", success=True)

        retrieved = await library.get("stats-1")
        assert retrieved is not None
        assert retrieved.usage_count == 1

    @pytest.mark.asyncio
    async def test_update_stats_updates_success_rate(self, library: ChromaConceptLibrary) -> None:
        """Test that update_stats updates success_rate correctly."""
        await library.add(create_concept(id="stats-1", name="stats_concept"))

        # First success
        await library.update_stats("stats-1", success=True)
        retrieved = await library.get("stats-1")
        assert retrieved.success_rate == 1.0

        # Then failure
        await library.update_stats("stats-1", success=False)
        retrieved = await library.get("stats-1")
        assert retrieved.success_rate == 0.5  # (1 + 0) / 2

    @pytest.mark.asyncio
    async def test_update_stats_does_nothing_for_missing_id(self, library: ChromaConceptLibrary) -> None:
        """Test that update_stats does nothing for missing ID."""
        # Should not raise
        await library.update_stats("nonexistent", success=True)

    @pytest.mark.asyncio
    async def test_update_stats_skips_primitives(self) -> None:
        """Test that update_stats skips primitives (they're immutable)."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        # Should not raise
        await library.update_stats("prim-1", success=True)

        # Primitive should be unchanged (still has initial stats)
        retrieved = await library.get("prim-1")
        assert retrieved.usage_count == 0


class TestChromaConceptLibraryLen:
    """Tests for __len__() method."""

    @pytest.mark.asyncio
    async def test_len_counts_primitives_plus_learned(self) -> None:
        """Test that __len__ counts primitives + learned."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive1", source="primitive"),
            "prim-2": create_concept(id="prim-2", name="primitive2", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        # Add learned concepts
        await library.add(create_concept(id="l1", name="learned1"))
        await library.add(create_concept(id="l2", name="learned2"))
        await library.add(create_concept(id="l3", name="learned3"))

        count = await library.__len__()

        assert count == 5  # 2 primitives + 3 learned

    @pytest.mark.asyncio
    async def test_len_empty_library(self) -> None:
        """Test __len__ on empty library."""
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

        count = await library.__len__()

        assert count == 0

    @pytest.mark.asyncio
    async def test_len_primitives_only(self) -> None:
        """Test __len__ with primitives only."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive1", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        count = await library.__len__()

        assert count == 1


class TestChromaConceptLibraryPrimitiveLoading:
    """Tests for primitive loading."""

    @pytest.mark.asyncio
    async def test_primitives_loaded_at_init(self) -> None:
        """Test that primitives are loaded at __init__."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive1", source="primitive"),
            "prim-2": create_concept(id="prim-2", name="primitive2", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
            primitive_loader=loader,
        )

        # Primitives should be immediately available
        p1 = await library.get("prim-1")
        p2 = await library.get("prim-2")

        assert p1 is not None
        assert p2 is not None

    @pytest.mark.asyncio
    async def test_primitives_not_in_vector_store(self) -> None:
        """Test that primitives are NOT stored in vector store."""
        primitives = {
            "prim-1": create_concept(id="prim-1", name="primitive1", source="primitive"),
        }
        loader = MockPrimitiveLoader(primitives)

        vector_store = MockVectorStore()
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=vector_store,
            primitive_loader=loader,
        )

        # Vector store should be empty
        count = await vector_store.count()
        assert count == 0

        # But primitive should still be retrievable
        p1 = await library.get("prim-1")
        assert p1 is not None

    @pytest.mark.asyncio
    async def test_no_primitives_when_loader_is_none(self) -> None:
        """Test that no primitives when loader is None."""
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

        count = await library.__len__()
        assert count == 0


class TestChromaConceptLibraryProtocolCompliance:
    """Tests for ConceptLibrary protocol compliance."""

    def test_implements_concept_library_protocol(self) -> None:
        """Test that ChromaConceptLibrary has all required methods."""
        library = ChromaConceptLibrary(
            embedder=MockEmbeddingProvider(),
            vector_store=MockVectorStore(),
        )

        # Check all required methods exist
        assert hasattr(library, "add")
        assert callable(library.add)

        assert hasattr(library, "search")
        assert callable(library.search)

        assert hasattr(library, "get")
        assert callable(library.get)

        assert hasattr(library, "compose")
        assert callable(library.compose)

        assert hasattr(library, "compress")
        assert callable(library.compress)

        assert hasattr(library, "update_stats")
        assert callable(library.update_stats)

        assert hasattr(library, "__len__")
        assert callable(library.__len__)
