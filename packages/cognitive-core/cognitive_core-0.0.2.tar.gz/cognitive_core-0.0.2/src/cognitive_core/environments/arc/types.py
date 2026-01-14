"""Type definitions for ARC (Abstraction and Reasoning Corpus) tasks.

Provides type aliases and data structures for working with ARC grid puzzles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

# Type alias for ARC grids - 2D arrays of integers (0-9 representing colors)
Grid = list[list[int]]


@dataclass
class ARCTask:
    """Representation of an ARC task.

    ARC tasks consist of training examples (input/output grid pairs) and
    test cases where the agent must predict the output grid.

    Attributes:
        id: Unique task identifier (e.g., "007bbfb7")
        train: List of (input_grid, output_grid) training pairs
        test: List of (input_grid, output_grid) test pairs

    Example:
        ```python
        task = ARCTask(
            id="example",
            train=[
                ([[0, 1], [1, 0]], [[1, 0], [0, 1]]),
                ([[0, 0], [0, 0]], [[1, 1], [1, 1]]),
            ],
            test=[
                ([[1, 1], [0, 0]], [[0, 0], [1, 1]]),
            ],
        )
        ```
    """

    id: str
    train: list[tuple[Grid, Grid]] = field(default_factory=list)
    test: list[tuple[Grid, Grid]] = field(default_factory=list)

    @classmethod
    def from_arckit(cls, arckit_task: Any) -> ARCTask:
        """Create ARCTask from an arckit.Task object.

        Args:
            arckit_task: Task object from the arckit library.

        Returns:
            ARCTask with data copied from arckit task.
        """
        train_pairs = [
            (np.array(inp).tolist(), np.array(out).tolist())
            for inp, out in arckit_task.train
        ]
        test_pairs = [
            (np.array(inp).tolist(), np.array(out).tolist())
            for inp, out in arckit_task.test
        ]
        return cls(
            id=arckit_task.id,
            train=train_pairs,
            test=test_pairs,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ARCTask:
        """Create ARCTask from a dictionary.

        Supports two formats:
        1. Tuple format: {"train": [(input, output), ...], "test": [...]}
        2. JSON format: {"train": [{"input": ..., "output": ...}], ...}

        Args:
            data: Dictionary with 'train' and 'test' keys containing
                  either tuple pairs or dict objects.

        Returns:
            ARCTask with data from dictionary.

        Example:
            ```python
            # Tuple format
            data = {
                "train": [([[0, 1]], [[1, 0]])],
                "test": [([[1, 1]], [[0, 0]])],
            }
            task = ARCTask.from_dict(data)

            # JSON format
            data = {
                "train": [{"input": [[0, 1]], "output": [[1, 0]]}],
                "test": [{"input": [[1, 1]], "output": [[0, 0]]}],
            }
            task = ARCTask.from_dict(data)
            ```
        """
        train_pairs = cls._parse_pairs(data.get("train", []))
        test_pairs = cls._parse_pairs(data.get("test", []))
        return cls(
            id=data.get("id", "unknown"),
            train=train_pairs,
            test=test_pairs,
        )

    @staticmethod
    def _parse_pairs(pairs: list[Any]) -> list[tuple[Grid, Grid]]:
        """Parse input/output pairs from either tuple or dict format.

        Args:
            pairs: List of pairs in either format.

        Returns:
            List of (input, output) tuples.
        """
        result: list[tuple[Grid, Grid]] = []
        for pair in pairs:
            if isinstance(pair, dict):
                # JSON format: {"input": ..., "output": ...}
                result.append((pair["input"], pair["output"]))
            elif isinstance(pair, (list, tuple)) and len(pair) == 2:
                # Tuple format: (input, output)
                result.append((pair[0], pair[1]))
            else:
                raise ValueError(f"Invalid pair format: {type(pair)}")
        return result

    @property
    def train_inputs(self) -> list[Grid]:
        """Get all training input grids."""
        return [inp for inp, _ in self.train]

    @property
    def train_outputs(self) -> list[Grid]:
        """Get all training output grids."""
        return [out for _, out in self.train]

    @property
    def test_inputs(self) -> list[Grid]:
        """Get all test input grids."""
        return [inp for inp, _ in self.test]

    @property
    def test_outputs(self) -> list[Grid]:
        """Get all expected test output grids."""
        return [out for _, out in self.test]


__all__ = ["ARCTask", "Grid"]
