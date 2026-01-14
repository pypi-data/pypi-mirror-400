---
id: s-2uov
title: 'Phase 4: Minimal Solver'
priority: 1
created_at: '2026-01-06 02:20:04'
parent_id: s-5o87
tags:
  - direct
  - end-to-end
  - minimal
  - phase-4
  - solver
relationships:
  - from_id: s-2uov
    from_uuid: 41a04d9a-72a2-4d8e-b250-24827e8c3f7e
    from_type: spec
    to_id: s-7h2g
    to_uuid: d4747f7d-ae45-4696-ac9e-f5c75d4c05e8
    to_type: spec
    relationship_type: depends-on
    created_at: '2026-01-06 02:20:21'
    metadata: null
---
# Phase 4: Minimal Solver

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Get a minimal end-to-end system running. Focus on the simplest path: DirectSolver with basic routing and verification.

## Goal

Solve simple tasks using memory retrieval without complex search algorithms. This validates the core loop before adding Mind Evolution or MCTS.

## Components

### DirectSolver
Simplest search strategy: retrieve → adapt → verify.

**Scope:**
- Retrieve most similar experience from memory
- Adapt solution to current task via LLM
- Verify against task criteria
- Fall back to next similar if verification fails

**Cost:** ~1-5 LLM calls per task

**Algorithm:**
```
1. Query memory for similar experiences
2. For each experience (by similarity):
   a. Adapt solution to current task
   b. Verify adapted solution
   c. If success, return
3. If all fail, return best partial result
```

### TaskRouter (Basic)
Minimal routing logic to select search strategy.

**Scope:**
- Query memory for similar experiences
- Estimate task difficulty
- Select between direct/evolutionary/mcts
- Initially: always route to DirectSolver

**Routing Logic (v1):**
- If similarity > 0.8 and previous success → `direct`
- Else → `direct` (expand later)

### Verifier (Basic)
Simple verification for initial testing.

**Scope:**
- Exact match verification
- Partial scoring (for ranking)
- Domain-agnostic interface

**Implementations:**
- `SimpleVerifier`: String/value equality
- `FunctionVerifier`: Execute and compare output

## Integration

### ATLASSolver
Top-level orchestrator combining all components.

```python
class ATLASSolver:
    def __init__(
        self,
        memory: MemorySystem,
        llm: LLM,
        search: SearchEngine = None,  # defaults to DirectSolver
    ):
        pass
    
    def solve(self, task: Task, env: Environment) -> Trajectory:
        routing = self.router.route(task, self.memory)
        candidates = self.search.search(task, routing, env)
        best = self.select_best(candidates)
        return self.build_trajectory(task, best)
```

## Dependencies

- Phase 2: LLM, Embeddings
- Phase 3: MemorySystem

## File Structure

```
atlas/search/
├── __init__.py
├── router.py          # TaskRouter implementation
├── direct.py          # DirectSolver implementation
└── verifier.py        # Verifier implementations

atlas/
└── solver.py          # ATLASSolver orchestrator
```

## Success Criteria

- [ ] DirectSolver retrieves and adapts solutions
- [ ] TaskRouter makes basic routing decisions
- [ ] Verifier validates solutions
- [ ] End-to-end: task in → trajectory out
- [ ] Works with empty memory (fallback to generation)
- [ ] Works with populated memory (retrieval-augmented)
