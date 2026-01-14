---
id: i-78el
title: Implement PromptFormatter with memory context
priority: 1
created_at: '2026-01-07 08:55:55'
tags:
  - execution
  - phase-2
  - prompt
status: open
---
# Implement PromptFormatter

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Format task and memory context into structured prompts with token limits.

## Files to Create

- `src/atlas/execution/prompt_formatter.py`

## Template Structure

```markdown
## Task
{task.description}

{if task.context}
## Context
{task.context}
{endif}

## Relevant Memory

### Similar Experiences ({count})
{for exp in experiences}
- **{exp.task_summary}**
  - Approach: {exp.solution_summary}
  - Outcome: {exp.outcome}
{endfor}

### Applicable Strategies ({count})
{for strategy in strategies}
- When: {strategy.situation}
  Try: {strategy.suggestion}
{endfor}

### Available Concepts ({count})
{for concept in concepts}
- `{concept.name}`: {concept.description}
{endfor}

## Notes
- You can query additional memory using `memory_search_*` tools if needed.
```

## Implementation

```python
from atlas.config import MemoryConfig
from atlas.core.types import Task
from atlas.protocols.memory import MemoryQueryResult

class PromptFormatter:
    """Formats task and memory into structured prompts."""
    
    def __init__(self, config: MemoryConfig = None):
        self._config = config or MemoryConfig()
    
    def format(
        self,
        task: Task,
        memory_result: MemoryQueryResult | None = None,
    ) -> str:
        """Format task and memory into prompt."""
        sections = []
        
        # Task section
        sections.append(self._format_task(task))
        
        # Memory section (if available)
        if memory_result and not memory_result.is_empty():
            sections.append(self._format_memory(memory_result))
        
        # Notes
        sections.append(self._format_notes())
        
        return "\n\n".join(sections)
    
    def _format_task(self, task: Task) -> str:
        ...
    
    def _format_memory(self, memory: MemoryQueryResult) -> str:
        # Respect max_experiences, max_strategies, max_concepts
        # Truncate to max_context_tokens if needed
        ...
    
    def _format_notes(self) -> str:
        ...
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (chars / 4)."""
        return len(text) // 4
```

## Acceptance Criteria

- [ ] Formats task description correctly
- [ ] Includes memory context when provided
- [ ] Respects max_experiences, max_strategies, max_concepts limits
- [ ] Truncates to max_context_tokens if needed
- [ ] Handles empty memory gracefully
- [ ] Unit tests for various scenarios
