---
id: s-3nub
title: Search Methods (Pillar 2)
priority: 1
created_at: '2025-12-07 08:21:07'
parent_id: s-5o87
tags:
  - mcts
  - mind-evolution
  - pillar-2
  - search
  - verifier
relationships:
  - from_id: s-3nub
    from_uuid: 8408a08a-551b-479f-a29d-d1d4e9daaebb
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:22:01'
    metadata: null
---
# Search Methods (Pillar 2)

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Search is **how to solve** - the algorithms for finding solutions. Different methods suit different task types.

## Task Router

Decides which search strategy to use based on task + memory context.

### Interface

```python
class TaskRouter(ABC):
    @abstractmethod
    def route(
        self,
        task: Task,
        memory: MemorySystem,
    ) -> RoutingDecision:
        """Decide how to approach a task"""
        pass
```

### Routing Decision

```python
@dataclass
class RoutingDecision:
    strategy: SearchStrategy  # direct | evolutionary | mcts | adapt
    relevant_concepts: List[CodeConcept]
    similar_experiences: List[Experience]
    suggested_strategies: List[Strategy]
    estimated_difficulty: float  # 0.0 - 1.0
    search_budget: int  # max LLM calls
```

### Routing Logic

| Condition | Strategy | Rationale |
|-----------|----------|-----------|
| High similarity + success | `adapt` | Modify existing solution |
| Clear strategy available | `direct` | Apply strategy directly |
| ARC domain | `evolutionary` | Mind Evolution for fitness-based |
| SWE domain | `mcts` | SWE-Search for sequential edits |
| Unknown/low confidence | `evolutionary` | Default to population search |

## Search Engine Interface

```python
class SearchEngine(ABC):
    def __init__(
        self,
        llm: LLM,
        memory: Optional[MemorySystem] = None,  # optional!
        config: Optional[SearchConfig] = None,
    ):
        pass
    
    @abstractmethod
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> List[Candidate]:
        """Search for candidate solutions"""
        pass
    
    @abstractmethod
    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine candidate based on feedback"""
        pass
```

### Candidate

```python
@dataclass
class Candidate:
    solution: Any           # Domain-specific solution
    confidence: float       # 0.0 - 1.0
    reasoning: str          # Explanation
    source: str             # "generated", "adapted", "retrieved"
    fitness: Optional[float] = None
    parent_ids: List[str] = field(default_factory=list)
```

## Mind Evolution Search

**Best for**: ARC-AGI, tasks with clear fitness functions

### Algorithm

```
1. Initialize population (50% from memory, 50% novel)
2. Evaluate fitness (via verifier)
3. Select elites (top 50%)
4. Mutate/crossover to fill population
5. Repeat for 5-10 generations
```

### Configuration

```python
@dataclass
class MindEvolutionConfig:
    population_size: int = 20
    generations: int = 10
    elite_fraction: float = 0.5
    memory_init_fraction: float = 0.5  # % from memory
    mutation_temperature: float = 0.7
```

### Cost

~100 LLM calls per task (population_size × generations / 2)

### Memory Integration

Population initialization:
1. Search memory for similar experiences
2. Adapt top-k experiences to current task
3. Search concepts and generate candidates using them
4. Fill remaining with novel generation

## SWE-Search (MCTS)

**Best for**: Software engineering, sequential edit tasks

### Algorithm

```
1. Root = task state
2. Select node via UCB (exploitation + exploration)
3. Expand with LLM-generated actions
4. Simulate rollout
5. Backpropagate value estimate
6. Repeat 50-200 times
```

### Configuration

```python
@dataclass
class SWESearchConfig:
    max_expansions: int = 100
    ucb_constant: float = 1.414
    max_depth: int = 20
    rollout_depth: int = 5
    use_discriminator: bool = True
```

### Cost

~200 LLM calls per task

### Discriminator

Optional model to estimate solution quality:
- Ranks candidates without full verification
- Enables early pruning of bad branches
- Can be trained on trajectory outcomes

## Direct Solver

**Best for**: High-confidence memory matches

### Algorithm

```
1. Retrieve most similar experience
2. Adapt solution to current task
3. Verify
4. If fail, try next most similar
```

### Cost

~1-5 LLM calls per task

### When to Use

- Experience similarity > 0.9
- Previous success on similar task
- Strategy bank has clear match

## Verifier

Verifies candidate solutions and enables inference-time scaling.

### Interface

```python
class Verifier(ABC):
    @abstractmethod
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a solution"""
        pass
    
    @abstractmethod
    def rank(
        self,
        task: Task,
        candidates: List[Candidate],
    ) -> List[Tuple[Candidate, float]]:
        """Rank candidates by estimated quality"""
        pass
```

### Domain Implementations

**ARC Verifier**:
- Exact grid match on training examples
- Partial score: cell-by-cell similarity

**SWE Verifier**:
- Execute tests in Docker sandbox
- Partial score: fraction of tests passing

### Key Insight

Verification enables **best-of-k scaling**:
- Generate k candidates
- Verify all
- Return best

SWE-Gym showed: 10% → 13.3% with best-of-8

## File Location

```
atlas/search/
├── __init__.py
├── router.py              # TaskRouter, RoutingDecision
├── base.py                # SearchEngine ABC, SearchConfig
├── mind_evolution.py      # MindEvolutionSearch
├── swe_search.py          # SWESearch (MCTS)
├── direct.py              # DirectSolver
└── verifier.py            # Verifier ABC + implementations
```
