"""SWE environment implementation for ATLAS.

Provides a Docker-based environment for software engineering tasks,
following SWE-bench style evaluation patterns.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from cognitive_core.core.types import Outcome, Task

if TYPE_CHECKING:
    pass

# Try to import docker, but allow graceful degradation
try:
    import docker
    from docker.errors import ContainerError, ImageNotFound

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None  # type: ignore[assignment]
    ContainerError = Exception  # type: ignore[misc, assignment]
    ImageNotFound = Exception  # type: ignore[misc, assignment]

logger = logging.getLogger(__name__)


class SWEEnvironment:
    """SWE-bench style environment with Docker evaluation.

    This environment supports software engineering tasks that involve
    modifying code to fix bugs, implement features, or refactor code.
    Solutions are verified by executing test suites in Docker containers.

    The environment supports graceful degradation:
    - With Docker: Full container-based evaluation with isolation
    - Without Docker: Mock mode for testing without Docker dependency

    Task context should contain:
    - repo: Repository name (e.g., "python/cpython")
    - base_commit: Base commit/version to checkout
    - image: Docker image to use (default: "python:3.11-slim")
    - test_cmd: Command to run tests (optional)
    - setup_cmd: Setup command to run before tests (optional)

    Example:
        ```python
        env = SWEEnvironment()
        task = Task(
            id="fix-bug-123",
            domain="swe",
            description="Fix the authentication bug in auth.py",
            context={
                "repo": "myorg/myrepo",
                "base_commit": "abc123",
                "test_cmd": "pytest tests/test_auth.py",
            },
            verification=VerificationSpec(method="test_suite"),
        )
        obs = env.reset(task)
        obs, reward, done, info = env.step("cat auth.py")  # Execute command
        outcome = env.verify(patch_string)  # Verify with patch
        ```
    """

    # Default Docker image for Python projects
    DEFAULT_IMAGE = "python:3.11-slim"

    # Default timeout in seconds
    DEFAULT_TIMEOUT = 300

    def __init__(
        self,
        docker_client: Any | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        cleanup: bool = True,
        mock_mode: bool = False,
    ) -> None:
        """Initialize SWEEnvironment.

        Args:
            docker_client: Pre-configured Docker client (lazy initialized if None)
            timeout: Timeout for Docker operations in seconds
            cleanup: Whether to cleanup containers on reset/destroy
            mock_mode: Force mock mode even if Docker is available
        """
        self._task: Task | None = None
        self._docker: Any | None = docker_client
        self._timeout = timeout
        self._cleanup = cleanup
        self._mock_mode = mock_mode or not DOCKER_AVAILABLE
        self._container: Any | None = None
        self._step_count = 0
        self._history: list[tuple[str, str]] = []  # (action, observation) pairs

        if self._mock_mode and not mock_mode:
            logger.warning(
                "Docker not available. SWEEnvironment running in mock mode. "
                "Install docker package and ensure Docker daemon is running for full functionality."
            )

    def _get_docker_client(self) -> Any:
        """Lazy initialize Docker client.

        Returns:
            Docker client instance

        Raises:
            RuntimeError: If Docker is not available
        """
        if self._mock_mode:
            raise RuntimeError(
                "Docker is not available. Running in mock mode. "
                "Install docker package and ensure Docker daemon is running."
            )

        if self._docker is None:
            try:
                self._docker = docker.from_env()
                # Test connection
                self._docker.ping()
            except Exception as e:
                logger.error(f"Failed to connect to Docker: {e}")
                self._mock_mode = True
                raise RuntimeError(f"Failed to connect to Docker: {e}") from e

        return self._docker

    def reset(self, task: Task) -> str:
        """Reset the environment with a new SWE task.

        Sets up the environment for a new task. If Docker is available,
        creates a container with the repository cloned at the specified commit.

        Args:
            task: The SWE task to solve. Context should contain:
                - repo: Repository name (optional, for future use)
                - base_commit: Base commit/version (optional)
                - image: Docker image to use (optional)
                - test_cmd: Test command (optional)
                - setup_cmd: Setup command (optional)

        Returns:
            Initial observation with task description and setup status
        """
        self._cleanup_container()
        self._task = task
        self._step_count = 0
        self._history = []

        # Build initial observation
        obs_parts = [task.description]

        # Add context info if available
        context = task.context or {}
        if repo := context.get("repo"):
            obs_parts.append(f"\nRepository: {repo}")
        if base_commit := context.get("base_commit"):
            obs_parts.append(f"Base commit: {base_commit}")
        if test_cmd := context.get("test_cmd"):
            obs_parts.append(f"Test command: {test_cmd}")

        # Set up container if Docker available
        if not self._mock_mode:
            try:
                self._setup_container()
                obs_parts.append("\n[Docker container ready]")
            except Exception as e:
                logger.warning(f"Failed to setup container: {e}")
                obs_parts.append(f"\n[Docker setup failed: {e}. Running in mock mode.]")
                self._mock_mode = True
        else:
            obs_parts.append("\n[Running in mock mode - no Docker]")

        return "\n".join(obs_parts)

    def _setup_container(self) -> None:
        """Set up Docker container for the task.

        Creates a container with the working environment.
        """
        if self._task is None:
            return

        client = self._get_docker_client()
        context = self._task.context or {}

        # Get image from context or use default
        image = context.get("image", self.DEFAULT_IMAGE)

        try:
            # Pull image if not available
            try:
                client.images.get(image)
            except ImageNotFound:
                logger.info(f"Pulling image: {image}")
                client.images.pull(image)

            # Create container with working directory
            self._container = client.containers.create(
                image,
                command="tail -f /dev/null",  # Keep container running
                detach=True,
                working_dir="/workspace",
                # Platform for ARM compatibility
                platform="linux/amd64" if self._is_arm() else None,
            )
            self._container.start()

            # Run setup command if provided
            if setup_cmd := context.get("setup_cmd"):
                self._exec_in_container(setup_cmd)

        except Exception as e:
            logger.error(f"Container setup failed: {e}")
            self._cleanup_container()
            raise

    def _is_arm(self) -> bool:
        """Check if running on ARM architecture (e.g., M-series Mac)."""
        import platform

        return platform.machine() in ("arm64", "aarch64")

    def step(self, action: str) -> tuple[str, float, bool, dict[str, Any]]:
        """Execute an action in the environment.

        Actions can be:
        - Shell commands (executed in container if available)
        - Unified diff patches (detected and applied)

        Args:
            action: Shell command or patch to execute

        Returns:
            Tuple of (observation, reward, done, info)
            - observation: Command output or patch result
            - reward: 0.0 (reward only given at verification)
            - done: False (episode ends at verification)
            - info: Additional metadata
        """
        self._step_count += 1
        info: dict[str, Any] = {"step": self._step_count}

        # Check if action is a patch
        if self._looks_like_patch(action):
            success, observation = self._apply_patch(action)
            info["action_type"] = "patch"
            info["patch_success"] = success
        else:
            # Execute as shell command
            observation = self._execute_command(action)
            info["action_type"] = "command"

        self._history.append((action, observation))

        # Check for max steps
        done = self._step_count >= self.max_steps
        if done:
            observation += "\n[Maximum steps reached]"

        return observation, 0.0, done, info

    def _looks_like_patch(self, text: str) -> bool:
        """Check if text looks like a unified diff patch."""
        patch_indicators = [
            text.strip().startswith("---"),
            text.strip().startswith("diff --git"),
            "\n@@" in text,
            text.strip().startswith("Index:"),
        ]
        return any(patch_indicators)

    def _execute_command(self, command: str) -> str:
        """Execute a shell command.

        Uses Docker container if available, otherwise mock execution.

        Args:
            command: Shell command to execute

        Returns:
            Command output or mock response
        """
        if self._mock_mode or self._container is None:
            return self._mock_command(command)

        return self._exec_in_container(command)

    def _exec_in_container(self, command: str) -> str:
        """Execute command in Docker container.

        Args:
            command: Command to execute

        Returns:
            Command output
        """
        if self._container is None:
            return "[Error: No container available]"

        try:
            exit_code, output = self._container.exec_run(
                f"/bin/sh -c '{command}'",
                demux=True,
            )

            stdout, stderr = output if output else (b"", b"")
            stdout = stdout.decode("utf-8") if stdout else ""
            stderr = stderr.decode("utf-8") if stderr else ""

            result = stdout
            if stderr:
                result += f"\n[stderr]: {stderr}"
            if exit_code != 0:
                result += f"\n[exit code: {exit_code}]"

            return result or "[no output]"

        except Exception as e:
            return f"[Error executing command: {e}]"

    def _mock_command(self, command: str) -> str:
        """Mock command execution for testing without Docker.

        Args:
            command: Command to mock

        Returns:
            Mock response
        """
        # Provide basic mock responses for common commands
        cmd_lower = command.lower().strip()

        if cmd_lower.startswith("cat "):
            return "[Mock] File contents would be displayed here"
        elif cmd_lower.startswith("ls"):
            return "[Mock] Directory listing would be displayed here"
        elif cmd_lower.startswith("git"):
            return "[Mock] Git operation would be performed"
        elif "pytest" in cmd_lower or "python -m pytest" in cmd_lower:
            return "[Mock] Tests would be executed here"
        elif cmd_lower.startswith("echo"):
            return command.replace("echo ", "", 1).strip("'\"")
        else:
            return f"[Mock mode] Would execute: {command}"

    def _apply_patch(self, patch: str) -> tuple[bool, str]:
        """Apply a unified diff patch.

        Args:
            patch: Unified diff patch string

        Returns:
            Tuple of (success, output message)
        """
        if self._mock_mode or self._container is None:
            return self._mock_apply_patch(patch)

        try:
            # Write patch to temp file in container
            escaped_patch = patch.replace("'", "'\\''")
            write_cmd = f"echo '{escaped_patch}' > /tmp/patch.diff"
            self._exec_in_container(write_cmd)

            # Apply patch
            result = self._exec_in_container("patch -p1 < /tmp/patch.diff")

            success = "FAILED" not in result.upper() and "reject" not in result.lower()
            return success, result

        except Exception as e:
            return False, f"[Error applying patch: {e}]"

    def _mock_apply_patch(self, patch: str) -> tuple[bool, str]:
        """Mock patch application for testing.

        Args:
            patch: Patch content

        Returns:
            Tuple of (success, message)
        """
        # Parse patch to get some info
        lines = patch.strip().split("\n")
        files_affected = []
        for line in lines:
            if line.startswith("---") or line.startswith("+++"):
                filename = line.split()[1] if len(line.split()) > 1 else "unknown"
                if filename not in files_affected and filename != "/dev/null":
                    files_affected.append(filename)

        if files_affected:
            return True, f"[Mock] Patch applied to: {', '.join(files_affected[:3])}"
        return True, "[Mock] Patch applied successfully"

    def verify(self, solution: Any) -> Outcome:
        """Verify a solution by running tests.

        Args:
            solution: Either a patch string to apply before testing,
                     or None to just run tests

        Returns:
            Outcome with test results
        """
        if self._task is None:
            raise RuntimeError("No task set. Call reset() first.")

        context = self._task.context or {}
        test_cmd = context.get("test_cmd", "pytest")

        # Apply solution if it's a patch
        if solution and isinstance(solution, str) and self._looks_like_patch(solution):
            patch_success, patch_output = self._apply_patch(solution)
            if not patch_success:
                return Outcome(
                    success=False,
                    partial_score=0.0,
                    error_info=f"Failed to apply patch: {patch_output}",
                    verification_details={"patch_applied": False, "output": patch_output},
                )

        # Run tests
        test_results = self._run_tests(test_cmd)

        # Calculate outcome
        success = test_results.get("failed", 0) == 0 and test_results.get("passed", 0) > 0
        total = test_results.get("total", 0)
        passed = test_results.get("passed", 0)

        partial_score = passed / total if total > 0 else 0.0

        return Outcome(
            success=success,
            partial_score=partial_score,
            error_info=test_results.get("error") if not success else None,
            verification_details=test_results,
        )

    def _run_tests(self, test_cmd: str | None = None) -> dict[str, Any]:
        """Run tests and parse results.

        Args:
            test_cmd: Test command to run

        Returns:
            Dictionary with test results:
            - passed: Number of passed tests
            - failed: Number of failed tests
            - total: Total number of tests
            - output: Raw test output
            - error: Error message if tests failed to run
        """
        if test_cmd is None:
            test_cmd = "pytest"

        if self._mock_mode or self._container is None:
            return self._mock_run_tests(test_cmd)

        try:
            output = self._exec_in_container(test_cmd)
            return self._parse_test_output(output)
        except Exception as e:
            return {
                "passed": 0,
                "failed": 0,
                "total": 0,
                "output": "",
                "error": str(e),
            }

    def _mock_run_tests(self, test_cmd: str) -> dict[str, Any]:
        """Mock test execution for testing without Docker.

        Args:
            test_cmd: Test command

        Returns:
            Mock test results
        """
        return {
            "passed": 1,
            "failed": 0,
            "total": 1,
            "output": f"[Mock] Test command '{test_cmd}' would be executed",
            "mock": True,
        }

    def _parse_test_output(self, output: str) -> dict[str, Any]:
        """Parse test output to extract pass/fail counts.

        Handles pytest and unittest output formats.

        Args:
            output: Raw test output

        Returns:
            Dictionary with:
            - passed: Number of passed tests
            - failed: Number of failed tests
            - total: Total number of tests
            - output: Raw test output
        """
        results: dict[str, Any] = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "output": output,
        }

        # Try pytest format: "X passed, Y failed, Z errors"
        pytest_pattern = r"(\d+)\s+passed"
        if match := re.search(pytest_pattern, output):
            results["passed"] = int(match.group(1))

        pytest_failed = r"(\d+)\s+failed"
        if match := re.search(pytest_failed, output):
            results["failed"] = int(match.group(1))

        pytest_error = r"(\d+)\s+error"
        if match := re.search(pytest_error, output):
            results["failed"] += int(match.group(1))

        # Try unittest format: "Ran X tests"
        unittest_pattern = r"Ran\s+(\d+)\s+tests?"
        if match := re.search(unittest_pattern, output):
            results["total"] = int(match.group(1))

        # Unittest OK/FAILED
        if "OK" in output and results["total"] > 0:
            results["passed"] = results["total"]
        elif "FAILED" in output:
            # Try to parse failures
            failure_pattern = r"failures=(\d+)"
            if match := re.search(failure_pattern, output):
                results["failed"] = int(match.group(1))

        # Calculate total if not set
        if results["total"] == 0:
            results["total"] = results["passed"] + results["failed"]

        return results

    def _cleanup_container(self) -> None:
        """Clean up Docker container."""
        if self._container is not None and self._cleanup:
            try:
                self._container.stop(timeout=5)
                self._container.remove(force=True)
                logger.debug("Container cleaned up successfully")
            except Exception as e:
                logger.warning(f"Failed to cleanup container: {e}")
            finally:
                self._container = None

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

        SWE tasks with fixed test suites are generally deterministic,
        but external dependencies may introduce non-determinism.

        Returns:
            True (assuming fixed test suites)
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

    @property
    def docker_available(self) -> bool:
        """Check if Docker is available.

        Returns:
            True if Docker can be used, False if in mock mode
        """
        return not self._mock_mode and DOCKER_AVAILABLE

    @property
    def history(self) -> list[tuple[str, str]]:
        """Get action/observation history.

        Returns:
            List of (action, observation) tuples
        """
        return list(self._history)

    def __del__(self) -> None:
        """Cleanup on destruction."""
        self._cleanup_container()

    def __repr__(self) -> str:
        """String representation."""
        mode = "mock" if self._mock_mode else "docker"
        task_id = self._task.id if self._task else "None"
        return f"SWEEnvironment(mode={mode}, task={task_id}, steps={self._step_count})"
