---
id: i-9lmj
title: Implement SWESearch (MCTS)
priority: 2
created_at: '2026-01-08 06:00:23'
tags:
  - mcts
  - phase-5
  - search
  - swe
relationships:
  - from_id: i-9lmj
    from_uuid: 27ed0f7f-d5f3-4e8f-8997-b38ec18de847
    from_type: issue
    to_id: i-1jkv
    to_uuid: e4741794-93ee-4b9d-ad88-86b78a9c84ff
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 06:18:13'
    metadata: null
  - from_id: i-9lmj
    from_uuid: 27ed0f7f-d5f3-4e8f-8997-b38ec18de847
    from_type: issue
    to_id: s-6d5x
    to_uuid: 883e1201-e690-4a7d-99ce-20a045f37b4c
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 06:18:13'
    metadata: null
status: closed
closed_at: '2026-01-08 06:18:13'
---
# SWESearch (MCTS) Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] SWESearch requirements.

## Goal

Implement Monte Carlo Tree Search for SWE tasks with sequential decision making.

## Algorithm Overview

```
1. Initialize root with task state
2. For each expansion (up to max_expansions):
   a. Select leaf via UCB traversal
   b. Expand with LLM-generated actions
   c. Estimate value (hybrid: discriminator + selective rollout)
   d. Backpropagate value to ancestors
3. Return best path from root to leaf
```

**Cost:** ~200-500 LLM calls per task (with hybrid value estimation)

## Requirements

### 1. MCTSNode Class

```python
@dataclass
class MCTSNode:
    """Node in the MCTS tree."""
    state: str  # Current code/repo state description
    action: str | None  # Action that led to this state
    parent: MCTSNode | None
    children: list[MCTSNode] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0
    candidate: Candidate | None = None
    
    @property
    def ucb_score(self) -> float:
        """Upper Confidence Bound score."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.value / self.visits
        exploration = sqrt(2 * log(self.parent.visits) / self.visits)
        return exploitation + self._ucb_constant * exploration
    
    def best_child(self) -> MCTSNode:
        """Select child with highest UCB score."""
        return max(self.children, key=lambda c: c.ucb_score)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
```

### 2. SWESearch Class

```python
class SWESearch:
    """MCTS-based search for SWE tasks."""
    
    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,
        discriminator: Discriminator | None = None,
        config: SWESearchConfig | None = None,
    ):
        self._memory = memory
        self._llm = llm
        self._executor = executor
        self._discriminator = discriminator
        self._config = config or SWESearchConfig()
    
    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Run MCTS search."""
        root = self._create_root(task, env)
        
        for _ in range(self._config.max_expansions):
            # Selection
            leaf = self._select(root)
            
            # Expansion
            if leaf.visits > 0 and not self._is_terminal(leaf):
                children = self._expand(leaf, task, env)
                leaf.children.extend(children)
                if children:
                    leaf = children[0]
            
            # Value estimation (hybrid)
            value = self._estimate_value(leaf, task, env)
            
            # Backpropagation
            self._backpropagate(leaf, value)
            
            # Early termination on success
            if value >= 1.0:
                break
        
        return self._extract_best_candidates(root, task)
    
    def refine(self, candidate: Candidate, feedback: str, task: Task) -> Candidate:
        """Refine via targeted action generation."""
        ...
    
    @property
    def name(self) -> str:
        return "mcts"
```

### 3. UCB Selection

```python
def _select(self, node: MCTSNode) -> MCTSNode:
    """Select leaf node via UCB traversal."""
    current = node
    while not current.is_leaf() and current.visits > 0:
        current = current.best_child()
    return current
```

### 4. Expansion (LLM-based)

```python
def _expand(
    self,
    node: MCTSNode,
    task: Task,
    env: Environment,
) -> list[MCTSNode]:
    """Expand node with LLM-generated actions.
    
    Prompt asks for possible next actions given current state.
    """
    prompt = f'''You are debugging a software issue.

Task: {task.description}

Current state:
{node.state}

What are the most promising next actions to take? 
Generate 2-4 distinct actions (patches, commands, or investigations).
Format each as:
ACTION: <description>
CONTENT: <patch or command>
---
'''
    
    response = self._llm.generate(prompt)
    actions = self._parse_actions(response)
    
    children = []
    for action in actions:
        # Simulate action to get new state
        new_state = self._simulate_action(node.state, action, env)
        child = MCTSNode(
            state=new_state,
            action=action,
            parent=node,
        )
        children.append(child)
    
    return children
```

### 5. Hybrid Value Estimation

```python
def _estimate_value(
    self,
    node: MCTSNode,
    task: Task,
    env: Environment,
) -> float:
    """Hybrid value estimation.
    
    1. Use discriminator for initial estimate
    2. If promising (above threshold), do agent rollout
    """
    # Create candidate from node
    candidate = self._node_to_candidate(node)
    
    if self._discriminator and self._config.use_discriminator:
        # Quick LLM-based estimate
        quick_score = self._discriminator.estimate(task, candidate)
        
        # If promising, do expensive rollout
        if self._discriminator.should_rollout(quick_score, self._config.discriminator_threshold):
            return self._discriminator.estimate_with_rollout(
                task, candidate, env, depth=self._config.rollout_depth
            )
        return quick_score
    
    # Fallback: direct verification
    outcome = env.verify(candidate.solution)
    return outcome.partial_score or 0.0
```

### 6. Backpropagation

```python
def _backpropagate(self, node: MCTSNode, value: float) -> None:
    """Backpropagate value to ancestors."""
    current = node
    while current is not None:
        current.visits += 1
        current.value += value
        current = current.parent
```

### 7. Best Path Extraction

```python
def _extract_best_candidates(
    self,
    root: MCTSNode,
    task: Task,
) -> list[Candidate]:
    """Extract best candidates from tree.
    
    Follow highest-value path and collect candidates.
    """
    candidates = []
    current = root
    
    while current.children:
        # Select best child by average value
        best = max(current.children, key=lambda c: c.value / max(c.visits, 1))
        if best.candidate:
            candidates.append(best.candidate)
        current = best
    
    # Sort by fitness
    candidates.sort(key=lambda c: c.fitness or 0.0, reverse=True)
    return candidates
```

## Files

- `src/atlas/search/mcts.py` - SWESearch and MCTSNode
- `tests/unit/test_mcts.py` - Unit tests

## Tests

- UCB selection explores and exploits
- Expansion generates valid actions
- Value estimation uses hybrid approach
- Backpropagation updates ancestors
- Best path extraction works
- Early termination on success
- Respects max_depth limit
- Implements SearchEngine protocol
