---
id: s-7xs8
title: 'Phase 2: Infrastructure Layer'
priority: 0
created_at: '2026-01-06 02:20:03'
parent_id: s-5o87
tags:
  - acp
  - async
  - embeddings
  - fastmcp
  - infrastructure
  - mcp
  - phase-2
  - vector-store
---
# Phase 2: Infrastructure Layer

Parent: [[s-5o87|ATLAS System Architecture]]

## Overview

Foundation infrastructure needed by all three pillars. This phase establishes the agent execution layer (via ACP), memory access infrastructure, and vector storage.

**Key Design Decision**: ATLAS uses the Agent Client Protocol (ACP) via `acp-factory` as the primary agent abstraction. This means:
- No raw LLM wrapper needed - agents handle LLM interactions
- All cognitive tasks (including internal ATLAS operations) go through agents
- ATLAS focuses on orchestration, memory, and learning - not agent internals

## Configuration

Centralized dataclass-based configuration with sensible defaults:

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ExecutorConfig:
    """TaskExecutor configuration."""
    agent_type: str = "claude-code"
    reuse_sessions: bool = False  # Default: new session per task
    timeout_seconds: int = 300
    permission_mode: str = "auto-approve"

@dataclass
class MemoryConfig:
    """Memory context limits for prompts."""
    max_experiences: int = 4      # From ReMem paper
    max_strategies: int = 3
    max_concepts: int = 5
    max_context_tokens: int = 4000

@dataclass
class EmbeddingConfig:
    """Embedding provider configuration."""
    model_name: str = "BAAI/bge-base-en-v1.5"
    device: str = "cpu"           # "cpu", "cuda", "mps"
    cache_enabled: bool = True    # In-memory cache

@dataclass
class StorageConfig:
    """Storage and persistence configuration."""
    base_path: Path = field(default_factory=lambda: Path(".atlas"))
    chroma_collection_prefix: str = ""
    distance_metric: str = "cosine"

