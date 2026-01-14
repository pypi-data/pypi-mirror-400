"""Shared pytest fixtures for ATLAS tests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pytest

from cognitive_core.core.types import (
    CodeConcept,
    Experience,
    Outcome,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="task-001",
        domain="test",
        description="Fix the bug in the login function",
        context={"cwd": "/tmp/test", "file": "auth.py"},
        verification=VerificationSpec(method="test_suite"),
    )


@pytest.fixture
def sample_task_with_embedding() -> Task:
    """Create a sample task with an embedding."""
    return Task(
        id="task-002",
        domain="test",
        description="Implement user authentication",
        context={"cwd": "/tmp/test"},
        verification=VerificationSpec(method="test_suite"),
        embedding=np.random.rand(768).astype(np.float32),
    )


@pytest.fixture
def sample_step() -> Step:
    """Create a sample step for testing."""
    return Step(
        thought="I need to check the login function",
        action="Read({\"file_path\": \"/tmp/auth.py\"})",
        observation="def login(user, password): ...",
        metadata={"tool_name": "Read"},
    )


@pytest.fixture
def sample_outcome_success() -> Outcome:
    """Create a successful outcome."""
    return Outcome(
        success=True,
        partial_score=1.0,
        verification_details={"tests_passed": 5, "tests_total": 5},
    )


@pytest.fixture
def sample_outcome_failure() -> Outcome:
    """Create a failed outcome."""
    return Outcome(
        success=False,
        partial_score=0.4,
        error_info="Test failed: expected True, got False",
        verification_details={"tests_passed": 2, "tests_total": 5},
    )


@pytest.fixture
def sample_trajectory(sample_task: Task, sample_step: Step, sample_outcome_success: Outcome) -> Trajectory:
    """Create a sample trajectory for testing."""
    return Trajectory(
        task=sample_task,
        steps=[sample_step],
        outcome=sample_outcome_success,
        agent_id="test-agent",
        llm_calls=3,
        total_tokens=1500,
        wall_time_seconds=12.5,
    )


@pytest.fixture
def sample_experience() -> Experience:
    """Create a sample experience for testing."""
    return Experience(
        id="exp-001",
        task_input="Fix authentication bug",
        solution_output="Added null check before password comparison",
        feedback="All tests passed",
        success=True,
        trajectory_id="traj-001",
        embedding=np.random.rand(768).astype(np.float32),
    )


@pytest.fixture
def sample_concept() -> CodeConcept:
    """Create a sample code concept for testing."""
    return CodeConcept(
        id="concept-001",
        name="null_check",
        description="Check if value is null before using",
        code="if value is None: raise ValueError('Value cannot be None')",
        signature="(value: Any) -> None",
        examples=[("None", "ValueError"), ("'valid'", "None")],
        usage_count=10,
        success_rate=0.9,
        embedding=np.random.rand(768).astype(np.float32),
        source="learned",
    )


@pytest.fixture
def sample_strategy() -> Strategy:
    """Create a sample strategy for testing."""
    return Strategy(
        id="strat-001",
        situation="When encountering null pointer errors",
        suggestion="Add defensive null checks before dereferencing",
        parameters=[{"name": "variable", "type": "str"}],
        usage_count=5,
        success_rate=0.8,
        embedding=np.random.rand(768).astype(np.float32),
    )


@pytest.fixture
def mock_embedding() -> np.ndarray:
    """Create a mock embedding vector."""
    return np.random.rand(768).astype(np.float32)


@pytest.fixture
def mock_embeddings_batch() -> np.ndarray:
    """Create a batch of mock embeddings."""
    return np.random.rand(5, 768).astype(np.float32)
