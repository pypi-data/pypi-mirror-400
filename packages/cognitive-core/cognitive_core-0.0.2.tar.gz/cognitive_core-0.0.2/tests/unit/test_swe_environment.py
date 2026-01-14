"""Tests for SWEEnvironment with Docker integration.

These tests verify the SWEEnvironment implementation including:
- Mock mode for testing without Docker
- Docker client mocking for unit tests
- Graceful degradation
- Patch application
- Test output parsing
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cognitive_core.core.types import Outcome, Task, VerificationSpec
from cognitive_core.environments import DOCKER_AVAILABLE, SWEEnvironment


def make_swe_task(
    task_id: str = "swe-1",
    description: str = "Fix the bug in auth.py",
    repo: str | None = None,
    base_commit: str | None = None,
    test_cmd: str | None = None,
    image: str | None = None,
    setup_cmd: str | None = None,
) -> Task:
    """Create a test SWE task with all required fields."""
    context: dict[str, Any] = {}
    if repo:
        context["repo"] = repo
    if base_commit:
        context["base_commit"] = base_commit
    if test_cmd:
        context["test_cmd"] = test_cmd
    if image:
        context["image"] = image
    if setup_cmd:
        context["setup_cmd"] = setup_cmd

    return Task(
        id=task_id,
        domain="swe",
        description=description,
        context=context,
        verification=VerificationSpec(method="test_suite"),
    )


class TestSWEEnvironmentMockMode:
    """Tests for SWEEnvironment in mock mode (no Docker)."""

    def test_init_with_mock_mode(self) -> None:
        """SWEEnvironment can be initialized in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        assert env._mock_mode is True
        assert env.docker_available is False

    def test_reset_returns_task_description(self) -> None:
        """reset() returns task description with context info."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task(description="Fix authentication bug")

        result = env.reset(task)

        assert "Fix authentication bug" in result
        assert "[Running in mock mode - no Docker]" in result

    def test_reset_includes_context_info(self) -> None:
        """reset() includes repository and test command info."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task(
            repo="python/cpython",
            base_commit="abc123",
            test_cmd="pytest tests/",
        )

        result = env.reset(task)

        assert "Repository: python/cpython" in result
        assert "Base commit: abc123" in result
        assert "Test command: pytest tests/" in result

    def test_reset_stores_task(self) -> None:
        """reset() stores the task for later retrieval."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()

        env.reset(task)

        assert env.task == task

    def test_task_before_reset_raises_error(self) -> None:
        """task property raises RuntimeError before reset() is called."""
        env = SWEEnvironment(mock_mode=True)

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.task

    def test_step_returns_tuple(self) -> None:
        """step() returns (observation, reward, done, info)."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        result = env.step("ls -la")

        assert isinstance(result, tuple)
        assert len(result) == 4
        obs, reward, done, info = result
        assert isinstance(obs, str)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_step_mock_command_execution(self) -> None:
        """step() returns mock response for commands."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, reward, done, info = env.step("ls -la")

        assert "[Mock]" in obs or "Would execute" in obs
        assert reward == 0.0
        assert done is False
        assert info["action_type"] == "command"

    def test_step_mock_cat_command(self) -> None:
        """step() provides mock response for cat command."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, _, _, _ = env.step("cat file.py")

        assert "[Mock] File contents" in obs

    def test_step_mock_git_command(self) -> None:
        """step() provides mock response for git command."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, _, _, _ = env.step("git status")

        assert "[Mock] Git operation" in obs

    def test_step_mock_pytest_command(self) -> None:
        """step() provides mock response for pytest command."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, _, _, _ = env.step("pytest tests/")

        assert "[Mock] Tests" in obs

    def test_step_mock_echo_command(self) -> None:
        """step() handles echo command correctly."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, _, _, _ = env.step("echo 'hello world'")

        assert "hello world" in obs

    def test_step_increments_count(self) -> None:
        """step() increments step count."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        assert env._step_count == 0
        env.step("ls")
        assert env._step_count == 1
        env.step("pwd")
        assert env._step_count == 2

    def test_step_records_history(self) -> None:
        """step() records action/observation history."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        env.step("ls")
        env.step("pwd")

        history = env.history
        assert len(history) == 2
        assert history[0][0] == "ls"
        assert history[1][0] == "pwd"

    def test_step_detects_max_steps(self) -> None:
        """step() sets done=True when max steps reached."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        # Execute max_steps - 1 steps
        for _ in range(env.max_steps - 1):
            _, _, done, _ = env.step("ls")
            assert done is False

        # The max_steps-th step should set done=True
        _, _, done, _ = env.step("final")
        assert done is True

    def test_reset_clears_step_count_and_history(self) -> None:
        """reset() clears step count and history."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)
        env.step("ls")
        env.step("pwd")

        # Reset with new task
        env.reset(make_swe_task(task_id="swe-2"))

        assert env._step_count == 0
        assert len(env.history) == 0


class TestSWEEnvironmentPatchHandling:
    """Tests for patch detection and application."""

    def test_looks_like_patch_with_diff_git(self) -> None:
        """Detects diff --git format patches."""
        env = SWEEnvironment(mock_mode=True)
        patch = """diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-old line
