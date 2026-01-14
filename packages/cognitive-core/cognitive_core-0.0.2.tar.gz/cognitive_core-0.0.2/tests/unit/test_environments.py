"""Tests for ATLAS environment implementations."""

from __future__ import annotations

import pytest

from cognitive_core.core.types import Outcome, Task, VerificationSpec
from cognitive_core.environments import (
    ARCEnvironment,
    PassthroughEnvironment,
    SWEEnvironment,
    create_environment,
)
from cognitive_core.protocols.environment import Environment


def make_task(
    task_id: str = "test-1",
    domain: str = "test",
    description: str = "Test task description",
) -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        domain=domain,
        description=description,
        verification=VerificationSpec(method="exact_match"),
    )


class TestPassthroughEnvironment:
    """Tests for PassthroughEnvironment implementation."""

    def test_implements_protocol(self) -> None:
        """PassthroughEnvironment implements Environment protocol after reset()."""
        env = PassthroughEnvironment()
        task = make_task()
        env.reset(task)
        assert isinstance(env, Environment)

    def test_reset_returns_task_description(self) -> None:
        """reset() returns the task description."""
        env = PassthroughEnvironment()
        task = make_task(description="Solve this problem")

        result = env.reset(task)

        assert result == "Solve this problem"

    def test_reset_stores_task(self) -> None:
        """reset() stores the task for later retrieval."""
        env = PassthroughEnvironment()
        task = make_task()

        env.reset(task)

        assert env.task == task

    def test_step_returns_passthrough_tuple(self) -> None:
        """step() returns (action, 0.0, False, {})."""
        env = PassthroughEnvironment()
        task = make_task()
        env.reset(task)

        result = env.step("test action")

        assert result == ("test action", 0.0, False, {})

    def test_step_passthrough_preserves_action(self) -> None:
        """step() returns the action unchanged."""
        env = PassthroughEnvironment()
        task = make_task()
        env.reset(task)

        action = "complex action with special chars !@#$%"
        observation, reward, done, info = env.step(action)

        assert observation == action
        assert reward == 0.0
        assert done is False
        assert info == {}

    def test_verify_returns_success(self) -> None:
        """verify() always returns success."""
        env = PassthroughEnvironment()
        task = make_task()
        env.reset(task)

        result = env.verify("any solution")

        assert isinstance(result, Outcome)
        assert result.success is True
        assert result.partial_score == 1.0

    def test_verify_ignores_solution(self) -> None:
        """verify() returns success regardless of solution content."""
        env = PassthroughEnvironment()
        task = make_task()
        env.reset(task)

        # Various solution types all succeed
        assert env.verify(None).success is True
        assert env.verify("").success is True
        assert env.verify({"complex": "object"}).success is True
        assert env.verify([1, 2, 3]).success is True

    def test_max_steps_returns_100(self) -> None:
        """max_steps returns 100."""
        env = PassthroughEnvironment()

        assert env.max_steps == 100

    def test_is_deterministic_returns_true(self) -> None:
        """is_deterministic returns True."""
        env = PassthroughEnvironment()

        assert env.is_deterministic is True

    def test_task_before_reset_raises_error(self) -> None:
        """task property raises RuntimeError before reset() is called."""
        env = PassthroughEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.task

    def test_task_after_reset_returns_task(self) -> None:
        """task property returns the set task after reset()."""
        env = PassthroughEnvironment()
        task = make_task(task_id="my-task")

        env.reset(task)

        assert env.task.id == "my-task"

    def test_multiple_resets_update_task(self) -> None:
        """reset() can be called multiple times with different tasks."""
        env = PassthroughEnvironment()
        task1 = make_task(task_id="task-1")
        task2 = make_task(task_id="task-2")

        env.reset(task1)
        assert env.task.id == "task-1"

        env.reset(task2)
        assert env.task.id == "task-2"


def make_arc_task(
    task_id: str = "arc-1",
    description: str = "Transform the grid",
    grids: dict | None = None,
) -> Task:
    """Create an ARC task with grid data."""
    if grids is None:
        grids = {
            "train": [
                ([[0, 1], [1, 0]], [[1, 0], [0, 1]]),  # invert colors
            ],
            "test": [
                ([[0, 0], [1, 1]], [[1, 1], [0, 0]]),
            ],
        }
    return Task(
        id=task_id,
        domain="arc",
        description=description,
        context={"grids": grids},
        verification=VerificationSpec(method="exact_match"),
    )


