---
id: i-7u8s
title: Implement basic Verifier (minimum methods)
priority: 1
created_at: '2026-01-08 02:11:19'
tags:
  - phase-4
  - search
  - verifier
status: open
---
# Basic Verifier Implementation

Implements [[s-2uov|Phase 4: Minimal Solver]] Verifier requirements.

## Goal

Create minimal Verifier implementations with only the required methods. Per user decision: only require minimum for verifiers.

## Requirements

### 1. Simplified Verifier Protocol

The existing Verifier protocol has `verify`, `rank`, `batch_verify`, and `supports_partial_scoring`. For Phase 4, only implement:

```python
class SimpleVerifier:
    """Basic verifier using environment verification."""
    
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify using task's verification spec."""
        ...
    
    @property
    def supports_partial_scoring(self) -> bool:
        return True  # or False based on implementation
```

### 2. Implementations

**SimpleVerifier** - Delegates to Environment.verify():
```python
class SimpleVerifier:
    def __init__(self, env: Environment):
        self._env = env
    
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        return self._env.verify(candidate.solution)
```

**ExactMatchVerifier** - String/value equality:
```python
class ExactMatchVerifier:
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        expected = task.verification.expected
        return Outcome(
            success=candidate.solution == expected,
            partial_score=1.0 if success else 0.0,
        )
```

### 3. Optional Methods

`rank()` and `batch_verify()` can have default implementations:
- `rank()` → Returns candidates unchanged (no ranking)
- `batch_verify()` → Calls verify() in loop

## Files

```
atlas/search/
├── __init__.py
└── verifier.py       # Verifier implementations
```

## Tests

- SimpleVerifier delegates to environment
- ExactMatchVerifier checks equality
- Partial scoring works correctly
- Default methods work
