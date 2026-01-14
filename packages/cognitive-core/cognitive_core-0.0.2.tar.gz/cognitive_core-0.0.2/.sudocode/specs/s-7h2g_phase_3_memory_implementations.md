---
id: s-7h2g
title: 'Phase 3: Memory Implementations'
priority: 1
created_at: '2026-01-06 02:20:03'
parent_id: s-5o87
tags:
  - implementation
  - memory
  - phase-3
  - pillar-1
---
# Phase 3: Memory Implementations

Parent: [[s-5o87|ATLAS System Architecture]]
Implements: [[s-3c37|Memory Systems (Pillar 1)]]
Depends on: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Overview

Concrete implementations of the three memory protocols defined in `src/atlas/protocols/memory.py`. Each component works standalone and can be composed via MemorySystem. The implementations are designed with **flexible strategy interfaces** to enable experimentation with different approaches.

## Design Principles

1. **Strategy Pattern for Experimentation**: Complex operations (refine, compose, compress, success updates) use pluggable strategy protocols
2. **Separation of Storage and Processing**: Vector DB handles storage/retrieval; strategies handle intelligent processing
3. **Success/Failure Differentiation**: Both stored, but processed differently based on outcome
4. **Async-First**: All query operations support asyncio for parallel execution

---

## Storage Architecture

### Database Strategy

**Hybrid Approach:**
- **Vector Storage**: ChromaDB collections (separate per component)
- **Metadata Storage**: TinyDB for lightweight JSON-based metadata
- **Abstraction Layer**: `VectorStore` protocol for swapping implementations

```python
# Storage abstraction for future flexibility
class VectorStore(Protocol):
    """Abstract vector storage - allows swapping ChromaDB for other backends."""
    async def add(self, ids: list[str], embeddings: list[list[float]],
                  metadatas: list[dict], documents: list[str]) -> None: ...
    async def query(self, embedding: list[float], k: int,
                    where: dict | None = None) -> QueryResult: ...
    async def delete(self, ids: list[str]) -> None: ...
    async def get(self, ids: list[str]) -> list[dict]: ...
```

### Collections

| Component | Collection Name | Embedding Source | Metadata DB |
|-----------|----------------|------------------|-------------|
| ExperienceMemory | `atlas_experiences` | Task description | `experiences_meta.json` |
| ConceptLibrary | `atlas_concepts` | Name + description | `concepts_meta.json` |
| StrategyBank | `atlas_strategies` | Situation field | `strategies_meta.json` |

---

## Component 1: ExperienceMemory Implementation

ChromaDB-backed experience storage with ReMem-style retrieval.

### Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Experience IDs | UUIDs (`uuid4`) | Globally unique, no collision concerns |
| Embedding source | Task description (configurable) | Start simple, option for LLM summarization later |
| Similarity key | Task description only (configurable) | Can expand to include context |
| Refine operation | **Agentic** (LLM meta-reasoning) | ReMem literature: requires intelligent pruning/reorganizing |
| Store behavior | Both success/failure stored | Different processing based on outcome |

### Strategy Protocols

```python
@runtime_checkable
class ExperienceExtractor(Protocol):
    """Extracts searchable content from trajectory for embedding."""
    def extract(self, trajectory: Trajectory) -> str:
        """Return text to embed for similarity search."""
        ...

@runtime_checkable
class RefineStrategy(Protocol):
    """ReMem-style refinement: exploit useful, prune noise, reorganize."""
    async def refine(self, experiences: list[Experience],
                     context: Task | None = None) -> list[Experience]:
        """
        Meta-reasoning over retrieved experiences.

        Implementations may:
        - Merge similar experiences
        - Remove low-quality/noisy ones
        - Reorganize for better relevance
        - Filter based on task context
        """
        ...
```

### Default Implementations

