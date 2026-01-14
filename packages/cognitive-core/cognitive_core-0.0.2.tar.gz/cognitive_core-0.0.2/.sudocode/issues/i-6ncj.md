---
id: i-6ncj
title: Implement MemorySystemImpl aggregator
priority: 1
created_at: '2026-01-08 00:04:33'
tags:
  - aggregator
  - implementation
  - memory
  - phase-3
relationships:
  - from_id: i-6ncj
    from_uuid: a4f38671-4f6a-4874-9f80-e1570faf6ebf
    from_type: issue
    to_id: i-1x7n
    to_uuid: 9e5daa7d-8990-4695-aeca-5eb72c08ba3d
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:27:24'
    metadata: null
  - from_id: i-6ncj
    from_uuid: a4f38671-4f6a-4874-9f80-e1570faf6ebf
    from_type: issue
    to_id: i-1yj0
    to_uuid: 45510e4b-c807-443d-bbe9-6df623e37c00
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:27:24'
    metadata: null
  - from_id: i-6ncj
    from_uuid: a4f38671-4f6a-4874-9f80-e1570faf6ebf
    from_type: issue
    to_id: i-3yjb
    to_uuid: 56fc5ab1-016f-4a18-a6c6-bbf58c1f98f9
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:27:24'
    metadata: null
  - from_id: i-6ncj
    from_uuid: a4f38671-4f6a-4874-9f80-e1570faf6ebf
    from_type: issue
    to_id: s-7h2g
    to_uuid: d4747f7d-ae45-4696-ac9e-f5c75d4c05e8
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 00:27:24'
    metadata: null
status: closed
closed_at: '2026-01-08 00:27:24'
---
## Overview

Implement the MemorySystem aggregator that combines all three memory components with parallel async queries.

Implements protocol: [[s-3c37|Memory Systems (Pillar 1)]]

## Scope

### File: `src/atlas/memory/system.py`

```python
class MemorySystemImpl:
    """Aggregator for all memory types."""

    def __init__(
        self,
        experience: ExperienceMemory | None = None,
        concepts: ConceptLibrary | None = None,
        strategies: StrategyBank | None = None,
    ): ...
```

### Methods to Implement

**Properties**
- `experience_memory -> ExperienceMemory | None`
- `concept_library -> ConceptLibrary | None`
- `strategy_bank -> StrategyBank | None`

**async query(task: Task, k: int = 5) -> MemoryQueryResult**
- Query all available components in parallel using `asyncio.gather`
- Handle None components gracefully (return empty list)
- Combine results into MemoryQueryResult
- Handle exceptions per-component (don't fail all if one fails)

```python
async def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
    tasks = []
    if self._experience:
        tasks.append(self._query_experience(task, k))
    if self._concepts:
        tasks.append(self._query_concepts(task, k))
    if self._strategies:
        tasks.append(self._query_strategies(task, k))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Process results...
```

**store(trajectory: Trajectory) -> dict[str, Any]**
- ExperienceMemory: Always stores (success and failure)
- ConceptLibrary: Skip (compression is batch operation)
- StrategyBank: Only write if trajectory.outcome.success
- Return dict with IDs from each component

```python
def store(self, trajectory: Trajectory) -> dict[str, Any]:
    result = {}
    
    if self._experience:
        result["experience_id"] = self._experience.store(trajectory)
    
    if self._strategies and trajectory.outcome.success:
        strategy = self._strategies.write(trajectory)
        if strategy:
            result["strategy_id"] = strategy.id
    
    return result
```

### MemoryQueryResult

Already defined in `atlas.protocols.memory`:

```python
class MemoryQueryResult:
    experiences: list[Experience]
    concepts: list[CodeConcept]
    strategies: list[Strategy]
    
    def is_empty(self) -> bool: ...
```

## Testing

- Unit tests with mock components
- Test with all components present
- Test with some components None (ablation)
- Test parallel query execution
- Test error handling (one component fails)
- Test store with success/failure trajectories

## Dependencies

- [[i-1yj0]] ChromaExperienceMemory
- [[i-1x7n]] ChromaConceptLibrary
- [[i-3yjb]] ChromaStrategyBank

## Acceptance Criteria

- [ ] Implements MemorySystem protocol
- [ ] All components are optional
- [ ] Parallel async queries via asyncio.gather
- [ ] Graceful degradation when components missing
- [ ] Store differentiates success/failure
- [ ] Error isolation (one failure doesn't break all)
- [ ] All unit tests pass
