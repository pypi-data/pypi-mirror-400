"""TaskExecutor for running tasks via ACP agents.

Main orchestrator that bridges ACP sessions and ATLAS's task/trajectory model.
Handles agent lifecycle, session management, and trajectory collection.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from cognitive_core.config import ATLASConfig
from cognitive_core.core.types import Outcome, Step, Trajectory
from cognitive_core.execution.prompt_formatter import PromptFormatter
from cognitive_core.execution.trajectory_builder import TrajectoryBuilder

if TYPE_CHECKING:
    from cognitive_core.core.types import Task
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemorySystem

logger = logging.getLogger("cognitive_core.execution")


class TaskExecutor:
    """Executes tasks via ACP agents, produces Trajectories.

    The TaskExecutor is the main orchestrator that:
    1. Queries memory for relevant context
    2. Formats prompts with task and memory
    3. Spawns and manages ACP agents
    4. Collects session updates into trajectories
    5. Handles timeouts and errors gracefully

    Example:
        ```python
        executor = TaskExecutor(config, memory)

        try:
            trajectory = await executor.execute(task, env)
            print(f"Task {'succeeded' if trajectory.outcome.success else 'failed'}")
        finally:
            await executor.close()
        ```
    """

    def __init__(
        self,
        config: ATLASConfig | None = None,
        memory: MemorySystem | None = None,
    ) -> None:
        """Initialize the task executor.

        Args:
            config: ATLAS configuration. Uses defaults if not provided.
            memory: Memory system for context retrieval. Optional.
        """
        self._config = config or ATLASConfig()
        self._memory = memory
        self._formatter = PromptFormatter(self._config.memory)
        self._agent_handle: Any = None  # AgentHandle when initialized
        self._reusable_session: Any = None  # Session when reusing

    async def execute(
        self,
        task: Task,
        env: Environment | None = None,
    ) -> Trajectory:
        """Execute a task and return complete trajectory.

        Args:
            task: The task to execute.
            env: Optional environment for verification and sandboxing.

        Returns:
            Complete Trajectory with steps and outcome.
        """
        logger.info(
            "Task started",
            extra={"task_id": task.id, "domain": task.domain},
        )

        start_time = datetime.now(timezone.utc)

        try:
            # 1. Query memory for context
            memory_result = None
            if self._memory is not None:
                try:
                    memory_result = self._memory.query(task)
                    logger.debug(
                        "Memory queried",
                        extra={
                            "experiences": len(memory_result.experiences),
                            "concepts": len(memory_result.concepts),
                            "strategies": len(memory_result.strategies),
                        },
                    )
                except Exception as e:
                    logger.warning("Memory query failed", extra={"error": str(e)})

            # 2. Format prompt
            prompt = self._formatter.format(task, memory_result)
            logger.debug("Prompt formatted", extra={"length": len(prompt)})

            # 3. Get or create agent and session
            session = await self._get_session(task)

            # 4. Run and collect trajectory
            builder = TrajectoryBuilder(
                task=task,
                agent_id=self._config.executor.agent_type,
            )

            try:
                # Run with timeout
                async with asyncio.timeout(self._config.executor.timeout_seconds):
                    async for update in session.prompt(prompt):
                        step = builder.process_update(update)
                        if step is not None:
                            logger.debug(
                                "Step completed",
                                extra={"action": step.action[:50] if step.action else ""},
                            )

            except asyncio.TimeoutError:
                logger.warning(
                    "Task timed out",
                    extra={"task_id": task.id, "timeout": self._config.executor.timeout_seconds},
                )
                await session.cancel()
                return builder.build(
                    Outcome(
                        success=False,
                        error_info=f"timeout after {self._config.executor.timeout_seconds}s",
                    )
                )

            # 5. Determine outcome
            outcome = self._determine_outcome(task, env, builder)

            # 6. Build and return trajectory
            trajectory = builder.build(outcome)

            logger.info(
                "Task completed",
                extra={
                    "task_id": task.id,
                    "success": outcome.success,
                    "steps": len(trajectory.steps),
                    "duration": (datetime.now(timezone.utc) - start_time).total_seconds(),
                },
            )

            # Clean up session if not reusing
            if not self._config.executor.reuse_sessions:
                self._reusable_session = None

            return trajectory

        except Exception as e:
            logger.error(
                "Task failed with error",
                extra={"task_id": task.id, "error": str(e)},
            )
            return Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=False, error_info=f"executor_error: {e}"),
                agent_id=self._config.executor.agent_type,
                metadata={
                    "error_type": type(e).__name__,
                    "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
                },
            )

    async def execute_with_session(
        self,
        task: Task,
        session: Any,  # Session from acp_factory
        env: Environment | None = None,
    ) -> Trajectory:
        """Execute using an existing session.

        Useful for forking scenarios (Mind Evolution/MCTS) where you want
        to continue from a specific point in a session.

        Args:
            task: The task to execute.
            session: An existing ACP Session to use.
            env: Optional environment for verification.

        Returns:
            Complete Trajectory with steps and outcome.
        """
        logger.info(
            "Task started with existing session",
            extra={"task_id": task.id, "session_id": session.id},
        )

        start_time = datetime.now(timezone.utc)

        try:
            # Query memory and format prompt
            memory_result = None
            if self._memory is not None:
                try:
                    memory_result = self._memory.query(task)
                except Exception:
                    pass

            prompt = self._formatter.format(task, memory_result)

            # Build trajectory from session
            builder = TrajectoryBuilder(
                task=task,
                agent_id=self._config.executor.agent_type,
            )

            try:
                async with asyncio.timeout(self._config.executor.timeout_seconds):
                    async for update in session.prompt(prompt):
                        builder.process_update(update)

            except asyncio.TimeoutError:
                await session.cancel()
                return builder.build(
                    Outcome(
                        success=False,
                        error_info=f"timeout after {self._config.executor.timeout_seconds}s",
                    )
                )

            outcome = self._determine_outcome(task, env, builder)
            return builder.build(outcome)

        except Exception as e:
            logger.error("Task failed", extra={"task_id": task.id, "error": str(e)})
            return Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=False, error_info=f"executor_error: {e}"),
                agent_id=self._config.executor.agent_type,
            )

    async def fork_and_execute(
        self,
        task: Task,
        source_session: Any,  # Session to fork from
        env: Environment | None = None,
    ) -> Trajectory:
        """Fork a session and execute a task on the fork.

        Creates an independent copy of the session state and executes
        the task on it. The original session is not affected.

        Args:
            task: The task to execute.
            source_session: Session to fork from.
            env: Optional environment for verification.

        Returns:
            Complete Trajectory from the forked execution.
        """
        logger.info(
            "Forking session for task",
            extra={"task_id": task.id, "source_session": source_session.id},
        )

        try:
            forked_session = await source_session.fork()
            return await self.execute_with_session(task, forked_session, env)
        except Exception as e:
            logger.error("Fork failed", extra={"error": str(e)})
            return Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=False, error_info=f"fork_failed: {e}"),
                agent_id=self._config.executor.agent_type,
            )

    async def _get_session(self, task: Task) -> Any:
        """Get or create an agent session.

        Handles session reuse based on configuration.

        Args:
            task: The task being executed (for cwd context).

        Returns:
            An ACP Session ready for prompting.
        """
        # Return existing session if reusing
        if self._config.executor.reuse_sessions and self._reusable_session is not None:
            logger.debug("Reusing existing session")
            return self._reusable_session

        # Ensure agent is spawned
        agent = await self._get_agent()

        # Get working directory from task context
        cwd = task.context.get("cwd", ".")

        # Create session options with MCP servers
        try:
            from acp_factory import SessionOptions
        except ImportError:
            # Fallback if acp_factory not installed
            class SessionOptions:  # type: ignore[no-redef]
                def __init__(self, mcp_servers: list[dict[str, Any]] | None = None) -> None:
                    self.mcp_servers = mcp_servers or []

        mcp_servers = self._get_mcp_server_configs()
        options = SessionOptions(mcp_servers=mcp_servers)

        session = await agent.create_session(cwd=cwd, options=options)

        logger.debug(
            "Session created",
            extra={"session_id": session.id, "cwd": cwd},
        )

        if self._config.executor.reuse_sessions:
            self._reusable_session = session

        return session

    async def _get_agent(self) -> Any:
        """Get or spawn an agent.

        Returns:
            An AgentHandle for the configured agent type.
        """
        if self._agent_handle is not None and self._agent_handle.is_running():
            return self._agent_handle

        try:
            from acp_factory import AgentFactory, SpawnOptions
        except ImportError as e:
            raise ImportError(
                "acp_factory is required for the TaskExecutor. "
                "Ensure acp-factory is installed or in your Python path."
            ) from e

        agent_type = self._config.executor.agent_type
        permission_mode = self._config.executor.permission_mode

        logger.info(
            "Spawning agent",
            extra={"type": agent_type, "permission_mode": permission_mode},
        )

        options = SpawnOptions(permission_mode=permission_mode)
        self._agent_handle = await AgentFactory.spawn(agent_type, options)

        return self._agent_handle

    def _get_mcp_server_configs(self) -> list[dict[str, Any]]:
        """Get MCP server configurations for sessions.

        Returns:
            List of MCP server configs to attach to sessions.
        """
        # Currently returns empty list - Memory MCP server would be configured here
        # when we have the full memory system set up
        #
        # Example configuration:
        # return [{
        #     "name": "atlas-memory",
        #     "command": "python",
        #     "args": ["-m", "cognitive_core.mcp.memory_server"],
        # }]
        return []

    def _determine_outcome(
        self,
        task: Task,
        env: Environment | None,
        builder: TrajectoryBuilder,
    ) -> Outcome:
        """Determine the outcome of task execution.

        Args:
            task: The executed task.
            env: Optional environment for verification.
            builder: The trajectory builder with collected steps.

        Returns:
            Outcome indicating success/failure.
        """
        # If we have an environment, use its verification
        if env is not None:
            try:
                # Get the current state as the solution
                # The environment should have the final state after agent execution
                solution = self._extract_solution(builder)
                return env.verify(solution)
            except Exception as e:
                logger.warning(
                    "Environment verification failed",
                    extra={"error": str(e)},
                )

        # Without environment, we can't verify - assume success if steps completed
        # This is a simplification; real verification needs domain-specific logic
        if builder.step_count > 0:
            return Outcome(
                success=True,  # Tentative - no verification
                verification_details={"verified": False, "reason": "no_verifier"},
            )

        return Outcome(
            success=False,
            error_info="no_steps_completed",
        )

    def _extract_solution(self, builder: TrajectoryBuilder) -> Any:
        """Extract the solution from completed steps.

        In the simplest case, the solution is the final observation.
        This can be extended for domain-specific extraction.

        Args:
            builder: The trajectory builder with completed steps.

        Returns:
            The extracted solution (domain-specific).
        """
        steps = builder.steps
        if not steps:
            return None

        # Return the last non-empty observation as the solution
        for step in reversed(steps):
            if step.observation:
                return step.observation

        return None

    async def close(self) -> None:
        """Clean up agent handle and sessions.

        Should be called when done with the executor.
        """
        if self._agent_handle is not None:
            logger.info("Closing agent handle")
            await self._agent_handle.close()
            self._agent_handle = None
            self._reusable_session = None

    @property
    def is_agent_running(self) -> bool:
        """Check if an agent is currently running."""
        return self._agent_handle is not None and self._agent_handle.is_running()

    async def __aenter__(self) -> TaskExecutor:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup."""
        await self.close()
