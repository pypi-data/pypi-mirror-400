---
id: s-5o87
title: ATLAS System Architecture
priority: 0
created_at: '2025-12-07 08:19:15'
tags:
  - acp
  - architecture
  - core
  - system-design
---
# ATLAS System Architecture

## Overview

ATLAS (Adaptive Trajectory Learning and Abstraction System) is a modular meta-learning framework that learns from agent trajectories to improve task-solving performance over time.

**Core Insight**: The trajectory is the curriculum. Rather than designing tasks, we let agents attempt tasks and learn from the resulting trajectories.

## Design Principles

1. **Modular & Composable**: Every component works standalone and can be composed with any subset of other components
2. **Emergent Organization**: Domains self-organize via embeddings rather than explicit hierarchy
3. **Ablation-Friendly**: Easy to enable/disable pieces for experimentation
4. **Protocol-Based**: Components depend on protocols, not concrete implementations
5. **Agent-Centric**: Use ACP (Agent Client Protocol) as the abstraction layer - ATLAS orchestrates, agents execute

## Agent Abstraction Layer

**Key Design Decision**: ATLAS uses the Agent Client Protocol (ACP) via `acp-factory` as the primary agent abstraction.

```
┌─────────────────────────────────────────────────────────┐
│                       ATLAS                             │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │   Memory    │  │  Search  │  │     Learning      │  │
│  │   System    │  │  Engine  │  │     Pipeline      │  │
│  └──────┬──────┘  └────┬─────┘  └─────────┬─────────┘  │
│         └──────────────┼──────────────────┘             │
│                        ▼                                │
│              ┌─────────────────┐                        │
│              │  TaskExecutor   │                        │
│              │  (ACP wrapper)  │                        │
│              └────────┬────────┘                        │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│               ACP (acp-factory)                         │
│     AgentFactory → Session → SessionUpdates             │
│     (Claude Code, Codex, Gemini, OpenCode)              │
└─────────────────────────────────────────────────────────┘
```

**Implications**:
- No raw LLM wrapper needed - agents handle LLM interactions
- All cognitive tasks (including internal ATLAS operations like analysis) go through agents
- ATLAS focuses on orchestration, memory, and learning - not agent internals
- Session forking enables search strategy branching (Mind Evolution, MCTS)

## Core Primitives

### Trajectory
The atomic unit of learning. Immutable record of an agent's attempt at a task.

```
Trajectory
├── Task (id, domain, description, context, verification)
├── Steps[] (thought, action, observation, metadata)
├── Outcome (success, partial_score, error_info, verification_details)
└── Metadata (agent_id, timestamp, embeddings)
```

### Environment
Execution context for verification, with optional sandboxing.

```
Environment
├── verify(task, candidate) → Outcome
├── get_sandbox_handlers() → ClientHandlers | None  # Optional sandboxing
└── Properties: deterministic, max_steps
```

**Execution Modes**:
- **Free**: Agent runs freely, Environment only verifies results
- **Sandboxed**: Environment provides handlers to control file/terminal access

### TaskExecutor
Bridges ACP sessions and ATLAS's task/trajectory model.

```
TaskExecutor
├── execute(task, env) → Trajectory
├── execute_with_session(task, env, session) → Trajectory  # For forking
└── Memory integration (upfront context + MCP tools)
```

## Three Pillars

### Pillar 1: Memory Systems

Three complementary memory types at different abstraction levels:

| Memory | Purpose | Abstraction Level | Key Insight |
|--------|---------|-------------------|-------------|
| **Strategy Bank** | Abstract reasoning patterns | High (concept-level) | ArcMemo: concept > instance at all scales |
| **Experience Memory** | Task-level retrieval | Medium (task-level) | ReMem: search-synthesize-evolve loop |
| **Concept Library** | Reusable code patterns | Low (code-level) | Stitch+LILO: fast, interpretable extraction |

**Memory Access** (Hybrid Approach):
1. **Upfront Context**: Structured prompt with relevant experiences, strategies, concepts
2. **On-Demand**: Memory MCP server exposes search tools for mid-execution queries

**Interfaces**:
- `ConceptLibrary`: add, search, compose, compress
- `ExperienceMemory`: store, search, refine, prune  
- `StrategyBank`: write, read, update_stats

### Pillar 2: Search Methods

Task Router decides which search strategy to use:

