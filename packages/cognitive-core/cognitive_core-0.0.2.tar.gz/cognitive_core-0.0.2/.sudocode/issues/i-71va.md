---
id: i-71va
title: Implement full ARCEnvironment with arckit
priority: 1
created_at: '2026-01-08 05:58:45'
tags:
  - arc
  - environment
  - phase-5
relationships:
  - from_id: i-71va
    from_uuid: 3a78442c-8815-4ae3-885d-27ec562df508
    from_type: issue
    to_id: i-41zr
    to_uuid: 5288585c-26a9-40ad-90c7-e39909d9bece
    to_type: issue
    relationship_type: blocks
    created_at: '2026-01-08 06:00:47'
    metadata: null
  - from_id: i-71va
    from_uuid: 3a78442c-8815-4ae3-885d-27ec562df508
    from_type: issue
    to_id: s-6d5x
    to_uuid: 883e1201-e690-4a7d-99ce-20a045f37b4c
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-08 06:00:47'
    metadata: null
status: closed
closed_at: '2026-01-08 06:10:42'
---
# Full ARCEnvironment Implementation

Implements [[s-6d5x|Phase 5: Advanced Search]] ARCEnvironment requirements.

## Goal

Replace the ARCEnvironment stub with a full implementation using the `arckit` library.

## Requirements

### 1. Dependencies

Add to pyproject.toml:
```toml
arckit = ">=1.0.1"
```

### 2. ARCEnvironment Class

```python
class ARCEnvironment:
    """ARC-AGI environment with grid verification using arckit."""
    
    def __init__(self, dataset: str = "arc"):
        """
        Args:
            dataset: Which dataset to use ("arc", "kaggle2024", "kaggle2025")
        """
        self._task: Task | None = None
        self._arc_task: arckit.Task | None = None
        self._dataset = arckit.load_data(dataset)
    
    def reset(self, task: Task) -> str:
        """Load ARC task from dataset or task.context."""
        # Option 1: Load by task ID from arckit
        # Option 2: Parse grid data from task.context
        ...
    
    def verify(self, solution: Any) -> Outcome:
        """Verify grid solution.
        
        Args:
            solution: numpy array or list of lists representing output grid
            
        Returns:
            Outcome with:
            - success: True if exact match on all test pairs
            - partial_score: Cell-by-cell similarity (0.0-1.0)
        """
        ...
    
    @property
    def task(self) -> Task:
        if self._task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return self._task
    
    @property
    def training_pairs(self) -> list[tuple[np.ndarray, np.ndarray]]:
        """Get training input/output pairs for the current task."""
        ...
    
    @property
    def test_inputs(self) -> list[np.ndarray]:
        """Get test inputs for the current task."""
        ...
```

### 3. Grid Verification Logic

```python
def _verify_grid(self, predicted: np.ndarray, expected: np.ndarray) -> tuple[bool, float]:
    """Verify a single grid prediction.
    
    Returns:
        (exact_match, similarity_score)
    """
    if predicted.shape != expected.shape:
        return False, 0.0
    
    exact_match = np.array_equal(predicted, expected)
    
    # Cell-by-cell similarity for partial scoring
    total_cells = expected.size
    matching_cells = np.sum(predicted == expected)
    similarity = matching_cells / total_cells
    
    return exact_match, similarity
```

### 4. Task Loading

Support multiple ways to specify ARC tasks:
1. By arckit task ID in `task.context["arc_task_id"]`
2. By raw grid data in `task.context["grids"]`
3. By task description matching (for generated tasks)

## Files

- `src/atlas/environments/arc.py` - Full implementation
- `tests/unit/test_arc_environment.py` - Comprehensive tests
- `tests/integration/test_arc_environment.py` - Integration with arckit

## Tests

- Load task from arckit dataset
- Load task from context grids
- Verify exact match returns success=True
- Verify partial match returns correct similarity
- Handle shape mismatches gracefully
- Properties return correct values
