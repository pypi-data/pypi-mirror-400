---
id: s-484m
title: 'Phase 7: Environments & Domains'
priority: 3
created_at: '2026-01-06 02:20:04'
parent_id: s-5o87
tags:
  - arc
  - environments
  - phase-7
  - sandbox
  - swe
  - verification
---
# Phase 7: Environments & Domains

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Domain-specific environments for task verification and optional sandboxed execution. Since agents are managed via ACP (see [[s-7xs8|Phase 2]]), this phase focuses on:
1. **Verification**: Checking if solutions are correct
2. **Sandboxing**: Optional controlled execution for untrusted contexts
3. **Domain primitives**: Task loaders, formatters, and domain-specific utilities

## Environment Protocol

Environments provide verification and optional sandbox control:

```python
class Environment(Protocol):
    """Environment for task verification with optional sandboxing."""
    
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a candidate solution against task requirements."""
        ...
    
    def get_sandbox_handlers(self) -> ClientHandlers | None:
        """Optional: Return handlers for sandboxed execution.
        
        Returns:
            None: Agent runs freely (default)
            ClientHandlers: Agent runs in sandbox with controlled access
        """
        return None
    
    @property
    def supports_partial_scoring(self) -> bool:
        """Whether this environment supports partial scores."""
        ...
```

## ARC Environment

Environment for ARC-AGI grid puzzle tasks.

### Verification

```python
class ARCEnvironment:
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """
        Verify grid solution.
        
        - Exact match: success=True, partial_score=1.0
        - Partial match: success=False, partial_score=matching_cells/total_cells
        - Wrong dimensions: success=False, partial_score=0.0
        """
```

### Task Format

```python
@dataclass
class ARCTask:
    task_id: str
    train_examples: list[tuple[Grid, Grid]]  # (input, output) pairs
    test_input: Grid
    test_output: Grid  # Hidden during solving
```

### Sandbox (Optional)

ARC tasks typically don't need sandboxing since they're pure computation:

```python
def get_sandbox_handlers(self) -> ClientHandlers | None:
    return None  # No sandbox needed for ARC
```

### Utilities

- `load_arc_dataset(path)` - Load ARC tasks from JSON
- `format_arc_task(task)` - Format task for agent prompt
- `parse_grid_response(response)` - Extract grid from agent output

## SWE Environment

Environment for software engineering tasks (SWE-bench style).

### Verification

```python
class SWEEnvironment:
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """
        Verify code solution by running tests.
        
        - All tests pass: success=True, partial_score=1.0
        - Some tests pass: success=False, partial_score=passing/total
        - Build fails: success=False, partial_score=0.0
        """
```

### Task Format

```python
@dataclass
class SWETask:
    task_id: str
    repo_url: str
    base_commit: str
    issue_description: str
    test_command: str
    setup_commands: list[str]
```

### Sandbox (Required)

SWE tasks run in Docker sandbox for safety:

```python
class SWEEnvironment:
    def __init__(self, docker_image: str = "python:3.11"):
        self._docker = DockerSandbox(docker_image)
    
    def get_sandbox_handlers(self) -> ClientHandlers:
        """Return Docker-backed handlers."""
        return ClientHandlers(
            on_file_read=self._docker.read_file,
            on_file_write=self._docker.write_file,
            on_terminal_create=self._docker.create_terminal,
            on_terminal_output=self._docker.get_output,
            on_terminal_kill=self._docker.kill_terminal,
            on_terminal_release=self._docker.release_terminal,
            on_terminal_wait_for_exit=self._docker.wait_for_exit,
        )
```

### Docker Sandbox

```python
class DockerSandbox:
    """Isolated execution environment using Docker."""
    
    def __init__(self, image: str, timeout: int = 300):
        ...
    
    async def setup(self, task: SWETask) -> None:
        """Clone repo, checkout commit, run setup commands."""
        ...
    
    async def run_tests(self, test_command: str) -> TestResult:
        """Execute test command and parse results."""
        ...
    
    async def cleanup(self) -> None:
        """Remove container and temporary files."""
        ...
```

## Generic Environment

Base environment for custom domains.

```python
class GenericEnvironment:
    """Flexible environment for custom task types."""
    
    def __init__(
        self,
        verifier: Callable[[Task, Candidate], Outcome],
        sandbox_handlers: ClientHandlers | None = None,
    ):
        self._verifier = verifier
        self._sandbox_handlers = sandbox_handlers
    
    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        return self._verifier(task, candidate)
    
    def get_sandbox_handlers(self) -> ClientHandlers | None:
        return self._sandbox_handlers
```

## Domain Registry

Register environments for different task domains:

```python
class DomainRegistry:
    """Registry for domain-specific environments."""
    
    _environments: dict[str, type[Environment]] = {}
    
    @classmethod
    def register(cls, domain: str, env_class: type[Environment]) -> None:
        cls._environments[domain] = env_class
    
    @classmethod
    def get(cls, domain: str) -> type[Environment]:
        return cls._environments[domain]
    
    @classmethod
    def create(cls, domain: str, **kwargs) -> Environment:
        return cls._environments[domain](**kwargs)

# Register built-in domains
DomainRegistry.register("arc", ARCEnvironment)
DomainRegistry.register("swe", SWEEnvironment)
```

## Agent Note

**Agents are NOT part of this phase.** Agent management is handled via ACP (`acp-factory`) in Phase 2:

- `AgentFactory.spawn("claude-code")` - Spawn Claude Code
- `AgentFactory.spawn("codex")` - Spawn Codex
- `AgentFactory.spawn("gemini")` - Spawn Gemini
- `AgentFactory.spawn("opencode")` - Spawn OpenCode

ATLAS's `TaskExecutor` wraps ACP sessions - no additional agent implementations needed.

## Dependencies

- Phase 2: TaskExecutor, ACP integration
- External: Docker (for SWE sandbox)

## File Structure

```
atlas/environments/
├── __init__.py
├── base.py            # Environment protocol, GenericEnvironment
├── registry.py        # DomainRegistry
├── arc/
│   ├── __init__.py
│   ├── environment.py # ARCEnvironment
│   ├── loader.py      # Dataset loading
│   └── types.py       # Grid, ARCTask
└── swe/
    ├── __init__.py
    ├── environment.py # SWEEnvironment
    ├── sandbox.py     # DockerSandbox
    └── types.py       # SWETask, TestResult
```

## Success Criteria

- [ ] ARCEnvironment loads tasks and verifies grid solutions
- [ ] ARCEnvironment supports partial scoring (cell-by-cell)
- [ ] SWEEnvironment runs tests in Docker sandbox
- [ ] SWEEnvironment supports partial scoring (test pass rate)
- [ ] Sandbox handlers integrate with ACP sessions
- [ ] DomainRegistry allows custom environment registration
- [ ] GenericEnvironment enables rapid domain prototyping
