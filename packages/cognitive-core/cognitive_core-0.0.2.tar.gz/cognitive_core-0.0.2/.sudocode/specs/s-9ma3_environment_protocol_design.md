---
id: s-9ma3
title: Environment Protocol Design
priority: 1
created_at: '2026-01-08 02:10:45'
parent_id: s-2uov
tags:
  - environment
  - protocol
  - phase-4
  - design
---
# Environment Protocol Design

Parent: [[s-2uov|Phase 4: Minimal Solver]]

## Overview

Generic interface for task execution environments. Supports different domains (ARC, SWE, custom) through a Gymnasium-like API with built-in verification.

## Design Principles

1. **Minimal Core**: Only `reset()` and `verify()` are required for Phase 4
2. **Progressive Enhancement**: Full step-by-step interface optional
3. **Domain Agnostic**: Same interface works for ARC grids, SWE code, etc.
4. **Verification Built-in**: Enables inference-time scaling via best-of-k

## Protocol Tiers

### Tier 1: Minimal Environment (Phase 4)

Required for DirectSolver integration:

```python
@runtime_checkable
class MinimalEnvironment(Protocol):
    """Minimum environment for verification-based solving."""
    
    def reset(self, task: Task) -> str:
        """Initialize environment with task, return initial observation."""
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Verify a candidate solution against task criteria."""
        ...
    
    @property
    def task(self) -> Task:
        """Current task being solved."""
        ...
```

### Tier 2: Interactive Environment (Future Phases)

For step-by-step search algorithms (MCTS, Mind Evolution):

```python
@runtime_checkable  
class InteractiveEnvironment(MinimalEnvironment, Protocol):
    """Full interactive environment for search algorithms."""
    
    def step(self, action: str) -> tuple[str, float, bool, dict[str, Any]]:
        """Execute action, return (observation, reward, done, info)."""
        ...
    
    @property
    def max_steps(self) -> int:
        """Maximum steps before timeout."""
        ...
    
    @property
    def is_deterministic(self) -> bool:
        """Whether environment is reproducible."""
        ...
    
    def get_state(self) -> dict[str, Any]:
        """Serialize current state for checkpointing."""
        ...
    
    def set_state(self, state: dict[str, Any]) -> None:
        """Restore from serialized state."""
        ...
```

## Domain Implementations

### PassthroughEnvironment (Default)

For tasks without explicit verification (agent decides success):

```python
class PassthroughEnvironment(MinimalEnvironment):
    def reset(self, task: Task) -> str:
        return task.description
    
    def verify(self, solution: Any) -> Outcome:
        # Always succeed - verification delegated to agent
        return Outcome(success=True, partial_score=1.0)
```

### ARCEnvironment (Stub)

```python
class ARCEnvironment(MinimalEnvironment):
    def verify(self, solution: Any) -> Outcome:
        # Compare solution grid to expected output
        # Return Outcome with exact_match success and partial_score
        raise NotImplementedError("ARC environment not yet implemented")
```

### SWEEnvironment (Stub)

```python
class SWEEnvironment(MinimalEnvironment):
    def verify(self, solution: Any) -> Outcome:
        # Execute test suite
        raise NotImplementedError("SWE environment not yet implemented")
```

## Factory Pattern

```python
def create_environment(task: Task) -> MinimalEnvironment:
    """Create appropriate environment for task domain."""
    if task.domain == "arc":
        return ARCEnvironment()
    elif task.domain == "swe":
        return SWEEnvironment()
    else:
        return PassthroughEnvironment()
```

## Integration with DirectSolver

DirectSolver uses environment for verification only:

```python
class DirectSolver:
    def solve(self, task: Task, env: MinimalEnvironment) -> Candidate:
        # 1. Query memory for similar experiences
        # 2. For each experience:
        #    a. Adapt solution using TaskExecutor
        #    b. outcome = env.verify(adapted_solution)
        #    c. If success, return
        # 3. Return best partial result
```

## File Structure

```
atlas/environments/
├── __init__.py
├── base.py           # Base classes and PassthroughEnvironment
├── arc.py            # ARCEnvironment (stub)
└── swe.py            # SWEEnvironment (stub)
```

## Phase 4 Scope

- [ ] Update Environment protocol with MinimalEnvironment tier
- [ ] Implement PassthroughEnvironment (default)
- [ ] Create stub implementations for ARC/SWE
- [ ] Add create_environment factory
- [ ] Export from atlas.environments
