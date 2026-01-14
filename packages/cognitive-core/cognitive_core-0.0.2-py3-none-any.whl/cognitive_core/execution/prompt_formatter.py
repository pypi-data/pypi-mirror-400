"""PromptFormatter for formatting task and memory context into prompts.

Creates structured prompts with task description and relevant memory context
for agent execution.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from cognitive_core.config import MemoryConfig

if TYPE_CHECKING:
    from cognitive_core.core.types import Task
    from cognitive_core.protocols.memory import MemoryQueryResult

logger = logging.getLogger("cognitive_core.execution")


class PromptFormatter:
    """Formats task and memory into structured prompts.

    Creates prompts with:
    - Task description and context
    - Similar experiences from memory
    - Applicable strategies
    - Available code concepts
    - Notes on using memory tools

    Example:
        ```python
        formatter = PromptFormatter()
        prompt = formatter.format(task, memory_result)
        ```
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        """Initialize the prompt formatter.

        Args:
            config: Memory configuration with limits. Uses defaults if not provided.
        """
        self._config = config or MemoryConfig()

    def format(
        self,
        task: Task,
        memory_result: MemoryQueryResult | None = None,
    ) -> str:
        """Format task and memory into prompt.

        Args:
            task: The task to execute.
            memory_result: Query results from memory system (optional).

        Returns:
            Formatted prompt string.
        """
        sections: list[str] = []

        # Task section (always present)
        sections.append(self._format_task(task))

        # Memory section (if available and not empty)
        if memory_result is not None and not memory_result.is_empty():
            memory_section = self._format_memory(memory_result)
            if memory_section:
                sections.append(memory_section)

        # Notes section
        sections.append(self._format_notes(has_memory=memory_result is not None))

        prompt = "\n\n".join(sections)

        # Check token limit and truncate if needed
        estimated_tokens = self._estimate_tokens(prompt)
        if estimated_tokens > self._config.max_context_tokens:
            logger.warning(
                "Prompt exceeds token limit, truncating",
                extra={
                    "estimated_tokens": estimated_tokens,
                    "limit": self._config.max_context_tokens,
                },
            )
            prompt = self._truncate_prompt(prompt)

        return prompt

    def _format_task(self, task: Task) -> str:
        """Format the task section."""
        lines = ["## Task", "", task.description]

        # Add context if present
        context = task.context or {}
        if context:
            # Filter out internal context keys
            display_context = {
                k: v for k, v in context.items()
                if not k.startswith("_") and k not in ("cwd",)
            }
            if display_context:
                lines.extend(["", "### Additional Context"])
                for key, value in display_context.items():
                    lines.append(f"- **{key}**: {value}")

        return "\n".join(lines)

    def _format_memory(self, memory: MemoryQueryResult) -> str:
        """Format the memory context section."""
        sections: list[str] = ["## Relevant Memory"]

        # Experiences
        if memory.experiences:
            exp_section = self._format_experiences(
                memory.experiences[: self._config.max_experiences]
            )
            if exp_section:
                sections.append(exp_section)

        # Strategies
        if memory.strategies:
            strat_section = self._format_strategies(
                memory.strategies[: self._config.max_strategies]
            )
            if strat_section:
                sections.append(strat_section)

        # Concepts
        if memory.concepts:
            concept_section = self._format_concepts(
                memory.concepts[: self._config.max_concepts]
            )
            if concept_section:
                sections.append(concept_section)

        # Only return if we have content beyond the header
        if len(sections) > 1:
            return "\n\n".join(sections)
        return ""

    def _format_experiences(self, experiences: list[Any]) -> str:
        """Format similar experiences."""
        if not experiences:
            return ""

        lines = [f"### Similar Experiences ({len(experiences)})"]

        for exp in experiences:
            # Handle both dict and object access
            if isinstance(exp, dict):
                task_summary = exp.get("task_input", exp.get("task_summary", "Unknown task"))
                solution = exp.get("solution_output", exp.get("solution_summary", ""))
                success = exp.get("success", False)
            else:
                task_summary = getattr(exp, "task_input", getattr(exp, "task_summary", "Unknown"))
                solution = getattr(exp, "solution_output", getattr(exp, "solution_summary", ""))
                success = getattr(exp, "success", False)

            outcome = "succeeded" if success else "failed"

            # Truncate long summaries
            if len(task_summary) > 200:
                task_summary = task_summary[:200] + "..."
            if len(solution) > 300:
                solution = solution[:300] + "..."

            lines.append(f"- **Task**: {task_summary}")
            lines.append(f"  - Approach: {solution}")
            lines.append(f"  - Outcome: {outcome}")

        return "\n".join(lines)

    def _format_strategies(self, strategies: list[Any]) -> str:
        """Format applicable strategies."""
        if not strategies:
            return ""

        lines = [f"### Applicable Strategies ({len(strategies)})"]

        for strat in strategies:
            if isinstance(strat, dict):
                situation = strat.get("situation", "Unknown situation")
                suggestion = strat.get("suggestion", "No suggestion")
            else:
                situation = getattr(strat, "situation", "Unknown situation")
                suggestion = getattr(strat, "suggestion", "No suggestion")

            lines.append(f"- **When**: {situation}")
            lines.append(f"  **Try**: {suggestion}")

        return "\n".join(lines)

    def _format_concepts(self, concepts: list[Any]) -> str:
        """Format available code concepts."""
        if not concepts:
            return ""

        lines = [f"### Available Concepts ({len(concepts)})"]

        for concept in concepts:
            if isinstance(concept, dict):
                name = concept.get("name", "unknown")
                description = concept.get("description", "No description")
            else:
                name = getattr(concept, "name", "unknown")
                description = getattr(concept, "description", "No description")

            # Truncate long descriptions
            if len(description) > 150:
                description = description[:150] + "..."

            lines.append(f"- `{name}`: {description}")

        return "\n".join(lines)

    def _format_notes(self, has_memory: bool) -> str:
        """Format the notes section."""
        lines = ["## Notes"]

        if has_memory:
            lines.append(
                "- You can query additional memory using `memory_search_*` tools if needed."
            )

        lines.append("- Focus on the task at hand and use the provided context as guidance.")
        lines.append("- If you encounter unexpected situations, try searching memory for similar cases.")

        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (characters / 4).

        This is a simple heuristic. For more accurate counting,
        use a proper tokenizer.
        """
        return len(text) // 4

    def _truncate_prompt(self, prompt: str) -> str:
        """Truncate prompt to fit within token limit.

        Preserves task section and notes, truncates memory section.
        """
        max_chars = self._config.max_context_tokens * 4  # Rough conversion

        if len(prompt) <= max_chars:
            return prompt

        # Find section boundaries
        task_end = prompt.find("## Relevant Memory")
        notes_start = prompt.find("## Notes")

        if task_end == -1 or notes_start == -1:
            # Can't find sections, just truncate
            return prompt[:max_chars] + "\n\n[Content truncated due to length]"

        task_section = prompt[:task_end]
        notes_section = prompt[notes_start:]

        # Calculate how much memory we can include
        available_for_memory = max_chars - len(task_section) - len(notes_section) - 50

        if available_for_memory > 100:
            memory_section = prompt[task_end:notes_start]
            truncated_memory = memory_section[:available_for_memory]
            truncated_memory += "\n\n[Memory context truncated due to length]\n\n"
            return task_section + truncated_memory + notes_section
        else:
            # Not enough room for memory, just include task and notes
            return task_section + "\n\n" + notes_section
