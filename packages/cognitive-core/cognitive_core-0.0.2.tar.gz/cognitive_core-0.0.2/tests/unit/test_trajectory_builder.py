"""Tests for TrajectoryBuilder."""

from __future__ import annotations

import pytest

from cognitive_core.core.types import Outcome, Task, VerificationSpec
from cognitive_core.execution.trajectory_builder import TrajectoryBuilder


class TestTrajectoryBuilder:
    """Tests for TrajectoryBuilder class."""

    @pytest.fixture
    def task(self) -> Task:
        """Create a sample task."""
        return Task(
            id="task-001",
            domain="test",
            description="Test task",
            verification=VerificationSpec(method="test_suite"),
        )

    @pytest.fixture
    def builder(self, task: Task) -> TrajectoryBuilder:
        """Create a TrajectoryBuilder instance."""
        return TrajectoryBuilder(task, agent_id="test-agent")

    def test_init(self, builder: TrajectoryBuilder) -> None:
        """Test initialization."""
        assert builder.step_count == 0
        assert builder.steps == []

    def test_process_message_chunk(self, builder: TrajectoryBuilder) -> None:
        """Test processing agent message chunks."""
        update = {
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Let me analyze this..."},
        }

        result = builder.process_update(update)

        # Message chunks don't complete a step
        assert result is None
        assert builder.step_count == 0

    def test_process_thought_chunk(self, builder: TrajectoryBuilder) -> None:
        """Test processing agent thought chunks."""
        update = {
            "session_update": "agent_thought_chunk",
            "content": {"type": "text", "text": "Thinking about the problem..."},
        }

        result = builder.process_update(update)

        assert result is None
        assert builder.step_count == 0

    def test_process_tool_call(self, builder: TrajectoryBuilder) -> None:
        """Test processing a tool call."""
        update = {
            "session_update": "tool_call",
            "title": "Read",
            "arguments": {"file_path": "/tmp/test.py"},
            "id": "call-001",
        }

        result = builder.process_update(update)

        # Tool call alone doesn't complete a step
        assert result is None
        assert builder.step_count == 0

    def test_process_tool_complete_creates_step(self, builder: TrajectoryBuilder) -> None:
        """Test that tool completion creates a step."""
        # First, add thought
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Reading the file..."},
        })

        # Then, tool call
        builder.process_update({
            "session_update": "tool_call",
            "title": "Read",
            "arguments": {"file_path": "/tmp/test.py"},
            "id": "call-001",
        })

        # Finally, tool completion
        step = builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "file contents here",
        })

        assert step is not None
        assert builder.step_count == 1
        assert step.thought == "Reading the file..."
        assert "Read" in step.action
        assert step.observation == "file contents here"
        assert step.metadata["tool_name"] == "Read"

    def test_pending_tool_call_no_step(self, builder: TrajectoryBuilder) -> None:
        """Test that pending tool updates don't create steps."""
        builder.process_update({
            "session_update": "tool_call",
            "title": "Bash",
            "arguments": {"command": "ls"},
        })

        result = builder.process_update({
            "session_update": "tool_call_update",
            "status": "pending",
        })

        assert result is None
        assert builder.step_count == 0

    def test_multiple_steps(self, builder: TrajectoryBuilder) -> None:
        """Test building multiple steps."""
        # Step 1
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Step 1 thought"},
        })
        builder.process_update({
            "session_update": "tool_call",
            "title": "Read",
            "arguments": {},
        })
        builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "Result 1",
        })

        # Step 2
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Step 2 thought"},
        })
        builder.process_update({
            "session_update": "tool_call",
            "title": "Write",
            "arguments": {},
        })
        builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "Result 2",
        })

        assert builder.step_count == 2
        assert len(builder.steps) == 2
        assert builder.steps[0].thought == "Step 1 thought"
        assert builder.steps[1].thought == "Step 2 thought"

    def test_build_trajectory_success(self, builder: TrajectoryBuilder, task: Task) -> None:
        """Test building a successful trajectory."""
        # Add a step
        builder.process_update({
            "session_update": "tool_call",
            "title": "Read",
            "arguments": {},
        })
        builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "done",
        })

        outcome = Outcome(success=True)
        trajectory = builder.build(outcome)

        assert trajectory.task == task
        assert len(trajectory.steps) == 1
        assert trajectory.outcome.success is True
        assert trajectory.agent_id == "test-agent"
        assert "start_time" in trajectory.metadata
        assert "end_time" in trajectory.metadata
        assert "step_count" in trajectory.metadata
        assert "duration_seconds" in trajectory.metadata

    def test_build_trajectory_failure(self, builder: TrajectoryBuilder) -> None:
        """Test building a failed trajectory."""
        outcome = Outcome(success=False, error_info="Test error")
        trajectory = builder.build(outcome)

        assert trajectory.outcome.success is False
        assert trajectory.outcome.error_info == "Test error"

    def test_build_with_remaining_thought(self, builder: TrajectoryBuilder) -> None:
        """Test that remaining thoughts become final step."""
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Final message without tool call"},
        })

        outcome = Outcome(success=True)
        trajectory = builder.build(outcome)

        # Should have a step with just the thought
        assert len(trajectory.steps) == 1
        assert trajectory.steps[0].thought == "Final message without tool call"
        assert trajectory.steps[0].action == ""

    def test_accumulates_multiple_chunks(self, builder: TrajectoryBuilder) -> None:
        """Test that multiple message chunks are accumulated."""
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Part 1 "},
        })
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Part 2 "},
        })
        builder.process_update({
            "session_update": "agent_message_chunk",
            "content": {"type": "text", "text": "Part 3"},
        })

        builder.process_update({
            "session_update": "tool_call",
            "title": "Test",
            "arguments": {},
        })
        step = builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "done",
        })

        assert step.thought == "Part 1 Part 2 Part 3"

    def test_handles_dict_result(self, builder: TrajectoryBuilder) -> None:
        """Test handling dict results from tools."""
        builder.process_update({
            "session_update": "tool_call",
            "title": "Test",
            "arguments": {},
        })
        step = builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": {"key": "value", "nested": {"a": 1}},
        })

        # Should be JSON serialized
        assert "key" in step.observation
        assert "value" in step.observation

    def test_handles_camel_case_keys(self, builder: TrajectoryBuilder) -> None:
        """Test handling camelCase update keys (ACP compatibility)."""
        update = {
            "sessionUpdate": "tool_call",  # camelCase
            "title": "Read",
            "arguments": {},
        }

        builder.process_update(update)

        update2 = {
            "sessionUpdate": "tool_call_update",
            "status": "completed",
            "result": "done",
        }

        step = builder.process_update(update2)
        assert step is not None

    def test_tool_call_without_prior_thought(self, builder: TrajectoryBuilder) -> None:
        """Test tool call without preceding thought."""
        builder.process_update({
            "session_update": "tool_call",
            "title": "Bash",
            "arguments": {"command": "ls"},
        })
        step = builder.process_update({
            "session_update": "tool_call_update",
            "status": "completed",
            "result": "file1.txt",
        })

        # Should still create a step with empty thought
        assert step is not None
        assert step.thought == ""
        assert "Bash" in step.action

    def test_unknown_update_type_ignored(self, builder: TrajectoryBuilder) -> None:
        """Test that unknown update types are ignored."""
        result = builder.process_update({
            "session_update": "unknown_type",
            "data": "whatever",
        })

        assert result is None
        assert builder.step_count == 0

    def test_metadata_includes_duration(self, builder: TrajectoryBuilder) -> None:
        """Test that trajectory metadata includes duration."""
        outcome = Outcome(success=True)
        trajectory = builder.build(outcome)

        assert "duration_seconds" in trajectory.metadata
        assert trajectory.metadata["duration_seconds"] >= 0
