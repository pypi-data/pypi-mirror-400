"""ATLAS: Adaptive Trajectory Learning and Abstraction System.

A meta-learning framework that learns from agent trajectories to improve
task-solving performance over time.

Core Insight: The trajectory is the curriculum. Rather than designing tasks,
we let agents attempt tasks and learn from the resulting trajectories.
"""

__version__ = "0.1.0"

from cognitive_core.config import (
    ATLASConfig,
    EmbeddingConfig,
    ExecutorConfig,
    LearningConfig,
    MemoryConfig,
    StorageConfig,
)
from cognitive_core.core import (
    Candidate,
    Outcome,
    RoutingDecision,
    Step,
    Task,
    Trajectory,
)
from cognitive_core.solver import ATLASSolver

__all__ = [
    "__version__",
    # Configuration
    "ATLASConfig",
    "ExecutorConfig",
    "LearningConfig",
    "MemoryConfig",
    "EmbeddingConfig",
    "StorageConfig",
    # Core types
    "Trajectory",
    "Task",
    "Step",
    "Outcome",
    "Candidate",
    "RoutingDecision",
    # Solver
    "ATLASSolver",
]
