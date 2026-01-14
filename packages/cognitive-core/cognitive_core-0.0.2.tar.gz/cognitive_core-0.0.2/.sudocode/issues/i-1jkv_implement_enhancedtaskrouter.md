---
id: i-1jkv
title: Implement EnhancedTaskRouter
priority: 2
created_at: '2026-01-08 06:00:23'
tags:
  - phase-5
  - router
  - search
status: open
---
# EnhancedTaskRouter Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] enhanced routing requirements.

## Goal

Replace BasicTaskRouter with smart routing based on task characteristics and configurable thresholds.

## Routing Logic

| Condition | Strategy | Rationale |
|-----------|----------|-----------|
| similarity > 0.9 + past success | `adapt` | High-confidence memory match |
| clear strategy match | `direct` | Apply strategy directly |
| ARC domain | `evolutionary` | Mind Evolution for fitness-based |
| SWE domain | `mcts` | SWE-Search for sequential edits |
| unknown/low confidence | configurable default | Usually `evolutionary` |

## Requirements

### 1. EnhancedTaskRouter Class

```python
class EnhancedTaskRouter:
    """Smart task routing based on task characteristics."""
    
    def __init__(
        self,
        config: RouterConfig | None = None,
    ):
        self._config = config or RouterConfig()
    
    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """Route task to appropriate search strategy.
        
        Decision process:
        1. Query memory for similar experiences
        2. Calculate similarity and check for success patterns
        3. Check domain for domain-specific routing
        4. Apply routing rules
        5. Return decision with context and budget
        """
        ...
```

### 2. Memory Analysis

```python
def _analyze_memory(
    self,
    task: Task,
    memory: MemorySystem,
) -> tuple[MemoryQueryResult, float, bool]:
    """Analyze memory for routing decision.
    
    Returns:
        (context, max_similarity, has_successful_similar)
    """
    context = memory.query(task, k=10)
    
    if context.is_empty():
        return context, 0.0, False
    
    # Calculate similarity scores
    max_similarity = self._calculate_max_similarity(task, context.experiences)
    
    # Check for successful similar experiences
    has_success = any(
        exp.success and self._is_similar(task, exp)
        for exp in context.experiences
    )
    
    return context, max_similarity, has_success
```

### 3. Similarity Calculation

```python
def _calculate_max_similarity(
    self,
    task: Task,
    experiences: list[Experience],
) -> float:
    """Calculate maximum similarity to past experiences.
    
    Uses embedding cosine similarity when available,
    falls back to text-based heuristics.
    """
    if not experiences:
        return 0.0
    
    max_sim = 0.0
    for exp in experiences:
        if task.embedding is not None and exp.embedding is not None:
            # Cosine similarity
            sim = np.dot(task.embedding, exp.embedding) / (
                np.linalg.norm(task.embedding) * np.linalg.norm(exp.embedding)
            )
        else:
            # Text-based fallback (simple word overlap)
            sim = self._text_similarity(task.description, exp.task_input)
        max_sim = max(max_sim, sim)
    
    return max_sim
```

### 4. Strategy Selection

```python
def _select_strategy(
    self,
    task: Task,
    similarity: float,
    has_success: bool,
    context: MemoryQueryResult,
) -> str:
    """Select search strategy based on analysis.
    
    Priority order:
    1. High similarity + success → adapt
    2. Strategy match → direct
    3. Domain routing → domain-specific
    4. Default → configured default
    """
    # Check for high-similarity adapt case
    if similarity >= self._config.similarity_threshold and has_success:
        return "adapt"
    
    # Check for strategy matches
    if context.strategies and self._has_strategy_match(task, context.strategies):
        return "direct"
    
    # Domain-based routing
    if self._config.use_domain_routing:
        if task.domain == "arc":
            return self._config.arc_strategy
        elif task.domain == "swe":
            return self._config.swe_strategy
    
    # Default
    return self._config.default_strategy
```

### 5. Budget Estimation

```python
def _estimate_budget(self, strategy: str, similarity: float) -> int:
    """Estimate LLM call budget for strategy.
    
    Higher similarity = lower budget (easier task).
    """
    base_budgets = {
        "adapt": 5,
        "direct": 10,
        "evolutionary": 100,
        "mcts": 200,
    }
    
    base = base_budgets.get(strategy, 100)
    
    # Reduce budget for high similarity
    if similarity > 0.8:
        return int(base * 0.5)
    elif similarity > 0.5:
        return int(base * 0.75)
    
    return base
```

### 6. Full Route Method

```python
def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
    """Route task to appropriate search strategy."""
    # Analyze memory
    context, similarity, has_success = self._analyze_memory(task, memory)
    
    # Select strategy
    strategy = self._select_strategy(task, similarity, has_success, context)
    
    # Estimate confidence and budget
    confidence = self._estimate_confidence(similarity, has_success, context)
    budget = self._estimate_budget(strategy, similarity)
    
    return RoutingDecision(
        strategy=strategy,
        context=context,
        confidence=confidence,
        budget=budget,
    )

def _estimate_confidence(
    self,
    similarity: float,
    has_success: bool,
    context: MemoryQueryResult,
) -> float:
    """Estimate confidence in routing decision."""
    base = similarity * 0.5
    
    if has_success:
        base += 0.3
    
    if context.strategies:
        base += 0.1
    
    return min(1.0, base)
```

## Files

- `src/atlas/search/router.py` - Add EnhancedTaskRouter (keep BasicTaskRouter)
- `tests/unit/test_router.py` - Update tests for both routers

## Tests

- Routes high-similarity success to "adapt"
- Routes ARC domain to "evolutionary"
- Routes SWE domain to "mcts"
- Routes unknown to default strategy
- Similarity calculation works with embeddings
- Similarity calculation falls back to text
- Budget estimation scales with similarity
- Confidence estimation is reasonable
- Implements TaskRouter protocol
- Configuration overrides work