| Strategy | Best For | Cost | Algorithm |
|----------|----------|------|-----------|
| **Direct** | High-confidence memory match | ~1 call | Retrieve → Adapt → Verify |
| **Mind Evolution** | ARC-AGI, clear fitness | ~100 calls | Population-based evolutionary |
| **SWE-Search** | SWE, sequential edits | ~200 calls | MCTS with UCB selection |

**Session Forking**: ACP's `session.fork()` enables branching for:
- Mind Evolution population exploration
- MCTS tree expansion
- Parallel candidate evaluation

**Interfaces**:
- `TaskRouter`: route(task, memory) → RoutingDecision
- `SearchEngine`: search(task, routing, env) → List[Candidate]
- `Verifier`: verify(task, candidate) → Outcome

### Pillar 3: Learning Engine

Extracts knowledge from trajectories to update memory:

| Component | Purpose | Method |
|-----------|---------|--------|
| **Trajectory Analyzer** | Credit assignment, error patterns | Step attribution |
| **Abstraction Extractor** | Code patterns, strategies | Stitch compression, ArcMemo abstraction |
| **Hindsight Learner** | Model improvement | SOAR fine-tuning or SAGE memory-only |

**Interfaces**:
- `TrajectoryAnalyzer`: analyze(trajectory) → AnalysisResult
- `AbstractionExtractor`: extract_code_patterns, extract_strategies, auto_document
- `HindsightLearner`: prepare_training_data, should_finetune, finetune

## Data Flow

```
Task → Memory Query → Router → Search → Verifier → Outcome
              │                   │                   │
              │            [ACP Sessions]             │
              │          [Session Forking]            │
              │                                       ▼
              │                               Learning Engine
              │                                       │
              └───────────────── Memory Update ◄──────┘
```

## Modularity Requirements

Each component MUST:
1. Work standalone with sensible defaults
2. Accept optional dependencies via constructor
3. Handle missing dependencies gracefully (return empty, not crash)
4. Be testable in isolation

Example:
```python
# Full system
solver = ATLASSolver(
    memory=MemorySystem(experience=exp, concepts=lib, strategies=bank),
    executor=TaskExecutor(agent_type="claude-code", memory=memory),
)

# Experience-only ablation
solver = ATLASSolver(
    memory=MemorySystem(experience=exp),  # concepts/strategies omitted
    executor=TaskExecutor(agent_type="claude-code", memory=memory),
)

# No memory baseline
solver = ATLASSolver(
    memory=MemorySystem(),  # empty
    executor=TaskExecutor(agent_type="claude-code"),
)
```

## Module Structure

```
atlas/
├── core/           # Primitives: Trajectory, Task, Step, Outcome
├── execution/      # TaskExecutor, TrajectoryBuilder, PromptFormatter
├── mcp/            # Memory MCP server for agent access
├── memory/         # Pillar 1: ConceptLibrary, ExperienceMemory, StrategyBank
├── search/         # Pillar 2: Router, MindEvolution, SWESearch, Verifier
├── learning/       # Pillar 3: Analyzer, Extractor, HindsightLearner
├── environments/   # ARC, SWE environments (verification + optional sandbox)
├── embeddings/     # BGE embeddings
└── vector/         # ChromaDB, Pinecone adapters
```

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent Abstraction | ACP via acp-factory | Supports multiple agents (Claude Code, Codex, Gemini, OpenCode), session forking for search |
| Embedding Model | BAAI/bge-base-en-v1.5 | Validated in ReMem paper |
| Vector Store | ChromaDB (start) | Local, simple, migrate if needed |
| Domain Organization | Emergent via embeddings | Self-organizing, no manual taxonomy |
| Memory Access | Hybrid (upfront + MCP) | Best of both: immediate context + on-demand queries |

## Implementation Phases

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| 1 ✓ | Protocols & Types | Core types, all protocol definitions |
| 2 | Infrastructure | TaskExecutor, Memory MCP, Embeddings, Vector |
| 3 | Memory | ExperienceMemory, ConceptLibrary, StrategyBank |
| 4 | Minimal Solver | DirectSolver, TaskRouter, basic Verifier |
| 5 | Advanced Search | MindEvolution, SWESearch |
| 6 | Learning | Analyzer, Extractor, HindsightLearner |
| 7 | Environments | ARC, SWE environments with sandbox support |

## References

- ACP Factory: `references/acp-factory/` (git submodule)
- Research synthesis: [[s-research]] (to be created)
- Modular design: See `docs/modular-design.md`
