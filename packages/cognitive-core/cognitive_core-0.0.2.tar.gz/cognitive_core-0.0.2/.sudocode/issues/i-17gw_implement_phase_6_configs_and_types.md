---
id: i-17gw
title: Implement Phase 6 Configs and Types
priority: 1
created_at: '2026-01-08 07:47:40'
tags:
  - config
  - phase-6
  - types
status: open
---
# Phase 6 Configs and Types

Implements [[s-7jda|Phase 6: Learning Pipeline]] configuration and type requirements.

## Goal

Add configuration models and types needed for the learning pipeline.

## Requirements

### 1. LearningConfig (in config.py)

```python
class LearningConfig(BaseModel):
    """Configuration for the learning pipeline."""
    
    model_config = ConfigDict(frozen=True)
    
    credit_strategy: str = Field(
        default="llm",
        description="Credit assignment strategy: 'simple', 'llm', 'counterfactual'"
    )
    pattern_extractor: str = Field(
        default="llm", 
        description="Pattern extraction method: 'llm', 'text', 'both'"
    )
    min_trajectories: int = Field(
        default=50, ge=1,
        description="Minimum trajectories for batch learning"
    )
    min_hours_since_last: float | None = Field(
        default=None, ge=0,
        description="Optional time-based trigger (hours)"
    )
    min_success_rate: float | None = Field(
        default=None, ge=0.0, le=1.0,
        description="Optional quality threshold"
    )
```

### 2. ErrorPattern Type (in core/types.py)

```python
class ErrorPattern(BaseModel):
    """Detected error pattern from trajectory analysis."""
    
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(description="Pattern name, e.g., 'null_pointer_dereference'")
    signature: str = Field(description="Pattern signature or regex")
    frequency: int = Field(default=1, ge=1, description="How often seen")
    suggested_fix: str = Field(description="Recommended resolution")
    examples: list[str] = Field(default_factory=list, description="Example occurrences")
```

### 3. ProcessResult and BatchResult Types

```python
class ProcessResult(BaseModel):
    """Result of processing a single trajectory."""
    
    model_config = ConfigDict(frozen=True)
    
    trajectory_id: str
    stored: bool
    analysis: AnalysisResult | None = None
    strategy_extracted: bool = False
    abstractable: bool = False

class BatchResult(BaseModel):
    """Result of batch learning."""
    
    model_config = ConfigDict(frozen=True)
    
    trajectories_processed: int
    concepts_extracted: int
    strategies_extracted: int
    experiences_pruned: int
    success_rate: float
```

## Files

- `src/atlas/config.py` - Add LearningConfig
- `src/atlas/core/types.py` - Add ErrorPattern, ProcessResult, BatchResult
- `tests/unit/test_config.py` - Add LearningConfig tests
- `tests/unit/test_types.py` - Add new type tests

## Tests

- LearningConfig validation (strategy names, thresholds)
- ErrorPattern creation and immutability
- ProcessResult and BatchResult creation
