---
id: i-2490
title: Implement Environment and Agent protocols
priority: 1
created_at: '2025-12-18 03:33:24'
tags:
  - core
  - phase-1
  - protocols
status: open
---
Define the abstract base classes for Environment and Agent - the execution context and actors.

## Files to Create
- `atlas/protocols/environment.py` (~40 lines)
- `atlas/protocols/agent.py` (~30 lines)

## Environment Protocol
Gymnasium-like interface for task execution:

```python
class Environment(Protocol):
    def reset(self, task: Task) -> str:
        """Reset with new task, return initial observation"""
        ...
    
    def step(self, action: str) -> Tuple[str, float, bool, Dict]:
        """Execute action → (observation, reward, done, info)"""
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Verify a solution"""
        ...
    
    @property
    def max_steps(self) -> int:
        """Maximum steps before timeout"""
        ...
```

## Agent Protocol
Actor that produces trajectories:

```python
class Agent(Protocol):
    def solve(self, task: Task, env: Environment) -> Trajectory:
        """Attempt to solve task, return trajectory"""
        ...
    
    def step(self, observation: str) -> str:
        """Given observation, return action"""
        ...
    
    def reset(self) -> None:
        """Reset agent state"""
        ...
```

## Design Requirements
- Use `typing.Protocol` with `@runtime_checkable`
- No concrete implementations in this issue
- Document when each method is called

## Acceptance Criteria
- [ ] Protocols defined with full type hints
- [ ] Docstrings explain interface contract
- [ ] Can be used for isinstance() checks

Implements [[s-3aok]]
