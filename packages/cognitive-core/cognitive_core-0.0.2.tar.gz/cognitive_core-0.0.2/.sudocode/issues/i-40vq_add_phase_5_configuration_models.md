---
id: i-40vq
title: Add Phase 5 configuration models
priority: 1
created_at: '2026-01-08 05:58:45'
tags:
  - config
  - foundation
  - phase-5
status: open
---
# Phase 5 Configuration Models

Implements [[s-6d5x|Phase 5: Advanced Search]] configuration requirements.

## Goal

Add Pydantic configuration models for Phase 5 search algorithms.

## Requirements

### 1. MindEvolutionConfig

```python
class MindEvolutionConfig(BaseModel):
    """Configuration for Mind Evolution search."""
    model_config = ConfigDict(frozen=True)
    
    population_size: int = Field(default=20, ge=4, description="Population size")
    generations: int = Field(default=10, ge=1, description="Number of generations")
    elite_fraction: float = Field(default=0.5, ge=0.1, le=0.9, description="Fraction of elites to keep")
    memory_init_fraction: float = Field(default=0.5, ge=0.0, le=1.0, description="Fraction from memory")
    mutation_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature for mutation")
    crossover_rate: float = Field(default=0.3, ge=0.0, le=1.0, description="Probability of crossover")
```

### 2. SWESearchConfig

```python
class SWESearchConfig(BaseModel):
    """Configuration for SWE-Search (MCTS)."""
    model_config = ConfigDict(frozen=True)
    
    max_expansions: int = Field(default=100, ge=1, description="Max tree expansions")
    ucb_constant: float = Field(default=1.414, ge=0.0, description="UCB exploration constant")
    max_depth: int = Field(default=20, ge=1, description="Max tree depth")
    rollout_depth: int = Field(default=5, ge=1, description="Rollout simulation depth")
    use_discriminator: bool = Field(default=True, description="Use discriminator for value estimation")
    discriminator_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Threshold for agent rollout")
```

### 3. RouterConfig

```python
class RouterConfig(BaseModel):
    """Configuration for task routing."""
    model_config = ConfigDict(frozen=True)
    
    similarity_threshold: float = Field(default=0.9, ge=0.0, le=1.0, description="Threshold for adapt strategy")
    use_domain_routing: bool = Field(default=True, description="Route by task domain")
    default_strategy: str = Field(default="evolutionary", description="Default strategy when uncertain")
    arc_strategy: str = Field(default="evolutionary", description="Strategy for ARC domain")
    swe_strategy: str = Field(default="mcts", description="Strategy for SWE domain")
```

## Files

- `src/atlas/config.py` - Add new config models
- `tests/unit/test_config.py` - Add config tests

## Tests

- Validation constraints work correctly
- Default values are sensible
- Configs are immutable (frozen)
