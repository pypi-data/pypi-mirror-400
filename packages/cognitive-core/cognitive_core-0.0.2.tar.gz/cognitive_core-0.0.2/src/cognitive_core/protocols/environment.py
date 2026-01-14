"""Environment protocol for ATLAS.

Environments are execution contexts where tasks are solved.
They follow a Gymnasium-like interface with built-in verification.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import Outcome, Task


@runtime_checkable
class Environment(Protocol):
    """Execution context where tasks are solved.

    Follows a Gymnasium-like interface for familiarity with RL practitioners.
    Key differences from standard Gym:
    - Verification is built-in, not external
    - Actions and observations are strings (for LLM compatibility)
    - Supports partial scoring for ranking and learning

    Example:
        ```python
        env = ARCEnvironment()
        obs = env.reset(task)
        while not done:
            action = agent.step(obs)
            obs, reward, done, info = env.step(action)
        outcome = env.verify(solution)
        ```
    """

    def reset(self, task: Task) -> str:
        """Reset the environment with a new task.

        Args:
            task: The task to solve

        Returns:
            Initial observation as a string
        """
        ...

    def step(self, action: str) -> tuple[str, float, bool, dict[str, Any]]:
        """Execute an action in the environment.

        Args:
            action: The action to take (as a string for LLM compatibility)

        Returns:
            A tuple of:
            - observation: Result/feedback from the action
            - reward: Immediate reward signal
            - done: Whether the episode has ended
            - info: Additional information (tool outputs, timing, etc.)
        """
        ...

    def verify(self, solution: Any) -> Outcome:
        """Verify a candidate solution.

        This enables self-contained testing and supports inference-time scaling
        via best-of-k selection.

        Args:
            solution: The solution to verify (domain-specific)

        Returns:
            Outcome with success status, partial score, and details
        """
        ...

    @property
    def max_steps(self) -> int:
        """Maximum steps before timeout.

        Returns:
            Maximum number of steps allowed in an episode
        """
        ...

    @property
    def is_deterministic(self) -> bool:
        """Whether the environment is deterministic.

        Deterministic environments enable reproducible testing.

        Returns:
            True if environment behavior is deterministic
        """
        ...

    @property
    def task(self) -> Task:
        """Current task being solved.

        Returns:
            The task that was set via reset()
        """
        ...
