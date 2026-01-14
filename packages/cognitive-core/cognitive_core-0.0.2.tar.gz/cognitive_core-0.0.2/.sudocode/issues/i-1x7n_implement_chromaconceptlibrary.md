---
id: i-1x7n
title: Implement ChromaConceptLibrary
priority: 1
created_at: '2026-01-08 00:04:01'
tags:
  - concepts
  - implementation
  - memory
  - phase-3
status: open
---
## Overview

Implement ConceptLibrary backed by ChromaDB with Stitch/LILO-style compression support.

Implements protocol: [[s-3c37|Memory Systems (Pillar 1)]]

## Scope

### File: `src/atlas/memory/concepts.py`

```python
class ChromaConceptLibrary:
    """ConceptLibrary implementation backed by ChromaDB."""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        primitive_loader: PrimitiveLoader | None = None,
        composition_strategy: CompositionStrategy | None = None,
        compression_strategy: CompressionStrategy | None = None,
        collection_name: str = "atlas_concepts",
    ): ...
```

### Methods to Implement

**add(concept: CodeConcept) -> str**
- Generate UUID if not provided
- Embed name + description concatenated
- Store in vector store with metadata
- Return concept_id

**search(query: str, k: int = 5) -> list[CodeConcept]**
- Embed query string
- Query vector store for top-k similar
- Reconstruct CodeConcept objects
- Include primitives in search results

**get(concept_id: str) -> CodeConcept | None**
- Check primitives first, then learned
- Return None if not found

**compose(concept_ids: list[str]) -> CodeConcept | None**
- Get concepts by IDs
- Delegate to composition_strategy
- Return None if strategy is None or composition fails

**compress(trajectories: list[Trajectory]) -> list[CodeConcept]**
- Filter to successful trajectories only
- Delegate to compression_strategy
- Return empty list if strategy is None
- Add extracted concepts to library

**update_stats(concept_id: str, success: bool) -> None**
- Update usage_count and success_rate in metadata
- Use simple average for success rate

**__len__() -> int**
- Return primitives count + learned count

### Primitive Loading

- Load primitives at init if loader provided
- Store primitives separately (not in vector store)
- Include primitives in search results

## CodeConcept Model

Ensure CodeConcept in `atlas.core.types` has:
- id: str
- name: str
- description: str
- code: str
- signature: str | None
- examples: list[tuple[str, str]]
- usage_count: int
- success_rate: float
- concept_type: Literal["primitive", "learned", "composed"]

## Testing

- Unit tests with mock VectorStore
- Test add/search/get flow
- Test primitive loading
- Test composition delegation
- Test compression delegation
- Test stats update

## Dependencies

- [[i-8h2g]] VectorStore protocol
- [[i-6orq]] Strategy protocols
- Phase 2 embeddings

## Acceptance Criteria

- [ ] Implements ConceptLibrary protocol
- [ ] Primitive loading works
- [ ] Name + description embedding
- [ ] Composition delegates to strategy
- [ ] Compression delegates to strategy
- [ ] Usage stats tracking works
- [ ] All unit tests pass
