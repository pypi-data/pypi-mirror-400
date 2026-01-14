---
id: s-3c37
title: Memory Systems (Pillar 1)
priority: 1
created_at: '2025-12-07 08:21:07'
parent_id: s-5o87
tags:
  - concepts
  - experience
  - memory
  - pillar-1
  - strategies
relationships:
  - from_id: s-3c37
    from_uuid: 0f82673e-83cc-4b0a-8e6c-de2e1cc03759
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:22:01'
    metadata: null
---
# Memory Systems (Pillar 1)

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Memory is **what to remember** - the accumulated knowledge from past trajectories. Three complementary memory types at different abstraction levels.

## Memory Hierarchy

```
Strategy Bank    →  "For symmetry tasks, reflect then duplicate"  (most abstract)
        ↓
Experience Memory →  "Task #123 was similar, here's what worked"   (task-level)
        ↓
Concept Library  →  "Use rotate_90() followed by flood_fill()"    (most concrete)
```

## Experience Memory

**Purpose**: Task-level retrieval of similar past experiences (ReMem-style)

### Data Structure

```python
@dataclass
class Experience:
    id: str
    task_input: str        # Task description
    solution_output: str   # Solution attempt
    feedback: str          # Outcome/error info
    success: bool
    embedding: np.ndarray  # BAAI/bge-base-en-v1.5
    trajectory_id: str     # Source tracking
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Interface

```python
class ExperienceMemory(ABC):
    @abstractmethod
    def store(self, trajectory: Trajectory) -> str:
        """Store trajectory as experience, return ID"""
        pass
    
    @abstractmethod
    def search(self, task: Task, k: int = 4) -> List[Experience]:
        """Find similar experiences via embedding similarity"""
        pass
    
    @abstractmethod
    def refine(self, experiences: List[Experience]) -> List[Experience]:
        """ReMem-style: exploit useful, prune noise, reorganize"""
        pass
    
    @abstractmethod
    def prune(self, criteria: Dict[str, Any]) -> int:
        """Remove low-value experiences, return count"""
        pass
```

### Key Insight: ReMem Loop

```
(task, memory) →[search] retrieved →[synthesis] solution →[evolve] updated_memory
```

- Search: Top-k retrieval via cosine similarity
- Synthesis: Use retrieved context in LLM prompt
- Evolve: Store new experience, refine existing

### Configuration

- Embedding model: BAAI/bge-base-en-v1.5 (validated in ReMem)
- Default k: 4 (from ReMem paper)
- Vector index: ChromaDB (local) or Pinecone (cloud)

## Concept Library

**Purpose**: Reusable code patterns and compositions (Stitch/LILO-style)

### Data Structure

```python
@dataclass
class CodeConcept:
    id: str
    name: str              # Human-readable name (AutoDoc)
    description: str       # What it does
    code: str              # The actual code
    signature: str         # Type signature
    examples: List[Tuple[str, str]]  # (input, output) pairs
    
    # Stats
    usage_count: int = 0
    success_rate: float = 0.0
    
    # Retrieval
    embedding: Optional[np.ndarray] = None
    
    # Metadata
    source: str = "primitive"  # "primitive", "learned", "composed"
```

### Interface

```python
class ConceptLibrary(ABC):
    @abstractmethod
    def add(self, concept: CodeConcept) -> str:
        """Add concept, return ID"""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[CodeConcept]:
        """Find relevant concepts by semantic similarity"""
        pass
    
    @abstractmethod
    def get(self, concept_id: str) -> Optional[CodeConcept]:
        """Get by ID"""
        pass
    
    @abstractmethod
    def compose(self, concept_ids: List[str]) -> Optional[CodeConcept]:
        """Compose multiple concepts into one"""
        pass
    
    @abstractmethod
    def compress(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Extract new concepts via Stitch compression"""
        pass
```

### Key Insight: Stitch + LILO

1. **Stitch**: Anti-unification for fast pattern extraction (1000x faster than DreamCoder)
2. **LILO AutoDoc**: LLM generates names/descriptions for interpretability

### Primitives vs Learned

- **Primitives**: Domain-specific base operations (loaded at init)
- **Learned**: Extracted from trajectories via compression
- **Composed**: Combinations of existing concepts

## Strategy Bank

**Purpose**: Abstract reasoning patterns (ArcMemo-style)

### Data Structure

```python
@dataclass
class Strategy:
    id: str
    situation: str         # When to apply
    suggestion: str        # What to do
    parameters: List[Dict[str, str]]  # Typed parameters
    
    # Stats
    usage_count: int = 0
    success_rate: float = 0.5
    
    # Retrieval
    embedding: Optional[np.ndarray] = None
```

### Interface

```python
class StrategyBank(ABC):
    @abstractmethod
    def write(self, trajectory: Trajectory) -> Optional[Strategy]:
        """Abstract trajectory into strategy"""
        pass
    
    @abstractmethod
    def read(self, task: Task, k: int = 5) -> List[Strategy]:
        """Find applicable strategies"""
        pass
    
    @abstractmethod
    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update usage statistics"""
        pass
```

### Key Insight: ArcMemo

**Concept-level beats instance-level at ALL compute scales.**

Instead of: "Task #123 had this exact solution"
Use: "For tasks with symmetry patterns, check horizontal/vertical reflection"

## Memory System Aggregator

Combines all three into unified interface:

```python
class MemorySystem:
    def __init__(
        self,
        experience_memory: Optional[ExperienceMemory] = None,
        concept_library: Optional[ConceptLibrary] = None,
        strategy_bank: Optional[StrategyBank] = None,
    ):
        # All optional for ablation studies
        pass
    
    def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
        """Query all available components"""
        pass
    
    def store(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Store in all available components"""
        pass
```

## Emergent Domain Organization

Domains self-organize via embedding space:
- Frontend tasks cluster with frontend
- Backend tasks cluster with backend
- No manual taxonomy required

Search naturally returns domain-appropriate results.

## File Location

```
atlas/memory/
├── __init__.py
├── experience_memory.py   # ExperienceMemory, Experience
├── concept_library.py     # ConceptLibrary, CodeConcept
├── strategy_bank.py       # StrategyBank, Strategy
├── system.py              # MemorySystem aggregator
├── embeddings.py          # EmbeddingProvider protocol
└── vector_index.py        # VectorIndex protocol + implementations
```
