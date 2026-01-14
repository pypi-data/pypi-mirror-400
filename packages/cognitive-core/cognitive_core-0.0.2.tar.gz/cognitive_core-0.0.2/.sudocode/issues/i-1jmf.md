---
id: i-1jmf
title: Implement Environment implementations (PassthroughEnvironment + stubs)
priority: 1
created_at: '2026-01-08 02:11:19'
tags:
  - environment
  - implementation
  - phase-4
relationships:
  - from_id: i-1jmf
    from_uuid: 1e47df2f-2372-408b-853a-d36fdb61f85f
    from_type: issue
    to_id: i-23hh
    to_uuid: 8d117871-2c4e-43bf-a21c-546a512c1b6a
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 02:12:17'
    metadata: null
  - from_id: i-1jmf
    from_uuid: 1e47df2f-2372-408b-853a-d36fdb61f85f
    from_type: issue
    to_id: s-9ma3
    to_uuid: 6a5ea1cd-349a-41e5-9be3-c6cad37cc11a
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 02:12:17'
    metadata: null
status: closed
closed_at: '2026-01-08 03:32:45'
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
