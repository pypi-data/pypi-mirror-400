---
id: i-3rat
title: Implement ATLASSolver orchestrator
priority: 1
created_at: '2026-01-08 02:11:54'
tags:
  - orchestrator
  - phase-4
  - solver
status: open
---
# ATLASSolver Implementation

Implements [[s-2uov|Phase 4: Minimal Solver]] ATLASSolver requirements.

## Goal

Create the top-level orchestrator that combines memory, routing, search, and verification into a complete solving pipeline.

## Requirements

### 1. Core Class

```python
class ATLASSolver:
    """Top-level solver combining all ATLAS components."""
    
    def __init__(
        self,
        memory: MemorySystem,
        executor: TaskExecutor,
        llm: SimpleLLM | None = None,
        router: TaskRouter | None = None,
        search: SearchEngine | None = None,
    ):
        self._memory = memory
        self._executor = executor
        self._llm = llm or SimpleLLM()
        self._router = router or BasicTaskRouter(memory)
        self._search = search or DirectSolver(memory, executor, self._llm)
    
    def solve(self, task: Task, env: Environment | None = None) -> Trajectory:
        """
        1. Route task to determine strategy
        2. Search for candidates
        3. Select best candidate
        4. Build and return trajectory
        """
        ...
```

### 2. Solve Pipeline

```python
def solve(self, task: Task, env: Environment | None = None) -> Trajectory:
    # Use passthrough environment if none provided
    if env is None:
        env = PassthroughEnvironment()
    env.reset(task)
    
    # Route to determine strategy
    routing = self._router.route(task, self._memory)
    
    # Search for candidates
    candidates = self._search.search(task, routing, env)
    
    # Select best
    best = self._select_best(candidates)
    
    # Store trajectory in memory
    trajectory = best.trajectory
    self._memory.store(trajectory)
    
    return trajectory
```

### 3. Selection Logic

```python
def _select_best(self, candidates: list[Candidate]) -> Candidate:
    """Select best candidate by fitness/success."""
    if not candidates:
        raise ValueError("No candidates generated")
    
    # Prefer successful candidates
    successful = [c for c in candidates if c.trajectory.outcome.success]
    if successful:
        return max(successful, key=lambda c: c.fitness or 0)
    
    # Otherwise, best partial
    return max(candidates, key=lambda c: c.fitness or 0)
```

### 4. Convenience Methods

```python
def solve_batch(
    self,
    tasks: list[Task],
    envs: list[Environment] | None = None,
) -> list[Trajectory]:
    """Solve multiple tasks."""
    ...

@classmethod
def create_default(cls, memory: MemorySystem | None = None) -> "ATLASSolver":
    """Create solver with default configuration."""
    ...
```

## Files

```
atlas/
├── solver.py         # ATLASSolver
└── search/
    ├── __init__.py
    ├── router.py
    ├── direct.py
    └── verifier.py
```

## Tests

- End-to-end: task in → trajectory out
- Works with empty memory
- Works with populated memory
- Stores results in memory
- Selects best candidate correctly
