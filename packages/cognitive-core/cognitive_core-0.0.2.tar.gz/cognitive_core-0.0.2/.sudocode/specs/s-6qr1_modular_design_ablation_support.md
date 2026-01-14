---
id: s-6qr1
title: Modular Design & Ablation Support
priority: 1
created_at: '2025-12-07 08:21:43'
parent_id: s-5o87
tags:
  - ablation
  - design-patterns
  - modular
  - testing
relationships:
  - from_id: s-6qr1
    from_uuid: 51de9b9f-5e1b-478d-a3f3-e831505605ca
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:22:02'
    metadata: null
---
# Modular Design & Ablation Support

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Every ATLAS component must be independently usable and composable. This enables:
- Ablation studies (test each component's contribution)
- Incremental development (build and test pieces independently)
- Flexible deployment (use only what you need)

## Design Principles

### 1. Standalone Operation

Each component works without other ATLAS components:

```python
# Just experience memory
from atlas.memory import ExperienceMemory
memory = ExperienceMemory()
memory.store(trajectory)
similar = memory.search(task)

# Just concept library
from atlas.memory import ConceptLibrary
library = ConceptLibrary()
library.add(concept)
relevant = library.search("rotate grid")

# Just search (no memory)
from atlas.search import MindEvolutionSearch
search = MindEvolutionSearch(llm=llm)  # memory=None is valid
candidates = search.search(task, env)
```

### 2. Optional Dependencies

Components accept optional dependencies via constructor:

```python
class ExperienceMemory:
    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,  # optional
        vector_index: Optional[VectorIndex] = None,              # optional
    ):
        # Use defaults if not provided
        self.embedder = embedding_provider or DefaultEmbeddingProvider()
        self.index = vector_index or InMemoryVectorIndex()
```

### 3. Graceful Degradation

Missing dependencies return empty results, not errors:

```python
class MemorySystem:
    def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
        experiences = []
        concepts = []
        strategies = []
        
        # Each is optional - missing components just return empty
        if self.experience_memory:
            experiences = self.experience_memory.search(task, k)
        if self.concept_library:
            concepts = self.concept_library.search(task.description, k)
        if self.strategy_bank:
            strategies = self.strategy_bank.read(task, k)
        
        return MemoryQueryResult(experiences, concepts, strategies)
```

### 4. Protocol-Based Interfaces

Depend on protocols, not concrete implementations:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class EmbeddingProvider(Protocol):
    def encode(self, text: str) -> np.ndarray: ...
    def encode_batch(self, texts: List[str]) -> List[np.ndarray]: ...

@runtime_checkable
class VectorIndex(Protocol):
    def add(self, id: str, vector: np.ndarray, metadata: dict) -> None: ...
    def search(self, vector: np.ndarray, k: int) -> List[tuple]: ...
    def delete(self, id: str) -> bool: ...
```

## Ablation Configurations

### Configuration Enum

```python
class MemoryConfig(Enum):
    NONE = auto()               # No memory (baseline)
    EXPERIENCE_ONLY = auto()    # Only experience memory
    CONCEPT_ONLY = auto()       # Only concept library
    STRATEGY_ONLY = auto()      # Only strategy bank
    EXPERIENCE_CONCEPT = auto() # Experience + concept
    EXPERIENCE_STRATEGY = auto()# Experience + strategy
    CONCEPT_STRATEGY = auto()   # Concept + strategy
    FULL = auto()               # All three

class SearchConfig(Enum):
    DIRECT = auto()             # Single-shot
    EVOLUTION = auto()          # Mind Evolution
    MCTS = auto()               # SWE-Search
    HYBRID = auto()             # Combined

class LearningConfig(Enum):
    NONE = auto()               # No learning
    MEMORY_ONLY = auto()        # SAGE-style (no fine-tuning)
    FINETUNE = auto()           # SOAR-style
    FULL = auto()               # Both
```

### Predefined Ablations

```python
ABLATION_CONFIGS = {
    # Baselines
    "baseline": AblationConfig(
        memory=MemoryConfig.NONE,
        search=SearchConfig.DIRECT,
        learning=LearningConfig.NONE,
    ),
    
    "baseline_search": AblationConfig(
        memory=MemoryConfig.NONE,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.NONE,
    ),
    
    # Memory ablations
    "experience_only": AblationConfig(
        memory=MemoryConfig.EXPERIENCE_ONLY,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.MEMORY_ONLY,
    ),
    
    "concept_only": AblationConfig(
        memory=MemoryConfig.CONCEPT_ONLY,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.MEMORY_ONLY,
    ),
    
    "strategy_only": AblationConfig(
        memory=MemoryConfig.STRATEGY_ONLY,
        search=SearchConfig.DIRECT,
        learning=LearningConfig.MEMORY_ONLY,
    ),
    
    # Full system
    "full": AblationConfig(
        memory=MemoryConfig.FULL,
        search=SearchConfig.EVOLUTION,
        learning=LearningConfig.FULL,
    ),
}
```

### Factory Functions

```python
def create_from_config(config: AblationConfig) -> ATLASSolver:
    """Create solver from ablation config"""
    # Build memory system
    exp_mem = ExperienceMemory() if config.needs_experience else None
    concept_lib = ConceptLibrary() if config.needs_concepts else None
    strat_bank = StrategyBank() if config.needs_strategies else None
    
    memory = MemorySystem(
        experience_memory=exp_mem,
        concept_library=concept_lib,
        strategy_bank=strat_bank,
    )
    
    # Build search
    search = create_search(config.search, memory)
    
    # Build learning
    learning = create_learning(config.learning, memory)
    
    return ATLASSolver(memory=memory, search=search, learning=learning)
```

## Running Ablation Studies

```python
def run_ablation_study(
    tasks: List[Task],
    configs: List[str] = None,
) -> Dict[str, Dict]:
    """Run ablation study"""
    configs = configs or list(ABLATION_CONFIGS.keys())
    results = {}
    
    for config_name in configs:
        config = ABLATION_CONFIGS[config_name]
        solver = create_from_config(config)
        
        successes = 0
        total_cost = 0
        
        for task in tasks:
            trajectory = solver.solve(task)
            if trajectory.outcome.success:
                successes += 1
            total_cost += trajectory.total_tokens
        
        results[config_name] = {
            "accuracy": successes / len(tasks),
            "cost": total_cost,
            "config": config,
        }
    
    return results

# Usage
results = run_ablation_study(
    tasks=test_tasks,
    configs=["baseline", "experience_only", "concept_only", "full"]
)

# Expected output:
# baseline: 32.5%
# experience_only: 41.2%
# concept_only: 38.7%
# full: 52.1%
```

## Default Implementations

Each component provides sensible defaults:

| Component | Default Implementation |
|-----------|----------------------|
| EmbeddingProvider | `DefaultEmbeddingProvider` (BAAI/bge-base-en-v1.5) |
| VectorIndex | `InMemoryVectorIndex` (simple numpy) |
| LLM | Must be provided (no default) |
| Compressor | `None` (compression disabled) |
| AutoDocumenter | `None` (no documentation) |

## Lazy Loading

Heavy dependencies load only when needed:

```python
class DefaultEmbeddingProvider:
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self._model = None  # Lazy
        self._model_name = model_name
    
    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model
    
    def encode(self, text: str) -> np.ndarray:
        return self.model.encode(text)
```

## Testing in Isolation

Each component can be tested independently:

```python
# Test experience memory alone
def test_experience_memory():
    memory = ExperienceMemory()
    
    # Store
    exp_id = memory.store(mock_trajectory)
    assert exp_id is not None
    
    # Search
    results = memory.search(mock_task, k=3)
    assert len(results) <= 3
    
    # Prune
    count = memory.prune({"max_age_days": 30})
    assert count >= 0

# Test search without memory
def test_search_no_memory():
    search = MindEvolutionSearch(llm=mock_llm)  # No memory
    candidates = search.search(mock_task, mock_env)
    assert len(candidates) > 0
```

## File Location

```
atlas/
├── experiments/
│   ├── __init__.py
│   ├── ablation.py      # AblationConfig, ABLATION_CONFIGS
│   ├── runner.py        # run_ablation_study
│   └── analysis.py      # Result analysis utilities
```
