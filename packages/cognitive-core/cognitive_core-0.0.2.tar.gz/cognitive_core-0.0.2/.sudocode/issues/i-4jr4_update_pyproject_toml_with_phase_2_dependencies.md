---
id: i-4jr4
title: Update pyproject.toml with Phase 2 dependencies
priority: 0
created_at: '2026-01-07 08:55:55'
tags:
  - dependencies
  - phase-2
  - setup
status: open
---
# Update pyproject.toml with Phase 2 dependencies

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Add all Phase 2 dependencies to pyproject.toml.

## Dependencies to Add

### Core dependencies
```toml
dependencies = [
    "numpy>=1.24.0",
    "pydantic>=2.0.0",
]
```

### Optional dependency groups

```toml
[project.optional-dependencies]
embeddings = [
    "sentence-transformers>=2.2.0",
    "torch>=2.0.0",
]

vector = [
    "chromadb>=0.4.0",
]

mcp = [
    "fastmcp>=0.1.0",
]

acp = [
    # acp-factory is a git submodule, may need special handling
]

# All Phase 2 deps
phase2 = [
    "atlas[embeddings,vector,mcp]",
]

# Development
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

## Notes

- `acp-factory` is in `references/acp-factory/python` as git submodule
- May need to add as editable install or path dependency
- Consider if torch should be optional (heavy dependency)

## Acceptance Criteria

- [ ] All Phase 2 deps added to pyproject.toml
- [ ] Optional groups work (`pip install -e ".[phase2]"`)
- [ ] Dev dependencies for testing
- [ ] `pip install -e .` still works (core only)
- [ ] Document installation in README or spec
