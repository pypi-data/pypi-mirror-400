"""Comprehensive tests for ARCEnvironment with arckit integration."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from cognitive_core.core.types import Outcome, Task, VerificationSpec
from cognitive_core.environments import ARCEnvironment


def make_arc_task(
    task_id: str = "arc-1",
    description: str = "Transform the grid",
    grids: dict[str, Any] | None = None,
    arc_task_id: str | None = None,
    arc_dataset: str | None = None,
) -> Task:
    """Create an ARC task with grid data."""
    context: dict[str, Any] = {}

    if grids is not None:
        context["grids"] = grids
    elif arc_task_id is not None:
        context["arc_task_id"] = arc_task_id
    else:
        # Default grids: simple color inversion pattern
        context["grids"] = {
            "train": [
                ([[0, 1], [1, 0]], [[1, 0], [0, 1]]),  # invert colors
            ],
            "test": [
                ([[0, 0], [1, 1]], [[1, 1], [0, 0]]),
            ],
        }

    if arc_dataset:
        context["arc_dataset"] = arc_dataset

    return Task(
        id=task_id,
        domain="arc",
        description=description,
        context=context,
        verification=VerificationSpec(method="exact_match"),
    )


class TestARCEnvironmentInit:
    """Tests for ARCEnvironment initialization."""

    def test_default_dataset(self) -> None:
        """Default dataset is 'arc'."""
        env = ARCEnvironment()
        assert env._dataset_name == "arc"

    def test_custom_dataset(self) -> None:
        """Can specify custom dataset."""
        env = ARCEnvironment(dataset="kaggle2024")
        assert env._dataset_name == "kaggle2024"

    def test_lazy_loading(self) -> None:
        """Dataset is not loaded until needed."""
        env = ARCEnvironment()
        assert env._dataset is None

    def test_no_task_initially(self) -> None:
        """No task set initially."""
        env = ARCEnvironment()
        assert env._task is None
        assert env._arc_task is None


class TestARCEnvironmentReset:
    """Tests for ARCEnvironment reset method."""

    def test_reset_with_grids(self) -> None:
        """reset() accepts raw grid data."""
        env = ARCEnvironment()
        task = make_arc_task()

        obs = env.reset(task)

        assert env.task == task
        assert env._arc_task is not None
        assert "Training Examples" in obs

    def test_reset_returns_enhanced_description(self) -> None:
        """reset() returns description with training examples and test inputs."""
        env = ARCEnvironment()
        task = make_arc_task(description="Find the pattern")

        obs = env.reset(task)

        assert "Find the pattern" in obs
        assert "Training Examples" in obs
        assert "Example 1" in obs
        assert "Test Input" in obs
        assert "Test 1" in obs

    def test_reset_formats_grids(self) -> None:
        """reset() formats grids in readable form."""
        env = ARCEnvironment()
        grids = {
            "train": [([[1, 2], [3, 4]], [[5, 6], [7, 8]])],
            "test": [([[9, 0], [1, 2]], [[3, 4], [5, 6]])],
        }
        task = make_arc_task(grids=grids)

        obs = env.reset(task)

        # Check grid values appear in output
        assert "1 2" in obs
        assert "3 4" in obs
        assert "9 0" in obs

    def test_reset_without_context_raises_error(self) -> None:
        """reset() raises ValueError without grid data or task ID."""
        env = ARCEnvironment()
        task = Task(
            id="bad-task",
            domain="arc",
            description="No grid data",
            context={},
            verification=VerificationSpec(method="exact_match"),
        )

        with pytest.raises(ValueError, match="arc_task_id.*grids"):
            env.reset(task)

    def test_reset_stores_task(self) -> None:
        """reset() stores the ATLAS task."""
        env = ARCEnvironment()
        task = make_arc_task(task_id="my-arc-task")

        env.reset(task)

        assert env.task.id == "my-arc-task"

    def test_multiple_resets(self) -> None:
        """Can reset multiple times with different tasks."""
        env = ARCEnvironment()
        task1 = make_arc_task(task_id="task-1")
        task2 = make_arc_task(task_id="task-2")

        env.reset(task1)
        assert env.task.id == "task-1"

        env.reset(task2)
        assert env.task.id == "task-2"


class TestARCEnvironmentVerify:
    """Tests for ARCEnvironment verify method."""

    def test_verify_exact_match(self) -> None:
        """verify() returns success for exact match."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        outcome = env.verify([[1, 1], [0, 0]])

        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_verify_with_numpy_array(self) -> None:
        """verify() accepts numpy arrays."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        outcome = env.verify(np.array([[1, 1], [0, 0]]))

        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_verify_partial_match_50_percent(self) -> None:
        """verify() returns 50% score for half-correct solution."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Expected: [[1, 1], [0, 0]]
        # Wrong solution: [[0, 0], [0, 0]] - matches 2 of 4 cells
        outcome = env.verify([[0, 0], [0, 0]])

        assert outcome.success is False
        assert outcome.partial_score == 0.5

    def test_verify_partial_match_75_percent(self) -> None:
        """verify() returns 75% score for mostly-correct solution."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Expected: [[1, 1], [0, 0]]
        # Wrong solution: [[1, 1], [0, 1]] - matches 3 of 4 cells
        outcome = env.verify([[1, 1], [0, 1]])

        assert outcome.success is False
        assert outcome.partial_score == 0.75

    def test_verify_no_match(self) -> None:
        """verify() returns 0% score for completely wrong solution."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Expected: [[1, 1], [0, 0]]
        # Completely wrong: [[2, 2], [3, 3]]
        outcome = env.verify([[2, 2], [3, 3]])

        assert outcome.success is False
        assert outcome.partial_score == 0.0

    def test_verify_wrong_shape(self) -> None:
        """verify() returns 0% for wrong shape."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Expected: 2x2, provided: 3x3
        outcome = env.verify([[1, 1, 1], [0, 0, 0], [1, 1, 1]])

        assert outcome.success is False
        assert outcome.partial_score == 0.0

    def test_verify_before_reset_raises_error(self) -> None:
        """verify() raises RuntimeError before reset() is called."""
        env = ARCEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            env.verify([[1, 0], [0, 1]])

    def test_verify_details(self) -> None:
        """verify() returns detailed verification info."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        outcome = env.verify([[1, 1], [0, 0]])

        assert "num_tests" in outcome.verification_details
        assert "test_results" in outcome.verification_details
        assert outcome.verification_details["num_tests"] == 1
        assert outcome.verification_details["all_exact_match"] is True


