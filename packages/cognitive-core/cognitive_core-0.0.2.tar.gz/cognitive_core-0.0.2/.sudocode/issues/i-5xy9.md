---
id: i-5xy9
title: Extract ARC utilities to separate modules
priority: 2
created_at: '2026-01-08 08:52:13'
tags:
  - arc
  - phase-7
  - refactoring
relationships:
  - from_id: i-5xy9
    from_uuid: 5cf8c7fa-7265-4d87-9174-7f42809e2fd0
    from_type: issue
    to_id: s-484m
    to_uuid: c72bef78-a632-4a3f-a410-a7dbab4420be
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 08:59:22'
    metadata: null
status: closed
closed_at: '2026-01-08 08:59:22'
---
# Extract ARC Utilities

Refactor ARCEnvironment to extract utilities into separate modules for better organization.

## Current State

All ARC logic is in `src/atlas/environments/arc.py`:
- Dataset loading (`_load_dataset()`)
- Grid formatting (`_format_grid()`)
- MockARCTask class
- Task finding (`_find_task_by_id()`)

## Target Structure

```
atlas/environments/
├── arc/
│   ├── __init__.py      # Re-exports
│   ├── environment.py   # ARCEnvironment class
│   ├── loader.py        # load_arc_dataset(), find_task_by_id()
│   ├── types.py         # Grid type alias, ARCTask dataclass
│   └── utils.py         # format_grid(), parse_grid_response()
```

## Utilities to Extract

1. **loader.py**:
   - `load_arc_dataset(dataset_name)` - Load arckit dataset
   - `find_task_by_id(task_id, dataset)` - Find task in dataset

2. **types.py**:
   - `Grid = list[list[int]]` type alias
   - `ARCTask` dataclass (or keep using arckit.Task)

3. **utils.py**:
   - `format_grid(grid)` - Format grid for display
   - `format_arc_task(task)` - Format full task for agent prompt
   - `parse_grid_response(response)` - Extract grid from agent text output

## Requirements

- Maintain backward compatibility (imports from `atlas.environments` still work)
- All existing tests must pass
- Add tests for new utility functions