class TestARCEnvironment:
    """Tests for ARCEnvironment implementation."""

    def test_reset_returns_task_description_with_grids(self) -> None:
        """reset() returns the task description enhanced with training examples."""
        env = ARCEnvironment()
        task = make_arc_task(description="Transform the grid")

        result = env.reset(task)

        assert "Transform the grid" in result
        assert "Training Examples" in result
        assert "Test Input" in result

    def test_reset_stores_task(self) -> None:
        """reset() stores the task for later retrieval."""
        env = ARCEnvironment()
        task = make_arc_task()

        env.reset(task)

        assert env.task == task

    def test_step_returns_passthrough_tuple(self) -> None:
        """step() returns (action, 0.0, False, {})."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        result = env.step("grid transformation")

        assert result == ("grid transformation", 0.0, False, {})

    def test_verify_exact_match_success(self) -> None:
        """verify() returns success for exact match."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # The expected output for the test case is [[1, 1], [0, 0]]
        outcome = env.verify([[1, 1], [0, 0]])

        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_verify_partial_match(self) -> None:
        """verify() returns partial score for incorrect solution."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Wrong solution
        outcome = env.verify([[0, 0], [0, 0]])

        assert outcome.success is False
        assert outcome.partial_score == 0.5  # 2 of 4 cells match

    def test_verify_no_match(self) -> None:
        """verify() returns 0.0 score for completely wrong solution."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Completely wrong
        outcome = env.verify([[2, 2], [2, 2]])

        assert outcome.success is False
        assert outcome.partial_score == 0.0

    def test_max_steps_returns_100(self) -> None:
        """max_steps returns 100."""
        env = ARCEnvironment()

        assert env.max_steps == 100

    def test_is_deterministic_returns_true(self) -> None:
        """is_deterministic returns True."""
        env = ARCEnvironment()

        assert env.is_deterministic is True

    def test_task_before_reset_raises_error(self) -> None:
        """task property raises RuntimeError before reset() is called."""
        env = ARCEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.task

    def test_training_pairs_property(self) -> None:
        """training_pairs returns list of (input, output) tuples."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        pairs = env.training_pairs
        assert len(pairs) == 1
        inp, out = pairs[0]
        assert inp.tolist() == [[0, 1], [1, 0]]
        assert out.tolist() == [[1, 0], [0, 1]]

    def test_test_inputs_property(self) -> None:
        """test_inputs returns list of test input grids."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        inputs = env.test_inputs
        assert len(inputs) == 1
        assert inputs[0].tolist() == [[0, 0], [1, 1]]

    def test_reset_without_grids_raises_error(self) -> None:
        """reset() raises ValueError when no grid data is provided."""
        env = ARCEnvironment()
        task = Task(
            id="arc-1",
            domain="arc",
            description="No grids",
            verification=VerificationSpec(method="exact_match"),
        )

        with pytest.raises(ValueError, match="arc_task_id.*grids"):
            env.reset(task)


class TestSWEEnvironment:
    """Tests for SWEEnvironment implementation."""

    def test_reset_returns_task_description(self) -> None:
        """reset() returns the task description with mode info."""
        env = SWEEnvironment(mock_mode=True)
        task = make_task(domain="swe", description="Fix the authentication bug")

        result = env.reset(task)

        assert "Fix the authentication bug" in result
        # In mock mode, should indicate mock mode
        assert "[Running in mock mode - no Docker]" in result

    def test_reset_stores_task(self) -> None:
        """reset() stores the task for later retrieval."""
        env = SWEEnvironment(mock_mode=True)
        task = make_task(domain="swe")

        env.reset(task)

        assert env.task == task

    def test_step_returns_tuple_with_info(self) -> None:
        """step() returns (observation, 0.0, False, info) with action info."""
        env = SWEEnvironment(mock_mode=True)
        task = make_task(domain="swe")
        env.reset(task)

        obs, reward, done, info = env.step("edit file auth.py")

        assert isinstance(obs, str)
        assert reward == 0.0
        assert done is False
        assert "action_type" in info
        assert info["action_type"] == "command"

    def test_verify_returns_outcome(self) -> None:
        """verify() returns Outcome instead of raising NotImplementedError."""
        env = SWEEnvironment(mock_mode=True)
        task = make_task(domain="swe")
        env.reset(task)

        outcome = env.verify("def fixed_function(): pass")

        # In mock mode, verify returns success
        assert isinstance(outcome, Outcome)
        assert outcome.success is True

    def test_max_steps_returns_100(self) -> None:
        """max_steps returns 100."""
        env = SWEEnvironment(mock_mode=True)

        assert env.max_steps == 100

    def test_is_deterministic_returns_true(self) -> None:
        """is_deterministic returns True."""
        env = SWEEnvironment(mock_mode=True)

        assert env.is_deterministic is True

    def test_task_before_reset_raises_error(self) -> None:
        """task property raises RuntimeError before reset() is called."""
        env = SWEEnvironment(mock_mode=True)

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.task


