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
status: open
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
