---
id: i-4zj6
title: 'Implement core data types (Trajectory, Task, Step, Outcome)'
priority: 0
created_at: '2025-12-18 03:33:24'
tags:
  - core
  - data-structures
  - phase-1
status: open
---
Implement the foundational data structures that all ATLAS components operate on.

## Files to Create
- `atlas/core/__init__.py`
- `atlas/core/types.py` (~150 lines)
- `atlas/core/serialization.py` (~50 lines)

## Data Structures

### Trajectory
```python
@dataclass
class Trajectory:
    task: Task
    steps: List[Step]
    outcome: Outcome
    agent_id: str
    timestamp: datetime
    llm_calls: int = 0
    total_tokens: int = 0
    wall_time_seconds: float = 0.0
```

### Task
```python
@dataclass
class Task:
    id: str
    domain: str  # emergent via embeddings, not enum
    description: str
    context: Dict[str, Any]
    verification: VerificationSpec
    embedding: Optional[np.ndarray] = None
```

### Step
```python
@dataclass
class Step:
    thought: Optional[str]
    action: str
    observation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    attribution_score: Optional[float] = None
```

### Outcome
```python
@dataclass
class Outcome:
    success: bool
    partial_score: Optional[float] = None
    error_info: Optional[str] = None
    verification_details: Dict[str, Any] = field(default_factory=dict)
```

## Design Requirements
- All types should be **immutable** after creation (frozen dataclasses or Pydantic models)
- Support JSON serialization via `to_json()` / `from_json()`
- Support pickle for fast local caching
- Embedding fields use `Optional[np.ndarray]`

## Acceptance Criteria
- [ ] All dataclasses implemented with type hints
- [ ] JSON round-trip serialization works
- [ ] Unit tests for each type

Implements [[s-3aok]]
