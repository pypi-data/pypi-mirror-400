"""Environment adapters for ATLAS.

Execution contexts where tasks are solved. Follows Gymnasium-like interface.
Includes adapters for ARC and SWE environments.

Example:
    ```python
    from cognitive_core.environments import (
        ARCEnvironment,
        SWEEnvironment,
        create_environment,
    )

    # Auto-create based on task domain
    env = create_environment(task)

    # Or create specific environment
    arc_env = ARCEnvironment(dataset="arc")
    swe_env = SWEEnvironment()
    ```
"""

from __future__ import annotations

from cognitive_core.core.types import Task
from cognitive_core.protocols.environment import Environment

from .arc import (
    ARCEnvironment,
    ARCTask,
    Grid,
    format_arc_task,
    format_grid,
    load_arc_dataset,
    parse_grid_response,
)
from .base import PassthroughEnvironment
from .swe import DOCKER_AVAILABLE, SWEEnvironment

__all__ = [
    # Environments
    "ARCEnvironment",
    "PassthroughEnvironment",
    "SWEEnvironment",
    # Protocols
    "Environment",
    # Factory
    "create_environment",
    # ARC utilities
    "ARCTask",
    "Grid",
    "format_arc_task",
    "format_grid",
    "load_arc_dataset",
    "parse_grid_response",
    # SWE
    "DOCKER_AVAILABLE",
]


def create_environment(task: Task) -> Environment:
    """Create appropriate environment for task domain.

    Factory function that returns the correct environment implementation
    based on the task's domain.

    Args:
        task: The task that needs an execution environment

    Returns:
        An Environment implementation appropriate for the task domain:
        - ARCEnvironment for domain="arc"
        - SWEEnvironment for domain="swe"
        - PassthroughEnvironment for all other domains

    Example:
        ```python
        task = Task(id="1", domain="arc", description="...", verification=...)
        env = create_environment(task)  # Returns ARCEnvironment
        ```
    """
    if task.domain == "arc":
        # Extract dataset from task context if available
        dataset = task.context.get("arc_dataset", "arc")
        return ARCEnvironment(dataset=dataset)
    elif task.domain == "swe":
        return SWEEnvironment()
    return PassthroughEnvironment()
