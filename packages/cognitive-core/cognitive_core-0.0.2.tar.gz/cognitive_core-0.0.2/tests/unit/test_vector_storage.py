"""Tests for VectorStore protocol and ChromaVectorStore implementation."""

from __future__ import annotations

import uuid

import chromadb
import pytest

from cognitive_core.memory.storage import ChromaVectorStore, QueryResult, VectorStore


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_create_query_result(self) -> None:
        """Test QueryResult can be created with all fields."""
        result = QueryResult(
            ids=["id-1", "id-2"],
            distances=[0.1, 0.2],
            metadatas=[{"key": "value1"}, {"key": "value2"}],
            documents=["doc1", "doc2"],
        )

        assert result.ids == ["id-1", "id-2"]
        assert result.distances == [0.1, 0.2]
        assert result.metadatas == [{"key": "value1"}, {"key": "value2"}]
        assert result.documents == ["doc1", "doc2"]

    def test_create_empty_query_result(self) -> None:
        """Test QueryResult with empty lists."""
        result = QueryResult(ids=[], distances=[], metadatas=[], documents=[])

        assert result.ids == []
        assert result.distances == []
        assert result.metadatas == []
        assert result.documents == []

    def test_query_result_equality(self) -> None:
        """Test QueryResult equality comparison."""
        result1 = QueryResult(
            ids=["id-1"],
            distances=[0.1],
            metadatas=[{"key": "value"}],
            documents=["doc1"],
        )
        result2 = QueryResult(
            ids=["id-1"],
            distances=[0.1],
            metadatas=[{"key": "value"}],
            documents=["doc1"],
        )

        assert result1 == result2


class TestVectorStoreProtocol:
    """Tests for VectorStore protocol compliance."""

    def test_chroma_vector_store_is_protocol_compliant(self) -> None:
        """Test that ChromaVectorStore implements VectorStore protocol."""
        # Create instance
        store = ChromaVectorStore(collection_name="test_protocol")

        # Check it's a runtime checkable protocol instance
        assert isinstance(store, VectorStore)


