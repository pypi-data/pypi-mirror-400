---
id: s-8fnx
title: Python Package Structure
priority: 0
created_at: '2025-12-07 08:36:25'
parent_id: s-5o87
tags:
  - dependencies
  - implementation
  - package-structure
  - python
relationships:
  - from_id: s-8fnx
    from_uuid: 7b5a1dd5-414a-4a57-902a-dee0988267f2
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:41:51'
    metadata: null
---
# Python Package Structure

Parent: [[s-5o87|ATLAS System Architecture]]

## Design Philosophy

1. **Interfaces first**: Define ABCs and Protocols before implementations
2. **Leverage existing code**: Wrap proven libraries rather than reimplement
3. **Thin wrappers**: Our code is glue, not the engine
4. **Dependency injection**: All heavy deps are optional and injectable

## Existing Codebases to Leverage

| Component | Existing Library | What We Build |
|-----------|-----------------|---------------|
| **Embeddings** | `sentence-transformers` | Thin wrapper protocol |
| **Vector Store** | `chromadb`, `faiss` | Protocol + adapter |
| **Stitch Compression** | `stitch` (Rust via PyO3) | Python bindings wrapper |
| **LILO AutoDoc** | `lilo` (Python) | Import directly or fork |
| **Mind Evolution** | `lucidrains/mind-evolution` | Adapter to our interfaces |
| **LLM Calls** | `litellm`, `anthropic`, `openai` | Protocol wrapper |
| **ARC Environment** | `arckit`, `arc-dsl` | Adapter |
| **SWE Environment** | `swe-gym`, `docker` | Adapter |

## What We Actually Build

### Must Build (Core Interfaces)
```
atlas/
├── core/              # ~200 lines - dataclasses only
├── protocols/         # ~150 lines - ABCs and Protocols
└── memory/system.py   # ~100 lines - aggregator
```

### Thin Wrappers (~50-100 lines each)
```
atlas/
├── memory/
│   ├── adapters/
│   │   ├── chroma.py      # ChromaDB adapter
│   │   └── faiss.py       # FAISS adapter
├── integration/
│   ├── stitch.py          # Stitch wrapper
│   ├── lilo.py            # LILO wrapper
│   ├── mind_evolution.py  # Mind Evolution adapter
│   └── llm.py             # LiteLLM wrapper
```

### Light Implementation (~200-300 lines each)
```
atlas/
├── memory/
│   ├── experience.py      # ExperienceMemory (ReMem-style)
│   ├── concepts.py        # ConceptLibrary
│   └── strategies.py      # StrategyBank
├── search/
│   ├── router.py          # Task routing logic
│   └── verifier.py        # Verification logic
├── learning/
│   └── pipeline.py        # Orchestration
```

## Package Structure

```
atlas/
├── __init__.py
├── py.typed                    # PEP 561 marker
│
├── core/                       # Core data structures
│   ├── __init__.py
│   ├── types.py               # Trajectory, Task, Step, Outcome (~150 lines)
│   └── serialization.py       # JSON/pickle helpers (~50 lines)
│
├── protocols/                  # Abstract interfaces
│   ├── __init__.py
│   ├── memory.py              # Memory protocols (~100 lines)
│   ├── search.py              # Search protocols (~80 lines)
│   ├── learning.py            # Learning protocols (~60 lines)
│   ├── environment.py         # Environment protocol (~40 lines)
│   └── llm.py                 # LLM protocol (~30 lines)
│
├── memory/                     # Pillar 1 implementations
│   ├── __init__.py
│   ├── system.py              # MemorySystem aggregator (~100 lines)
│   ├── experience.py          # ExperienceMemory (~250 lines)
│   ├── concepts.py            # ConceptLibrary (~200 lines)
│   ├── strategies.py          # StrategyBank (~150 lines)
│   ├── embeddings.py          # Embedding providers (~80 lines)
│   └── adapters/
│       ├── __init__.py
│       ├── chroma.py          # ChromaDB VectorIndex (~60 lines)
│       ├── faiss.py           # FAISS VectorIndex (~60 lines)
│       └── memory_index.py    # In-memory fallback (~40 lines)
│
├── search/                     # Pillar 2 implementations
│   ├── __init__.py
│   ├── router.py              # TaskRouter (~150 lines)
│   ├── direct.py              # DirectSolver (~80 lines)
│   ├── verifier.py            # Verifier base + impls (~120 lines)
│   └── adapters/
│       ├── __init__.py
│       └── mind_evolution.py  # Wrap lucidrains lib (~100 lines)
│
├── learning/                   # Pillar 3 implementations
│   ├── __init__.py
│   ├── analyzer.py            # TrajectoryAnalyzer (~150 lines)
│   ├── pipeline.py            # LearningPipeline (~200 lines)
│   └── adapters/
│       ├── __init__.py
│       ├── stitch.py          # Stitch compression (~80 lines)
│       └── lilo.py            # LILO AutoDoc (~60 lines)
│
├── environments/               # Environment adapters
│   ├── __init__.py
│   ├── base.py                # Base classes (~50 lines)
│   └── adapters/
│       ├── __init__.py
│       ├── arc.py             # ARC environment (~100 lines)
│       └── swe.py             # SWE environment (~150 lines)
│
├── llm/                        # LLM integration
│   ├── __init__.py
│   ├── base.py                # LLM protocol (~40 lines)
│   └── adapters/
│       ├── __init__.py
│       ├── litellm.py         # LiteLLM adapter (~50 lines)
│       ├── anthropic.py       # Direct Anthropic (~50 lines)
│       └── openai.py          # Direct OpenAI (~50 lines)
│
├── solver.py                   # ATLASSolver orchestrator (~150 lines)
│
└── experiments/                # Ablation support
    ├── __init__.py
    ├── configs.py             # Ablation configs (~100 lines)
    └── runner.py              # Experiment runner (~150 lines)
```

