"""Tests for TaskExecutor."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from cognitive_core.config import ATLASConfig, ExecutorConfig
from cognitive_core.core.types import Outcome, Task, VerificationSpec
from cognitive_core.execution.executor import TaskExecutor


class MockSession:
    """Mock ACP Session for testing."""

    def __init__(
        self,
        session_id: str = "session-001",
        updates: list[dict[str, Any]] | None = None,
    ):
        self._id = session_id
        self._updates = updates or []
        self._cancelled = False

    @property
    def id(self) -> str:
        return self._id

    async def prompt(self, content: str) -> AsyncIterator[dict[str, Any]]:
        """Yield mock session updates."""
        for update in self._updates:
            if self._cancelled:
                break
            yield update

    async def cancel(self) -> None:
        """Cancel the session."""
        self._cancelled = True

    async def fork(self) -> MockSession:
        """Fork the session."""
        return MockSession(f"{self._id}-fork", self._updates)


class MockAgentHandle:
    """Mock ACP AgentHandle for testing."""

    def __init__(self, session: MockSession | None = None):
        self._session = session or MockSession()
        self._running = True
        self._closed = False

    def is_running(self) -> bool:
        return self._running and not self._closed

    async def create_session(
        self, cwd: str, options: Any = None
    ) -> MockSession:
        return self._session

    async def close(self) -> None:
        self._closed = True
        self._running = False


class TestTaskExecutor:
    """Tests for TaskExecutor class."""

    @pytest.fixture
    def task(self) -> Task:
        """Create a sample task."""
        return Task(
            id="task-001",
            domain="test",
            description="Fix the authentication bug",
            context={"cwd": "/tmp/project"},
            verification=VerificationSpec(method="test_suite"),
        )

    @pytest.fixture
    def config(self) -> ATLASConfig:
        """Create a test configuration."""
        return ATLASConfig(
            executor=ExecutorConfig(
                agent_type="test-agent",
                timeout_seconds=10,
                reuse_sessions=False,
            ),
        )

    @pytest.fixture
    def successful_updates(self) -> list[dict[str, Any]]:
        """Create updates for a successful execution."""
        return [
            {
                "session_update": "agent_message_chunk",
                "content": {"type": "text", "text": "Analyzing the bug..."},
            },
            {
                "session_update": "tool_call",
                "title": "Read",
                "arguments": {"file_path": "/tmp/auth.py"},
                "id": "call-001",
            },
            {
                "session_update": "tool_call_update",
                "status": "completed",
                "result": "def login(): ...",
            },
            {
                "session_update": "agent_message_chunk",
                "content": {"type": "text", "text": "Found the issue."},
            },
            {
                "session_update": "tool_call",
                "title": "Edit",
                "arguments": {"file_path": "/tmp/auth.py"},
                "id": "call-002",
            },
            {
                "session_update": "tool_call_update",
                "status": "completed",
                "result": "File edited successfully",
            },
        ]

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        executor = TaskExecutor()

        assert executor._config is not None
        assert executor._memory is None
        assert executor._agent_handle is None

    def test_init_custom_config(self, config: ATLASConfig) -> None:
        """Test initialization with custom config."""
        executor = TaskExecutor(config=config)

        assert executor._config.executor.agent_type == "test-agent"
        assert executor._config.executor.timeout_seconds == 10

    @pytest.mark.asyncio
    async def test_execute_basic(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test basic task execution."""
        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        # Mock the agent spawning
        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task)

        assert trajectory is not None
        assert trajectory.task == task
        assert len(trajectory.steps) == 2  # Two tool completions
        assert trajectory.agent_id == "test-agent"

    @pytest.mark.asyncio
    async def test_execute_collects_steps(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test that execution collects steps correctly."""
        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task)

        # Check step content
        assert trajectory.steps[0].thought == "Analyzing the bug..."
        assert "Read" in trajectory.steps[0].action
        assert "login" in trajectory.steps[0].observation

    @pytest.mark.asyncio
    async def test_execute_timeout(self, task: Task) -> None:
        """Test execution timeout handling."""
        # Create updates that would take too long
        async def slow_updates() -> AsyncIterator[dict[str, Any]]:
            yield {"session_update": "agent_message_chunk", "content": {"type": "text", "text": "Starting..."}}
            await asyncio.sleep(10)  # Simulate long-running operation
            yield {"session_update": "tool_call", "title": "Read", "arguments": {}}

        session = MockSession()
        session.prompt = lambda _: slow_updates()  # type: ignore

        agent = MockAgentHandle(session)

        config = ATLASConfig(
            executor=ExecutorConfig(timeout_seconds=1),  # 1 second timeout
        )
        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task)

        assert trajectory.outcome.success is False
        assert "timeout" in trajectory.outcome.error_info.lower()

    @pytest.mark.asyncio
    async def test_execute_handles_agent_error(self, task: Task, config: ATLASConfig) -> None:
        """Test handling of agent errors."""
        executor = TaskExecutor(config=config)

        # Mock get_agent to raise an error
        with patch.object(executor, "_get_agent", side_effect=Exception("Agent spawn failed")):
            trajectory = await executor.execute(task)

        assert trajectory.outcome.success is False
        assert "Agent spawn failed" in trajectory.outcome.error_info

    @pytest.mark.asyncio
    async def test_close(self, config: ATLASConfig) -> None:
        """Test closing the executor."""
        agent = MockAgentHandle()
        executor = TaskExecutor(config=config)
        executor._agent_handle = agent

        await executor.close()

        assert agent._closed is True
        assert executor._agent_handle is None

    @pytest.mark.asyncio
    async def test_context_manager(self, config: ATLASConfig) -> None:
        """Test async context manager usage."""
        agent = MockAgentHandle()

        async with TaskExecutor(config=config) as executor:
            executor._agent_handle = agent
            assert executor.is_agent_running

        # Agent should be closed after exiting context
        assert agent._closed is True

    @pytest.mark.asyncio
    async def test_execute_with_session(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test execution with an existing session."""
        session = MockSession(updates=successful_updates)
        executor = TaskExecutor(config=config)

        trajectory = await executor.execute_with_session(task, session)

        assert trajectory is not None
        assert len(trajectory.steps) == 2

    @pytest.mark.asyncio
    async def test_fork_and_execute(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test fork and execute."""
        session = MockSession(updates=successful_updates)
        executor = TaskExecutor(config=config)

        trajectory = await executor.fork_and_execute(task, session)

        assert trajectory is not None
        # Should have used forked session
        assert trajectory.task == task

    @pytest.mark.asyncio
    async def test_session_reuse_disabled(
        self,
        task: Task,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test that sessions are not reused when disabled."""
        config = ATLASConfig(
            executor=ExecutorConfig(reuse_sessions=False),
        )

        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            await executor.execute(task)
            # Session should be cleared after execution
            assert executor._reusable_session is None

    @pytest.mark.asyncio
    async def test_session_reuse_enabled(
        self,
        task: Task,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test that sessions are reused when enabled."""
        config = ATLASConfig(
            executor=ExecutorConfig(reuse_sessions=True),
        )

        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            await executor.execute(task)
            # Session should be saved for reuse
            assert executor._reusable_session is session

    def test_is_agent_running_false_initially(self, config: ATLASConfig) -> None:
        """Test is_agent_running when no agent."""
        executor = TaskExecutor(config=config)

        assert executor.is_agent_running is False

    def test_is_agent_running_true_when_running(self, config: ATLASConfig) -> None:
        """Test is_agent_running with running agent."""
        agent = MockAgentHandle()
        executor = TaskExecutor(config=config)
        executor._agent_handle = agent

        assert executor.is_agent_running is True

    @pytest.mark.asyncio
    async def test_determine_outcome_without_env(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test outcome determination without environment."""
        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task, env=None)

        # Without env, should assume success if steps completed
        assert trajectory.outcome.success is True
        assert "verified" in trajectory.outcome.verification_details

    @pytest.mark.asyncio
    async def test_empty_execution_fails(
        self,
        task: Task,
        config: ATLASConfig,
    ) -> None:
        """Test that execution with no steps fails."""
        session = MockSession(updates=[])  # No updates
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task)

        assert trajectory.outcome.success is False
        assert "no_steps" in trajectory.outcome.error_info

    @pytest.mark.asyncio
    async def test_extract_solution(
        self,
        task: Task,
        config: ATLASConfig,
        successful_updates: list[dict[str, Any]],
    ) -> None:
        """Test solution extraction from steps."""
        session = MockSession(updates=successful_updates)
        agent = MockAgentHandle(session)

        executor = TaskExecutor(config=config)

        with patch.object(executor, "_get_agent", return_value=agent):
            trajectory = await executor.execute(task)

        # Last observation should be extractable as solution
        # The _extract_solution method returns the last non-empty observation


class TestTaskExecutorMemoryIntegration:
    """Tests for TaskExecutor with memory integration."""

    @pytest.fixture
    def task(self) -> Task:
        return Task(
            id="task-001",
            domain="test",
            description="Test task",
            verification=VerificationSpec(method="test_suite"),
        )

    @pytest.fixture
    def mock_memory(self) -> MagicMock:
        """Create a mock memory system."""
        from cognitive_core.protocols.memory import MemoryQueryResult

        memory = MagicMock()
        memory.query.return_value = MemoryQueryResult()
        return memory

    @pytest.mark.asyncio
    async def test_queries_memory(
        self,
        task: Task,
        mock_memory: MagicMock,
    ) -> None:
        """Test that memory is queried during execution."""
        session = MockSession(updates=[
            {"session_update": "tool_call", "title": "Test", "arguments": {}},
            {"session_update": "tool_call_update", "status": "completed", "result": "done"},
        ])
        agent = MockAgentHandle(session)

        config = ATLASConfig()
        executor = TaskExecutor(config=config, memory=mock_memory)

        with patch.object(executor, "_get_agent", return_value=agent):
            await executor.execute(task)

        mock_memory.query.assert_called_once_with(task)

    @pytest.mark.asyncio
    async def test_memory_query_failure_handled(
        self,
        task: Task,
    ) -> None:
        """Test that memory query failures are handled gracefully."""
        mock_memory = MagicMock()
        mock_memory.query.side_effect = Exception("Memory error")

        session = MockSession(updates=[
            {"session_update": "tool_call", "title": "Test", "arguments": {}},
            {"session_update": "tool_call_update", "status": "completed", "result": "done"},
        ])
        agent = MockAgentHandle(session)

        executor = TaskExecutor(memory=mock_memory)

        with patch.object(executor, "_get_agent", return_value=agent):
            # Should not raise, should continue without memory
            trajectory = await executor.execute(task)

        # Execution should still complete
        assert trajectory is not None