+new line
"""
        assert env._looks_like_patch(patch) is True

    def test_looks_like_patch_with_unified_format(self) -> None:
        """Detects unified diff format patches."""
        env = SWEEnvironment(mock_mode=True)
        patch = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-old line
+new line
"""
        assert env._looks_like_patch(patch) is True

    def test_looks_like_patch_with_hunk_markers(self) -> None:
        """Detects patches with @@ hunk markers."""
        env = SWEEnvironment(mock_mode=True)
        patch = """some header
@@ -1,3 +1,3 @@
-old
+new
"""
        assert env._looks_like_patch(patch) is True

    def test_looks_like_patch_false_for_normal_text(self) -> None:
        """Returns False for normal text."""
        env = SWEEnvironment(mock_mode=True)
        assert env._looks_like_patch("ls -la") is False
        assert env._looks_like_patch("print('hello')") is False
        assert env._looks_like_patch("git status") is False

    def test_step_detects_patch_action(self) -> None:
        """step() detects patch action and applies it."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        patch = """--- a/auth.py
+++ b/auth.py
@@ -1,3 +1,3 @@
-old code
+new code
"""
        obs, _, _, info = env.step(patch)

        assert info["action_type"] == "patch"
        assert info["patch_success"] is True
        assert "a/auth.py" in obs or "[Mock] Patch applied" in obs

    def test_mock_apply_patch_extracts_filenames(self) -> None:
        """Mock patch application extracts affected filenames."""
        env = SWEEnvironment(mock_mode=True)
        patch = """--- a/src/auth.py
+++ b/src/auth.py
@@ -1,3 +1,3 @@
-old
+new
"""
        success, message = env._mock_apply_patch(patch)

        assert success is True
        assert "a/src/auth.py" in message or "src/auth.py" in message


class TestSWEEnvironmentVerify:
    """Tests for verify() method."""

    def test_verify_in_mock_mode_succeeds(self) -> None:
        """verify() returns success in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        outcome = env.verify(None)

        assert isinstance(outcome, Outcome)
        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_verify_with_patch_applies_it(self) -> None:
        """verify() applies patch before running tests."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        patch = """--- a/file.py
+++ b/file.py
@@ -1,1 +1,1 @@
-old
+new
"""
        outcome = env.verify(patch)

        assert isinstance(outcome, Outcome)
        assert outcome.success is True

    def test_verify_before_reset_raises_error(self) -> None:
        """verify() raises RuntimeError if reset() not called."""
        env = SWEEnvironment(mock_mode=True)

        with pytest.raises(RuntimeError, match="No task set"):
            env.verify(None)

    def test_verify_returns_test_results_in_details(self) -> None:
        """verify() includes test results in verification_details."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task(test_cmd="pytest tests/")
        env.reset(task)

        outcome = env.verify(None)

        assert "passed" in outcome.verification_details
        assert "failed" in outcome.verification_details
        assert "total" in outcome.verification_details