```python
class SimpleExperienceExtractor(ExperienceExtractor):
    """Extract task description only (default)."""
    def extract(self, trajectory: Trajectory) -> str:
        return trajectory.task.description

class LLMSummarizingExtractor(ExperienceExtractor):
    """LLM summarizes trajectory into searchable text (future)."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract(self, trajectory: Trajectory) -> str:
        # Summarize task + key steps + outcome
        ...

class PassthroughRefineStrategy(RefineStrategy):
    """No-op refinement (baseline for ablation)."""
    async def refine(self, experiences: list[Experience],
                     context: Task | None = None) -> list[Experience]:
        return experiences

class LLMRefineStrategy(RefineStrategy):
    """LLM-based meta-reasoning refinement (ReMem-style)."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def refine(self, experiences: list[Experience],
                     context: Task | None = None) -> list[Experience]:
        # LLM analyzes experiences, decides which to keep/merge/reorganize
        ...
```

### Implementation Signature

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

    def store(self, trajectory: Trajectory) -> str:
        """
        Store trajectory as experience.

        - Generates UUID for experience_id
        - Extracts embedding text via extractor
        - Stores success/failure status in metadata
        - Successful trajectories prioritized in search ranking
        """
        ...

    def search(self, task: Task, k: int = 4) -> list[Experience]:
        """
        Find similar experiences via embedding similarity.

        - Default k=4 from ReMem paper
        - Prioritizes successful experiences in ranking
        - Returns both success/failure for learning (metadata indicates which)
        """
        ...

    def get(self, experience_id: str) -> Experience | None: ...

    def refine(self, experiences: list[Experience]) -> list[Experience]:
        """Delegates to refine_strategy."""
        ...

    def prune(self, criteria: dict[str, Any]) -> int:
        """
        Remove low-value experiences.

        Criteria:
        - min_success_rate: float - minimum success rate to keep
        - max_age_days: int - maximum age in days
        - keep_diverse: bool - preserve diversity even if low-performing
        """
        ...
```

---

## Component 2: ConceptLibrary Implementation

Code pattern storage with Stitch/LILO-style compression and semantic search.

### Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Concept IDs | UUIDs (`uuid4`) | Consistent with other components |
| Embedding source | Name + description | Captures semantic meaning |
| Composition | **Agentic** (LLM-guided) | LILO: LLM determines meaningful combinations |
| Compression | **Hybrid** (Stitch + LLM AutoDoc) | Fast symbolic extraction + interpretable naming |
| Primitives | Domain-specific, loaded at init | Hardcoded base operations per domain |

### Strategy Protocols

```python
@runtime_checkable
class CompositionStrategy(Protocol):
    """Combines multiple concepts into a new composed concept."""
    async def compose(self, concepts: list[CodeConcept]) -> CodeConcept | None:
        """
        Compose concepts into a new one.

        Returns None if composition is not meaningful/possible.
        """
        ...

@runtime_checkable
class CompressionStrategy(Protocol):
    """Extracts new concepts from trajectories (Stitch/LILO-style)."""
    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """
        Extract reusable patterns from successful trajectories.

        Implementations may use:
        - Anti-unification (Stitch)
        - LLM-based pattern recognition
        - Hybrid approaches
        """
        ...

@runtime_checkable
class ConceptDocumenter(Protocol):
    """Generates documentation for concepts (LILO AutoDoc)."""
    async def document(self, concept: CodeConcept,
                       usage_examples: list[tuple[str, str]]) -> CodeConcept:
        """Add name, description, signature, usage guidance."""
        ...
```

### Default Implementations

```python
class LLMCompositionStrategy(CompositionStrategy):
    """LLM determines how to combine concepts meaningfully."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def compose(self, concepts: list[CodeConcept]) -> CodeConcept | None:
        # LLM analyzes concepts and generates composed code
        ...

class StitchCompressionStrategy(CompressionStrategy):
    """Symbolic anti-unification for pattern extraction."""
    def __init__(self, documenter: ConceptDocumenter | None = None):
        self.documenter = documenter

    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        # 1. Extract successful code from trajectories
        # 2. Parse to AST, find common patterns via anti-unification
        # 3. Score by MDL compression benefit
        # 4. Optionally document with AutoDoc
        ...

class LLMAutoDocumenter(ConceptDocumenter):
    """LILO-style AutoDoc using LLM."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def document(self, concept: CodeConcept,
                       usage_examples: list[tuple[str, str]]) -> CodeConcept:
        # Generate: name, description, signature, usage_guidance
        ...
