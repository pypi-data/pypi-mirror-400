"""BGE embeddings implementation.

Uses BAAI/bge-base-en-v1.5, validated in the ReMem paper for experience retrieval.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

from cognitive_core.config import EmbeddingConfig

logger = logging.getLogger("cognitive_core.embedding")


class BGEEmbeddings:
    """BAAI/bge-base-en-v1.5 embeddings with in-memory caching.

    Implements the EmbeddingProvider protocol with lazy model loading
    and optional caching for repeated queries.

    Example:
        ```python
        embeddings = BGEEmbeddings()
        vec = embeddings.encode("Find similar tasks")
        batch = embeddings.encode_batch(["task 1", "task 2"])
        ```
    """

    # BGE base model dimension
    _DIMENSION = 768

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize BGE embeddings.

        Args:
            config: Embedding configuration. Uses defaults if not provided.
        """
        self._config = config or EmbeddingConfig()
        self._model: SentenceTransformer | None = None
        self._tokenizer = None  # For compatibility with tests
        self._cache: dict[str, np.ndarray] = {}
        self._cache_hits = 0

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model.

        Returns:
            The loaded SentenceTransformer model.

        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required for BGE embeddings. "
                    "Install with: pip install sentence-transformers"
                ) from e

            logger.info(
                "Loading embedding model",
                extra={
                    "model": self._config.model_name,
                    "device": self._config.device,
                },
            )
            self._model = SentenceTransformer(
                self._config.model_name,
                device=self._config.device,
            )
            logger.info("Embedding model loaded")

        return self._model

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text to a vector.

        Uses cache if enabled and text was previously encoded.

        Args:
            text: Text to encode.

        Returns:
            1-dimensional embedding vector of shape (768,).
        """
        # Check cache first
        if self._config.cache_enabled and text in self._cache:
            logger.debug("Cache hit for embedding")
            self._cache_hits += 1
            return self._cache[text]

        # Encode
        embedding = self._get_model().encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        # Ensure it's the right type
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)

        # Cache if enabled
        if self._config.cache_enabled:
            self._cache[text] = embedding

        return embedding

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts efficiently.

        For texts already in cache, uses cached values.
        Only encodes uncached texts in a batch.

        Args:
            texts: List of texts to encode.

        Returns:
            2-dimensional array of shape (n_texts, 768).
        """
        if not texts:
            return np.array([]).reshape(0, self._DIMENSION)

        results: list[np.ndarray] = []
        uncached_texts: list[str] = []
        uncached_indices: list[int] = []

        # Separate cached and uncached
        for i, text in enumerate(texts):
            if self._config.cache_enabled and text in self._cache:
                results.append(self._cache[text])
            else:
                results.append(None)  # type: ignore
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Batch encode uncached texts
        if uncached_texts:
            embeddings = self._get_model().encode(
                uncached_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=len(uncached_texts) > 10,
            )

            # Ensure it's the right type
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)

            # Fill in results and update cache
            for idx, text, embedding in zip(
                uncached_indices, uncached_texts, embeddings
            ):
                results[idx] = embedding
                if self._config.cache_enabled:
                    self._cache[text] = embedding

        return np.stack(results)

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        self._cache_hits = 0
        logger.debug("Cleared embedding cache", extra={"size": cache_size})

    @property
    def cache_info(self) -> dict[str, int]:
        """Cache statistics.

        Returns:
            Dict with 'size' (current entries) and 'hits' (total cache hits).
        """
        return {
            "size": len(self._cache),
            "hits": getattr(self, "_cache_hits", 0),
        }

    @property
    def dimension(self) -> int:
        """Embedding dimension (768 for BGE base)."""
        return self._DIMENSION

    @property
    def model_name(self) -> str:
        """Model name/identifier."""
        return self._config.model_name
