"""Agent protocol for ATLAS.

Agents are actors that produce trajectories by attempting to solve tasks.
They can be external (Claude Code, OpenHands) or ATLAS-native.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import Task, Trajectory
    from cognitive_core.protocols.environment import Environment


@runtime_checkable
class Agent(Protocol):
    """Actor that produces trajectories.

    Agents interact with environments to solve tasks. They maintain internal
    state that is reset between tasks.

    Types of agents:
    - External: Wrapped versions of Claude Code, OpenHands, SWE-agent
    - ATLAS-native: Memory-augmented agents with library awareness

    Example:
        ```python
        agent = ATLASAgent(memory=memory, llm=llm)
        trajectory = agent.solve(task, env)
        ```
    """

    def solve(self, task: Task, env: Environment) -> Trajectory:
        """Attempt to solve a task, producing a complete trajectory.

        This is the main entry point for task solving. The agent will:
        1. Reset its internal state
        2. Interact with the environment until done or max_steps
        3. Return the complete trajectory

        Args:
            task: The task to solve
            env: The environment to solve it in

        Returns:
            Complete trajectory including all steps and outcome
        """
        ...

    def step(self, observation: str) -> str:
        """Given an observation, return the next action.

        This is called repeatedly during solving. The agent should:
        1. Process the observation
        2. Decide on the next action
        3. Return the action as a string

        Args:
            observation: Current observation from environment

        Returns:
            Action to take
        """
        ...

    def reset(self) -> None:
        """Reset agent state.

        Called before starting a new task. Should clear any
        episode-specific state while preserving learned knowledge.
        """
        ...

    @property
    def agent_id(self) -> str:
        """Unique identifier for this agent.

        Used for tracking which agent produced which trajectories.

        Returns:
            Agent identifier string
        """
        ...
