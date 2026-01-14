"""Utility functions for ARC tasks.

Provides formatting and parsing utilities for working with ARC grids
and tasks in agent interactions.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from cognitive_core.environments.arc.types import ARCTask, Grid


# ARC color palette for display (optional visual representation)
ARC_COLORS = {
    0: "black",
    1: "blue",
    2: "red",
    3: "green",
    4: "yellow",
    5: "gray",
    6: "magenta",
    7: "orange",
    8: "cyan",
    9: "brown",
}


def format_grid(grid: Grid | np.ndarray, use_symbols: bool = False) -> str:
    """Format a grid for text display.

    Args:
        grid: 2D grid of integers (0-9).
        use_symbols: If True, use symbols instead of numbers for better visual
                    distinction. Defaults to False (numbers).

    Returns:
        String representation of the grid with space-separated values.

    Example:
        ```python
        grid = [[0, 1, 2], [3, 4, 5]]
        print(format_grid(grid))
        # Output:
        # 0 1 2
        # 3 4 5
        ```
    """
    grid_arr = np.array(grid)

    if use_symbols:
        # Map numbers to symbols for visual distinction
        symbols = "·█▪▫◆◇●○□■"
        rows = []
        for row in grid_arr:
            row_str = " ".join(symbols[min(cell, 9)] for cell in row)
            rows.append(row_str)
        return "\n".join(rows)

    # Default: space-separated numbers
    rows = []
    for row in grid_arr:
        rows.append(" ".join(str(cell) for cell in row))
    return "\n".join(rows)


def format_arc_task(
    task: ARCTask,
    include_test_output: bool = False,
) -> str:
    """Format an ARC task for agent prompt.

    Creates a structured text representation of the task with training
    examples and test inputs.

    Args:
        task: The ARCTask to format.
        include_test_output: If True, include expected test outputs
                            (for debugging/analysis only, not for agents).

    Returns:
        Formatted string representation of the task.

    Example:
        ```python
        prompt = format_arc_task(task)
        response = agent.generate(prompt)
        ```
    """
    parts = [f"# ARC Task: {task.id}", ""]

    # Training examples
    parts.append("## Training Examples")
    parts.append("")

    for i, (inp, out) in enumerate(task.train, 1):
        parts.append(f"### Example {i}")
        parts.append("")
        parts.append("**Input:**")
        parts.append("```")
        parts.append(format_grid(inp))
        parts.append("```")
        parts.append("")
        parts.append("**Output:**")
        parts.append("```")
        parts.append(format_grid(out))
        parts.append("```")
        parts.append("")

    # Test inputs
    parts.append("## Test Input(s)")
    parts.append("")

    for i, (inp, out) in enumerate(task.test, 1):
        parts.append(f"### Test {i}")
        parts.append("")
        parts.append("**Input:**")
        parts.append("```")
        parts.append(format_grid(inp))
        parts.append("```")
        parts.append("")

        if include_test_output:
            parts.append("**Expected Output:**")
            parts.append("```")
            parts.append(format_grid(out))
            parts.append("```")
            parts.append("")

    return "\n".join(parts)


def parse_grid_response(response: str) -> list[Grid] | None:
    """Extract grid(s) from agent text response.

    Attempts to parse grids from various formats agents might use:
    - Code blocks with space/comma-separated numbers
    - JSON arrays
    - Plain text grids

    Args:
        response: Agent's text response containing grid output.

    Returns:
        List of parsed grids, or None if parsing fails.

    Example:
        ```python
        response = '''
        Here's my answer:
        ```
        0 1 2
        3 4 5
        ```
        '''
        grids = parse_grid_response(response)
        # Returns: [[[0, 1, 2], [3, 4, 5]]]
        ```
    """
    grids: list[Grid] = []

    # Try to find code blocks first
    code_block_pattern = r"```(?:\w*\n)?([\s\S]*?)```"
    code_blocks = re.findall(code_block_pattern, response)

    for block in code_blocks:
        grid = _parse_grid_text(block.strip())
        if grid:
            grids.append(grid)

    # If no code blocks, try to find grid patterns in plain text
    if not grids:
        grid = _parse_grid_text(response)
        if grid:
            grids.append(grid)

    # Try JSON parsing as fallback
    if not grids:
        grids = _parse_json_grids(response)

    return grids if grids else None


def _parse_grid_text(text: str) -> Grid | None:
    """Parse a grid from plain text.

    Args:
        text: Text potentially containing a grid.

    Returns:
        Parsed grid or None.
    """
    lines = text.strip().split("\n")
    grid: Grid = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to extract numbers from the line
        row = _parse_row(line)
        if row is not None:
            grid.append(row)

    # Validate grid
    if not grid:
        return None

    # Check all rows have same length
    row_lens = set(len(row) for row in grid)
    if len(row_lens) != 1:
        return None

    return grid


def _parse_row(line: str) -> list[int] | None:
    """Parse a single row from a line of text.

    Args:
        line: Line potentially containing grid row.

    Returns:
        List of integers or None.
    """
    # Remove common delimiters and brackets
    line = line.strip("[](),")

    # Try space-separated
    parts = line.split()
    if parts:
        try:
            return [int(p.strip(",[]")) for p in parts]
        except ValueError:
            pass

    # Try comma-separated
    parts = line.split(",")
    if len(parts) > 1:
        try:
            return [int(p.strip(" []")) for p in parts if p.strip()]
        except ValueError:
            pass

    return None


def _parse_json_grids(response: str) -> list[Grid]:
    """Try to parse grids as JSON arrays.

    Args:
        response: Text potentially containing JSON arrays.

    Returns:
        List of parsed grids (may be empty).
    """
    import json

    grids: list[Grid] = []

    # Find JSON array patterns
    json_pattern = r"\[\s*\[[\d\s,\[\]]+\]\s*\]"
    matches = re.findall(json_pattern, response)

    for match in matches:
        try:
            parsed = json.loads(match)
            if _is_valid_grid(parsed):
                grids.append(parsed)
        except json.JSONDecodeError:
            continue

    return grids


def _is_valid_grid(obj: Any) -> bool:
    """Check if object is a valid ARC grid.

    Args:
        obj: Object to validate.

    Returns:
        True if valid grid (2D list of integers 0-9).
    """
    if not isinstance(obj, list) or not obj:
        return False

    if not all(isinstance(row, list) for row in obj):
        return False

    row_lens = set(len(row) for row in obj)
    if len(row_lens) != 1:
        return False

    for row in obj:
        if not all(isinstance(cell, int) and 0 <= cell <= 9 for cell in row):
            return False

    return True


def verify_grid(predicted: Grid, expected: Grid) -> tuple[bool, float]:
    """Verify a predicted grid against expected output.

    Args:
        predicted: Agent's predicted grid.
        expected: Expected output grid.

    Returns:
        Tuple of (exact_match, similarity_score).
        - exact_match: True if grids are identical
        - similarity_score: Fraction of matching cells (0.0-1.0)

    Example:
        ```python
        match, score = verify_grid(predicted, expected)
        if match:
            print("Exact match!")
        else:
            print(f"Partial match: {score:.1%}")
        ```
    """
    predicted_arr = np.array(predicted)
    expected_arr = np.array(expected)

    # Shape mismatch
    if predicted_arr.shape != expected_arr.shape:
        return False, 0.0

    exact_match = bool(np.array_equal(predicted_arr, expected_arr))

    # Cell-by-cell similarity
    total_cells = expected_arr.size
    matching_cells = int(np.sum(predicted_arr == expected_arr))
    similarity = matching_cells / total_cells if total_cells > 0 else 0.0

    return exact_match, similarity


__all__ = [
    "ARC_COLORS",
    "format_arc_task",
    "format_grid",
    "parse_grid_response",
    "verify_grid",
]
