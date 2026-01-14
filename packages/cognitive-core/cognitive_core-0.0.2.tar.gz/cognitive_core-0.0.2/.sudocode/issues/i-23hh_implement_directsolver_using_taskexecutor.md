---
id: i-23hh
title: Implement DirectSolver using TaskExecutor
priority: 1
created_at: '2026-01-08 02:11:53'
tags:
  - direct-solver
  - phase-4
  - search
status: open
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
