---
id: i-23hh
title: Implement DirectSolver using TaskExecutor
priority: 1
created_at: '2026-01-08 02:11:53'
tags:
  - direct-solver
  - phase-4
  - search
relationships:
  - from_id: i-23hh
    from_uuid: 8d117871-2c4e-43bf-a21c-546a512c1b6a
    from_type: issue
    to_id: i-3rat
    to_uuid: a62c70bd-3941-470a-9d1d-f8aebda4aed2
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 02:12:17'
    metadata: null
  - from_id: i-23hh
    from_uuid: 8d117871-2c4e-43bf-a21c-546a512c1b6a
    from_type: issue
    to_id: s-2uov
    to_uuid: 41a04d9a-72a2-4d8e-b250-24827e8c3f7e
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 02:12:17'
    metadata: null
status: closed
closed_at: '2026-01-08 03:40:10'
---
# DirectSolver Implementation

Implements [[s-2uov|Phase 4: Minimal Solver]] DirectSolver requirements.

## Goal

Create DirectSolver that retrieves similar experiences from memory, adapts solutions using TaskExecutor with an ACP agent, and verifies results.

## Requirements

### 1. Core Algorithm

Per user decision: use TaskExecutor with agent for solving.

```python
class DirectSolver(SearchEngine):
    def __init__(
        self,
        memory: MemorySystem,
        executor: TaskExecutor,
        llm: SimpleLLM,  # For adaptation prompts
    ):
        ...
    
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """
        1. Query memory for similar experiences (use routing.context if provided)
        2. For each experience (by similarity):
           a. Create adaptation prompt
           b. If empty memory: fall back to normal TaskExecutor execution
           c. Adapt solution using TaskExecutor
           d. Verify via env.verify()
           e. If success, return candidate
        3. Return best partial result(s)
        """
        ...
```

### 2. Empty Memory Fallback

Per user decision: fall back to normal TaskExecutor execution when memory is empty.

```python
if not experiences:
    # No similar experiences - pure generation
    trajectory = self.executor.execute(task, env)
    return [Candidate(
        solution=trajectory.steps[-1].observation if trajectory.steps else "",
        trajectory=trajectory,
        fitness=trajectory.outcome.partial_score,
    )]
```

### 3. Solution Adaptation

Use SimpleLLM to adapt retrieved solutions:
```python
adaptation_prompt = f"""
Given a similar solved task:
Task: {experience.task_input}
Solution: {experience.solution_output}

Adapt this solution for the new task:
Task: {task.description}

Return the adapted solution:
"""
```

### 4. SearchEngine Protocol

Implement required methods:
- `search()` - Main solve logic
- `refine()` - Re-run with feedback (optional, can delegate to search)
- `name` property - "direct"

## Files

```
atlas/search/
├── __init__.py
├── direct.py         # DirectSolver
└── verifier.py       # (from previous issue)
```

## Tests

- DirectSolver retrieves from memory
- Empty memory falls back to generation
- Verification loop works
- Returns best partial on all failures
