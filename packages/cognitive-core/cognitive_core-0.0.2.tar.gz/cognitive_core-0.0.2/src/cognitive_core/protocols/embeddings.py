"""Embedding provider protocol for ATLAS.

Provides text embeddings for semantic similarity search.
Default model: BAAI/bge-base-en-v1.5 (validated in ReMem paper).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Provider for text embeddings.

    Used by memory systems for semantic similarity search.
    The default model (BAAI/bge-base-en-v1.5) was validated in the ReMem paper.

    Example:
        ```python
        embedder = DefaultEmbeddingProvider()
        vec = embedder.encode("Find similar tasks")
        batch = embedder.encode_batch(["task 1", "task 2"])
        ```
    """

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text to a vector.

        Args:
            text: Text to encode

        Returns:
            1-dimensional embedding vector
        """
        ...

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts efficiently.

        Args:
            texts: List of texts to encode

        Returns:
            2-dimensional array of shape (n_texts, dimension)
        """
        ...

    @property
    def dimension(self) -> int:
        """Embedding dimension.

        Returns:
            Size of embedding vectors
        """
        ...

    @property
    def model_name(self) -> str:
        """Model name/identifier.

        Returns:
            Name of the embedding model
        """
        ...
