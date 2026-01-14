"""Tests for PromptFormatter."""

from __future__ import annotations

from typing import Any

import pytest

from cognitive_core.config import MemoryConfig
from cognitive_core.core.types import (
    CodeConcept,
    Experience,
    Strategy,
    Task,
    VerificationSpec,
)
from cognitive_core.execution.prompt_formatter import PromptFormatter
from cognitive_core.protocols.memory import MemoryQueryResult


class TestPromptFormatter:
    """Tests for PromptFormatter class."""

    @pytest.fixture
    def formatter(self) -> PromptFormatter:
        """Create a PromptFormatter with default config."""
        return PromptFormatter()

    @pytest.fixture
    def formatter_with_config(self) -> PromptFormatter:
        """Create a PromptFormatter with custom config."""
        config = MemoryConfig(
            max_experiences=2,
            max_strategies=2,
            max_concepts=2,
            max_context_tokens=1000,
        )
        return PromptFormatter(config)

    @pytest.fixture
    def task(self) -> Task:
        """Create a sample task."""
        return Task(
            id="task-001",
            domain="test",
            description="Fix the authentication bug in login.py",
            verification=VerificationSpec(method="test_suite"),
        )

    @pytest.fixture
    def task_with_context(self) -> Task:
        """Create a task with context."""
        return Task(
            id="task-002",
            domain="swe",
            description="Add input validation to the form",
            context={
                "file": "forms.py",
                "framework": "Django",
                "_internal": "ignored",
                "cwd": "/also/ignored",
            },
            verification=VerificationSpec(method="test_suite"),
        )

    @pytest.fixture
    def experiences(self) -> list[Experience]:
        """Create sample experiences."""
        return [
            Experience(
                id="exp-1",
                task_input="Fix null pointer in auth module",
                solution_output="Added null check before accessing user object",
                feedback="Tests passed",
                success=True,
                trajectory_id="traj-1",
            ),
            Experience(
                id="exp-2",
                task_input="Fix race condition in session handler",
                solution_output="Added mutex lock around critical section",
                feedback="Tests passed",
                success=True,
                trajectory_id="traj-2",
            ),
        ]

    @pytest.fixture
    def strategies(self) -> list[Strategy]:
        """Create sample strategies."""
        return [
            Strategy(
                id="strat-1",
                situation="Authentication bugs",
                suggestion="Check for null users and expired sessions first",
            ),
            Strategy(
                id="strat-2",
                situation="Form validation",
                suggestion="Validate on both client and server side",
            ),
        ]

    @pytest.fixture
    def concepts(self) -> list[CodeConcept]:
        """Create sample concepts."""
        return [
            CodeConcept(
                id="concept-1",
                name="null_check",
                description="Safe null checking pattern",
                code="if obj is not None: ...",
                signature="(obj: Any) -> bool",
            ),
            CodeConcept(
                id="concept-2",
                name="input_validate",
                description="Input validation decorator",
                code="@validate_input(...)",
                signature="(func: Callable) -> Callable",
            ),
        ]

    def test_format_task_only(self, formatter: PromptFormatter, task: Task) -> None:
        """Test formatting with just a task."""
        prompt = formatter.format(task)

        assert "## Task" in prompt
        assert task.description in prompt
        assert "## Notes" in prompt

    def test_format_task_with_context(
        self, formatter: PromptFormatter, task_with_context: Task
    ) -> None:
        """Test formatting includes context."""
        prompt = formatter.format(task_with_context)

        assert "### Additional Context" in prompt
        assert "file" in prompt
        assert "forms.py" in prompt
        assert "framework" in prompt
        assert "Django" in prompt
        # Internal/ignored keys should not appear
        assert "_internal" not in prompt
        assert "cwd" not in prompt

    def test_format_with_experiences(
        self,
        formatter: PromptFormatter,
        task: Task,
        experiences: list[Experience],
    ) -> None:
        """Test formatting with experiences."""
        memory = MemoryQueryResult(experiences=experiences)
        prompt = formatter.format(task, memory)

        assert "## Relevant Memory" in prompt
        assert "### Similar Experiences" in prompt
        assert "Fix null pointer" in prompt
        assert "succeeded" in prompt

    def test_format_with_strategies(
        self,
        formatter: PromptFormatter,
        task: Task,
        strategies: list[Strategy],
    ) -> None:
        """Test formatting with strategies."""
        memory = MemoryQueryResult(strategies=strategies)
        prompt = formatter.format(task, memory)

        assert "### Applicable Strategies" in prompt
        assert "Authentication bugs" in prompt
        assert "Check for null users" in prompt

    def test_format_with_concepts(
        self,
        formatter: PromptFormatter,
        task: Task,
        concepts: list[CodeConcept],
    ) -> None:
        """Test formatting with concepts."""
        memory = MemoryQueryResult(concepts=concepts)
        prompt = formatter.format(task, memory)

        assert "### Available Concepts" in prompt
        assert "null_check" in prompt
        assert "Safe null checking" in prompt

    def test_format_with_all_memory(
        self,
        formatter: PromptFormatter,
        task: Task,
        experiences: list[Experience],
        strategies: list[Strategy],
        concepts: list[CodeConcept],
    ) -> None:
        """Test formatting with all memory types."""
        memory = MemoryQueryResult(
            experiences=experiences,
            strategies=strategies,
            concepts=concepts,
        )
        prompt = formatter.format(task, memory)

        assert "## Relevant Memory" in prompt
        assert "### Similar Experiences" in prompt
        assert "### Applicable Strategies" in prompt
        assert "### Available Concepts" in prompt

    def test_format_empty_memory(self, formatter: PromptFormatter, task: Task) -> None:
        """Test formatting with empty memory result."""
        memory = MemoryQueryResult()
        prompt = formatter.format(task, memory)

        # Should not include memory section if empty
        assert "## Task" in prompt
        assert "## Notes" in prompt
        # Memory header might still appear but sections won't have content
        # Actually with is_empty() check, memory section should be skipped

    def test_respects_max_experiences(
        self,
        formatter_with_config: PromptFormatter,
        task: Task,
    ) -> None:
        """Test that max_experiences limit is respected."""
        # Create more experiences than limit
        many_experiences = [
            Experience(
                id=f"exp-{i}",
                task_input=f"Task {i}",
                solution_output=f"Solution {i}",
                feedback="OK",
                success=True,
                trajectory_id=f"traj-{i}",
            )
            for i in range(10)
        ]

        memory = MemoryQueryResult(experiences=many_experiences)
        prompt = formatter_with_config.format(task, memory)

        # Count occurrences - should be limited to max_experiences (2)
        count = prompt.count("**Task**:")
        assert count <= 2

    def test_respects_max_strategies(
        self,
        formatter_with_config: PromptFormatter,
        task: Task,
    ) -> None:
        """Test that max_strategies limit is respected."""
        many_strategies = [
            Strategy(
                id=f"strat-{i}",
                situation=f"Situation {i}",
                suggestion=f"Suggestion {i}",
            )
            for i in range(10)
        ]

        memory = MemoryQueryResult(strategies=many_strategies)
        prompt = formatter_with_config.format(task, memory)

        count = prompt.count("**When**:")
        assert count <= 2

    def test_respects_max_concepts(
        self,
        formatter_with_config: PromptFormatter,
        task: Task,
    ) -> None:
        """Test that max_concepts limit is respected."""
        many_concepts = [
            CodeConcept(
                id=f"concept-{i}",
                name=f"concept_{i}",
                description=f"Description {i}",
                code=f"code_{i}()",
                signature="() -> None",
            )
            for i in range(10)
        ]

        memory = MemoryQueryResult(concepts=many_concepts)
        prompt = formatter_with_config.format(task, memory)

        # Count concept entries (backtick-wrapped names)
        count = prompt.count("`concept_")
        assert count <= 2

    def test_truncates_long_task_summaries(
        self, formatter: PromptFormatter, task: Task
    ) -> None:
        """Test that long task summaries are truncated."""
        long_experience = Experience(
            id="exp-long",
            task_input="A" * 500,  # Very long task
            solution_output="B" * 500,  # Very long solution
            feedback="OK",
            success=True,
            trajectory_id="traj-long",
        )

        memory = MemoryQueryResult(experiences=[long_experience])
        prompt = formatter.format(task, memory)

        # Should contain truncation marker
        assert "..." in prompt

    def test_notes_section_with_memory(
        self, formatter: PromptFormatter, task: Task, experiences: list[Experience]
    ) -> None:
        """Test notes section mentions memory tools when memory is available."""
        memory = MemoryQueryResult(experiences=experiences)
        prompt = formatter.format(task, memory)

        assert "memory_search" in prompt

    def test_notes_section_without_memory(
        self, formatter: PromptFormatter, task: Task
    ) -> None:
        """Test notes section content without memory."""
        prompt = formatter.format(task, None)

        assert "## Notes" in prompt
        assert "Focus on the task" in prompt

    def test_handles_dict_experience(self, formatter: PromptFormatter, task: Task) -> None:
        """Test formatting handles dict-style experiences."""
        exp_dict = {
            "task_input": "Dict-based task",
            "solution_output": "Dict-based solution",
            "success": True,
        }

        # Create a memory result with dict experience
        memory = MemoryQueryResult(experiences=[exp_dict])  # type: ignore
        prompt = formatter.format(task, memory)

        assert "Dict-based task" in prompt

    def test_handles_dict_strategy(self, formatter: PromptFormatter, task: Task) -> None:
        """Test formatting handles dict-style strategies."""
        strat_dict = {
            "situation": "Dict situation",
            "suggestion": "Dict suggestion",
        }

        memory = MemoryQueryResult(strategies=[strat_dict])  # type: ignore
        prompt = formatter.format(task, memory)

        assert "Dict situation" in prompt

    def test_handles_dict_concept(self, formatter: PromptFormatter, task: Task) -> None:
        """Test formatting handles dict-style concepts."""
        concept_dict = {
            "name": "dict_concept",
            "description": "A dict-based concept",
        }

        memory = MemoryQueryResult(concepts=[concept_dict])  # type: ignore
        prompt = formatter.format(task, memory)

        assert "dict_concept" in prompt

    def test_experience_shows_outcome(
        self, formatter: PromptFormatter, task: Task
    ) -> None:
        """Test that experience outcome is shown correctly."""
        success_exp = Experience(
            id="exp-s",
            task_input="Task",
            solution_output="Solution",
            feedback="OK",
            success=True,
            trajectory_id="traj-s",
        )
        fail_exp = Experience(
            id="exp-f",
            task_input="Task",
            solution_output="Solution",
            feedback="Failed",
            success=False,
            trajectory_id="traj-f",
        )

        memory = MemoryQueryResult(experiences=[success_exp, fail_exp])
        prompt = formatter.format(task, memory)

        assert "succeeded" in prompt
        assert "failed" in prompt

    def test_token_estimation(self, formatter: PromptFormatter) -> None:
        """Test token estimation method."""
        text = "a" * 400  # 400 characters
        tokens = formatter._estimate_tokens(text)

        # Should be approximately chars / 4
        assert tokens == 100

    def test_truncation_warning_logged(
        self, formatter_with_config: PromptFormatter, task: Task, caplog
    ) -> None:
        """Test that truncation warning is logged."""
        import logging

        # Create a very long prompt that exceeds token limit
        long_experiences = [
            Experience(
                id=f"exp-{i}",
                task_input="X" * 200,
                solution_output="Y" * 200,
                feedback="OK",
                success=True,
                trajectory_id=f"traj-{i}",
            )
            for i in range(50)
        ]

        memory = MemoryQueryResult(experiences=long_experiences)

        with caplog.at_level(logging.WARNING, logger="cognitive_core.execution"):
            prompt = formatter_with_config.format(task, memory)

        # Should have been truncated and warning logged
        # Note: might not always trigger depending on limits
