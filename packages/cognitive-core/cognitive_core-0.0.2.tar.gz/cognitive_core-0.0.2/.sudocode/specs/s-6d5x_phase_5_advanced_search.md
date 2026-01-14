---
id: s-6d5x
title: 'Phase 5: Advanced Search'
priority: 2
created_at: '2026-01-06 02:20:04'
parent_id: s-5o87
tags:
  - mcts
  - mind-evolution
  - phase-5
  - pillar-2
  - search
---
# Phase 5: Advanced Search

Parent: [[s-5o87|ATLAS System Architecture]]
Implements: [[s-3nub|Search Methods (Pillar 2)]]

## Overview

Advanced search algorithms for harder tasks where DirectSolver isn't enough.

## Implementation Decisions

### Scope
- Implement **both** MindEvolutionSearch and SWESearch (MCTS)
- Full environment implementations for ARC (arckit) and SWE (Docker)
- Full routing logic with configurable thresholds
- Pydantic config models

### MCTS Value Estimation
Hybrid approach:
1. LLM discriminator for initial estimates on all nodes
2. Full/partial agent rollouts on top 10-20% promising nodes
3. Balances cost (~300-500 calls) with accuracy

### Environment Integration
- **ARC**: Use `arckit` library for data loading and grid verification
- **SWE**: Full `swebench` Docker integration with harness

## Components

### 1. Configuration Models

```python
class MindEvolutionConfig(BaseModel):
    """Configuration for Mind Evolution search."""
    population_size: int = 20
    generations: int = 10
    elite_fraction: float = 0.5
    memory_init_fraction: float = 0.5  # % from memory
    mutation_temperature: float = 0.7
    crossover_rate: float = 0.3

class SWESearchConfig(BaseModel):
    """Configuration for SWE-Search (MCTS)."""
    max_expansions: int = 100
    ucb_constant: float = 1.414
    max_depth: int = 20
    rollout_depth: int = 5
    use_discriminator: bool = True
    discriminator_threshold: float = 0.7  # Top % for agent rollout

class RouterConfig(BaseModel):
    """Configuration for task routing."""
    similarity_threshold: float = 0.9
    use_domain_routing: bool = True
    default_strategy: str = "evolutionary"
```

### 2. ARCEnvironment

Full implementation using `arckit`:

```python
class ARCEnvironment:
    """ARC-AGI environment with grid verification."""
    
    def __init__(self, task_id: str | None = None):
        self._task: Task | None = None
        self._arc_task: arckit.Task | None = None
    
    def reset(self, task: Task) -> str:
        """Load ARC task and return description."""
        # Load from arckit dataset
        # Parse task.context for grid data
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Verify grid solution with partial scoring."""
        # Exact match check
        # Cell-by-cell similarity for partial score
        ...
    
    @property
    def task(self) -> Task:
        return self._task
```

### 3. SWEEnvironment

Full Docker integration with swebench:

```python
class SWEEnvironment:
    """SWE-bench environment with Docker evaluation."""
    
    def __init__(
        self,
        docker_client: docker.DockerClient | None = None,
        timeout: int = 300,
    ):
        self._task: Task | None = None
        self._docker = docker_client or docker.from_env()
    
    def reset(self, task: Task) -> str:
        """Set up Docker container for task."""
        # Pull/build image for repo version
        # Initialize container
        ...
    
    def step(self, action: str) -> tuple[str, float, bool]:
        """Execute action (patch/command) in container."""
        # Apply patch or run command
        # Return observation, reward, done
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Run tests and return outcome."""
        # Execute test suite in container
        # Parse results for pass/fail
        # Calculate partial score (tests passed / total)
        ...
```

### 4. MindEvolutionSearch

Population-based evolutionary search:

