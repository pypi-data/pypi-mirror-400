---
id: i-6orq
title: Define memory strategy protocols
priority: 0
created_at: '2026-01-08 00:03:31'
tags:
  - memory
  - phase-3
  - protocols
  - strategies
status: open
---
## Overview

Define all pluggable strategy protocols for Phase 3 memory components. These enable experimentation with different approaches.

## Scope

### File: `src/atlas/memory/strategies/__init__.py`

Export all strategy protocols.

### File: `src/atlas/memory/strategies/experience.py`

```python
@runtime_checkable
class ExperienceExtractor(Protocol):
    """Extracts searchable content from trajectory for embedding."""
    def extract(self, trajectory: Trajectory) -> str: ...

@runtime_checkable  
class RefineStrategy(Protocol):
    """ReMem-style refinement: exploit useful, prune noise, reorganize."""
    async def refine(self, experiences: list[Experience],
                     context: Task | None = None) -> list[Experience]: ...
```

### File: `src/atlas/memory/strategies/concepts.py`

```python
@runtime_checkable
class CompositionStrategy(Protocol):
    """Combines multiple concepts into a new composed concept."""
    async def compose(self, concepts: list[CodeConcept]) -> CodeConcept | None: ...

@runtime_checkable
class CompressionStrategy(Protocol):
    """Extracts new concepts from trajectories (Stitch/LILO-style)."""
    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]: ...

@runtime_checkable
class ConceptDocumenter(Protocol):
    """Generates documentation for concepts (LILO AutoDoc)."""
    async def document(self, concept: CodeConcept,
                       usage_examples: list[tuple[str, str]]) -> CodeConcept: ...

@runtime_checkable
class PrimitiveLoader(Protocol):
    """Loads domain-specific primitive concepts."""
    def load(self) -> dict[str, CodeConcept]: ...
```

### File: `src/atlas/memory/strategies/strategy_bank.py`

```python
@runtime_checkable
class StrategyAbstractor(Protocol):
    """Abstracts a trajectory into a reusable strategy."""
    async def abstract(self, trajectory: Trajectory) -> Strategy | None: ...

@runtime_checkable
class SuccessRateUpdater(Protocol):
    """Updates success rate statistics."""
    def update(self, current_rate: float, current_count: int,
               success: bool) -> tuple[float, int]: ...
```

## Default Implementations

Include simple/passthrough defaults for each:
- `SimpleExperienceExtractor` - returns task.description
- `PassthroughRefineStrategy` - returns experiences unchanged
- `EMASuccessUpdater` - exponential moving average
- `SimpleAverageUpdater` - running average

## Testing

- Protocol compliance tests
- Default implementation unit tests

## Acceptance Criteria

- [ ] All protocols defined with proper typing
- [ ] Default implementations for baselines
- [ ] Protocols are runtime_checkable
- [ ] Unit tests for default implementations
