"""Tests for BGE embeddings."""

from __future__ import annotations

import numpy as np
import pytest

from cognitive_core.config import EmbeddingConfig


# Mark all tests that require model loading as slow
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


class TestBGEEmbeddings:
    """Tests for BGEEmbeddings class."""

    @pytest.fixture
    def embeddings(self):
        """Create embeddings instance with caching enabled."""
        # Import here to avoid loading model during test collection
        from cognitive_core.embeddings.bge import BGEEmbeddings

        config = EmbeddingConfig(cache_enabled=True)
        return BGEEmbeddings(config)

    @pytest.fixture
    def embeddings_no_cache(self):
        """Create embeddings instance without caching."""
        from cognitive_core.embeddings.bge import BGEEmbeddings

        config = EmbeddingConfig(cache_enabled=False)
        return BGEEmbeddings(config)

    def test_lazy_loading(self) -> None:
        """Test that model is not loaded until first use."""
        from cognitive_core.embeddings.bge import BGEEmbeddings

        config = EmbeddingConfig()
        embeddings = BGEEmbeddings(config)

        # Model should not be loaded yet
        assert embeddings._model is None

    def test_encode_single_text(self, embeddings) -> None:
        """Test encoding a single text string."""
        text = "This is a test sentence for embedding."
        embedding = embeddings.encode(text)

        # Check output shape and type
        assert isinstance(embedding, np.ndarray)
        assert embedding.ndim == 1
        assert embedding.shape[0] == 768  # BGE base dimension

        # Check normalized (L2 norm should be ~1)
        norm = np.linalg.norm(embedding)
        assert 0.99 < norm < 1.01

    def test_encode_empty_string(self, embeddings) -> None:
        """Test encoding an empty string."""
        embedding = embeddings.encode("")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 768

    def test_encode_consistency(self, embeddings) -> None:
        """Test that same text produces same embedding."""
        text = "Consistent embedding test"

        embedding1 = embeddings.encode(text)
        embedding2 = embeddings.encode(text)

        np.testing.assert_array_almost_equal(embedding1, embedding2)

    def test_encode_batch(self, embeddings) -> None:
        """Test encoding a batch of texts."""
        texts = [
            "First sentence to embed",
            "Second sentence to embed",
            "Third sentence to embed",
        ]
        embeddings_batch = embeddings.encode_batch(texts)

        # Check output shape
        assert isinstance(embeddings_batch, np.ndarray)
        assert embeddings_batch.ndim == 2
        assert embeddings_batch.shape == (3, 768)

        # Each should be normalized
        for i in range(3):
            norm = np.linalg.norm(embeddings_batch[i])
            assert 0.99 < norm < 1.01

    def test_encode_batch_empty(self, embeddings) -> None:
        """Test encoding an empty batch."""
        embeddings_batch = embeddings.encode_batch([])

        assert isinstance(embeddings_batch, np.ndarray)
        assert embeddings_batch.shape == (0, 768)

    def test_encode_batch_single(self, embeddings) -> None:
        """Test encoding a batch with single item."""
        texts = ["Single item batch"]
        embeddings_batch = embeddings.encode_batch(texts)

        assert embeddings_batch.shape == (1, 768)

    def test_caching_works(self, embeddings) -> None:
        """Test that caching stores and retrieves embeddings."""
        text = "Cache test sentence"

        # First call should compute
        embedding1 = embeddings.encode(text)
        cache_info1 = embeddings.cache_info

        # Second call should hit cache
        embedding2 = embeddings.encode(text)
        cache_info2 = embeddings.cache_info

        # Results should be identical
        np.testing.assert_array_equal(embedding1, embedding2)

        # Cache should have a hit
        assert cache_info2["hits"] > cache_info1["hits"]

    def test_cache_disabled(self, embeddings_no_cache) -> None:
        """Test that caching can be disabled."""
        text = "No cache test"

        embeddings_no_cache.encode(text)
        cache_info = embeddings_no_cache.cache_info

        # Cache should be empty/disabled
        assert cache_info["size"] == 0

    def test_clear_cache(self, embeddings) -> None:
        """Test clearing the cache."""
        # Populate cache
        embeddings.encode("Text 1")
        embeddings.encode("Text 2")

        assert embeddings.cache_info["size"] > 0

        # Clear cache
        embeddings.clear_cache()

        assert embeddings.cache_info["size"] == 0

    def test_dimension_property(self, embeddings) -> None:
        """Test dimension property."""
        assert embeddings.dimension == 768

    def test_different_texts_different_embeddings(self, embeddings) -> None:
        """Test that different texts produce different embeddings."""
        text1 = "The quick brown fox"
        text2 = "Machine learning is interesting"

        embedding1 = embeddings.encode(text1)
        embedding2 = embeddings.encode(text2)

        # Should be different
        assert not np.allclose(embedding1, embedding2)

    def test_similar_texts_similar_embeddings(self, embeddings) -> None:
        """Test that similar texts produce similar embeddings."""
        text1 = "The cat sat on the mat"
        text2 = "The cat was sitting on the mat"
        text3 = "Quantum physics is complex"

        embedding1 = embeddings.encode(text1)
        embedding2 = embeddings.encode(text2)
        embedding3 = embeddings.encode(text3)

        # Similarity using cosine (dot product since normalized)
        sim_1_2 = np.dot(embedding1, embedding2)
        sim_1_3 = np.dot(embedding1, embedding3)

        # Similar texts should have higher similarity
        assert sim_1_2 > sim_1_3
