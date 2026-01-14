---
id: i-1jmf
title: Implement Environment implementations (PassthroughEnvironment + stubs)
priority: 1
created_at: '2026-01-08 02:11:19'
tags:
  - environment
  - implementation
  - phase-4
status: open
---
# Environment Implementations

Implements [[s-9ma3|Environment Protocol Design]]

## Goal

Create the base environment implementations for Phase 4, including a working PassthroughEnvironment and stub implementations for domain-specific environments.

## Requirements

### 1. Update Environment Protocol

Add `task` property to existing Environment protocol:
```python
@property
def task(self) -> Task:
    """Current task being solved."""
    ...
```

### 2. PassthroughEnvironment

Default environment when no domain-specific verification is needed:
- `reset(task)` → Returns task description
- `verify(solution)` → Always returns success
- Used when agent determines its own success

### 3. Stub Environments

Create placeholder implementations that raise NotImplementedError:
- `ARCEnvironment` - For ARC grid tasks
- `SWEEnvironment` - For software engineering tasks

### 4. Factory Function

```python
def create_environment(task: Task) -> Environment:
    """Create appropriate environment for task domain."""
```

## Files

```
atlas/environments/
├── __init__.py       # Exports + factory
├── base.py           # PassthroughEnvironment  
├── arc.py            # ARCEnvironment stub
└── swe.py            # SWEEnvironment stub
```

## Tests

- PassthroughEnvironment returns task description on reset
- PassthroughEnvironment.verify() returns success
- Factory returns correct environment type
- Stub environments raise NotImplementedError
