---
id: i-3xxe
title: 'Implement Memory protocols (ExperienceMemory, ConceptLibrary, StrategyBank)'
priority: 1
created_at: '2025-12-18 03:33:24'
tags:
  - memory
  - phase-1
  - pillar-1
  - protocols
relationships:
  - from_id: i-3xxe
    from_uuid: 7d9b3185-161f-4ca9-bfc5-66e7ed43fa33
    from_type: issue
    to_id: i-4zj6
    to_uuid: f7fdaab5-ec46-410d-a60d-5350250ac750
    to_type: issue
    relationship_type: depends-on
    created_at: '2025-12-18 04:33:19'
    metadata: null
  - from_id: i-3xxe
    from_uuid: 7d9b3185-161f-4ca9-bfc5-66e7ed43fa33
    from_type: issue
    to_id: s-3c37
    to_uuid: 0f82673e-83cc-4b0a-8e6c-de2e1cc03759
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-18 04:33:19'
    metadata: null
status: closed
closed_at: '2025-12-18 04:33:19'
---
Define the protocols for the three memory systems (Pillar 1).

## Files to Create
- `atlas/protocols/memory.py` (~100 lines)

## ExperienceMemory Protocol
Task-level retrieval (ReMem-style):

```python
class ExperienceMemory(Protocol):
    def store(self, trajectory: Trajectory) -> str:
        """Store trajectory as experience, return ID"""
        ...
    
    def search(self, task: Task, k: int = 4) -> List[Experience]:
        """Find similar experiences via embedding similarity"""
        ...
    
    def refine(self, experiences: List[Experience]) -> List[Experience]:
        """ReMem-style: exploit useful, prune noise, reorganize"""
        ...
    
    def prune(self, criteria: Dict[str, Any]) -> int:
        """Remove low-value experiences, return count"""
        ...
```

## ConceptLibrary Protocol
Reusable code patterns (Stitch/LILO-style):

```python
class ConceptLibrary(Protocol):
    def add(self, concept: CodeConcept) -> str:
        """Add concept, return ID"""
        ...
    
    def search(self, query: str, k: int = 5) -> List[CodeConcept]:
        """Find relevant concepts by semantic similarity"""
        ...
    
    def get(self, concept_id: str) -> Optional[CodeConcept]:
        """Get by ID"""
        ...
    
    def compose(self, concept_ids: List[str]) -> Optional[CodeConcept]:
        """Compose multiple concepts into one"""
        ...
    
    def compress(self, trajectories: List[Trajectory]) -> List[CodeConcept]:
        """Extract new concepts via Stitch compression"""
        ...
```

## StrategyBank Protocol
Abstract reasoning patterns (ArcMemo-style):

```python
class StrategyBank(Protocol):
    def write(self, trajectory: Trajectory) -> Optional[Strategy]:
        """Abstract trajectory into strategy"""
        ...
    
    def read(self, task: Task, k: int = 5) -> List[Strategy]:
        """Find applicable strategies"""
        ...
    
    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update usage statistics"""
        ...
```

## Supporting Types
Also define in `atlas/core/types.py` or separate file:
- `Experience` dataclass
- `CodeConcept` dataclass  
- `Strategy` dataclass

## Acceptance Criteria
- [ ] All three protocols defined
- [ ] Supporting dataclasses implemented
- [ ] Type hints complete

Implements [[s-3c37]]
