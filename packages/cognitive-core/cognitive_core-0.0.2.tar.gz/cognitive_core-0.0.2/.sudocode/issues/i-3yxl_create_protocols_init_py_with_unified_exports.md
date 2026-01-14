---
id: i-3yxl
title: Create protocols __init__.py with unified exports
priority: 2
created_at: '2025-12-18 03:33:25'
tags:
  - phase-1
  - protocols
status: open
---
Create the protocols package entry point that exports all protocols from a single location.

## File to Create
- `atlas/protocols/__init__.py`

## Implementation
```python
from atlas.protocols.llm import LLM
from atlas.protocols.embeddings import EmbeddingProvider
from atlas.protocols.vector_index import VectorIndex
from atlas.protocols.memory import (
    ExperienceMemory,
    ConceptLibrary,
    StrategyBank,
)
from atlas.protocols.search import SearchEngine, Verifier, TaskRouter
from atlas.protocols.learning import TrajectoryAnalyzer, AbstractionExtractor, HindsightLearner
from atlas.protocols.environment import Environment
from atlas.protocols.agent import Agent

__all__ = [
    # Infrastructure
    "LLM",
    "EmbeddingProvider",
    "VectorIndex",
    # Memory (Pillar 1)
    "ExperienceMemory",
    "ConceptLibrary",
    "StrategyBank",
    # Search (Pillar 2)
    "SearchEngine",
    "Verifier",
    "TaskRouter",
    # Learning (Pillar 3)
    "TrajectoryAnalyzer",
    "AbstractionExtractor",
    "HindsightLearner",
    # Core
    "Environment",
    "Agent",
]
```

## Purpose
- Single import point: `from atlas.protocols import LLM, ExperienceMemory, ...`
- Makes it easy for implementations to import interfaces
- Documents what protocols exist in the system

## Acceptance Criteria
- [ ] All protocols importable from `atlas.protocols`
- [ ] `__all__` correctly defined
- [ ] No circular import issues

Implements [[s-8fnx]]
