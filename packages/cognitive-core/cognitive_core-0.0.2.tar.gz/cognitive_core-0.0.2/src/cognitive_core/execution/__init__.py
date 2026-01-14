"""Execution layer for ATLAS.

Provides TaskExecutor and supporting components for running tasks
via ACP agents and building trajectories.
"""

from cognitive_core.execution.executor import TaskExecutor
from cognitive_core.execution.prompt_formatter import PromptFormatter
from cognitive_core.execution.trajectory_builder import TrajectoryBuilder

__all__ = [
    "TaskExecutor",
    "TrajectoryBuilder",
    "PromptFormatter",
]
