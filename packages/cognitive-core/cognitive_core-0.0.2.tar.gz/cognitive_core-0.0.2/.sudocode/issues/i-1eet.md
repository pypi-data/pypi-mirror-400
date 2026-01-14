---
id: i-1eet
title: Implement TaskExecutor (ACP integration)
priority: 1
created_at: '2026-01-07 08:55:55'
tags:
  - acp
  - core
  - execution
  - phase-2
relationships:
  - from_id: i-1eet
    from_uuid: dc621918-7b0e-46f9-bf30-0862d50ba48e
    from_type: issue
    to_id: i-4jr4
    to_uuid: 891a6104-7560-42f5-b2d2-c8b00498989d
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 08:56:21'
    metadata: null
  - from_id: i-1eet
    from_uuid: dc621918-7b0e-46f9-bf30-0862d50ba48e
    from_type: issue
    to_id: i-402r
    to_uuid: 4c4c2edb-1a65-4bc2-b746-efd017905f11
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 08:56:20'
    metadata: null
  - from_id: i-1eet
    from_uuid: dc621918-7b0e-46f9-bf30-0862d50ba48e
    from_type: issue
    to_id: i-4ow1
    to_uuid: 44c8882e-cf2f-4657-b22d-14769206f127
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 08:56:20'
    metadata: null
  - from_id: i-1eet
    from_uuid: dc621918-7b0e-46f9-bf30-0862d50ba48e
    from_type: issue
    to_id: i-78el
    to_uuid: b281f8bc-00a0-4807-b962-02bcbbbf7276
    to_type: issue
    relationship_type: depends-on
    created_at: '2026-01-07 08:56:20'
    metadata: null
  - from_id: i-1eet
    from_uuid: dc621918-7b0e-46f9-bf30-0862d50ba48e
    from_type: issue
    to_id: s-7xs8
    to_uuid: 12efd4e8-865b-4b65-91e0-fad14c400a33
    to_type: spec
    relationship_type: implements
    created_at: '2026-01-07 08:56:07'
    metadata: null
status: closed
closed_at: '2026-01-07 09:41:01'
---
# Implement TaskExecutor

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Main orchestrator that bridges ACP sessions and ATLAS's task/trajectory model.

## Files to Create

- `src/atlas/execution/executor.py`

## Dependencies

- ATLASConfig
- TrajectoryBuilder
- PromptFormatter
- Memory MCP Server
- `acp-factory` library

## Implementation

```python
import asyncio
import logging
from acp_factory import AgentFactory, SpawnOptions, SessionOptions

from atlas.config import ExecutorConfig, ATLASConfig
from atlas.core.types import Task, Trajectory, Outcome, Candidate
from atlas.protocols.environment import Environment
from atlas.protocols.memory import MemorySystem
from atlas.execution.trajectory_builder import TrajectoryBuilder
from atlas.execution.prompt_formatter import PromptFormatter

logger = logging.getLogger("atlas.execution")

class TaskExecutor:
    """Executes tasks via ACP agents, produces Trajectories."""
    
    def __init__(
        self,
        config: ATLASConfig = None,
        memory: MemorySystem | None = None,
    ):
        self._config = config or ATLASConfig()
        self._memory = memory
        self._agent_handle = None
        self._formatter = PromptFormatter(self._config.memory)
    
    async def execute(
        self,
        task: Task,
        env: Environment,
    ) -> Trajectory:
        """Execute a task and return complete trajectory."""
        logger.info("Task started", extra={"task_id": task.id})
        
        try:
            # 1. Query memory for context
            memory_result = None
            if self._memory:
                memory_result = self._memory.query(task)
            
            # 2. Format prompt
            prompt = self._formatter.format(task, memory_result)
            
            # 3. Get or create agent
            agent = await self._get_agent()
            
            # 4. Create session with MCP server
            sandbox = env.get_sandbox_handlers() if hasattr(env, 'get_sandbox_handlers') else None
            session = await agent.create_session(
                cwd=task.context.get("cwd", "."),
                options=SessionOptions(
                    mcp_servers=self._get_mcp_servers(),
                ),
            )
            
            # 5. Run and collect trajectory
            builder = TrajectoryBuilder(task, agent_id=self._config.executor.agent_type)
            
            try:
                async for update in asyncio.wait_for(
                    self._run_session(session, prompt, builder),
                    timeout=self._config.executor.timeout_seconds,
                ):
                    pass  # Updates processed in builder
            except asyncio.TimeoutError:
                await session.cancel()
                return builder.build(Outcome(
                    success=False,
                    error_info="timeout",
                ))
            
            # 6. Get solution and verify
            candidate = Candidate(
                solution=env.get_current_state() if hasattr(env, 'get_current_state') else None,
                confidence=1.0,
                reasoning="Agent execution completed",
                source="agent",
            )
            outcome = env.verify(task, candidate)
            
            # 7. Build and return trajectory
            trajectory = builder.build(outcome)
            logger.info("Task completed", extra={"task_id": task.id, "success": outcome.success})
            return trajectory
            
        except Exception as e:
            logger.error("Task failed", extra={"task_id": task.id, "error": str(e)})
            return Trajectory(
                task=task,
                steps=[],
                outcome=Outcome(success=False, error_info=f"agent_crashed: {e}"),
                metadata={"agent_id": self._config.executor.agent_type},
            )
    
    async def _run_session(self, session, prompt: str, builder: TrajectoryBuilder):
        """Run session and yield updates."""
        async for update in session.prompt(prompt):
            builder.process_update(update)
            yield update
    
    async def _get_agent(self):
        """Get or create agent handle."""
        if self._agent_handle is None or not self._agent_handle.is_running():
            self._agent_handle = await AgentFactory.spawn(
                self._config.executor.agent_type,
                SpawnOptions(permission_mode=self._config.executor.permission_mode),
            )
        return self._agent_handle
    
    def _get_mcp_servers(self) -> list:
        """Get MCP server configs."""
        # TODO: Return memory MCP server config
        return []
    
    async def execute_with_session(
        self,
        task: Task,
        env: Environment,
        session,
    ) -> Trajectory:
        """Execute using existing session (for forking)."""
        ...
    
    async def close(self) -> None:
        """Clean up agent handle."""
        if self._agent_handle:
            await self._agent_handle.close()
            self._agent_handle = None
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Agent crashes | Return partial Trajectory with error_info="agent_crashed" |
| Timeout | Cancel session, return with error_info="timeout" |
| Verification fails | Normal flow, Outcome.success=False |

## Acceptance Criteria

- [ ] Spawns ACP agent correctly
- [ ] Creates sessions with MCP servers
- [ ] Collects updates into Trajectory via TrajectoryBuilder
- [ ] Timeout handling works
- [ ] Error handling returns partial trajectories
- [ ] Session reuse config works
- [ ] Logging throughout
- [ ] Integration test with mock agent
