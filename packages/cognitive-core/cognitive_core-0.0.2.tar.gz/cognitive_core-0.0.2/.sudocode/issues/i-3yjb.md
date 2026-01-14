---
id: i-3yjb
title: Implement ChromaStrategyBank
priority: 1
created_at: '2026-01-08 00:04:16'
tags:
  - implementation
  - memory
  - phase-3
  - strategies
relationships:
  - from_id: i-3yjb
    from_uuid: 56fc5ab1-016f-4a18-a6c6-bbf58c1f98f9
    from_type: issue
    to_id: i-8h2g
    to_uuid: 0bece71d-baed-44b4-9447-a7cf33303109
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-08 00:22:05'
    metadata: null
  - from_id: i-3yjb
    from_uuid: 56fc5ab1-016f-4a18-a6c6-bbf58c1f98f9
    from_type: issue
    to_id: s-7h2g
    to_uuid: d4747f7d-ae45-4696-ac9e-f5c75d4c05e8
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 00:22:05'
    metadata: null
status: closed
closed_at: '2026-01-08 00:22:08'
---
## Overview

Implement StrategyBank backed by ChromaDB with ArcMemo-style abstract strategy storage.

Implements protocol: [[s-3c37|Memory Systems (Pillar 1)]]

## Scope

### File: `src/atlas/memory/strategies_impl.py`

(Note: Named differently from strategies/ directory to avoid confusion)

```python
class ChromaStrategyBank:
    """StrategyBank implementation backed by ChromaDB."""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        abstractor: StrategyAbstractor,
        success_updater: SuccessRateUpdater = EMASuccessUpdater(),
        collection_name: str = "atlas_strategies",
    ): ...
```

### Methods to Implement

**write(trajectory: Trajectory) -> Strategy | None**
- Check trajectory.outcome.success - return None if failed
- Delegate to abstractor strategy
- If abstractor returns None, return None
- Generate UUID for strategy
- Embed situation field
- Store in vector store
- Return strategy

**read(task: Task, k: int = 5) -> list[Strategy]**
- Embed task description
- Query vector store for top-k similar
- Reconstruct Strategy objects
- Sort by relevance (distance) and success_rate

**get(strategy_id: str) -> Strategy | None**
- Retrieve by ID from vector store
- Return None if not found

**update_stats(strategy_id: str, success: bool) -> None**
- Get current stats from metadata
- Delegate to success_updater strategy
- Update metadata in vector store

**__len__() -> int**
- Return count from vector store

## Strategy Model

Ensure Strategy in `atlas.core.types` has:
- id: str
- situation: str (when to apply - used for embedding)
- approach: str (high-level steps)
- rationale: str (why this works)
- source_task_id: str | None
- usage_count: int
- success_rate: float
- created_at: datetime

## Success Rate Updaters

Implement in strategies/strategy_bank.py:

```python
class EMASuccessUpdater(SuccessRateUpdater):
    def __init__(self, alpha: float = 0.1): ...
    def update(self, current_rate, current_count, success) -> tuple[float, int]: ...

class SimpleAverageUpdater(SuccessRateUpdater):
    def update(self, current_rate, current_count, success) -> tuple[float, int]: ...
```

## Testing

- Unit tests with mock VectorStore and abstractor
- Test write only processes successful trajectories
- Test read returns sorted by relevance
- Test update_stats with different updaters
- Test EMA vs Simple average updaters

## Dependencies

- [[i-8h2g]] VectorStore protocol
- [[i-6orq]] Strategy protocols
- Phase 2 embeddings

## Acceptance Criteria

- [ ] Implements StrategyBank protocol
- [ ] Only abstracts successful trajectories
- [ ] Situation field used for embedding
- [ ] Success rate update is configurable
- [ ] EMA and Simple updaters work correctly
- [ ] All unit tests pass