```

### Primitive Loading

```python
class PrimitiveLoader(Protocol):
    """Loads domain-specific primitive concepts."""
    def load(self) -> dict[str, CodeConcept]: ...

class ARCPrimitiveLoader(PrimitiveLoader):
    """Load ARC-AGI grid manipulation primitives."""
    def load(self) -> dict[str, CodeConcept]:
        return {
            "get_objects": CodeConcept(...),
            "flood_fill": CodeConcept(...),
            "rotate_90": CodeConcept(...),
            "mirror_horizontal": CodeConcept(...),
            "get_background_color": CodeConcept(...),
            # ... more ARC primitives
        }

class SWEPrimitiveLoader(PrimitiveLoader):
    """Load software engineering primitives."""
    def load(self) -> dict[str, CodeConcept]:
        return {
            "read_file": CodeConcept(...),
            "write_file": CodeConcept(...),
            "search_codebase": CodeConcept(...),
            # ... more SWE primitives
        }
```

### Implementation Signature

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

    def add(self, concept: CodeConcept) -> str:
        """Add concept, embed name + description."""
        ...

    def search(self, query: str, k: int = 5) -> list[CodeConcept]:
        """Semantic search by natural language query."""
        ...

    def get(self, concept_id: str) -> CodeConcept | None: ...

    def compose(self, concept_ids: list[str]) -> CodeConcept | None:
        """Delegates to composition_strategy."""
        ...

    def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """Delegates to compression_strategy."""
        ...

    def update_stats(self, concept_id: str, success: bool) -> None:
        """Update usage count and success rate."""
        ...
```

---

## Component 3: StrategyBank Implementation

Abstract strategy storage (ArcMemo-style) for high-level reasoning patterns.

### Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Strategy IDs | UUIDs (`uuid4`) | Consistent with other components |
| Embedding source | Situation field (configurable) | Start with "when to apply" text |
| Write operation | **Agentic** (LLM abstraction) | Requires understanding trajectory to extract abstract pattern |
| Success rate update | Configurable (EMA default) | Exponential moving average, easy to swap |
| Source trajectories | **Success only** | Only abstract winning strategies |

### Strategy Protocols

```python
@runtime_checkable
class StrategyAbstractor(Protocol):
    """Abstracts a trajectory into a reusable strategy."""
    async def abstract(self, trajectory: Trajectory) -> Strategy | None:
        """
        Extract high-level strategy from successful trajectory.

        Returns None if trajectory is not abstractable (e.g., too specific).
        """
        ...

@runtime_checkable
class SuccessRateUpdater(Protocol):
    """Updates success rate statistics for strategies."""
    def update(self, current_rate: float, current_count: int,
               success: bool) -> tuple[float, int]:
        """
        Returns (new_rate, new_count).

        Implementations may use:
        - Simple average
        - Exponential moving average
        - Bayesian update
        - Recency-weighted
        """
        ...
```

### Default Implementations

```python
class LLMStrategyAbstractor(StrategyAbstractor):
    """LLM extracts abstract strategy from trajectory."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def abstract(self, trajectory: Trajectory) -> Strategy | None:
        # LLM analyzes trajectory and generates:
        # - situation: when to apply this strategy
        # - approach: high-level steps
        # - rationale: why this works
        ...

class EMASuccessUpdater(SuccessRateUpdater):
    """Exponential moving average for success rate."""
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha

    def update(self, current_rate: float, current_count: int,
               success: bool) -> tuple[float, int]:
        new_value = 1.0 if success else 0.0
        new_rate = self.alpha * new_value + (1 - self.alpha) * current_rate
        return (new_rate, current_count + 1)

class SimpleAverageUpdater(SuccessRateUpdater):
    """Simple running average (baseline)."""
    def update(self, current_rate: float, current_count: int,
               success: bool) -> tuple[float, int]:
        new_count = current_count + 1
        new_rate = (current_rate * current_count + (1.0 if success else 0.0)) / new_count
        return (new_rate, new_count)

class BayesianUpdater(SuccessRateUpdater):
    """Beta-Bernoulli Bayesian update (future experiment)."""
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta

    def update(self, current_rate: float, current_count: int,
               success: bool) -> tuple[float, int]:
        # Update beta distribution parameters
        ...
```