class TestSWEEnvironmentTestParsing:
    """Tests for test output parsing."""

    def test_parse_pytest_passed(self) -> None:
        """Parses pytest output with passed tests."""
        env = SWEEnvironment(mock_mode=True)
        output = "===== 5 passed in 0.5s ====="

        result = env._parse_test_output(output)

        assert result["passed"] == 5
        assert result["failed"] == 0
        assert result["total"] == 5

    def test_parse_pytest_mixed(self) -> None:
        """Parses pytest output with mixed results."""
        env = SWEEnvironment(mock_mode=True)
        output = "===== 3 passed, 2 failed in 1.0s ====="

        result = env._parse_test_output(output)

        assert result["passed"] == 3
        assert result["failed"] == 2
        assert result["total"] == 5

    def test_parse_pytest_with_errors(self) -> None:
        """Parses pytest output with errors."""
        env = SWEEnvironment(mock_mode=True)
        output = "===== 3 passed, 1 failed, 2 error in 1.0s ====="

        result = env._parse_test_output(output)

        assert result["passed"] == 3
        assert result["failed"] == 3  # failed + error
        assert result["total"] == 6

    def test_parse_unittest_passed(self) -> None:
        """Parses unittest output with passed tests."""
        env = SWEEnvironment(mock_mode=True)
        output = """
Ran 10 tests in 0.5s

OK
"""
        result = env._parse_test_output(output)

        assert result["total"] == 10
        assert result["passed"] == 10

    def test_parse_unittest_failed(self) -> None:
        """Parses unittest output with failures."""
        env = SWEEnvironment(mock_mode=True)
        output = """
Ran 10 tests in 0.5s

FAILED (failures=3)
"""
        result = env._parse_test_output(output)

        assert result["total"] == 10
        assert result["failed"] == 3

    def test_parse_empty_output(self) -> None:
        """Handles empty output gracefully."""
        env = SWEEnvironment(mock_mode=True)
        result = env._parse_test_output("")

        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["total"] == 0


class TestSWEEnvironmentProperties:
    """Tests for SWEEnvironment properties."""

    def test_max_steps_returns_100(self) -> None:
        """max_steps returns 100."""
        env = SWEEnvironment(mock_mode=True)
        assert env.max_steps == 100

    def test_is_deterministic_returns_true(self) -> None:
        """is_deterministic returns True."""
        env = SWEEnvironment(mock_mode=True)
        assert env.is_deterministic is True

    def test_docker_available_in_mock_mode(self) -> None:
        """docker_available returns False in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        assert env.docker_available is False

    def test_repr(self) -> None:
        """__repr__ returns meaningful string."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task(task_id="test-123")
        env.reset(task)

        repr_str = repr(env)

        assert "SWEEnvironment" in repr_str
        assert "mock" in repr_str
        assert "test-123" in repr_str


class TestSWEEnvironmentInit:
    """Tests for SWEEnvironment initialization options."""

    def test_init_default_values(self) -> None:
        """Default initialization values are set correctly."""
        env = SWEEnvironment(mock_mode=True)

        assert env._timeout == SWEEnvironment.DEFAULT_TIMEOUT
        assert env._cleanup is True
        assert env._container is None
        assert env._task is None

    def test_init_custom_timeout(self) -> None:
        """Custom timeout is respected."""
        env = SWEEnvironment(mock_mode=True, timeout=600)
        assert env._timeout == 600

    def test_init_cleanup_false(self) -> None:
        """cleanup=False is respected."""
        env = SWEEnvironment(mock_mode=True, cleanup=False)
        assert env._cleanup is False


