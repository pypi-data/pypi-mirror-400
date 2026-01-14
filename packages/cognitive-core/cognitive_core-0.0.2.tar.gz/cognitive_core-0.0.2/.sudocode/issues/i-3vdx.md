---
id: i-3vdx
title: 'Implement Search protocols (TaskRouter, SearchEngine, Verifier)'
priority: 1
created_at: '2025-12-18 03:33:24'
tags:
  - phase-1
  - pillar-2
  - protocols
  - search
relationships:
  - from_id: i-3vdx
    from_uuid: 12104cbc-42a9-4929-bc6e-9258824f29d0
    from_type: issue
    to_id: i-3xxe
    to_uuid: 7d9b3185-161f-4ca9-bfc5-66e7ed43fa33
    to_type: issue
    relationship_type: depends-on
    created_at: '2025-12-18 04:33:19'
    metadata: null
  - from_id: i-3vdx
    from_uuid: 12104cbc-42a9-4929-bc6e-9258824f29d0
    from_type: issue
    to_id: s-3nub
    to_uuid: 8408a08a-551b-479f-a29d-d1d4e9daaebb
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-18 04:33:19'
    metadata: null
status: closed
closed_at: '2025-12-18 04:33:19'
---
Define the protocols for the search systems (Pillar 2).

## Files to Create
- `atlas/protocols/search.py` (~80 lines)

## TaskRouter Protocol
Decides which search strategy to use:

```python
class TaskRouter(Protocol):
    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """Decide how to approach a task"""
        ...
```

## SearchEngine Protocol
```python
class SearchEngine(Protocol):
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> List[Candidate]:
        """Search for candidate solutions"""
        ...
    
    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine candidate based on feedback"""
        ...
```

## Verifier Protocol
```python
class Verifier(Protocol):
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a solution"""
        ...
    
    def rank(
        self,
        task: Task,
        candidates: List[Candidate],
    ) -> List[Tuple[Candidate, float]]:
        """Rank candidates by estimated quality"""
        ...
```

## Supporting Types
Define in `atlas/core/types.py`:

```python
@dataclass
class RoutingDecision:
    strategy: str  # "direct" | "evolutionary" | "mcts" | "adapt"
    relevant_concepts: List[CodeConcept]
    similar_experiences: List[Experience]
    suggested_strategies: List[Strategy]
    estimated_difficulty: float
    search_budget: int

@dataclass
class Candidate:
    solution: Any
    confidence: float
    reasoning: str
    source: str  # "generated", "adapted", "retrieved"
    fitness: Optional[float] = None
    parent_ids: List[str] = field(default_factory=list)
```

## Acceptance Criteria
- [ ] All protocols defined with type hints
- [ ] RoutingDecision and Candidate dataclasses implemented
- [ ] Clear docstrings

Implements [[s-3nub]]