### Implementation Signature

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

    def write(self, trajectory: Trajectory) -> Strategy | None:
        """
        Abstract trajectory into strategy.

        - Only processes successful trajectories
        - Delegates to abstractor strategy
        - Embeds situation field for retrieval
        """
        ...

    def read(self, task: Task, k: int = 5) -> list[Strategy]:
        """Find applicable strategies for task."""
        ...

    def get(self, strategy_id: str) -> Strategy | None: ...

    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Delegates to success_updater strategy."""
        ...
```

---

## Component 4: MemorySystem Aggregator

Unified interface combining all three memory components.

### Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component optionality | All optional | Enable ablation studies |
| Query parallelism | `asyncio.gather` | Parallel queries across components |
| Store behavior | Success to all; failure to experience only | Strategies/concepts only from success |

### Implementation Signature

```python
class MemorySystemImpl:
    """Aggregator for all memory types."""

    def __init__(
        self,
        experience: ExperienceMemory | None = None,
        concepts: ConceptLibrary | None = None,
        strategies: StrategyBank | None = None,
    ): ...

    @property
    def experience_memory(self) -> ExperienceMemory | None: ...

    @property
    def concept_library(self) -> ConceptLibrary | None: ...

    @property
    def strategy_bank(self) -> StrategyBank | None: ...

    async def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
        """
        Query all available components in parallel.

        Uses asyncio.gather for concurrent queries.
        Missing components return empty results.
        """
        ...

    def store(self, trajectory: Trajectory) -> dict[str, Any]:
        """
        Store in available components.

        - ExperienceMemory: Always stores (success and failure)
        - ConceptLibrary: Only extracts from successful trajectories
        - StrategyBank: Only abstracts from successful trajectories

        Returns dict with IDs from each component that stored.
        """
        ...
```

---

## File Structure

```
src/atlas/memory/
├── __init__.py
├── experience.py          # ChromaExperienceMemory + strategies
├── concepts.py            # ChromaConceptLibrary + strategies
├── strategies.py          # ChromaStrategyBank + strategies
├── system.py              # MemorySystemImpl aggregator
├── storage.py             # VectorStore protocol + ChromaDB adapter
└── primitives/
    ├── __init__.py
    ├── arc.py             # ARCPrimitiveLoader
    └── swe.py             # SWEPrimitiveLoader
```

---

## Dependencies

- Phase 2 infrastructure:
  - `atlas.infra.embeddings.Embedder`
  - `atlas.infra.vector_index.VectorIndex`
- Core types from `atlas.core.types`:
  - `Task`, `Trajectory`, `Experience`, `CodeConcept`, `Strategy`
- Protocols from `atlas.protocols.memory`

---

## Testing Strategy

### Unit Tests
- Each component in isolation with mock strategies
- Strategy implementations independently
- Storage layer with mock vector store

### Integration Tests
- Components with real ChromaDB (ephemeral)
- End-to-end store -> search -> retrieve flows
- MemorySystem with various component combinations

### Ablation Test Fixtures
- Memory-only (no concepts, no strategies)
- Concepts-only (no experience, no strategies)
- Full system vs individual components

---

## Success Criteria

- [ ] ExperienceMemory stores and retrieves experiences
  - [ ] UUID generation for experience IDs
  - [ ] Configurable extraction strategy
  - [ ] Pluggable refine strategy
  - [ ] Success/failure differentiation in storage
- [ ] ConceptLibrary indexes and searches code patterns
  - [ ] Primitive loading by domain
  - [ ] Pluggable composition strategy
  - [ ] Pluggable compression strategy (Stitch + AutoDoc)
  - [ ] Usage statistics tracking
- [ ] StrategyBank manages abstract strategies
  - [ ] Only abstracts successful trajectories
  - [ ] Configurable success rate update strategy
  - [ ] Pluggable abstraction strategy
- [ ] MemorySystem combines all three
  - [ ] Parallel async queries via asyncio.gather
  - [ ] Graceful degradation when components missing
  - [ ] Differential store behavior for success/failure
- [ ] Each component works in isolation
- [ ] All strategies are swappable for experimentation
