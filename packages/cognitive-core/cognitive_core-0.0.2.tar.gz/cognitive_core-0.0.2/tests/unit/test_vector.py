"""Tests for ChromaDB vector index."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from cognitive_core.config import StorageConfig
from cognitive_core.vector.chroma import ChromaIndex


class TestChromaIndex:
    """Tests for ChromaIndex class."""

    @pytest.fixture
    def temp_storage(self) -> StorageConfig:
        """Create a temporary storage config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield StorageConfig(base_path=Path(tmpdir))

    @pytest.fixture
    def index(self, temp_storage: StorageConfig) -> ChromaIndex:
        """Create a ChromaIndex for testing."""
        return ChromaIndex("test_collection", config=temp_storage)

    @pytest.fixture
    def sample_vector(self) -> np.ndarray:
        """Create a sample vector."""
        vec = np.random.rand(768).astype(np.float32)
        return vec / np.linalg.norm(vec)  # Normalize

    def test_init_creates_collection(self, index: ChromaIndex) -> None:
        """Test that initialization creates a collection."""
        assert index.collection_name == "test_collection"
        assert len(index) == 0

    def test_init_with_prefix(self, temp_storage: StorageConfig) -> None:
        """Test collection name prefix."""
        config = StorageConfig(
            base_path=temp_storage.base_path,
            chroma_collection_prefix="atlas_",
        )
        index = ChromaIndex("experiences", config=config)

        assert index.collection_name == "atlas_experiences"

    def test_add_single_vector(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test adding a single vector."""
        index.add("vec-1", sample_vector, {"type": "test"})

        assert len(index) == 1

    def test_add_with_metadata(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test adding a vector with metadata."""
        metadata = {"task_id": "task-001", "success": True, "score": 0.95}
        index.add("vec-1", sample_vector, metadata)

        result = index.get("vec-1")
        assert result is not None
        vector, meta = result
        assert meta["task_id"] == "task-001"
        assert meta["success"] is True

    def test_add_without_metadata(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test adding a vector without metadata."""
        index.add("vec-1", sample_vector)

        result = index.get("vec-1")
        assert result is not None

    def test_add_batch(self, index: ChromaIndex) -> None:
        """Test batch add operation."""
        vectors = np.random.rand(5, 768).astype(np.float32)
        ids = [f"vec-{i}" for i in range(5)]
        metadatas = [{"index": i} for i in range(5)]

        index.add_batch(ids, vectors, metadatas)

        assert len(index) == 5

    def test_add_batch_empty(self, index: ChromaIndex) -> None:
        """Test batch add with empty list."""
        index.add_batch([], np.array([]).reshape(0, 768), [])

        assert len(index) == 0

    def test_search_basic(self, index: ChromaIndex) -> None:
        """Test basic search functionality."""
        # Add some vectors
        for i in range(5):
            vec = np.random.rand(768).astype(np.float32)
            vec = vec / np.linalg.norm(vec)
            index.add(f"vec-{i}", vec, {"index": i})

        # Search with a query vector
        query = np.random.rand(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        results = index.search(query, k=3)

        assert len(results) == 3
        # Results should be tuples of (id, score, metadata)
        for id_, score, meta in results:
            assert id_.startswith("vec-")
            assert isinstance(score, float)
            assert "index" in meta

    def test_search_returns_sorted(self, index: ChromaIndex) -> None:
        """Test that search results are sorted by similarity."""
        # Add a known vector and its perturbations
        base = np.ones(768, dtype=np.float32)
        base = base / np.linalg.norm(base)

        # Create vectors at different distances
        close = base + np.random.rand(768).astype(np.float32) * 0.1
        close = close / np.linalg.norm(close)

        medium = base + np.random.rand(768).astype(np.float32) * 0.5
        medium = medium / np.linalg.norm(medium)

        far = np.random.rand(768).astype(np.float32)
        far = far / np.linalg.norm(far)

        index.add("close", close)
        index.add("medium", medium)
        index.add("far", far)

        # Search for base
        results = index.search(base, k=3)

        # Should be sorted by similarity (highest first for cosine)
        assert len(results) == 3
        scores = [r[1] for r in results]
        # For cosine, higher is more similar
        assert scores[0] >= scores[1] >= scores[2]

    def test_search_empty_collection(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test searching an empty collection."""
        results = index.search(sample_vector, k=5)

        assert results == []

    def test_search_k_larger_than_collection(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test search when k is larger than collection size."""
        index.add("vec-1", sample_vector)
        index.add("vec-2", sample_vector)

        results = index.search(sample_vector, k=10)

        # Should return only available items
        assert len(results) == 2

    def test_search_with_filter(self, index: ChromaIndex) -> None:
        """Test search with metadata filter."""
        for i in range(10):
            vec = np.random.rand(768).astype(np.float32)
            vec = vec / np.linalg.norm(vec)
            index.add(f"vec-{i}", vec, {"category": "A" if i < 5 else "B"})

        query = np.random.rand(768).astype(np.float32)
        query = query / np.linalg.norm(query)

        # Filter to only category A
        results = index.search(query, k=10, filter={"category": "A"})

        assert len(results) == 5
        for _, _, meta in results:
            assert meta["category"] == "A"

    def test_get_existing(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test getting an existing vector."""
        index.add("vec-1", sample_vector, {"key": "value"})

        result = index.get("vec-1")

        assert result is not None
        vector, metadata = result
        np.testing.assert_array_almost_equal(vector, sample_vector, decimal=5)
        assert metadata["key"] == "value"

    def test_get_nonexistent(self, index: ChromaIndex) -> None:
        """Test getting a nonexistent vector."""
        result = index.get("nonexistent")

        assert result is None

    def test_delete_existing(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test deleting an existing vector."""
        index.add("vec-1", sample_vector)
        assert len(index) == 1

        deleted = index.delete("vec-1")

        assert deleted is True
        assert len(index) == 0

    def test_delete_nonexistent(self, index: ChromaIndex) -> None:
        """Test deleting a nonexistent vector."""
        deleted = index.delete("nonexistent")

        assert deleted is False

    def test_update_vector(self, index: ChromaIndex) -> None:
        """Test updating a vector."""
        original = np.ones(768, dtype=np.float32)
        original = original / np.linalg.norm(original)

        new_vec = np.zeros(768, dtype=np.float32)
        new_vec[0] = 1.0

        index.add("vec-1", original)
        updated = index.update("vec-1", vector=new_vec)

        assert updated is True

        result = index.get("vec-1")
        assert result is not None
        retrieved, _ = result
        np.testing.assert_array_almost_equal(retrieved, new_vec, decimal=5)

    def test_update_metadata(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test updating metadata only."""
        index.add("vec-1", sample_vector, {"version": 1})

        updated = index.update("vec-1", metadata={"version": 2})

        assert updated is True

        result = index.get("vec-1")
        assert result is not None
        _, metadata = result
        assert metadata["version"] == 2

    def test_update_nonexistent(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test updating a nonexistent vector."""
        updated = index.update("nonexistent", vector=sample_vector)

        assert updated is False

    def test_clear(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test clearing the index."""
        for i in range(5):
            index.add(f"vec-{i}", sample_vector)

        assert len(index) == 5

        index.clear()

        assert len(index) == 0

    def test_len(self, index: ChromaIndex, sample_vector: np.ndarray) -> None:
        """Test __len__ method."""
        assert len(index) == 0

        index.add("vec-1", sample_vector)
        assert len(index) == 1

        index.add("vec-2", sample_vector)
        assert len(index) == 2

    def test_persistence(self, temp_storage: StorageConfig) -> None:
        """Test that data persists across instances."""
        vec = np.random.rand(768).astype(np.float32)
        vec = vec / np.linalg.norm(vec)

        # Create and populate index
        index1 = ChromaIndex("persist_test", config=temp_storage)
        index1.add("vec-1", vec, {"test": True})

        # Create new instance pointing to same storage
        index2 = ChromaIndex("persist_test", config=temp_storage)

        assert len(index2) == 1
        result = index2.get("vec-1")
        assert result is not None

    def test_different_distance_metrics(self, temp_storage: StorageConfig) -> None:
        """Test different distance metrics."""
        for metric in ["cosine", "l2", "ip"]:
            config = StorageConfig(
                base_path=temp_storage.base_path,
                distance_metric=metric,
            )
            index = ChromaIndex(f"test_{metric}", config=config)

            vec = np.random.rand(768).astype(np.float32)
            vec = vec / np.linalg.norm(vec)
            index.add("vec-1", vec)

            results = index.search(vec, k=1)
            assert len(results) == 1
