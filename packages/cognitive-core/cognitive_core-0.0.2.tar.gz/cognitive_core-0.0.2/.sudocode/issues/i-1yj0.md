---
id: i-1yj0
title: Implement ChromaExperienceMemory
priority: 1
created_at: '2026-01-08 00:03:48'
tags:
  - experience
  - implementation
  - memory
  - phase-3
relationships:
  - from_id: i-1yj0
    from_uuid: 45510e4b-c807-443d-bbe9-6df623e37c00
    from_type: issue
    to_id: i-6orq
    to_uuid: ca2b87dd-6588-4be7-b06f-6c139f6e4ea2
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:18:03'
    metadata: null
  - from_id: i-1yj0
    from_uuid: 45510e4b-c807-443d-bbe9-6df623e37c00
    from_type: issue
    to_id: i-8h2g
    to_uuid: 0bece71d-baed-44b4-9447-a7cf33303109
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:18:03'
    metadata: null
  - from_id: i-1yj0
    from_uuid: 45510e4b-c807-443d-bbe9-6df623e37c00
    from_type: issue
    to_id: s-7h2g
    to_uuid: d4747f7d-ae45-4696-ac9e-f5c75d4c05e8
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 00:18:03'
    metadata: null
status: closed
closed_at: '2026-01-08 00:21:30'
---
## Overview

Implement ExperienceMemory backed by ChromaDB with ReMem-style retrieval.

Implements protocol: [[s-3c37|Memory Systems (Pillar 1)]]

## Scope

### File: `src/atlas/memory/experience.py`

```python
class ChromaExperienceMemory:
    """ExperienceMemory implementation backed by ChromaDB."""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        extractor: ExperienceExtractor = SimpleExperienceExtractor(),
        refine_strategy: RefineStrategy = PassthroughRefineStrategy(),
        collection_name: str = "atlas_experiences",
    ): ...
```

### Methods to Implement

**store(trajectory: Trajectory) -> str**
- Generate UUID for experience_id
- Extract embedding text via extractor strategy
- Create Experience from trajectory
- Embed and store in vector store
- Store success/failure status in metadata
- Return experience_id

**search(task: Task, k: int = 4) -> list[Experience]**
- Embed task description
- Query vector store for top-k similar
- Reconstruct Experience objects from results
- Prioritize successful experiences in ranking
- Default k=4 from ReMem paper

**get(experience_id: str) -> Experience | None**
- Retrieve by ID from vector store
- Return None if not found

**refine(experiences: list[Experience]) -> list[Experience]**
- Delegate to refine_strategy
- Pass through context if available

**prune(criteria: dict[str, Any]) -> int**
- Support criteria: min_success_rate, max_age_days, keep_diverse
- Delete matching experiences from vector store
- Return count removed

**__len__() -> int**
- Return count from vector store

## Experience Model

Ensure Experience type in `atlas.core.types` has:
- id: str (UUID)
- task: Task
- trajectory_summary: str
- outcome: Outcome  
- embedding_text: str
- created_at: datetime
- metadata: dict

## Testing

- Unit tests with mock VectorStore and strategies
- Test store/search/get flow
- Test prune with various criteria
- Test with different extractor strategies

## Dependencies

- [[i-8h2g]] VectorStore protocol
- [[i-6orq]] Strategy protocols
- Phase 2 embeddings

## Acceptance Criteria

- [ ] Implements ExperienceMemory protocol from `atlas.protocols.memory`
- [ ] UUID generation for experience IDs
- [ ] Configurable extractor strategy works
- [ ] Configurable refine strategy works
- [ ] Success/failure stored in metadata
- [ ] Prune operation works with criteria
- [ ] All unit tests pass
