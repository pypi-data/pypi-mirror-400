---
id: i-81oi
title: Implement ChromaDB Vector Index
priority: 1
created_at: '2026-01-07 08:55:54'
tags:
  - chromadb
  - infrastructure
  - phase-2
  - vector
relationships:
  - from_id: i-81oi
    from_uuid: c7f3ee79-bc4f-48db-a14e-38355ea71993
    from_type: issue
    to_id: i-4ow1
    to_uuid: 44c8882e-cf2f-4657-b22d-14769206f127
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 09:31:16'
    metadata: null
  - from_id: i-81oi
    from_uuid: c7f3ee79-bc4f-48db-a14e-38355ea71993
    from_type: issue
    to_id: s-7xs8
    to_uuid: 12efd4e8-865b-4b65-91e0-fad14c400a33
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-07 09:31:16'
    metadata: null
status: closed
closed_at: '2026-01-07 09:33:06'
---
# Implement ChromaDB Vector Index

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Implement the `VectorIndex` protocol using ChromaDB with project-local storage.

## Files to Create

- `src/atlas/vector/__init__.py`
- `src/atlas/vector/chroma.py`

## Dependencies

- `chromadb` package
- ATLASConfig (for StorageConfig)

## Implementation

```python
class ChromaIndex:
    """ChromaDB-backed vector index."""
    
    def __init__(
        self,
        collection_name: str,
        config: StorageConfig = None,
    ):
        self._config = config or StorageConfig()
        self._collection_name = self._prefixed_name(collection_name)
        self._client = None
        self._collection = None
    
    def _prefixed_name(self, name: str) -> str:
        prefix = self._config.chroma_collection_prefix
        return f"{prefix}{name}" if prefix else name
    
    def _get_client(self):
        if self._client is None:
            import chromadb
            persist_dir = self._config.base_path / "chroma"
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
        return self._client
    
    def _get_collection(self):
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": self._config.distance_metric},
            )
        return self._collection
    
    def add(self, id: str, vector: np.ndarray, metadata: dict = None) -> None:
        ...
    
    def add_batch(self, ids: list[str], vectors: np.ndarray, metadatas: list[dict] = None) -> None:
        ...
    
    def search(self, vector: np.ndarray, k: int = 5, filter: dict = None) -> list[tuple[str, float, dict]]:
        ...
    
    def get(self, id: str) -> tuple[np.ndarray, dict] | None:
        ...
    
    def delete(self, id: str) -> bool:
        ...
    
    def __len__(self) -> int:
        ...
    
    def clear(self) -> None:
        ...
```

## Storage Location

- Base path: `.atlas/` (project-local)
- Chroma data: `.atlas/chroma/`
- Collections: `experiences`, `concepts`, `strategies`

## Acceptance Criteria

- [ ] Implements `VectorIndex` protocol
- [ ] Lazy client/collection initialization
- [ ] Persists to `.atlas/chroma/`
- [ ] Collection prefix works
- [ ] Cosine similarity by default
- [ ] All CRUD operations work
- [ ] Integration tests with real ChromaDB
