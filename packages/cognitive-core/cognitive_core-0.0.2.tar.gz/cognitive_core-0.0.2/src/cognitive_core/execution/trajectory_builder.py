"""TrajectoryBuilder for converting ACP session updates to ATLAS trajectories.

Uses tool-centric mapping: each tool_call + tool_call_update = one Step.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from cognitive_core.core.types import Outcome, Step, Task, Trajectory

logger = logging.getLogger("cognitive_core.execution")


class TrajectoryBuilder:
    """Builds Trajectory from ACP session updates.

    Uses tool-centric mapping where each tool call becomes a Step:
    - agent_message_chunk (before tool) → step.thought
    - tool_call → step.action
    - tool_call_update (completed) → step.observation

    Example:
        ```python
        builder = TrajectoryBuilder(task, agent_id="claude-code")

        async for update in session.prompt(prompt):
            builder.process_update(update)

        trajectory = builder.build(outcome)
        ```
    """

    def __init__(self, task: Task, agent_id: str) -> None:
        """Initialize the trajectory builder.

        Args:
            task: The task being executed.
            agent_id: Identifier for the agent (e.g., "claude-code").
        """
        self._task = task
        self._agent_id = agent_id
        self._steps: list[Step] = []
        self._current_thought_chunks: list[str] = []
        self._current_tool_call: dict[str, Any] | None = None
        self._start_time = datetime.now(timezone.utc)

    def process_update(self, update: dict[str, Any]) -> Step | None:
        """Process a single session update.

        Args:
            update: ACP session update dict.

        Returns:
            A Step if one was completed, None otherwise.
        """
        update_type = update.get("session_update") or update.get("sessionUpdate")

        if update_type == "agent_message_chunk":
            self._handle_message_chunk(update)
        elif update_type == "tool_call":
            self._handle_tool_call(update)
        elif update_type == "tool_call_update":
            return self._handle_tool_update(update)
        elif update_type == "agent_thought_chunk":
            self._handle_thought_chunk(update)

        return None

    def _handle_message_chunk(self, update: dict[str, Any]) -> None:
        """Accumulate agent text as thought."""
        content = update.get("content", {})
        if content.get("type") == "text":
            text = content.get("text", "")
            if text:
                self._current_thought_chunks.append(text)

    def _handle_thought_chunk(self, update: dict[str, Any]) -> None:
        """Handle agent thinking/reasoning chunks."""
        content = update.get("content", {})
        if content.get("type") == "text":
            text = content.get("text", "")
            if text:
                # Prefix thinking with indicator
                self._current_thought_chunks.append(f"[thinking] {text}")

    def _handle_tool_call(self, update: dict[str, Any]) -> None:
        """Start tracking a new tool call."""
        # Extract tool information
        tool_name = update.get("title") or update.get("name") or "unknown"

        # Arguments might be in different places
        args = update.get("arguments") or update.get("input") or {}

        self._current_tool_call = {
            "name": tool_name,
            "args": args,
            "id": update.get("id") or update.get("tool_call_id"),
        }

        logger.debug("Tool call started", extra={"tool": tool_name})

    def _handle_tool_update(self, update: dict[str, Any]) -> Step | None:
        """Complete a step when tool finishes.

        Returns:
            The completed Step, or None if no tool was active.
        """
        status = update.get("status")

        # Only create step on completion
        if status != "completed":
            return None

        if self._current_tool_call is None:
            logger.warning("Tool update without active tool call")
            return None

        # Get result
        result = update.get("result") or update.get("output") or ""
        if isinstance(result, dict):
            result = json.dumps(result, indent=2)

        # Build the step
        thought = "".join(self._current_thought_chunks).strip()

        # Format action as tool name with args
        tool_name = self._current_tool_call["name"]
        tool_args = self._current_tool_call["args"]

        if isinstance(tool_args, dict):
            args_str = json.dumps(tool_args)
        else:
            args_str = str(tool_args)

        action = f"{tool_name}({args_str})"

        step = Step(
            thought=thought,
            action=action,
            observation=str(result),
            metadata={
                "tool_name": tool_name,
                "tool_id": self._current_tool_call.get("id"),
            },
        )

        self._steps.append(step)

        # Reset for next step
        self._current_thought_chunks = []
        self._current_tool_call = None

        logger.debug(
            "Step completed",
            extra={"tool": tool_name, "step_count": len(self._steps)},
        )

        return step

    def build(self, outcome: Outcome) -> Trajectory:
        """Finalize and return the trajectory.

        Args:
            outcome: The outcome of the task execution.

        Returns:
            Complete Trajectory with all steps and metadata.
        """
        # Handle any remaining thought without a completed tool call
        # This could be final reasoning or error message
        if self._current_thought_chunks:
            final_thought = "".join(self._current_thought_chunks).strip()
            if final_thought:
                # Create a final step with just thought (no action)
                final_step = Step(
                    thought=final_thought,
                    action="",
                    observation="",
                    metadata={"type": "final_message"},
                )
                self._steps.append(final_step)

        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - self._start_time).total_seconds()

        trajectory = Trajectory(
            task=self._task,
            steps=self._steps,
            outcome=outcome,
            agent_id=self._agent_id,
            wall_time_seconds=duration_seconds,
            metadata={
                "start_time": self._start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration_seconds,
                "step_count": len(self._steps),
            },
        )

        logger.info(
            "Trajectory built",
            extra={
                "task_id": self._task.id,
                "steps": len(self._steps),
                "success": outcome.success,
                "duration": duration_seconds,
            },
        )

        return trajectory

    @property
    def step_count(self) -> int:
        """Number of completed steps so far."""
        return len(self._steps)

    @property
    def steps(self) -> list[Step]:
        """Current list of completed steps."""
        return list(self._steps)