class TestChromaVectorStore:
    """Tests for ChromaVectorStore implementation."""

    @pytest.fixture
    def store(self) -> ChromaVectorStore:
        """Create an ephemeral ChromaVectorStore for testing with unique collection."""
        # Use a unique collection name per test to ensure isolation
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
        client = chromadb.Client()
        collection = client.get_or_create_collection(collection_name)
        return ChromaVectorStore(collection=collection)

    @pytest.fixture
    def sample_embedding(self) -> list[float]:
        """Create a sample embedding vector."""
        import random

        random.seed(42)
        return [random.random() for _ in range(384)]

    @pytest.mark.asyncio
    async def test_init_with_collection_name(self) -> None:
        """Test initialization with collection name."""
        collection_name = f"my_collection_{uuid.uuid4().hex[:8]}"
        store = ChromaVectorStore(collection_name=collection_name)

        # Should be able to count (triggers collection creation)
        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_init_with_existing_collection(self) -> None:
        """Test initialization with an existing ChromaDB collection."""
        collection_name = f"existing_collection_{uuid.uuid4().hex[:8]}"
        client = chromadb.Client()
        collection = client.get_or_create_collection(collection_name)

        store = ChromaVectorStore(collection=collection)
        count = await store.count()
        assert count == 0

    def test_init_without_collection_or_name_raises(self) -> None:
        """Test that initialization without collection or name raises error."""
        with pytest.raises(ValueError, match="Either collection or collection_name"):
            ChromaVectorStore()

    @pytest.mark.asyncio
    async def test_add_single_item(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test adding a single item."""
        await store.add(
            ids=["item-1"],
            embeddings=[sample_embedding],
            metadatas=[{"type": "test"}],
            documents=["Test document"],
        )

        count = await store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_multiple_items(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test adding multiple items."""
        await store.add(
            ids=["item-1", "item-2", "item-3"],
            embeddings=[sample_embedding, sample_embedding, sample_embedding],
            metadatas=[{"index": 1}, {"index": 2}, {"index": 3}],
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        count = await store.count()
        assert count == 3

    @pytest.mark.asyncio
    async def test_add_empty_list(self, store: ChromaVectorStore) -> None:
        """Test adding empty list does nothing."""
        await store.add(ids=[], embeddings=[], metadatas=[], documents=[])

        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_add_with_empty_metadata(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test adding items with empty metadata dicts."""
        await store.add(
            ids=["item-1"],
            embeddings=[sample_embedding],
            metadatas=[{}],
            documents=["Test document"],
        )

        count = await store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_query_basic(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test basic query functionality."""
        # Add some items
        await store.add(
            ids=["item-1", "item-2", "item-3"],
            embeddings=[sample_embedding, sample_embedding, sample_embedding],
            metadatas=[{"type": "a"}, {"type": "b"}, {"type": "c"}],
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        # Query
        results = await store.query(embedding=sample_embedding, k=2)

        assert len(results.ids) == 2
        assert len(results.distances) == 2
        assert len(results.metadatas) == 2
        assert len(results.documents) == 2

    @pytest.mark.asyncio
    async def test_query_empty_collection(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test querying an empty collection returns empty result."""
        results = await store.query(embedding=sample_embedding, k=5)

        assert results.ids == []
        assert results.distances == []
        assert results.metadatas == []
        assert results.documents == []

    @pytest.mark.asyncio
    async def test_query_k_larger_than_collection(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test query when k is larger than collection size."""
        await store.add(
            ids=["item-1", "item-2"],
            embeddings=[sample_embedding, sample_embedding],
            metadatas=[{}, {}],
            documents=["Doc 1", "Doc 2"],
        )

        results = await store.query(embedding=sample_embedding, k=10)

        # Should return only available items
        assert len(results.ids) == 2

    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test query with metadata filtering."""
        await store.add(
            ids=["item-1", "item-2", "item-3", "item-4"],
            embeddings=[sample_embedding, sample_embedding, sample_embedding, sample_embedding],
            metadatas=[
                {"category": "A"},
                {"category": "B"},
                {"category": "A"},
                {"category": "B"},
            ],
            documents=["Doc 1", "Doc 2", "Doc 3", "Doc 4"],
        )

        # Filter to only category A
        results = await store.query(
            embedding=sample_embedding,
            k=10,
            where={"category": "A"},
        )

        assert len(results.ids) == 2
        for metadata in results.metadatas:
            assert metadata["category"] == "A"

    @pytest.mark.asyncio
    async def test_get_existing_items(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test getting existing items by ID."""
        await store.add(
            ids=["item-1", "item-2"],
            embeddings=[sample_embedding, sample_embedding],
            metadatas=[{"key": "value1"}, {"key": "value2"}],
            documents=["Doc 1", "Doc 2"],
        )

        items = await store.get(ids=["item-1"])

        assert len(items) == 1
        assert items[0]["id"] == "item-1"
        assert items[0]["metadata"]["key"] == "value1"
        assert items[0]["document"] == "Doc 1"
        assert "embedding" in items[0]

    @pytest.mark.asyncio
    async def test_get_multiple_items(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test getting multiple items by ID."""
        await store.add(
            ids=["item-1", "item-2", "item-3"],
            embeddings=[sample_embedding, sample_embedding, sample_embedding],
            metadatas=[{"index": 1}, {"index": 2}, {"index": 3}],
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        items = await store.get(ids=["item-1", "item-3"])

        assert len(items) == 2
        item_ids = [item["id"] for item in items]
        assert "item-1" in item_ids
        assert "item-3" in item_ids

    @pytest.mark.asyncio
    async def test_get_nonexistent_items(
        self, store: ChromaVectorStore
    ) -> None:
        """Test getting nonexistent items returns empty list."""
        items = await store.get(ids=["nonexistent"])

        assert items == []

    @pytest.mark.asyncio
    async def test_get_empty_list(self, store: ChromaVectorStore) -> None:
        """Test getting with empty list returns empty list."""
        items = await store.get(ids=[])

        assert items == []

    @pytest.mark.asyncio
    async def test_delete_existing_items(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test deleting existing items."""
        await store.add(
            ids=["item-1", "item-2", "item-3"],
            embeddings=[sample_embedding, sample_embedding, sample_embedding],
            metadatas=[{}, {}, {}],
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        assert await store.count() == 3

        await store.delete(ids=["item-1", "item-2"])

        assert await store.count() == 1
        items = await store.get(ids=["item-3"])
        assert len(items) == 1

    @pytest.mark.asyncio
    async def test_delete_empty_list(self, store: ChromaVectorStore) -> None:
        """Test deleting empty list does nothing."""
        await store.delete(ids=[])

        # Should not raise
        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_empty(self, store: ChromaVectorStore) -> None:
        """Test count on empty store."""
        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_after_operations(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test count after various operations."""
        # Add items
        await store.add(
            ids=["item-1", "item-2"],
            embeddings=[sample_embedding, sample_embedding],
            metadatas=[{}, {}],
            documents=["Doc 1", "Doc 2"],
        )
        assert await store.count() == 2

        # Delete one
        await store.delete(ids=["item-1"])
        assert await store.count() == 1

        # Add more
        await store.add(
            ids=["item-3", "item-4"],
            embeddings=[sample_embedding, sample_embedding],
            metadatas=[{}, {}],
            documents=["Doc 3", "Doc 4"],
        )
        assert await store.count() == 3

    @pytest.mark.asyncio
    async def test_query_returns_query_result(
        self, store: ChromaVectorStore, sample_embedding: list[float]
    ) -> None:
        """Test that query returns a QueryResult instance."""
        await store.add(
            ids=["item-1"],
            embeddings=[sample_embedding],
            metadatas=[{"key": "value"}],
            documents=["Test doc"],
        )

        result = await store.query(embedding=sample_embedding, k=1)

        assert isinstance(result, QueryResult)
        assert result.ids == ["item-1"]
        assert len(result.distances) == 1
        assert result.metadatas == [{"key": "value"}]
        assert result.documents == ["Test doc"]

    @pytest.mark.asyncio
    async def test_similarity_ordering(self) -> None:
        """Test that query results are ordered by similarity."""
        # Create a fresh store for this test to ensure isolation
        collection_name = f"similarity_test_{uuid.uuid4().hex[:8]}"
        client = chromadb.Client()
        collection = client.get_or_create_collection(collection_name)
        store = ChromaVectorStore(collection=collection)

        # Create distinct embeddings
        base = [1.0] * 384
        close = [1.0 + 0.01 * i for i in range(384)]
        far = [0.5 - 0.01 * i for i in range(384)]

        await store.add(
            ids=["close", "far"],
            embeddings=[close, far],
            metadatas=[{"type": "close"}, {"type": "far"}],
            documents=["Close doc", "Far doc"],
        )

        results = await store.query(embedding=base, k=2)

        # Close should be first (smaller distance)
        assert results.ids[0] == "close"
        assert results.ids[1] == "far"
        # First distance should be smaller than second
        assert results.distances[0] <= results.distances[1]