```python
class MindEvolutionSearch:
    """Mind Evolution search for ARC-style tasks."""
    
    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        config: MindEvolutionConfig | None = None,
    ):
        ...
    
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """
        Algorithm:
        1. Initialize population (50% memory, 50% novel)
        2. For each generation:
           a. Evaluate fitness via env.verify()
           b. Select elites (top 50%)
           c. Generate children via mutation/crossover
        3. Return best candidates
        """
        ...
    
    def _initialize_population(self, task: Task, routing: RoutingDecision) -> list[Candidate]:
        """Initialize from memory + novel generation."""
        ...
    
    def _mutate(self, candidate: Candidate, task: Task) -> Candidate:
        """LLM-based mutation."""
        ...
    
    def _crossover(self, parent1: Candidate, parent2: Candidate, task: Task) -> Candidate:
        """LLM-based crossover."""
        ...
```

### 5. SWESearch (MCTS)

Monte Carlo Tree Search:

```python
class SWESearch:
    """MCTS-based search for SWE tasks."""
    
    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,  # For agent rollouts
        config: SWESearchConfig | None = None,
    ):
        ...
    
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """
        Algorithm:
        1. Initialize root with task state
        2. For each expansion:
           a. Select leaf via UCB
           b. Expand with LLM-generated actions
           c. Estimate value (discriminator + selective rollout)
           d. Backpropagate
        3. Return best path
        """
        ...
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """UCB selection."""
        ...
    
    def _expand(self, node: MCTSNode, task: Task) -> list[MCTSNode]:
        """LLM-generated action expansion."""
        ...
    
    def _estimate_value(self, node: MCTSNode, task: Task, env: Environment) -> float:
        """Hybrid: discriminator + selective agent rollout."""
        ...
```

### 6. Discriminator

Hybrid value estimation:

```python
class Discriminator:
    """Estimates solution quality for MCTS and pruning."""
    
    def __init__(
        self,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,
    ):
        ...
    
    def estimate(self, task: Task, candidate: Candidate) -> float:
        """LLM-based quality estimation."""
        ...
    
    def estimate_with_rollout(
        self,
        task: Task,
        candidate: Candidate,
        env: Environment,
        depth: int = 5,
    ) -> float:
        """Agent rollout for high-confidence estimation."""
        ...
    
    def should_rollout(self, score: float, threshold: float = 0.7) -> bool:
        """Decide if candidate warrants expensive rollout."""
        ...
```

### 7. Enhanced TaskRouter

Smart routing with configuration:

```python
class EnhancedTaskRouter:
    """Smart task routing based on task characteristics."""
    
    def __init__(
        self,
        memory: MemorySystem,
        config: RouterConfig | None = None,
    ):
        ...
    
    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """
        Routing logic:
        1. Query memory for similar experiences
        2. Calculate similarity score
        3. Check domain
        4. Apply routing rules:
           - similarity > 0.9 + success → adapt
           - clear strategy match → direct
           - ARC domain → evolutionary
           - SWE domain → mcts
           - unknown → evolutionary (default)
        """
        ...
    
    def _calculate_similarity(self, task: Task, experiences: list[Experience]) -> float:
        """Calculate max similarity to past experiences."""
        ...
```

## File Structure

```
atlas/
├── config.py                    # Add new config models
├── environments/
│   ├── arc.py                   # Full ARCEnvironment
│   └── swe.py                   # Full SWEEnvironment with Docker
├── search/
│   ├── mind_evolution.py        # MindEvolutionSearch
│   ├── mcts.py                  # SWESearch
│   ├── discriminator.py         # Discriminator
│   └── router.py                # EnhancedTaskRouter
```

## Dependencies

- `arckit>=1.0.1` - ARC data loading and manipulation
- `swebench` - SWE-bench evaluation harness
- `docker` - Docker SDK for Python

## Success Criteria

- [ ] MindEvolution improves over DirectSolver on ARC tasks
- [ ] SWESearch handles multi-step code edits
- [ ] ARCEnvironment correctly verifies grid solutions
- [ ] SWEEnvironment runs tests in Docker containers
- [ ] Router correctly selects strategy by task type
- [ ] Memory integration boosts population quality
- [ ] Configurable search budgets work correctly
- [ ] All components have comprehensive tests