class TestARCEnvironmentMultiTest:
    """Tests for multi-test task verification."""

    def test_multi_test_all_correct(self) -> None:
        """verify() returns success when all test cases match."""
        env = ARCEnvironment()
        grids = {
            "train": [([[0]], [[1]])],
            "test": [
                ([[0]], [[1]]),
                ([[1]], [[0]]),
            ],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        outcome = env.verify([[[1]], [[0]]])

        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_multi_test_partial_correct(self) -> None:
        """verify() returns average score for partial matches."""
        env = ARCEnvironment()
        grids = {
            "train": [([[0]], [[1]])],
            "test": [
                ([[0]], [[1]]),
                ([[1]], [[0]]),
            ],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        # First correct, second wrong
        outcome = env.verify([[[1]], [[1]]])

        assert outcome.success is False
        assert outcome.partial_score == 0.5  # (1.0 + 0.0) / 2

    def test_multi_test_wrong_count(self) -> None:
        """verify() returns error for wrong number of solutions."""
        env = ARCEnvironment()
        grids = {
            "train": [([[0]], [[1]])],
            "test": [
                ([[0]], [[1]]),
                ([[1]], [[0]]),
            ],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        # Only one solution for two tests
        outcome = env.verify([[[1]]])

        assert outcome.success is False
        assert outcome.partial_score == 0.0
        assert "Expected 2 solutions" in (outcome.error_info or "")


class TestARCEnvironmentTrainingPairs:
    """Tests for training_pairs property."""

    def test_training_pairs_returns_list(self) -> None:
        """training_pairs returns list of tuples."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        pairs = env.training_pairs

        assert isinstance(pairs, list)
        assert len(pairs) == 1
        assert len(pairs[0]) == 2  # (input, output)

    def test_training_pairs_contains_arrays(self) -> None:
        """training_pairs contains numpy arrays."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        pairs = env.training_pairs
        inp, out = pairs[0]

        assert isinstance(inp, np.ndarray)
        assert isinstance(out, np.ndarray)

    def test_training_pairs_correct_values(self) -> None:
        """training_pairs contains correct grid values."""
        env = ARCEnvironment()
        grids = {
            "train": [
                ([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
                ([[9, 0], [1, 2]], [[3, 4], [5, 6]]),
            ],
            "test": [([[0]], [[1]])],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        pairs = env.training_pairs

        assert len(pairs) == 2
        assert pairs[0][0].tolist() == [[1, 2], [3, 4]]
        assert pairs[0][1].tolist() == [[5, 6], [7, 8]]

    def test_training_pairs_before_reset_raises(self) -> None:
        """training_pairs raises RuntimeError before reset()."""
        env = ARCEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.training_pairs


class TestARCEnvironmentTestInputs:
    """Tests for test_inputs property."""

    def test_test_inputs_returns_list(self) -> None:
        """test_inputs returns list of input grids."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        inputs = env.test_inputs

        assert isinstance(inputs, list)
        assert len(inputs) == 1

    def test_test_inputs_contains_arrays(self) -> None:
        """test_inputs contains numpy arrays."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        inputs = env.test_inputs

        assert isinstance(inputs[0], np.ndarray)

    def test_test_inputs_correct_values(self) -> None:
        """test_inputs contains correct grid values."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        inputs = env.test_inputs

        assert inputs[0].tolist() == [[0, 0], [1, 1]]

    def test_test_inputs_before_reset_raises(self) -> None:
        """test_inputs raises RuntimeError before reset()."""
        env = ARCEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.test_inputs


class TestARCEnvironmentStep:
    """Tests for step method."""

    def test_step_passthrough(self) -> None:
        """step() returns passthrough tuple."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        result = env.step("analyze pattern")

        assert result == ("analyze pattern", 0.0, False, {})

    def test_step_preserves_action(self) -> None:
        """step() preserves action text exactly."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        action = "complex action with special chars !@#$%"
        obs, reward, done, info = env.step(action)

        assert obs == action


class TestARCEnvironmentProperties:
    """Tests for environment properties."""

    def test_max_steps(self) -> None:
        """max_steps returns 100."""
        env = ARCEnvironment()
        assert env.max_steps == 100

    def test_is_deterministic(self) -> None:
        """is_deterministic returns True."""
        env = ARCEnvironment()
        assert env.is_deterministic is True

    def test_task_before_reset(self) -> None:
        """task raises RuntimeError before reset()."""
        env = ARCEnvironment()

        with pytest.raises(RuntimeError, match="No task set"):
            _ = env.task

    def test_task_after_reset(self) -> None:
        """task returns the set task after reset()."""
        env = ARCEnvironment()
        task = make_arc_task(task_id="my-task")

        env.reset(task)

        assert env.task.id == "my-task"


class TestARCEnvironmentGridVerification:
    """Tests for internal grid verification logic."""

    def test_verify_grid_exact_match(self) -> None:
        """_verify_grid returns (True, 1.0) for exact match."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        match, score = env._verify_grid([[1, 2], [3, 4]], [[1, 2], [3, 4]])

        assert match is True
        assert score == 1.0

    def test_verify_grid_partial_match(self) -> None:
        """_verify_grid returns correct similarity for partial match."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # 3 of 4 cells match
        match, score = env._verify_grid([[1, 2], [3, 4]], [[1, 2], [3, 5]])

        assert match is False
        assert score == 0.75

    def test_verify_grid_shape_mismatch(self) -> None:
        """_verify_grid returns (False, 0.0) for shape mismatch."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        match, score = env._verify_grid([[1, 2], [3, 4]], [[1, 2, 3]])

        assert match is False
        assert score == 0.0

    def test_verify_grid_empty(self) -> None:
        """_verify_grid handles empty grids."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        match, score = env._verify_grid([], [])

        assert match is True
        assert score == 0.0  # No cells to compare


class TestARCEnvironmentEdgeCases:
    """Tests for edge cases and error handling."""

    def test_large_grid(self) -> None:
        """Handles large grids correctly."""
        env = ARCEnvironment()
        size = 30
        large_grid = [[i % 10 for _ in range(size)] for i in range(size)]
        grids = {
            "train": [(large_grid, large_grid)],
            "test": [(large_grid, large_grid)],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        outcome = env.verify(large_grid)

        assert outcome.success is True
        assert outcome.partial_score == 1.0

    def test_single_cell_grid(self) -> None:
        """Handles 1x1 grids correctly."""
        env = ARCEnvironment()
        grids = {
            "train": [([[0]], [[1]])],
            "test": [([[0]], [[1]])],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        outcome = env.verify([[1]])

        assert outcome.success is True

    def test_non_square_grid(self) -> None:
        """Handles non-square grids correctly."""
        env = ARCEnvironment()
        grids = {
            "train": [([[0, 1, 2]], [[2, 1, 0]])],  # 1x3
            "test": [([[0, 1, 2]], [[2, 1, 0]])],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        outcome = env.verify([[2, 1, 0]])

        assert outcome.success is True

    def test_empty_training_pairs(self) -> None:
        """Handles empty training pairs."""
        env = ARCEnvironment()
        grids = {
            "train": [],
            "test": [([[0]], [[1]])],
        }
        task = make_arc_task(grids=grids)
        env.reset(task)

        assert len(env.training_pairs) == 0

    def test_verify_with_integer_list(self) -> None:
        """verify() accepts integer lists."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        outcome = env.verify([[1, 1], [0, 0]])

        assert outcome.success is True

    def test_is_list_of_grids_detection(self) -> None:
        """_is_list_of_grids correctly identifies grid lists vs single grids."""
        env = ARCEnvironment()
        task = make_arc_task()
        env.reset(task)

        # Single grid (list of 1D lists) - NOT a list of grids
        assert env._is_list_of_grids([[1, 2], [3, 4]]) is False

        # List of grids (list of 2D lists)
        assert env._is_list_of_grids([[[1, 2]], [[3, 4]]]) is True

        # Numpy arrays
        assert env._is_list_of_grids([np.array([[1, 2]])]) is True

        # Empty list
        assert env._is_list_of_grids([]) is False

        # Not a list
        assert env._is_list_of_grids("not a grid") is False