@dataclass
class ATLASConfig:
    """Root configuration for ATLAS."""
    executor: ExecutorConfig = field(default_factory=ExecutorConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
```

## Components

### TaskExecutor (ACP Integration)

Bridges ACP sessions and ATLAS's task/trajectory model. **Fully async API.**

**Responsibilities:**
- Spawn and manage ACP agent sessions
- Convert SessionUpdates → Trajectory Steps
- Integrate memory context (upfront + MCP tools)
- Coordinate with Environment for verification
- Support session forking for search strategies

**Interface:**

```python
class TaskExecutor:
    """Executes tasks via ACP agents, produces Trajectories."""
    
    def __init__(
        self,
        config: ExecutorConfig = None,
        memory: MemorySystem | None = None,
    ):
        self._config = config or ExecutorConfig()
        self._memory = memory
        self._agent_handle: AgentHandle | None = None
    
    async def execute(
        self,
        task: Task,
        env: Environment,
    ) -> Trajectory:
        """
        Execute a task and return complete trajectory.
        
        1. Query memory for initial context
        2. Format structured prompt with task + context
        3. Create ACP session with Memory MCP server
        4. Run session, collect Steps from updates
        5. Get solution from environment state
        6. Verify result via Environment
        7. Return Trajectory with Outcome
        """
        ...
    
    async def execute_with_session(
        self,
        task: Task,
        env: Environment,
        session: Session,
    ) -> Trajectory:
        """Execute using existing session (for forking/branching)."""
        ...
    
    async def close(self) -> None:
        """Clean up agent handle."""
        ...
```

**Session Management:**

| Mode | Config | Behavior |
|------|--------|----------|
| Fresh (default) | `reuse_sessions=False` | New session per task, clean isolation |
| Reuse | `reuse_sessions=True` | Persistent agent, new session per task |

### TrajectoryBuilder

Converts ACP SessionUpdates into ATLAS Steps using **tool-centric mapping**.

**Mapping Rules:**

| ACP Update | ATLAS Step Component |
|------------|---------------------|
| `agent_message_chunk` (before tool) | `step.thought` |
| `tool_call` | `step.action` (tool name + args) |
| `tool_call_update` (completed) | `step.observation` (tool result) |
| `agent_message_chunk` (after tool) | Next step's `thought` |

**Implementation:**

```python
class TrajectoryBuilder:
    """Builds Trajectory from ACP session updates."""
    
    def __init__(self, task: Task, agent_id: str):
        self._task = task
        self._agent_id = agent_id
        self._steps: list[Step] = []
        self._current_thought: list[str] = []
        self._current_tool_call: dict | None = None
    
    def process_update(self, update: ExtendedSessionUpdate) -> None:
        """Process a single session update."""
        match update.get("session_update"):
            case "agent_message_chunk":
                self._handle_message_chunk(update)
            case "tool_call":
                self._handle_tool_call(update)
            case "tool_call_update":
                self._handle_tool_update(update)
    
    def build(self, outcome: Outcome) -> Trajectory:
        """Finalize and return the trajectory."""
        return Trajectory(
            task=self._task,
            steps=self._steps,
            outcome=outcome,
            metadata={"agent_id": self._agent_id, "timestamp": datetime.now()},
        )
```

### Memory MCP Server (FastMCP)

Exposes ATLAS memory as MCP tools for agent mid-execution access.

**Implementation with FastMCP:**

```python
from fastmcp import FastMCP

mcp = FastMCP("atlas-memory")

@mcp.tool()
def memory_search_experiences(query: str, k: int = 4) -> list[dict]:
    """Search for similar past experiences.
    
    Args:
        query: Natural language description of what you're looking for
        k: Number of results to return (default: 4)
    
    Returns:
        List of relevant experiences with task, solution, and outcome
    """
    return memory.experience_memory.search(query, k=k)

@mcp.tool()
def memory_search_concepts(query: str, k: int = 5) -> list[dict]:
    """Search for relevant code patterns and concepts.
    
    Args:
        query: Description of the pattern or functionality needed
        k: Number of results to return (default: 5)
    
    Returns:
        List of code concepts with name, description, and code
    """
    return memory.concept_library.search(query, k=k)

@mcp.tool()
def memory_search_strategies(query: str, k: int = 3) -> list[dict]:
    """Search for applicable high-level strategies.
    
    Args:
        query: Description of the problem or situation
        k: Number of results to return (default: 3)
    
    Returns:
        List of strategies with situation and suggestion
    """
    return memory.strategy_bank.read(query, k=k)

@mcp.tool()
def memory_get_concept(concept_id: str) -> dict | None:
    """Get a specific code concept by ID.
    
    Args:
        concept_id: The concept identifier
    
    Returns:
        Full concept details or None if not found
    """
    return memory.concept_library.get(concept_id)
```

### Prompt Formatter

Formats task and memory context into structured prompts.

**Template:**

```markdown
## Task
{task.description}

{if task.context}
## Context
{task.context}
{endif}

## Relevant Memory

### Similar Experiences ({len(experiences)})
{for exp in experiences}
- **{exp.task_summary}**
  - Approach: {exp.solution_summary}
  - Outcome: {exp.outcome}
{endfor}

### Applicable Strategies ({len(strategies)})
{for strategy in strategies}
- When: {strategy.situation}
  Try: {strategy.suggestion}
{endfor}

### Available Concepts ({len(concepts)})
{for concept in concepts}
- `{concept.name}`: {concept.description}
{endfor}

## Notes
- You can query additional memory using `memory_search_*` tools if needed.
- Focus on the task at hand and use the provided context as guidance.
```

**Token Management:**

```python
class PromptFormatter:
    def __init__(self, config: MemoryConfig):
        self._config = config
    
    def format(
        self,
        task: Task,
        memory_result: MemoryQueryResult | None,
    ) -> str:
        """Format task and memory into prompt, respecting token limits."""
        # Truncate each section to fit within max_context_tokens
        ...
```

### Embedding Provider

BGE embeddings with in-memory caching.

```python
class BGEEmbeddings:
    """BAAI/bge-base-en-v1.5 embeddings with caching."""
    
    def __init__(self, config: EmbeddingConfig = None):
        self._config = config or EmbeddingConfig()
        self._model = None  # Lazy loading
        self._cache: dict[str, np.ndarray] = {}  # In-memory cache
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text, using cache if available."""
        if self._config.cache_enabled and text in self._cache:
            return self._cache[text]
        
        embedding = self._get_model().encode(text)
        
        if self._config.cache_enabled:
            self._cache[text] = embedding
        
        return embedding
    
    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts efficiently."""
        ...
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
    
    @property
    def dimension(self) -> int:
        return 768  # BGE base dimension
    
    @property
    def model_name(self) -> str:
        return self._config.model_name
```

### Vector Index (ChromaDB)

Project-local storage with one collection per memory type.

```python
class ChromaIndex:
    """ChromaDB-backed vector index."""
    
    def __init__(
        self,
        collection_name: str,
        config: StorageConfig = None,
    ):
        self._config = config or StorageConfig()
        self._collection_name = self._prefixed_name(collection_name)
        self._client = None  # Lazy init
        self._collection = None
    
    def _prefixed_name(self, name: str) -> str:
        prefix = self._config.chroma_collection_prefix
        return f"{prefix}{name}" if prefix else name
    
    def _get_client(self) -> chromadb.Client:
        if self._client is None:
            persist_dir = self._config.base_path / "chroma"
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
        return self._client
    
    def _get_collection(self) -> chromadb.Collection:
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": self._config.distance_metric},
            )
        return self._collection
    
    # ... implement VectorIndex protocol methods
