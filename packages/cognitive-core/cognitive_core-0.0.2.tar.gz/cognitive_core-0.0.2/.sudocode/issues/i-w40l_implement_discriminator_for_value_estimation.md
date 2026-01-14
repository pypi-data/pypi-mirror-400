---
id: i-w40l
title: Implement Discriminator for value estimation
priority: 2
created_at: '2026-01-08 06:00:23'
tags:
  - discriminator
  - phase-5
  - search
  - value-estimation
status: open
---
# Discriminator Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] Discriminator requirements.

## Goal

Implement hybrid value estimation for MCTS and population pruning.

## Overview

The Discriminator provides two estimation methods:
1. **Quick LLM estimate** - Single LLM call to estimate quality (~1 call)
2. **Agent rollout** - Run partial agent execution for high-confidence estimate (~5-50 calls)

The hybrid approach uses quick estimates for all nodes, then expensive rollouts only for promising candidates (top 10-20%).

## Requirements

### 1. Discriminator Class

```python
class Discriminator:
    """Estimates solution quality for MCTS and pruning."""
    
    def __init__(
        self,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,
    ):
        self._llm = llm
        self._executor = executor
    
    def estimate(self, task: Task, candidate: Candidate) -> float:
        """Quick LLM-based quality estimation.
        
        Returns:
            Estimated quality score (0.0-1.0)
        """
        ...
    
    def estimate_with_rollout(
        self,
        task: Task,
        candidate: Candidate,
        env: Environment,
        depth: int = 5,
    ) -> float:
        """Agent rollout for high-confidence estimation.
        
        Args:
            task: The task being solved
            candidate: Current candidate/state
            env: Environment for execution
            depth: Number of steps to roll out
            
        Returns:
            Estimated quality based on rollout outcome
        """
        ...
    
    def should_rollout(self, score: float, threshold: float = 0.7) -> bool:
        """Decide if candidate warrants expensive rollout.
        
        Args:
            score: Quick estimate score
            threshold: Minimum score to trigger rollout
            
        Returns:
            True if rollout is warranted
        """
        return score >= threshold
    
    def batch_estimate(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[float]:
        """Estimate quality for multiple candidates efficiently."""
        ...
```

### 2. LLM-based Estimation

```python
def estimate(self, task: Task, candidate: Candidate) -> float:
    """Quick LLM-based quality estimation."""
    prompt = f'''Evaluate the quality of this solution attempt.

Task: {task.description}

Solution/Approach:
{candidate.solution}

Reasoning provided:
{candidate.reasoning}

Rate the likelihood this solution is correct on a scale of 0.0 to 1.0.
Consider:
- Does it address the core problem?
- Is the approach sound?
- Are there obvious errors?

Return only a decimal number between 0.0 and 1.0.
'''
    
    response = self._llm.generate(prompt, temperature=0.0)
    
    try:
        score = float(response.strip())
        return max(0.0, min(1.0, score))
    except ValueError:
        return 0.5  # Default to uncertain
```

### 3. Agent Rollout Estimation

```python
async def estimate_with_rollout(
    self,
    task: Task,
    candidate: Candidate,
    env: Environment,
    depth: int = 5,
) -> float:
    """Run partial agent execution for estimation.
    
    Executes up to `depth` steps and evaluates the outcome.
    """
    if self._executor is None:
        # Fall back to LLM estimate
        return self.estimate(task, candidate)
    
    # Create a sub-task starting from candidate's state
    sub_task = self._create_continuation_task(task, candidate)
    
    try:
        # Run executor with limited steps
        trajectory = await self._executor.execute(
            sub_task,
            env,
            max_steps=depth,
        )
        
        # Score based on trajectory outcome
        if trajectory.outcome.success:
            return 1.0
        return trajectory.outcome.partial_score or 0.0
        
    except Exception:
        return 0.0
```

### 4. Batch Estimation

```python
def batch_estimate(
    self,
    task: Task,
    candidates: list[Candidate],
) -> list[float]:
    """Estimate quality for multiple candidates.
    
    Uses a single LLM call for efficiency when possible.
    """
    if len(candidates) <= 3:
        # Few candidates - individual calls
        return [self.estimate(task, c) for c in candidates]
    
    # Many candidates - batch prompt
    prompt = f'''Evaluate these solution attempts for the task.

Task: {task.description}

Solutions:
'''
    for i, c in enumerate(candidates):
        prompt += f"\n[{i+1}] {c.solution[:200]}...\n"
    
    prompt += '''
Rate each solution from 0.0 to 1.0.
Return as: 1: 0.X, 2: 0.X, 3: 0.X, ...
'''
    
    response = self._llm.generate(prompt)
    return self._parse_batch_scores(response, len(candidates))
```

## Files

- `src/atlas/search/discriminator.py` - Discriminator class
- `tests/unit/test_discriminator.py` - Unit tests

## Tests

- LLM estimate returns valid score (0.0-1.0)
- Handles malformed LLM responses gracefully
- should_rollout respects threshold
- Rollout estimation runs limited steps
- Batch estimation works for multiple candidates
- Falls back gracefully when executor unavailable
