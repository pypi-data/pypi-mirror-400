---
id: i-396o
title: >-
  Implement Learning protocols (TrajectoryAnalyzer, AbstractionExtractor,
  HindsightLearner)
priority: 1
created_at: '2025-12-18 03:33:25'
tags:
  - learning
  - phase-1
  - pillar-3
  - protocols
status: open
---
Define the protocols for the learning engine (Pillar 3).

## Files to Create
- `atlas/protocols/learning.py` (~60 lines)

## TrajectoryAnalyzer Protocol
Extract learning signals from trajectories:

```python
class TrajectoryAnalyzer(Protocol):
    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Full analysis of a trajectory"""
        ...
    
    def attribute_outcome(
        self,
        trajectory: Trajectory,
    ) -> List[Tuple[int, float]]:
        """Credit assignment: (step_index, contribution_score)"""
        ...
```

## AbstractionExtractor Protocol
Extract reusable patterns:

```python
class AbstractionExtractor(Protocol):
    def extract_code_patterns(
        self,
        trajectories: List[Trajectory],
    ) -> List[CodeConcept]:
        """Stitch-style compression"""
        ...
    
    def extract_strategies(
        self,
        trajectories: List[Trajectory],
    ) -> List[Strategy]:
        """ArcMemo-style abstraction"""
        ...
    
    def auto_document(self, concept: CodeConcept) -> CodeConcept:
        """LILO-style documentation generation"""
        ...
```

## HindsightLearner Protocol
Learn from trajectories to improve model:

```python
class HindsightLearner(Protocol):
    def prepare_training_data(
        self,
        trajectories: List[Trajectory],
    ) -> Dict[str, Any]:
        """Convert trajectories to training format"""
        ...
    
    def should_finetune(self) -> bool:
        """Check if enough data for fine-tuning"""
        ...
    
    def finetune(self, training_data: Dict) -> FinetuneResult:
        """Execute fine-tuning"""
        ...
```

## Supporting Types
```python
@dataclass
class AnalysisResult:
    success: bool
    key_steps: List[int]
    step_attribution: List[float]
    error_patterns: List[Dict]
    abstractable: bool
    training_examples: List[Dict]

@dataclass
class FinetuneResult:
    success: bool
    model_path: Optional[str]
    metrics: Dict[str, float]
```

## Acceptance Criteria
- [ ] All protocols defined
- [ ] Supporting dataclasses implemented
- [ ] Type hints complete

Implements [[s-w56w]]
