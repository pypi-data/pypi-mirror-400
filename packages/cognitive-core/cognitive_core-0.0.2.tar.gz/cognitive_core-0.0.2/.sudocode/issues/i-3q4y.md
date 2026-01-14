---
id: i-3q4y
title: Implement BGE Embeddings with in-memory cache
priority: 1
created_at: '2026-01-07 08:55:54'
tags:
  - embeddings
  - infrastructure
  - phase-2
relationships:
  - from_id: i-3q4y
    from_uuid: 34f6a518-65db-4058-bf12-c0af57bd7a45
    from_type: issue
    to_id: i-4ow1
    to_uuid: 44c8882e-cf2f-4657-b22d-14769206f127
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 09:31:16'
    metadata: null
  - from_id: i-3q4y
    from_uuid: 34f6a518-65db-4058-bf12-c0af57bd7a45
    from_type: issue
    to_id: s-7xs8
    to_uuid: 12efd4e8-865b-4b65-91e0-fad14c400a33
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-07 09:31:16'
    metadata: null
status: closed
closed_at: '2026-01-07 09:33:05'
---
# Implement BGE Embeddings with in-memory cache

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Implement the `EmbeddingProvider` protocol using BAAI/bge-base-en-v1.5 with in-memory caching.

## Files to Create

- `src/atlas/embeddings/__init__.py`
- `src/atlas/embeddings/bge.py`

## Dependencies

- `sentence-transformers` package
- ATLASConfig (for EmbeddingConfig)

## Implementation

```python
class BGEEmbeddings:
    """BAAI/bge-base-en-v1.5 embeddings with caching."""
    
    def __init__(self, config: EmbeddingConfig = None):
        self._config = config or EmbeddingConfig()
        self._model = None  # Lazy loading
        self._cache: dict[str, np.ndarray] = {}
    
    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self._config.model_name,
                device=self._config.device,
            )
        return self._model
    
    def encode(self, text: str) -> np.ndarray:
        if self._config.cache_enabled and text in self._cache:
            return self._cache[text]
        embedding = self._get_model().encode(text, normalize_embeddings=True)
        if self._config.cache_enabled:
            self._cache[text] = embedding
        return embedding
    
    def encode_batch(self, texts: list[str]) -> np.ndarray:
        # Handle cache for batch
        ...
    
    def clear_cache(self) -> None:
        self._cache.clear()
    
    @property
    def dimension(self) -> int:
        return 768
    
    @property
    def model_name(self) -> str:
        return self._config.model_name
```

## Acceptance Criteria

- [ ] Implements `EmbeddingProvider` protocol
- [ ] Lazy model loading works
- [ ] In-memory cache works (encode same text twice, second is cached)
- [ ] Batch encoding works
- [ ] Device configuration works (cpu/cuda/mps)
- [ ] Unit tests for all methods
