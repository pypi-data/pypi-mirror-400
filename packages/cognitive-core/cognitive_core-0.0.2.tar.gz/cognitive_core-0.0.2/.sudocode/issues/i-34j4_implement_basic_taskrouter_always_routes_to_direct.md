---
id: i-34j4
title: Implement basic TaskRouter (always routes to DirectSolver)
priority: 1
created_at: '2026-01-08 02:11:54'
tags:
  - phase-4
  - router
  - search
status: open
---
# Basic TaskRouter Implementation

Implements [[s-2uov|Phase 4: Minimal Solver]] TaskRouter requirements.

## Goal

Create a minimal TaskRouter that makes basic routing decisions. For Phase 4, it always routes to DirectSolver.

## Requirements

### 1. Routing Logic v1

Per spec: initially always route to DirectSolver.

```python
class BasicTaskRouter(TaskRouter):
    def __init__(self, memory: MemorySystem):
        self._memory = memory
    
    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        # Query memory for context
        result = memory.query(task, k=5)
        
        # Calculate similarity/confidence
        similarity = self._estimate_similarity(result)
        
        # v1: Always use direct strategy
        return RoutingDecision(
            strategy="direct",
            context=result,
            confidence=similarity,
            budget=5,  # Max LLM calls
        )
```

### 2. RoutingDecision Type

Ensure core types include:
```python
@dataclass
class RoutingDecision:
    strategy: str  # "direct", "evolutionary", "mcts", "adapt"
    context: MemoryQueryResult  # Retrieved experiences/strategies
    confidence: float  # 0-1 confidence in strategy
    budget: int  # Max iterations/calls for search
```

### 3. Future Expansion Points

Structure for future routing logic:
```python
def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
    result = memory.query(task, k=5)
    similarity = self._estimate_similarity(result)
    
    # Future: more sophisticated routing
    # if similarity > 0.8 and has_success:
    #     strategy = "adapt"
    # elif task.domain == "arc":
    #     strategy = "evolutionary"
    # elif task.domain == "swe":
    #     strategy = "mcts"
    # else:
    #     strategy = "direct"
    
    return RoutingDecision(strategy="direct", ...)
```

## Files

```
atlas/search/
├── __init__.py
├── router.py         # BasicTaskRouter
├── direct.py
└── verifier.py
```

## Tests

- Router queries memory
- Always returns "direct" strategy
- RoutingDecision has required fields
- Works with empty memory
