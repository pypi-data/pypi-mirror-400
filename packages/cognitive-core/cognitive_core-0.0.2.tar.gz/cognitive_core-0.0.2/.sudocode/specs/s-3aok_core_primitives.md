---
id: s-3aok
title: Core Primitives
priority: 1
created_at: '2025-12-07 08:21:07'
parent_id: s-5o87
tags:
  - core
  - data-structures
  - primitives
relationships:
  - from_id: s-3aok
    from_uuid: a0408b8b-cef6-49ab-9e4e-a7edbbe9515f
    from_type: spec
    to_id: s-5o87
    to_uuid: 315749e5-c7a0-41c9-8fd2-8124b1d9c2f7
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-07 08:22:01'
    metadata: null
---
# Core Primitives

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

The foundational data structures that all ATLAS components operate on. These are the "atoms" of the system.

## Trajectory

The **atomic unit of learning**. Everything in ATLAS flows through trajectories.

### Structure

```python
@dataclass
class Trajectory:
    task: Task
    steps: List[Step]
    outcome: Outcome
    agent_id: str
    timestamp: datetime
    
    # Optional metadata
    llm_calls: int = 0
    total_tokens: int = 0
    wall_time_seconds: float = 0.0
```

### Design Decisions

- **Immutable**: Trajectories are never modified after creation
- **Complete**: Every trajectory has an outcome (even partial/failed ones)
- **Attributable**: Agent ID enables analysis of which agents produce what
- **Embeddable**: Can precompute embeddings for efficient retrieval

## Task

Domain-agnostic representation of work to be done.

### Structure

```python
@dataclass
class Task:
    id: str
    domain: TaskDomain  # emergent, not hard-coded enum
    description: str
    context: Dict[str, Any]  # domain-specific data
    verification: VerificationSpec
    embedding: Optional[np.ndarray] = None
```

### Domain Handling

Domains are **emergent via embeddings**, not a fixed enum:
- Frontend tasks cluster with frontend tasks
- Backend tasks cluster with backend tasks
- No manual taxonomy required

For routing purposes, can use string tags:
```python
task.context["domain_hints"] = ["swe", "frontend", "react"]
```

## Step

Single step in a trajectory following ReAct pattern.

### Structure

```python
@dataclass
class Step:
    thought: Optional[str]   # Agent's reasoning (if available)
    action: str              # Action taken
    observation: str         # Result/feedback
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Computed during analysis
    attribution_score: Optional[float] = None
```

### Metadata Examples

```python
step.metadata = {
    "tool": "bash",
    "duration_ms": 1234,
    "tokens_used": 500,
    "files_modified": ["src/main.py"],
}
```

## Outcome

Result of a trajectory attempt.

### Structure

```python
@dataclass
class Outcome:
    success: bool
    partial_score: Optional[float] = None  # 0.0 - 1.0
    error_info: Optional[str] = None
    verification_details: Dict[str, Any] = field(default_factory=dict)
```

### Partial Scoring

Support for partial credit enables:
- Ranking candidates during search
- Learning from partially successful attempts
- More granular feedback

## Environment

Execution context where tasks are solved.

### Interface

```python
class Environment(ABC):
    @abstractmethod
    def reset(self, task: Task) -> str:
        """Reset with new task, return initial observation"""
        pass
    
    @abstractmethod
    def step(self, action: str) -> Tuple[str, float, bool, Dict]:
        """Execute action → (observation, reward, done, info)"""
        pass
    
    @abstractmethod
    def verify(self, solution: Any) -> Outcome:
        """Verify a solution"""
        pass
    
    @property
    @abstractmethod
    def max_steps(self) -> int:
        """Maximum steps before timeout"""
        pass
```

### Design Decisions

- **Gymnasium-like**: Familiar interface for RL practitioners
- **Verification built-in**: Not external, enables self-contained testing
- **Sandboxed**: Reproducible, isolated execution
- **Partial scoring**: Supports ranking and learning from failures

## Agent

Actor that produces trajectories.

### Interface

```python
class Agent(ABC):
    @abstractmethod
    def solve(self, task: Task, env: Environment) -> Trajectory:
        """Attempt to solve task, return trajectory"""
        pass
    
    @abstractmethod
    def step(self, observation: str) -> str:
        """Given observation, return action"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset agent state"""
        pass
```

### Agent Types

1. **External Agents**: Wrapped versions of Claude Code, OpenHands, SWE-agent
2. **ATLAS Agent**: Memory-augmented agent with library awareness

## Serialization

All primitives must support:
- JSON serialization for storage/transfer
- Pickle for fast local caching
- Embedding storage (numpy arrays)

```python
trajectory.to_json() → str
Trajectory.from_json(data: str) → Trajectory
```

## File Location

```
atlas/core/
├── __init__.py
├── trajectory.py    # Trajectory, Step, Outcome
├── task.py          # Task, VerificationSpec
├── environment.py   # Environment ABC
├── agent.py         # Agent ABC
└── types.py         # Shared types, enums
```