```

**Collections:**

| Collection | Contents |
|------------|----------|
| `experiences` | Task-level experiences from trajectories |
| `concepts` | Code patterns and compositions |
| `strategies` | Abstract reasoning patterns |

## Error Handling

| Scenario | Handling |
|----------|----------|
| Agent crashes mid-execution | Return partial Trajectory with `Outcome(success=False, error_info="agent_crashed")` |
| Agent times out | Cancel session, return partial Trajectory with `Outcome(success=False, error_info="timeout")` |
| Verification fails | Return complete Trajectory with `Outcome(success=False)` - normal flow |
| MCP server unavailable | Continue without memory tools (graceful degradation), log warning |
| Embedding model fails to load | Raise exception on first use (fail fast) |
| ChromaDB connection fails | Raise exception (storage is required) |

## Logging

Standard Python logging with module-based loggers:

```python
import logging

# Module loggers
logger_execution = logging.getLogger("atlas.execution")
logger_memory = logging.getLogger("atlas.memory")
logger_mcp = logging.getLogger("atlas.mcp")
logger_embedding = logging.getLogger("atlas.embedding")
logger_storage = logging.getLogger("atlas.storage")

# Usage
logger_execution.info("Task started", extra={"task_id": task.id})
logger_execution.debug("Step completed", extra={"step": step.action})
logger_memory.info("Memory query", extra={"k": k, "results": len(results)})
```

## Solution Extraction

The solution is the **environment state at the end of the trajectory**.

```python
async def execute(self, task: Task, env: Environment) -> Trajectory:
    # ... run session, collect steps ...
    
    # Solution = environment state after agent execution
    candidate = Candidate(
        solution=env.get_current_state(),  # Domain-specific
        confidence=1.0,
        reasoning="Agent execution completed",
        source="agent",
    )
    
    # Verify
    outcome = env.verify(task, candidate)
    
    return trajectory_builder.build(outcome)
```

For domains needing custom extraction, `Environment` can override:

```python
class Environment(Protocol):
    def get_current_state(self) -> Any:
        """Get current state as solution candidate."""
        ...  # Default: return None, subclasses override
```

## Dependencies

- `acp-factory` - Agent Client Protocol library (git submodule)
- `fastmcp` - MCP server framework
- `sentence-transformers` - Local embeddings
- `chromadb` - Vector storage

## File Structure

```
atlas/
├── config.py              # ATLASConfig and sub-configs
├── execution/
│   ├── __init__.py
│   ├── executor.py        # TaskExecutor
│   ├── trajectory_builder.py  # SessionUpdate → Step conversion
│   └── prompt_formatter.py    # Task + memory → structured prompt
├── mcp/
│   ├── __init__.py
│   └── memory_server.py   # FastMCP memory server
├── embeddings/
│   ├── __init__.py
│   └── bge.py             # BGE embeddings with cache
└── vector/
    ├── __init__.py
    └── chroma.py          # ChromaDB index
```

## Success Criteria

- [ ] ATLASConfig provides centralized, typed configuration
- [ ] TaskExecutor spawns ACP agents and executes tasks
- [ ] SessionUpdates correctly convert to Steps (tool-centric)
- [ ] Session reuse is configurable (default: new per task)
- [ ] Memory MCP server exposes search tools via FastMCP
- [ ] Upfront memory context is formatted with token limits
- [ ] BGE embeddings work with in-memory caching
- [ ] ChromaDB stores vectors in project-local `.atlas/`
- [ ] Graceful error handling for crashes/timeouts
- [ ] Standard Python logging throughout
- [ ] Async API for all I/O operations
