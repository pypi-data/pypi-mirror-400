---
id: i-8h2g
title: Implement VectorStore protocol and ChromaDB adapter
priority: 0
created_at: '2026-01-08 00:03:05'
tags:
  - infrastructure
  - memory
  - phase-3
  - storage
relationships:
  - from_id: i-8h2g
    from_uuid: 0bece71d-baed-44b4-9447-a7cf33303109
    from_type: issue
    to_id: s-7h2g
    to_uuid: d4747f7d-ae45-4696-ac9e-f5c75d4c05e8
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 00:14:44'
    metadata: null
status: closed
closed_at: '2026-01-08 00:14:47'
---
## Overview

Create the storage abstraction layer for Phase 3 memory implementations.

## Scope

### VectorStore Protocol (`src/atlas/memory/storage.py`)

Define the abstract interface for vector storage operations:

```python
@runtime_checkable
class VectorStore(Protocol):
    """Abstract vector storage - allows swapping ChromaDB for other backends."""
    async def add(self, ids: list[str], embeddings: list[list[float]],
                  metadatas: list[dict], documents: list[str]) -> None: ...
    async def query(self, embedding: list[float], k: int,
                    where: dict | None = None) -> QueryResult: ...
    async def delete(self, ids: list[str]) -> None: ...
    async def get(self, ids: list[str]) -> list[dict]: ...
    async def count(self) -> int: ...
```

### ChromaDB Adapter

Implement `ChromaVectorStore` that wraps ChromaDB collection:
- Initialize with collection name and persist directory
- Handle async wrapping of sync ChromaDB operations
- Support metadata filtering in queries
- Return `QueryResult` dataclass with ids, distances, metadatas, documents

### QueryResult Dataclass

```python
@dataclass
class QueryResult:
    ids: list[str]
    distances: list[float]
    metadatas: list[dict]
    documents: list[str]
```

## Testing

- Unit tests with mock ChromaDB
- Integration test with ephemeral ChromaDB collection

## Dependencies

- Phase 2 infrastructure (embeddings)
- chromadb package

## Acceptance Criteria

- [ ] VectorStore protocol defined
- [ ] ChromaVectorStore implements protocol
- [ ] QueryResult dataclass defined
- [ ] Unit tests pass
- [ ] Integration test with real ChromaDB passes
