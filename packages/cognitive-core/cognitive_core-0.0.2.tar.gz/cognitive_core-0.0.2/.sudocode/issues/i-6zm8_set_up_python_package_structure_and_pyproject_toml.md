---
id: i-6zm8
title: Set up Python package structure and pyproject.toml
priority: 0
created_at: '2025-12-18 03:33:24'
tags:
  - infrastructure
  - phase-1
  - setup
status: open
---
Set up the base `atlas` Python package with proper structure and configuration.

## Requirements
- Create `atlas/` package directory with `__init__.py`
- Create `pyproject.toml` with:
  - Required dependencies: `numpy>=1.24`, `pydantic>=2.0`
  - Optional dependency groups: `embeddings`, `vector-stores`, `llm`, `arc`, `swe`, `all`, `dev`
  - Package metadata (name, version, description, etc.)
- Add `py.typed` marker for PEP 561 type checking support
- Create subdirectory structure:
  ```
  atlas/
  ├── __init__.py
  ├── py.typed
  ├── core/
  ├── protocols/
  ├── memory/
  ├── search/
  ├── learning/
  ├── environments/
  ├── llm/
  └── experiments/
  ```

## Acceptance Criteria
- [ ] Package is installable with `pip install -e .`
- [ ] `import atlas` works
- [ ] Type checking marker present

Implements [[s-8fnx]]
