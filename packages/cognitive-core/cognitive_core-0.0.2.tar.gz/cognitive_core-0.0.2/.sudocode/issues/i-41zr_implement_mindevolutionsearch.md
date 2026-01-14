---
id: i-41zr
title: Implement MindEvolutionSearch
priority: 2
created_at: '2026-01-08 06:00:23'
tags:
  - arc
  - evolutionary
  - phase-5
  - search
status: open
---
# MindEvolutionSearch Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] MindEvolutionSearch requirements.

## Goal

Implement population-based evolutionary search for ARC-style tasks with clear fitness functions.

## Algorithm Overview

```
1. Initialize population (50% from memory, 50% novel)
2. For each generation:
   a. Evaluate fitness for all candidates via env.verify()
   b. Select top 50% as elites
   c. Generate children via mutation/crossover
   d. Replace population
3. Return best candidates
```

**Cost:** ~100 LLM calls per task (population_size × generations / 2)

## Requirements

### 1. MindEvolutionSearch Class

```python
class MindEvolutionSearch:
    """Mind Evolution search for ARC-style tasks."""
    
    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        config: MindEvolutionConfig | None = None,
    ):
        self._memory = memory
        self._llm = llm
        self._config = config or MindEvolutionConfig()
    
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Run evolutionary search."""
        ...
    
    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine via targeted mutation."""
        ...
    
    @property
    def name(self) -> str:
        return "evolutionary"
```

### 2. Population Initialization

```python
def _initialize_population(
    self,
    task: Task,
    routing: RoutingDecision,
) -> list[Candidate]:
    """Initialize population from memory + novel generation.
    
    Split based on config.memory_init_fraction:
    - memory_init_fraction from adapted experiences
    - (1 - memory_init_fraction) from novel LLM generation
    """
    population = []
    memory_count = int(self._config.population_size * self._config.memory_init_fraction)
    
    # From memory (adapt similar experiences)
    if routing.context and routing.context.experiences:
        for exp in routing.context.experiences[:memory_count]:
            adapted = self._adapt_from_experience(task, exp)
            population.append(adapted)
    
    # Novel generation
    while len(population) < self._config.population_size:
        novel = self._generate_novel(task)
        population.append(novel)
    
    return population
```

### 3. Mutation (LLM-based)

```python
def _mutate(self, candidate: Candidate, task: Task) -> Candidate:
    """LLM-based mutation of a candidate.
    
    Prompt template (ARC-specific):
    - Show task examples
    - Show current solution
    - Ask for variation/improvement
    """
    prompt = f'''Given an ARC task:
{self._format_task(task)}

Current solution approach:
{candidate.solution}

Generate a variation of this solution. Make a small but meaningful change 
to the approach while keeping the core idea. Return only the modified solution.
'''
    
    mutated = self._llm.generate(prompt, temperature=self._config.mutation_temperature)
    
    return Candidate(
        solution=mutated,
        confidence=candidate.confidence * 0.9,
        reasoning=f"Mutated from {candidate.source}",
        source="mutated",
        parent_ids=[str(id(candidate))],
    )
```

### 4. Crossover (LLM-based)

```python
def _crossover(
    self,
    parent1: Candidate,
    parent2: Candidate,
    task: Task,
) -> Candidate:
    """LLM-based crossover of two candidates.
    
    Combine ideas from both parents into a new solution.
    """
    prompt = f'''Given an ARC task:
{self._format_task(task)}

Parent solution 1:
{parent1.solution}

Parent solution 2:
{parent2.solution}

Combine the best ideas from both solutions into a new approach.
Return only the combined solution.
'''
    
    child = self._llm.generate(prompt, temperature=self._config.mutation_temperature)
    
    return Candidate(
        solution=child,
        confidence=(parent1.confidence + parent2.confidence) / 2,
        reasoning=f"Crossover of two parents",
        source="crossover",
        parent_ids=[str(id(parent1)), str(id(parent2))],
    )
```

### 5. Selection

```python
def _select_elites(
    self,
    population: list[Candidate],
) -> list[Candidate]:
    """Select top candidates by fitness."""
    sorted_pop = sorted(population, key=lambda c: c.fitness or 0.0, reverse=True)
    elite_count = int(len(sorted_pop) * self._config.elite_fraction)
    return sorted_pop[:max(elite_count, 1)]
```

### 6. Main Evolution Loop

```python
def _evolve(
    self,
    population: list[Candidate],
    task: Task,
    env: Environment,
) -> list[Candidate]:
    """Run evolution for configured generations."""
    for gen in range(self._config.generations):
        # Evaluate fitness
        for candidate in population:
            if candidate.fitness is None:
                outcome = env.verify(candidate.solution)
                candidate = candidate.model_copy(
                    update={"fitness": outcome.partial_score}
                )
        
        # Check for success
        successful = [c for c in population if (c.fitness or 0) >= 1.0]
        if successful:
            return successful
        
        # Selection
        elites = self._select_elites(population)
        
        # Generate children
        children = []
        while len(children) < self._config.population_size - len(elites):
            if random.random() < self._config.crossover_rate and len(elites) >= 2:
                p1, p2 = random.sample(elites, 2)
                child = self._crossover(p1, p2, task)
            else:
                parent = random.choice(elites)
                child = self._mutate(parent, task)
            children.append(child)
        
        population = elites + children
    
    return sorted(population, key=lambda c: c.fitness or 0.0, reverse=True)
```

## Files

- `src/atlas/search/mind_evolution.py` - MindEvolutionSearch
- `tests/unit/test_mind_evolution.py` - Unit tests

## Tests

- Population initialization from memory
- Population initialization with novel generation
- Mutation produces valid variations
- Crossover combines parent ideas
- Selection keeps top candidates
- Evolution improves fitness over generations
- Early termination on success
- Implements SearchEngine protocol