## Estimated Line Counts

| Category | Lines | Notes |
|----------|-------|-------|
| Core + Protocols | ~500 | Interfaces only |
| Memory | ~900 | Includes adapters |
| Search | ~450 | Mostly routing logic |
| Learning | ~500 | Light orchestration |
| Environments | ~300 | Thin adapters |
| LLM | ~200 | Thin wrappers |
| Experiments | ~250 | Ablation support |
| **Total** | **~3,100** | Excluding tests |

## Dependencies

### Required (Core)
```toml
[project]
dependencies = [
    "numpy>=1.24",
    "pydantic>=2.0",        # Serialization
]
```

### Optional (Feature Groups)
```toml
[project.optional-dependencies]
embeddings = [
    "sentence-transformers>=2.2",
]
vector-stores = [
    "chromadb>=0.4",
    # or: "faiss-cpu>=1.7",
]
llm = [
    "litellm>=1.0",
    # or specific: "anthropic>=0.18", "openai>=1.0"
]
compression = [
    "stitch-core>=0.1",     # If available
]
arc = [
    "arckit>=0.1",          # ARC utilities
]
swe = [
    "docker>=6.0",
]
all = [
    "atlas[embeddings,vector-stores,llm,arc,swe]",
]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "ruff>=0.1",
    "mypy>=1.0",
]
```

## Implementation Priority

### Phase 1: Interfaces (Day 1-2)
```
atlas/
├── core/types.py          # Data structures
├── protocols/             # All protocols
└── py.typed
```

### Phase 2: Memory (Day 3-5)
```
atlas/memory/
├── system.py              # Aggregator
├── experience.py          # With in-memory index
├── embeddings.py          # Default provider
└── adapters/memory_index.py
```

### Phase 3: Minimal Solver (Day 6-7)
```
atlas/
├── search/router.py       # Basic routing
├── search/direct.py       # Direct solver
├── solver.py              # Orchestrator
└── llm/adapters/litellm.py
```

### Phase 4: Learning (Day 8-10)
```
atlas/learning/
├── analyzer.py
└── pipeline.py
```

### Phase 5: Advanced (Week 2+)
- Mind Evolution adapter
- Stitch/LILO integration
- SWE environment
- Full search methods

## Key Interfaces to Define First

### 1. LLM Protocol (everything depends on this)
```python
class LLM(Protocol):
    def generate(self, prompt: str, **kwargs) -> str: ...
    async def agenerate(self, prompt: str, **kwargs) -> str: ...
```

### 2. EmbeddingProvider Protocol
```python
class EmbeddingProvider(Protocol):
    def encode(self, text: str) -> np.ndarray: ...
    def encode_batch(self, texts: List[str]) -> np.ndarray: ...
```

### 3. VectorIndex Protocol
```python
class VectorIndex(Protocol):
    def add(self, id: str, vector: np.ndarray, metadata: Dict) -> None: ...
    def search(self, vector: np.ndarray, k: int) -> List[Tuple[str, float]]: ...
    def delete(self, id: str) -> bool: ...
```

### 4. Memory Protocols
```python
class ExperienceMemory(Protocol):
    def store(self, trajectory: Trajectory) -> str: ...
    def search(self, task: Task, k: int) -> List[Experience]: ...

class ConceptLibrary(Protocol):
    def add(self, concept: CodeConcept) -> str: ...
    def search(self, query: str, k: int) -> List[CodeConcept]: ...

class StrategyBank(Protocol):
    def write(self, trajectory: Trajectory) -> Optional[Strategy]: ...
    def read(self, task: Task, k: int) -> List[Strategy]: ...
```

## Testing Strategy

```
tests/
├── unit/
│   ├── test_types.py          # Core data structures
│   ├── test_memory.py         # Memory components
│   └── test_search.py         # Search components
├── integration/
│   ├── test_solver.py         # End-to-end
│   └── test_ablation.py       # Ablation configs
└── fixtures/
    ├── trajectories.py        # Sample trajectories
    └── tasks.py               # Sample tasks
```

## File to Create First

`atlas/protocols/__init__.py` - Export all protocols so implementations can import from one place:

```python
from atlas.protocols.llm import LLM
from atlas.protocols.memory import (
    EmbeddingProvider,
    VectorIndex,
    ExperienceMemory,
    ConceptLibrary,
    StrategyBank,
)
from atlas.protocols.search import SearchEngine, Verifier, TaskRouter
from atlas.protocols.learning import TrajectoryAnalyzer, AbstractionExtractor
from atlas.protocols.environment import Environment

__all__ = [
    "LLM",
    "EmbeddingProvider",
    "VectorIndex",
    "ExperienceMemory",
    "ConceptLibrary",
    "StrategyBank",
    "SearchEngine",
    "Verifier",
    "TaskRouter",
    "TrajectoryAnalyzer",
    "AbstractionExtractor",
    "Environment",
]
```
