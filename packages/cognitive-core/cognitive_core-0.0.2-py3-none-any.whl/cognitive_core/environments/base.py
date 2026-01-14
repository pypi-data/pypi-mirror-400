"""Base environment implementations for ATLAS.

Provides default implementations for when no domain-specific verification is needed.
"""

from __future__ import annotations

from typing import Any

from cognitive_core.core.types import Outcome, Task
from cognitive_core.protocols.environment import Environment


class PassthroughEnvironment:
    """Default environment when no domain-specific verification is needed.

    This environment passes actions through without modification and always
    reports success on verification. Used when the agent determines its own
    success criteria.

    Example:
        ```python
        env = PassthroughEnvironment()
        obs = env.reset(task)
        outcome = env.verify(solution)  # Always succeeds
        ```
    """

    def __init__(self) -> None:
        """Initialize PassthroughEnvironment with no task."""
        self._task: Task | None = None

    def reset(self, task: Task) -> str:
        """Reset the environment with a new task.

        Args:
            task: The task to solve

        Returns:
            Initial observation as the task description
        """
        self._task = task
        return task.description

    def step(self, action: str) -> tuple[str, float, bool, dict[str, Any]]:
        """Execute an action in the environment.

        For PassthroughEnvironment, this simply returns the action as the
        observation with no reward and never terminates.

        Args:
            action: The action to take

        Returns:
            A tuple of (action, 0.0, False, {})
        """
        return (action, 0.0, False, {})

    def verify(self, solution: Any) -> Outcome:
        """Verify a candidate solution.

        PassthroughEnvironment always returns success since verification
        is delegated to the agent.

        Args:
            solution: The solution to verify (ignored)

        Returns:
            Outcome with success=True and partial_score=1.0
        """
        return Outcome(success=True, partial_score=1.0)

    @property
    def max_steps(self) -> int:
        """Maximum steps before timeout.

        Returns:
            100 (default maximum steps)
        """
        return 100

    @property
    def is_deterministic(self) -> bool:
        """Whether the environment is deterministic.

        Returns:
            True (PassthroughEnvironment is always deterministic)
        """
        return True

    @property
    def task(self) -> Task:
        """Current task being solved.

        Returns:
            The task that was set via reset()

        Raises:
            RuntimeError: If reset() has not been called
        """
        if self._task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return self._task
