---
id: s-7jda
title: 'Phase 6: Learning Pipeline'
priority: 2
created_at: '2026-01-06 02:20:04'
parent_id: s-5o87
tags:
  - abstraction
  - analysis
  - learning
  - phase-6
  - pillar-3
---
# Phase 6: Learning Pipeline

Parent: [[s-5o87|ATLAS System Architecture]]
Implements: [[s-w56w|Learning Engine (Pillar 3)]]

## Overview

Extract knowledge from trajectories to improve memory. Uses SAGE-style memory-only improvement (no fine-tuning for now).

## Implementation Decisions

### Credit Assignment
Implement all three methods with a strategy pattern:
1. **Simple**: Last successful action gets credit
2. **LLM-based**: Ask LLM to identify key steps
3. **Counterfactual**: Would removing step change outcome?

Default: LLM-based (most accurate)

### Pattern Extraction
Use LLM-based pattern extraction + text-based heuristics (no Stitch dependency):
- LLM extracts conceptual patterns from code
- Text heuristics find syntactic patterns (AST-based)
- Both methods configurable

### Fine-tuning Approach
SAGE-only for now:
- Store plans as retrievable documents
- In-context learning with retrieved plans
- No weight updates, only memory growth
- `HindsightLearner` prepares data but doesn't execute fine-tuning

### Error Pattern Structure
```python
class ErrorPattern(BaseModel):
    name: str           # e.g., "null_pointer_dereference"
    signature: str      # Pattern signature/regex
    frequency: int      # How often seen
    suggested_fix: str  # Recommended resolution
    examples: list[str] # Example occurrences
```

### Abstractability Assessment
LLM/agent assessment determines if trajectory is worth extracting:
- Evaluates novelty, generalizability, complexity
- Returns boolean with reasoning

### Batch Learning Triggers
- `min_trajectories`: Default 50 (required)
- `min_hours_since_last`: Optional time-based trigger (default: None)
- `min_success_rate`: Optional quality threshold (default: None)

## Components

### TrajectoryAnalyzer
Extract learning signals from trajectories.

**Credit Assignment Strategies:**
```python
class CreditStrategy(Protocol):
    def attribute(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        """Return (step_index, contribution_score) pairs."""
        ...

class SimpleCreditStrategy:
    """Last successful action gets credit."""
    
class LLMCreditStrategy:
    """Ask LLM to identify key steps."""
    
class CounterfactualCreditStrategy:
    """Would removing step change outcome?"""
```

**Key Methods:**
- `analyze(trajectory) → AnalysisResult`
- `attribute_outcome(trajectory) → list[tuple[int, float]]`
- `extract_error_patterns(trajectories) → list[ErrorPattern]`

### AbstractionExtractor
Extract reusable patterns from trajectories.

**Pattern Extraction Methods:**
```python
class PatternExtractor(Protocol):
    def extract(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        ...

class LLMPatternExtractor:
    """LLM identifies conceptual patterns."""
    
class TextPatternExtractor:
    """AST-based syntactic pattern matching."""
```

**Key Methods:**
- `extract_code_patterns(trajectories) → list[CodeConcept]`
- `extract_strategies(trajectories) → list[Strategy]`
- `auto_document(concept) → CodeConcept`
- `is_abstractable(trajectory) → bool` (LLM assessment)

### HindsightLearner
SAGE-style memory improvement (no fine-tuning).

**Key Methods:**
- `prepare_training_data(trajectories) → dict` (for future fine-tuning)
- `should_finetune() → bool` (always False for SAGE)
- `accumulate(trajectory)` (add to memory for in-context learning)

**SOAR Training Data Format (prepared but not used):**
```python
{
    "sampling": [{"input": ..., "output": ..., "weight": 2.0}],
    "refinement": [{"input": ..., "output": ..., "weight": 1.5}],
    "error": [{"input": ..., "output": ..., "weight": 1.0}],
}
```

### LearningPipeline
Orchestrates the full learning process.

**Key Methods:**
- `process_trajectory(trajectory) → ProcessResult`
- `run_batch_learning(min_trajectories=50) → BatchResult`

**Configuration:**
```python
class LearningConfig(BaseModel):
    credit_strategy: str = "llm"  # "simple", "llm", "counterfactual"
    pattern_extractor: str = "llm"  # "llm", "text", "both"
    min_trajectories: int = 50
    min_hours_since_last: float | None = None  # Optional time trigger
    min_success_rate: float | None = None  # Optional quality trigger
```

**Pipeline Flow:**
```
Trajectory → Store in Memory
          → Analyze (credit assignment)
          → Check abstractability (LLM assessment)
          → Extract Strategy (if abstractable)
          → Accumulate for batch

Batch (when triggers met) → Extract Code Patterns
                         → Add to ConceptLibrary
                         → Prune low-value experiences
```

## Dependencies

- Phase 3: Memory system for storage
- Phase 4/5: Search for generating trajectories
- SimpleLLM: For LLM-based analysis and extraction

## File Structure

```
atlas/learning/
├── __init__.py
├── analyzer.py        # TrajectoryAnalyzer + CreditStrategies
├── extractor.py       # AbstractionExtractor + PatternExtractors
├── hindsight.py       # HindsightLearner (SAGE-style)
└── pipeline.py        # LearningPipeline + LearningConfig
```

## Success Criteria

- [ ] Analyzer correctly identifies key steps (all 3 credit strategies)
- [ ] Extractor finds patterns (LLM + text-based)
- [ ] Strategies generalize across similar tasks
- [ ] Pipeline processes trajectories end-to-end
- [ ] Memory improves with accumulated experience
- [ ] Batch triggers work correctly (count, time, quality)
