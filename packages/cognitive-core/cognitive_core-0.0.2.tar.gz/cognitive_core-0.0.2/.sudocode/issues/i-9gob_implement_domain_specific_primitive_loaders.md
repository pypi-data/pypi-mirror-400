---
id: i-9gob
title: Implement domain-specific primitive loaders
priority: 2
created_at: '2026-01-08 00:04:49'
tags:
  - arc
  - memory
  - phase-3
  - primitives
  - swe
status: open
---
## Overview

Implement primitive loaders for ARC-AGI and Software Engineering domains.

## Scope

### File: `src/atlas/memory/primitives/__init__.py`

Export loaders.

### File: `src/atlas/memory/primitives/arc.py`

```python
class ARCPrimitiveLoader(PrimitiveLoader):
    """Load ARC-AGI grid manipulation primitives."""
    
    def load(self) -> dict[str, CodeConcept]:
        return {
            "get_objects": CodeConcept(
                id="arc_get_objects",
                name="get_objects",
                description="Extract connected components from grid",
                code="def get_objects(grid): ...",
                signature="(grid: np.ndarray) -> list[Object]",
                concept_type="primitive",
                ...
            ),
            "flood_fill": CodeConcept(...),
            "rotate_90": CodeConcept(...),
            "rotate_180": CodeConcept(...),
            "rotate_270": CodeConcept(...),
            "mirror_horizontal": CodeConcept(...),
            "mirror_vertical": CodeConcept(...),
            "get_background_color": CodeConcept(...),
            "get_colors": CodeConcept(...),
            "crop_to_content": CodeConcept(...),
            "scale_grid": CodeConcept(...),
            "tile_pattern": CodeConcept(...),
        }
```

### File: `src/atlas/memory/primitives/swe.py`

```python
class SWEPrimitiveLoader(PrimitiveLoader):
    """Load software engineering primitives."""
    
    def load(self) -> dict[str, CodeConcept]:
        return {
            "read_file": CodeConcept(
                id="swe_read_file",
                name="read_file",
                description="Read contents of a file",
                code="def read_file(path): ...",
                signature="(path: str) -> str",
                concept_type="primitive",
                ...
            ),
            "write_file": CodeConcept(...),
            "search_codebase": CodeConcept(...),
            "find_definition": CodeConcept(...),
            "find_references": CodeConcept(...),
            "run_tests": CodeConcept(...),
            "apply_patch": CodeConcept(...),
            "git_diff": CodeConcept(...),
        }
```

## Notes

- Primitives are placeholder implementations for now
- Real implementations will be added when domains are integrated
- Focus on defining the interface and structure
- Each primitive should have meaningful description for embedding search

## Testing

- Test loaders return valid CodeConcept dicts
- Test all required fields are populated
- Test primitives have unique IDs

## Dependencies

- [[i-6orq]] Strategy protocols (PrimitiveLoader)
- Core types (CodeConcept)

## Acceptance Criteria

- [ ] ARCPrimitiveLoader implements PrimitiveLoader protocol
- [ ] SWEPrimitiveLoader implements PrimitiveLoader protocol
- [ ] All primitives have valid CodeConcept structure
- [ ] Primitives have meaningful descriptions for search
- [ ] Unit tests pass
