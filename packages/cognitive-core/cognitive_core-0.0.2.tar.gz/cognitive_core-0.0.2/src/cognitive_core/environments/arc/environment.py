"""ARC environment implementation for ATLAS.

Provides an environment for ARC (Abstraction and Reasoning Corpus) grid tasks
with full verification using the arckit library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from cognitive_core.core.types import Outcome, Task
from cognitive_core.environments.arc.loader import find_task_by_id, load_arc_dataset
from cognitive_core.environments.arc.types import ARCTask, Grid
from cognitive_core.environments.arc.utils import format_grid, verify_grid

if TYPE_CHECKING:
    pass


class ARCEnvironment:
    """Environment for ARC grid tasks using arckit.

    ARC tasks involve transforming input grids to output grids based on
    learned patterns. This environment verifies solutions by comparing
    the agent's output grid to the expected output using exact matching
    and cell-by-cell similarity scoring.

    Example:
        ```python
        env = ARCEnvironment(dataset="arc")
        obs = env.reset(arc_task)
        outcome = env.verify(output_grid)
        ```
    """

    def __init__(self, dataset: str = "arc") -> None:
        """Initialize ARCEnvironment.

        Args:
            dataset: Which dataset to use ("arc", "kaggle2024", "kaggle2025").
                     Datasets are lazy-loaded on first use.
        """
        self._task: Task | None = None
        self._arc_task: ARCTask | None = None
        self._dataset_name = dataset
        self._dataset_loaded = False

    def reset(self, task: Task) -> str:
        """Reset the environment with a new ARC task.

        Task can specify ARC data via:
        - task.context["arc_task_id"] - load from arckit dataset
        - task.context["grids"] - raw grid data {"train": [...], "test": [...]}

        Args:
            task: The ARC task to solve.

        Returns:
            Initial observation as the task description with training examples.

        Raises:
            ValueError: If neither arc_task_id nor grids is provided.
        """
        self._task = task

        # Load ARC task from context
        if "arc_task_id" in task.context:
            arc_task = find_task_by_id(
                task.context["arc_task_id"],
                self._dataset_name,
            )
            if arc_task is None:
                raise ValueError(
                    f"Task ID '{task.context['arc_task_id']}' not found "
                    f"in {self._dataset_name} dataset"
                )
            self._arc_task = arc_task
        elif "grids" in task.context:
            self._arc_task = ARCTask.from_dict({
                "id": task.id,
                **task.context["grids"],
            })
        else:
            raise ValueError(
                "Task must have either 'arc_task_id' or 'grids' in context"
            )

        # Build description with training examples
        description = task.description
        if self._arc_task is not None:
            description += "\n\n## Training Examples\n"
            for i, (inp, out) in enumerate(self._arc_task.train):
                description += f"\n### Example {i + 1}\n"
                description += f"Input:\n{format_grid(inp)}\n"
                description += f"Output:\n{format_grid(out)}\n"

            description += "\n## Test Input(s)\n"
            for i, inp in enumerate(self._arc_task.test_inputs):
                description += f"\n### Test {i + 1}\n"
                description += f"Input:\n{format_grid(inp)}\n"

        return description

    def step(self, action: str) -> tuple[str, float, bool, dict[str, Any]]:
        """Execute an action in the environment.

        For ARC tasks, step is a no-op since solutions are verified directly.

        Args:
            action: The action to take.

        Returns:
            A tuple of (action, 0.0, False, {}).
        """
        return (action, 0.0, False, {})

    def verify(self, solution: Any) -> Outcome:
        """Verify a candidate solution against the expected output grid(s).

        Args:
            solution: numpy array, list of lists, or list of grids for multi-test tasks.
                     For single-test tasks, can be a single grid.
                     For multi-test tasks, should be a list of grids.

        Returns:
            Outcome with:
            - success: True if exact match on all test outputs
            - partial_score: Average cell-by-cell similarity (0.0-1.0)
            - verification_details: Per-test results

        Raises:
            RuntimeError: If reset() has not been called.
        """
        if self._arc_task is None:
            raise RuntimeError("No task set. Call reset() first.")

        # Get expected outputs from test cases
        test_pairs = self._arc_task.test
        num_tests = len(test_pairs)

        # Normalize solution to list of grids
        if num_tests == 1 and not self._is_list_of_grids(solution):
            # Single test case with single grid solution
            solutions = [solution]
        else:
            solutions = solution if isinstance(solution, list) else [solution]

        # Validate solution count
        if len(solutions) != num_tests:
            return Outcome(
                success=False,
                partial_score=0.0,
                error_info=f"Expected {num_tests} solutions, got {len(solutions)}",
                verification_details={
                    "expected_count": num_tests,
                    "actual_count": len(solutions),
                },
            )

        # Verify each test case
        all_match = True
        total_similarity = 0.0
        test_results = []

        for i, (pred, (_, expected)) in enumerate(zip(solutions, test_pairs)):
            exact_match, similarity = verify_grid(pred, expected)

            test_results.append({
                "test_index": i,
                "exact_match": exact_match,
                "similarity": similarity,
            })

            if not exact_match:
                all_match = False
            total_similarity += similarity

        avg_similarity = total_similarity / num_tests if num_tests > 0 else 0.0

        return Outcome(
            success=all_match,
            partial_score=avg_similarity,
            verification_details={
                "num_tests": num_tests,
                "test_results": test_results,
                "all_exact_match": all_match,
                "average_similarity": avg_similarity,
            },
        )

    def _is_list_of_grids(self, obj: Any) -> bool:
        """Check if obj is a list of grids (list of 2D arrays/lists).

        Args:
            obj: Object to check.

        Returns:
            True if obj is a list of grids.
        """
        if not isinstance(obj, list) or len(obj) == 0:
            return False

        first = obj[0]
        # Check if first element is itself a 2D structure
        if isinstance(first, np.ndarray):
            return first.ndim == 2
        if isinstance(first, list) and len(first) > 0:
            return isinstance(first[0], list)
        return False

    @property
    def max_steps(self) -> int:
        """Maximum steps before timeout.

        Returns:
            100 (default maximum steps).
        """
        return 100

    @property
    def is_deterministic(self) -> bool:
        """Whether the environment is deterministic.

        Returns:
            True (ARC tasks are deterministic).
        """
        return True

    @property
    def task(self) -> Task:
        """Current task being solved.

        Returns:
            The task that was set via reset().

        Raises:
            RuntimeError: If reset() has not been called.
        """
        if self._task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return self._task

    @property
    def arc_task(self) -> ARCTask | None:
        """Current ARC task data.

        Returns:
            The ARCTask for the current task, or None if not set.
        """
        return self._arc_task

    @property
    def training_pairs(self) -> list[tuple[np.ndarray, np.ndarray]]:
        """Get training input/output pairs for current task.

        Returns:
            List of (input_grid, output_grid) tuples as numpy arrays.

        Raises:
            RuntimeError: If reset() has not been called.
        """
        if self._arc_task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return [
            (np.array(inp), np.array(out))
            for inp, out in self._arc_task.train
        ]

    @property
    def test_inputs(self) -> list[np.ndarray]:
        """Get test inputs for current task.

        Returns:
            List of test input grids as numpy arrays.

        Raises:
            RuntimeError: If reset() has not been called.
        """
        if self._arc_task is None:
            raise RuntimeError("No task set. Call reset() first.")
        return [np.array(inp) for inp in self._arc_task.test_inputs]

    @property
    def _dataset(self) -> Any:
        """Lazy-loaded dataset reference.

        For backward compatibility. Returns None until dataset is accessed.

        Returns:
            None (datasets are now loaded via loader functions).
        """
        return None

    def _verify_grid(
        self, predicted: Grid | np.ndarray, expected: Grid | np.ndarray
    ) -> tuple[bool, float]:
        """Verify a predicted grid against expected output.

        Backward compatibility wrapper around utils.verify_grid.

        Args:
            predicted: Agent's predicted grid.
            expected: Expected output grid.

        Returns:
            Tuple of (exact_match, similarity_score).
        """
        return verify_grid(predicted, expected)


__all__ = ["ARCEnvironment"]
