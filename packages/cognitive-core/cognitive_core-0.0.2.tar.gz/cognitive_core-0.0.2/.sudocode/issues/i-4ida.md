---
id: i-4ida
title: Implement TrajectoryAnalyzer with Credit Strategies
priority: 1
created_at: '2026-01-08 07:49:25'
tags:
  - analyzer
  - credit-assignment
  - phase-6
relationships:
  - from_id: i-4ida
    from_uuid: 36e280c4-4fc9-4228-8545-cc20fd77b1a3
    from_type: issue
    to_id: i-73dj
    to_uuid: 6305bbdd-5bf5-4c90-9008-aeebeb6429af
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-4ida
    from_uuid: 36e280c4-4fc9-4228-8545-cc20fd77b1a3
    from_type: issue
    to_id: s-7jda
    to_uuid: 49803afb-f589-4d66-94ea-aeb7367a3801
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 07:49:43'
    metadata: null
status: closed
closed_at: '2026-01-08 08:02:55'
---
# TrajectoryAnalyzer Implementation

Implements [[s-7jda|Phase 6: Learning Pipeline]] trajectory analysis requirements.

## Goal

Implement TrajectoryAnalyzer with three credit assignment strategies.

## Requirements

### 1. CreditStrategy Protocol

```python
class CreditStrategy(Protocol):
    """Protocol for credit assignment strategies."""
    
    def attribute(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        """Assign credit to trajectory steps.
        
        Args:
            trajectory: The trajectory to analyze.
            
        Returns:
            List of (step_index, contribution_score) pairs.
            Scores should sum to 1.0 for successful trajectories.
        """
        ...
```

### 2. SimpleCreditStrategy

```python
class SimpleCreditStrategy:
    """Last successful action gets credit.
    
    Simple heuristic: the final step before success gets most credit.
    """
    
    def attribute(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        if not trajectory.steps:
            return []
        
        if trajectory.outcome.success:
            # Last step gets 70%, second-to-last 20%, rest 10%
            ...
        else:
            # Distribute blame to last few steps
            ...
```

### 3. LLMCreditStrategy

```python
class LLMCreditStrategy:
    """Ask LLM to identify key steps.
    
    Uses SimpleLLM to analyze trajectory and identify which
    steps were critical for the outcome.
    """
    
    def __init__(self, llm: SimpleLLM | None = None):
        self._llm = llm
    
    def attribute(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        prompt = f'''
        Analyze this trajectory and identify key steps:
        
        Task: {trajectory.task.description}
        Outcome: {"Success" if trajectory.outcome.success else "Failure"}
        
        Steps:
        {format_steps(trajectory.steps)}
        
        Return JSON with step indices and their contribution scores (0.0-1.0):
        {{"attributions": [{"step": 0, "score": 0.5, "reason": "..."}]}}
        '''
        ...
```

### 4. CounterfactualCreditStrategy

```python
class CounterfactualCreditStrategy:
    """Would removing step change outcome?
    
    Uses LLM to reason counterfactually about each step.
    """
    
    def attribute(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        # For each step, ask: "If we removed this step, 
        # would the outcome change?"
        # Steps where removal would change outcome get high credit.
        ...
```

### 5. TrajectoryAnalyzer

```python
class TrajectoryAnalyzer:
    """Analyze trajectories for learning signals.
    
    Example:
        analyzer = TrajectoryAnalyzer(strategy=LLMCreditStrategy(llm))
        result = analyzer.analyze(trajectory)
    """
    
    def __init__(
        self,
        strategy: CreditStrategy | None = None,
        llm: SimpleLLM | None = None,
    ):
        self._strategy = strategy or SimpleCreditStrategy()
        self._llm = llm
    
    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Full analysis of a trajectory."""
        # 1. Credit assignment
        attributions = self._strategy.attribute(trajectory)
        
        # 2. Identify key steps (top 30% by score)
        key_steps = [idx for idx, score in attributions if score > threshold]
        
        # 3. Check abstractability (LLM assessment)
        abstractable = self._assess_abstractability(trajectory)
        
        # 4. Generate training examples
        training_examples = self._generate_examples(trajectory, key_steps)
        
        return AnalysisResult(...)
    
    def attribute_outcome(self, trajectory: Trajectory) -> list[tuple[int, float]]:
        """Credit assignment wrapper."""
        return self._strategy.attribute(trajectory)
    
    def extract_error_patterns(
        self, 
        trajectories: list[Trajectory],
    ) -> list[ErrorPattern]:
        """Extract common error patterns from failed trajectories."""
        failed = [t for t in trajectories if not t.outcome.success]
        # Group by error type, extract patterns
        ...
```

## Files

- `src/atlas/learning/analyzer.py` - TrajectoryAnalyzer + strategies
- `tests/unit/test_analyzer.py` - Comprehensive tests

## Tests

- SimpleCreditStrategy assigns credit correctly
- LLMCreditStrategy parses LLM response correctly (mock LLM)
- CounterfactualCreditStrategy reasoning (mock LLM)
- TrajectoryAnalyzer.analyze returns valid AnalysisResult
- extract_error_patterns groups similar errors
- Abstractability assessment works