class TestCreateEnvironment:
    """Tests for create_environment factory function."""

    def test_arc_domain_returns_arc_environment(self) -> None:
        """create_environment returns ARCEnvironment for domain='arc'."""
        task = make_task(domain="arc")

        env = create_environment(task)

        assert isinstance(env, ARCEnvironment)

    def test_swe_domain_returns_swe_environment(self) -> None:
        """create_environment returns SWEEnvironment for domain='swe'."""
        task = make_task(domain="swe")

        env = create_environment(task)

        assert isinstance(env, SWEEnvironment)

    def test_other_domain_returns_passthrough_environment(self) -> None:
        """create_environment returns PassthroughEnvironment for other domains."""
        task = make_task(domain="custom")

        env = create_environment(task)

        assert isinstance(env, PassthroughEnvironment)

    def test_empty_domain_returns_passthrough_environment(self) -> None:
        """create_environment returns PassthroughEnvironment for empty domain."""
        task = make_task(domain="")

        env = create_environment(task)

        assert isinstance(env, PassthroughEnvironment)

    def test_unknown_domain_returns_passthrough_environment(self) -> None:
        """create_environment returns PassthroughEnvironment for unknown domains."""
        for domain in ["math", "code", "frontend", "backend", "test"]:
            task = make_task(domain=domain)

            env = create_environment(task)

            assert isinstance(env, PassthroughEnvironment), f"Expected PassthroughEnvironment for domain '{domain}'"

    def test_returns_environment_protocol(self) -> None:
        """create_environment always returns an Environment protocol instance."""
        # Test with appropriate tasks for each domain
        test_cases = [
            ("arc", make_arc_task()),
            ("swe", make_task(domain="swe")),
            ("custom", make_task(domain="custom")),
            ("other", make_task(domain="other")),
        ]
        for domain, task in test_cases:
            env = create_environment(task)
            # Reset first so task property is available for isinstance check
            env.reset(task)

            assert isinstance(env, Environment), f"Expected Environment protocol for domain '{domain}'"


class TestEnvironmentProtocolCompliance:
    """Tests to verify all environments comply with the Environment protocol."""

    @pytest.fixture(params=[PassthroughEnvironment, ARCEnvironment, SWEEnvironment])
    def env_class(self, request: pytest.FixtureRequest) -> type:
        """Parametrized fixture for environment classes."""
        return request.param

    def _make_task_for_env(self, env_class: type) -> Task:
        """Create appropriate task for the environment type."""
        if env_class == ARCEnvironment:
            return make_arc_task()
        return make_task()

    def test_has_reset_method(self, env_class: type) -> None:
        """Environment has reset method."""
        env = env_class()
        assert hasattr(env, "reset")
        assert callable(env.reset)

    def test_has_step_method(self, env_class: type) -> None:
        """Environment has step method."""
        env = env_class()
        assert hasattr(env, "step")
        assert callable(env.step)

    def test_has_verify_method(self, env_class: type) -> None:
        """Environment has verify method."""
        env = env_class()
        assert hasattr(env, "verify")
        assert callable(env.verify)

    def test_has_max_steps_property(self, env_class: type) -> None:
        """Environment has max_steps property."""
        env = env_class()
        assert hasattr(env, "max_steps")
        assert isinstance(env.max_steps, int)

    def test_has_is_deterministic_property(self, env_class: type) -> None:
        """Environment has is_deterministic property."""
        env = env_class()
        assert hasattr(env, "is_deterministic")
        assert isinstance(env.is_deterministic, bool)

    def test_has_task_property(self, env_class: type) -> None:
        """Environment has task property after reset."""
        env = env_class()
        task = self._make_task_for_env(env_class)
        env.reset(task)
        # Verify task property exists and returns the task
        assert hasattr(env, "task")
        assert env.task == task

    def test_reset_returns_string(self, env_class: type) -> None:
        """reset() returns a string."""
        env = env_class()
        task = self._make_task_for_env(env_class)

        result = env.reset(task)

        assert isinstance(result, str)

    def test_step_returns_tuple(self, env_class: type) -> None:
        """step() returns a tuple of (str, float, bool, dict)."""
        env = env_class()
        task = self._make_task_for_env(env_class)
        env.reset(task)

        result = env.step("action")

        assert isinstance(result, tuple)
        assert len(result) == 4
        obs, reward, done, info = result
        assert isinstance(obs, str)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)
