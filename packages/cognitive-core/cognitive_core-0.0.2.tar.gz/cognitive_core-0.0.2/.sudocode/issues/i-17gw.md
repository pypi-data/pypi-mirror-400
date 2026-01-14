---
id: i-17gw
title: Implement Phase 6 Configs and Types
priority: 1
created_at: '2026-01-08 07:47:40'
tags:
  - config
  - phase-6
  - types
relationships:
  - from_id: i-17gw
    from_uuid: 728c4908-e4cd-4a91-8e86-25c12a8a8efa
    from_type: issue
    to_id: i-1eqy
    to_uuid: 5d46066d-9bd1-442e-840a-7a301a0d6a56
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-17gw
    from_uuid: 728c4908-e4cd-4a91-8e86-25c12a8a8efa
    from_type: issue
    to_id: i-4ida
    to_uuid: 36e280c4-4fc9-4228-8545-cc20fd77b1a3
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-17gw
    from_uuid: 728c4908-e4cd-4a91-8e86-25c12a8a8efa
    from_type: issue
    to_id: i-57ba
    to_uuid: 97d0ed81-11c8-46d3-9aeb-87088a3be3b5
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-17gw
    from_uuid: 728c4908-e4cd-4a91-8e86-25c12a8a8efa
    from_type: issue
    to_id: s-7jda
    to_uuid: 49803afb-f589-4d66-94ea-aeb7367a3801
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 07:49:43'
    metadata: null
status: closed
closed_at: '2026-01-08 07:55:17'
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
