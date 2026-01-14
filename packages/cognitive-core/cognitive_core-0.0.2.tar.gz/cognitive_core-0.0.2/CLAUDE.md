# CLAUDE.md

This file provides context for Claude Code agents working on the Cognitive Core codebase.

## Project Overview

Cognitive Core (internally "ATLAS" - Adaptive Trajectory Learning and Abstraction System) is a meta-learning framework that learns from agent trajectories. It extracts reusable patterns and strategies from successful/failed task attempts to improve future performance.

**Package names:**
- PyPI: `cognitive-core`
- npm: `cognitive-core`
- Python import: `from cognitive_core import ...`

**Target domains**: ARC-AGI puzzles, Software Engineering tasks (SWE-bench style)

## Architecture

Three pillars, three primitives:

```
Primitives:
- Trajectory: Task + Steps + Outcome (immutable after creation)
- Environment: Execution context (reset/step/verify interface)
- Agent: Produces trajectories by interacting with environments

Pillars:
1. Memory (what to remember): ExperienceMemory, ConceptLibrary, StrategyBank
2. Search (how to solve): TaskRouter, DirectSolver, MindEvolution, MCTS
3. Learning (how to improve): TrajectoryAnalyzer, AbstractionExtractor, HindsightLearner
```

## Key Directories

```
meta-learning-engine/
├── src/cognitive_core/    # Python package source
│   ├── core/              # Task, Trajectory, Outcome, Step types
│   ├── protocols/         # Protocol definitions (interfaces)
│   ├── environments/      # ARCEnvironment, SWEEnvironment, PassthroughEnvironment
│   ├── memory/            # Three memory systems + unified MemorySystem
│   ├── search/            # Router, solvers, verifiers
│   ├── learning/          # Analysis, extraction, hindsight learning
│   ├── embeddings/        # BGE embedding model wrapper
│   ├── vector/            # ChromaDB vector store wrapper
│   ├── llm/               # LLM adapters (SimpleLLM using litellm)
│   └── cli.py             # CLI for TypeScript subprocess communication
├── ts/                    # TypeScript subprocess wrapper
│   ├── src/
│   │   ├── index.ts       # High-level CognitiveCore API
│   │   ├── client.ts      # Python subprocess manager
│   │   └── types.ts       # TypeScript interfaces
│   └── package.json
└── tests/                 # Python tests
```

## Conventions

### Protocols over ABCs
We use `typing.Protocol` with `@runtime_checkable` instead of ABCs. This enables structural subtyping - classes don't need to explicitly inherit from protocols.

```python
# Good - in protocols/
@runtime_checkable
class Environment(Protocol):
    def reset(self, task: Task) -> str: ...
    def verify(self, solution: Any) -> Outcome: ...

# Good - implementation doesn't need to inherit
class ARCEnvironment:  # No inheritance needed
    def reset(self, task: Task) -> str: ...
    def verify(self, solution: Any) -> Outcome: ...
```

### Type Hints
All code uses type hints. Use `from __future__ import annotations` for forward references.

### Dataclasses
Core types use `@dataclass` with explicit field definitions. See `core/types.py` for Task, Trajectory, Outcome, Step, etc.

### Optional Dependencies
Features with heavy dependencies are optional:
- `arckit` for ARC dataset loading
- `docker` for SWE environment
- `chromadb` for vector storage
- `sentence-transformers` for embeddings
- `litellm` for LLM calls

Code should gracefully degrade when optional deps aren't installed:
```python
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_arc_environment.py

# Run with coverage
pytest --cov=cognitive_core

# Run tests matching pattern
pytest -k "test_verify"
```

**Test structure**: Tests mirror source structure in `tests/unit/`. Each module has corresponding test file.

**Test conventions**:
- Use `pytest` fixtures for setup
- Group related tests in classes (`TestARCEnvironmentVerify`)
- Mock external dependencies (LLM calls, Docker, etc.)
- Tests should be fast - mock I/O and network calls

## TypeScript Package

The `ts/` directory contains a TypeScript wrapper that communicates with Python via subprocess:

```bash
cd ts
npm install
npm run build    # Build with tsup
npm test         # Run tests with vitest
```

The TypeScript client spawns `python -m cognitive_core.cli --json` and communicates via JSON over stdin/stdout.

## Common Tasks

### Adding a new Environment

1. Create class implementing the Environment protocol methods:
   - `reset(task: Task) -> str`
   - `step(action: str) -> tuple[str, float, bool, dict]`
   - `verify(solution: Any) -> Outcome`
   - Properties: `max_steps`, `is_deterministic`, `task`

2. Add to `environments/__init__.py` exports

3. Update `create_environment()` factory if domain-specific

4. Add tests in `tests/unit/test_<name>_environment.py`

### Adding CLI Commands

The CLI (`cli.py`) handles subprocess communication. Add new commands in `handle_command()`:

```python
def handle_command(command: str, args: dict) -> dict:
    if command == "my.command":
        return {"success": True, "result": {...}}
```

Then add corresponding TypeScript methods in `ts/src/index.ts`.

### Working with ARC

ARC utilities are in `environments/arc/`:
- `types.py`: `Grid` type alias, `ARCTask` dataclass
- `loader.py`: `load_arc_dataset()`, `find_task_by_id()`
- `utils.py`: `format_grid()`, `parse_grid_response()`, `verify_grid()`
- `environment.py`: `ARCEnvironment` class

`ARCTask.from_dict()` accepts both formats:
```python
# Tuple format
{"train": [([[0,1]], [[1,0]])], "test": [...]}

# JSON format
{"train": [{"input": [[0,1]], "output": [[1,0]]}], "test": [...]}
```

## Specs and Issues

This project uses sudocode for spec-driven development. Specs live in `.sudocode/specs/`, issues in `.sudocode/issues/`.

## Key Files

- `src/cognitive_core/core/types.py` - All core dataclasses (Task, Trajectory, Outcome, etc.)
- `src/cognitive_core/protocols/` - All protocol definitions
- `src/cognitive_core/environments/__init__.py` - `create_environment()` factory
- `src/cognitive_core/memory/system.py` - Unified `MemorySystem`
- `src/cognitive_core/search/router.py` - `TaskRouter` for search strategy selection
- `src/cognitive_core/learning/pipeline.py` - `LearningPipeline` orchestrator
- `src/cognitive_core/cli.py` - CLI for TypeScript subprocess wrapper

## Publishing

### PyPI

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

### npm

```bash
cd ts
npm run build
npm publish
```

## Gotchas

1. **ARCEnvironment returns numpy arrays** for `training_pairs` and `test_inputs` properties (for backward compatibility), but internally uses plain Python lists.

2. **SWEEnvironment has mock mode** - gracefully degrades when Docker isn't available. Check `docker_available` property.

3. **Embeddings are lazy-loaded** - BGE model downloads on first use (~400MB).

4. **ChromaDB creates persistent storage** - Default path is `.chroma/`. Use `persist_directory` param to customize.

5. **LLM calls use litellm** - Supports OpenAI, Anthropic, etc. Set appropriate env vars (OPENAI_API_KEY, ANTHROPIC_API_KEY).

6. **TypeScript client requires Python** - The npm package spawns a Python subprocess, so `cognitive-core` Python package must be installed.

## Development Workflow

1. Check `ready` issues in sudocode
2. Read the spec for context
3. Implement with tests
4. Run `pytest` to verify
5. Add feedback to spec when closing issue
6. Update docs if needed (README.md, this file)
