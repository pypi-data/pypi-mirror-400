---
id: i-1eqy
title: Implement HindsightLearner (SAGE-style)
priority: 1
created_at: '2026-01-08 07:49:25'
tags:
  - hindsight
  - phase-6
  - sage
relationships:
  - from_id: i-1eqy
    from_uuid: 5d46066d-9bd1-442e-840a-7a301a0d6a56
    from_type: issue
    to_id: i-73dj
    to_uuid: 6305bbdd-5bf5-4c90-9008-aeebeb6429af
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 07:49:56'
    metadata: null
  - from_id: i-1eqy
    from_uuid: 5d46066d-9bd1-442e-840a-7a301a0d6a56
    from_type: issue
    to_id: s-7jda
    to_uuid: 49803afb-f589-4d66-94ea-aeb7367a3801
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 07:49:43'
    metadata: null
status: closed
closed_at: '2026-01-08 08:01:35'
---
# HindsightLearner Implementation

Implements [[s-7jda|Phase 6: Learning Pipeline]] SAGE-style hindsight learning.

## Goal

Implement HindsightLearner for memory-based improvement (no fine-tuning).

## Requirements

### 1. HindsightLearner Class

```python
class HindsightLearner:
    """SAGE-style memory improvement without fine-tuning.
    
    Accumulates trajectories for in-context learning.
    Prepares training data format for future fine-tuning support.
    
    Example:
        learner = HindsightLearner(memory=memory_system)
        learner.accumulate(trajectory)
        
        # Check if batch learning should run
        if learner.should_run_batch():
            data = learner.prepare_training_data()
    """
    
    def __init__(
        self,
        memory: MemorySystem | None = None,
        config: LearningConfig | None = None,
    ):
        self._memory = memory
        self._config = config or LearningConfig()
        self._accumulated: list[Trajectory] = []
        self._last_batch_time: datetime | None = None
    
    def accumulate(self, trajectory: Trajectory) -> None:
        """Add trajectory to accumulator for batch learning."""
        self._accumulated.append(trajectory)
    
    def should_finetune(self) -> bool:
        """Check if fine-tuning should run.
        
        For SAGE-style, always returns False.
        """
        return False  # SAGE: no fine-tuning
    
    def should_run_batch(self) -> bool:
        """Check if batch learning should run.
        
        Checks:
        1. min_trajectories threshold met
        2. Optional time trigger (min_hours_since_last)
        3. Optional quality trigger (min_success_rate)
        """
        if len(self._accumulated) < self._config.min_trajectories:
            return False
        
        # Time trigger
        if self._config.min_hours_since_last is not None:
            if self._last_batch_time is not None:
                hours = (datetime.now() - self._last_batch_time).total_seconds() / 3600
                if hours < self._config.min_hours_since_last:
                    return False
        
        # Quality trigger
        if self._config.min_success_rate is not None:
            success_count = sum(1 for t in self._accumulated if t.outcome.success)
            success_rate = success_count / len(self._accumulated)
            if success_rate < self._config.min_success_rate:
                return False
        
        return True
    
    def prepare_training_data(
        self,
        trajectories: list[Trajectory] | None = None,
    ) -> dict[str, Any]:
        """Prepare SOAR-style training data.
        
        Formats trajectories into training examples for future
        fine-tuning support. Not used in SAGE mode.
        
        Returns:
            {
                "sampling": [...],     # Good solutions (2x weight)
                "refinement": [...],   # Key steps (1.5x weight)  
                "error": [...],        # Failures (1x weight)
            }
        """
        trajs = trajectories or self._accumulated
        
        sampling_data = []
        refinement_data = []
        error_data = []
        
        for traj in trajs:
            if traj.outcome.success:
                # Sampling: full solution
                sampling_data.append({
                    "input": self._format_task(traj.task),
                    "output": self._extract_solution(traj),
                    "weight": 2.0,
                })
                
                # Refinement: key steps
                for i, step in enumerate(traj.steps):
                    if self._is_key_step(traj, i):
                        refinement_data.append({
                            "input": self._format_with_history(traj, i),
                            "output": step.action,
                            "weight": 1.5,
                        })
            else:
                # Error: learn from failures
                if traj.outcome.error_info:
                    error_data.append({
                        "input": self._format_with_history(traj, len(traj.steps)),
                        "output": f"[ERROR] {traj.outcome.error_info}",
                        "weight": 1.0,
                    })
        
        return {
            "sampling": sampling_data,
            "refinement": refinement_data,
            "error": error_data,
        }
    
    def get_accumulated(self) -> list[Trajectory]:
        """Get accumulated trajectories."""
        return self._accumulated.copy()
    
    def clear_accumulated(self) -> None:
        """Clear accumulated trajectories after batch processing."""
        self._accumulated = []
        self._last_batch_time = datetime.now(timezone.utc)
    
    @property
    def accumulated_count(self) -> int:
        """Number of accumulated trajectories."""
        return len(self._accumulated)
```

## Files

- `src/atlas/learning/hindsight.py` - HindsightLearner
- `tests/unit/test_hindsight.py` - Comprehensive tests

## Tests

- accumulate adds trajectories
- should_finetune always returns False (SAGE)
- should_run_batch respects min_trajectories
- should_run_batch respects time trigger
- should_run_batch respects quality trigger
- prepare_training_data formats correctly
- clear_accumulated resets state