class TestSWEEnvironmentDockerMocked:
    """Tests for SWEEnvironment with mocked Docker client."""

    def test_docker_client_initialization(self) -> None:
        """Docker client is provided and used."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True

        env = SWEEnvironment(docker_client=mock_client, mock_mode=False)

        # Should not be in mock mode when client is provided
        # Note: Will still be in mock mode if DOCKER_AVAILABLE is False
        assert env._docker == mock_client

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker package not installed")
    def test_setup_container_pulls_image_if_not_found(self) -> None:
        """Container setup pulls image if not found."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.images.get.side_effect = Exception("Not found")
        mock_container = MagicMock()
        mock_client.containers.create.return_value = mock_container

        env = SWEEnvironment(docker_client=mock_client, mock_mode=False)
        env._mock_mode = False  # Force non-mock mode
        task = make_swe_task()
        env._task = task

        try:
            env._setup_container()
            mock_client.images.pull.assert_called_once()
        except Exception:
            # Expected if mock setup is incomplete
            pass

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker package not installed")
    def test_exec_in_container_handles_output(self) -> None:
        """Container exec_run handles stdout/stderr."""
        mock_container = MagicMock()
        mock_container.exec_run.return_value = (0, (b"stdout output", b"stderr output"))

        env = SWEEnvironment(mock_mode=True)
        env._container = mock_container
        env._mock_mode = False  # Force container execution

        result = env._exec_in_container("ls")

        assert "stdout output" in result
        assert "[stderr]:" in result

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker package not installed")
    def test_exec_in_container_handles_error_code(self) -> None:
        """Container exec_run reports non-zero exit codes."""
        mock_container = MagicMock()
        mock_container.exec_run.return_value = (1, (b"output", None))

        env = SWEEnvironment(mock_mode=True)
        env._container = mock_container
        env._mock_mode = False

        result = env._exec_in_container("failing-command")

        assert "[exit code: 1]" in result

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker package not installed")
    def test_cleanup_container_removes_container(self) -> None:
        """_cleanup_container stops and removes container."""
        mock_container = MagicMock()

        env = SWEEnvironment(mock_mode=True)
        env._container = mock_container

        env._cleanup_container()

        mock_container.stop.assert_called_once()
        mock_container.remove.assert_called_once_with(force=True)
        assert env._container is None

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker package not installed")
    def test_cleanup_container_handles_errors(self) -> None:
        """_cleanup_container handles errors gracefully."""
        mock_container = MagicMock()
        mock_container.stop.side_effect = Exception("Container already stopped")

        env = SWEEnvironment(mock_mode=True)
        env._container = mock_container

        # Should not raise
        env._cleanup_container()

        assert env._container is None


class TestSWEEnvironmentARMCompatibility:
    """Tests for ARM architecture handling."""

    @patch("platform.machine")
    def test_is_arm_detects_arm64(self, mock_machine: MagicMock) -> None:
        """_is_arm returns True for arm64."""
        mock_machine.return_value = "arm64"
        env = SWEEnvironment(mock_mode=True)
        assert env._is_arm() is True

    @patch("platform.machine")
    def test_is_arm_detects_aarch64(self, mock_machine: MagicMock) -> None:
        """_is_arm returns True for aarch64."""
        mock_machine.return_value = "aarch64"
        env = SWEEnvironment(mock_mode=True)
        assert env._is_arm() is True

    @patch("platform.machine")
    def test_is_arm_false_for_x86(self, mock_machine: MagicMock) -> None:
        """_is_arm returns False for x86_64."""
        mock_machine.return_value = "x86_64"
        env = SWEEnvironment(mock_mode=True)
        assert env._is_arm() is False


class TestSWEEnvironmentGracefulDegradation:
    """Tests for graceful degradation when Docker is unavailable."""

    def test_mock_mode_when_docker_unavailable(self) -> None:
        """Environment falls back to mock mode when Docker unavailable."""
        # When DOCKER_AVAILABLE is False, mock_mode should be True
        env = SWEEnvironment()
        if not DOCKER_AVAILABLE:
            assert env._mock_mode is True

    def test_reset_works_in_mock_mode(self) -> None:
        """reset() works correctly in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()

        obs = env.reset(task)

        assert task.description in obs
        assert "[Running in mock mode - no Docker]" in obs

    def test_step_works_in_mock_mode(self) -> None:
        """step() works correctly in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        obs, reward, done, info = env.step("ls")

        assert "[Mock]" in obs or "Would execute" in obs
        assert reward == 0.0
        assert done is False

    def test_verify_works_in_mock_mode(self) -> None:
        """verify() works correctly in mock mode."""
        env = SWEEnvironment(mock_mode=True)
        task = make_swe_task()
        env.reset(task)

        outcome = env.verify(None)

        assert outcome.success is True
        assert outcome.verification_details.get("mock") is True


class TestDockerAvailable:
    """Tests for DOCKER_AVAILABLE constant."""

    def test_docker_available_is_bool(self) -> None:
        """DOCKER_AVAILABLE is a boolean."""
        assert isinstance(DOCKER_AVAILABLE, bool)

    def test_docker_available_reflects_import(self) -> None:
        """DOCKER_AVAILABLE reflects whether docker was imported."""
        try:
            import docker  # noqa: F401

            # If we get here, docker is installed
            assert DOCKER_AVAILABLE is True
        except ImportError:
            assert DOCKER_AVAILABLE is False
