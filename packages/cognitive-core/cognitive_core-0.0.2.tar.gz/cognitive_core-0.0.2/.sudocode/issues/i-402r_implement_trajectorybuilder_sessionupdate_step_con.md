---
id: i-402r
title: Implement TrajectoryBuilder (SessionUpdate → Step conversion)
priority: 1
created_at: '2026-01-07 08:55:54'
tags:
  - execution
  - phase-2
  - trajectory
status: open
---
# Implement TrajectoryBuilder

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Convert ACP SessionUpdates into ATLAS Trajectory Steps using tool-centric mapping.

## Files to Create

- `src/atlas/execution/__init__.py`
- `src/atlas/execution/trajectory_builder.py`

## Mapping Rules

| ACP Update | ATLAS Step Component |
|------------|---------------------|
| `agent_message_chunk` (before tool) | `step.thought` |
| `tool_call` | `step.action` (tool name + args) |
| `tool_call_update` (completed) | `step.observation` (tool result) |
| `agent_message_chunk` (after tool) | Next step's `thought` |

## Implementation

```python
from datetime import datetime
from atlas.core.types import Step, Trajectory, Task, Outcome

class TrajectoryBuilder:
    """Builds Trajectory from ACP session updates."""
    
    def __init__(self, task: Task, agent_id: str):
        self._task = task
        self._agent_id = agent_id
        self._steps: list[Step] = []
        self._current_thought: list[str] = []
        self._current_tool_call: dict | None = None
    
    def process_update(self, update: dict) -> None:
        """Process a single session update."""
        match update.get("session_update"):
            case "agent_message_chunk":
                self._handle_message_chunk(update)
            case "tool_call":
                self._handle_tool_call(update)
            case "tool_call_update":
                self._handle_tool_update(update)
    
    def _handle_message_chunk(self, update: dict) -> None:
        """Accumulate agent text as thought."""
        content = update.get("content", {})
        if content.get("type") == "text":
            self._current_thought.append(content.get("text", ""))
    
    def _handle_tool_call(self, update: dict) -> None:
        """Start tracking a new tool call."""
        self._current_tool_call = {
            "name": update.get("title", "unknown"),
            "args": update.get("arguments", {}),
        }
    
    def _handle_tool_update(self, update: dict) -> None:
        """Complete a step when tool finishes."""
        if update.get("status") == "completed" and self._current_tool_call:
            step = Step(
                thought="".join(self._current_thought),
                action=f"{self._current_tool_call['name']}: {self._current_tool_call['args']}",
                observation=update.get("result", ""),
                metadata={"tool_name": self._current_tool_call["name"]},
            )
            self._steps.append(step)
            self._current_thought = []
            self._current_tool_call = None
    
    def build(self, outcome: Outcome) -> Trajectory:
        """Finalize and return the trajectory."""
        # Handle any remaining thought without tool call
        if self._current_thought and not self._current_tool_call:
            # Final message without action
            pass
        
        return Trajectory(
            task=self._task,
            steps=self._steps,
            outcome=outcome,
            metadata={"agent_id": self._agent_id, "timestamp": datetime.now().isoformat()},
        )
```

## Acceptance Criteria

- [ ] Correctly maps tool_call + tool_call_update to Step
- [ ] Accumulates agent_message_chunk as thought
- [ ] Handles multiple steps in sequence
- [ ] Builds valid Trajectory with metadata
- [ ] Unit tests with mock session updates
