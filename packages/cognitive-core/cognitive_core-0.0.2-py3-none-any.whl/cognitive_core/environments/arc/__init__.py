"""ARC (Abstraction and Reasoning Corpus) environment module.

Provides environment, types, and utilities for working with ARC grid tasks.

Example:
    ```python
    from cognitive_core.environments.arc import (
        ARCEnvironment,
        ARCTask,
        format_arc_task,
        load_arc_dataset,
        parse_grid_response,
    )

    # Load dataset
    train_tasks, eval_tasks = load_arc_dataset("arc")

    # Create environment
    env = ARCEnvironment(dataset="arc")

    # Format task for agent
    prompt = format_arc_task(train_tasks[0])

    # Parse agent response
    grids = parse_grid_response(agent_output)
    ```
"""

from cognitive_core.environments.arc.environment import ARCEnvironment
from cognitive_core.environments.arc.loader import (
    clear_dataset_cache,
    find_task_by_id,
    load_arc_dataset,
    load_arc_tasks_from_directory,
    load_arc_tasks_from_json,
)
from cognitive_core.environments.arc.types import ARCTask, Grid
from cognitive_core.environments.arc.utils import (
    ARC_COLORS,
    format_arc_task,
    format_grid,
    parse_grid_response,
    verify_grid,
)

__all__ = [
    # Environment
    "ARCEnvironment",
    # Types
    "ARCTask",
    "Grid",
    # Loading
    "clear_dataset_cache",
    "find_task_by_id",
    "load_arc_dataset",
    "load_arc_tasks_from_directory",
    "load_arc_tasks_from_json",
    # Utilities
    "ARC_COLORS",
    "format_arc_task",
    "format_grid",
    "parse_grid_response",
    "verify_grid",
]
