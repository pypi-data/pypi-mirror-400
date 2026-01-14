"""ARC dataset loading utilities.

Provides functions for loading ARC tasks from various sources:
- arckit library datasets
- JSON files
- Raw dictionaries
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from cognitive_core.environments.arc.types import ARCTask

logger = logging.getLogger(__name__)

# Cache for loaded datasets
_dataset_cache: dict[str, tuple[list[Any], list[Any]]] = {}


def load_arc_dataset(
    dataset_name: str = "arc",
    use_cache: bool = True,
) -> tuple[list[ARCTask], list[ARCTask]]:
    """Load ARC dataset from arckit library.

    Args:
        dataset_name: Dataset to load. Options:
            - "arc" (default): Original ARC dataset
            - "kaggle2024": ARC Prize 2024 dataset
            - "kaggle2025": ARC Prize 2025 dataset
        use_cache: Whether to cache loaded datasets.

    Returns:
        Tuple of (train_tasks, eval_tasks) as ARCTask objects.

    Raises:
        ImportError: If arckit is not installed.
        ValueError: If dataset_name is not recognized.

    Example:
        ```python
        train_tasks, eval_tasks = load_arc_dataset("arc")
        print(f"Loaded {len(train_tasks)} training tasks")
        ```
    """
    # Check cache
    if use_cache and dataset_name in _dataset_cache:
        arckit_train, arckit_eval = _dataset_cache[dataset_name]
        return (
            [ARCTask.from_arckit(t) for t in arckit_train],
            [ARCTask.from_arckit(t) for t in arckit_eval],
        )

    try:
        import arckit

        arckit_train, arckit_eval = arckit.load_data(dataset_name)

        # Cache the raw arckit data
        if use_cache:
            _dataset_cache[dataset_name] = (arckit_train, arckit_eval)

        return (
            [ARCTask.from_arckit(t) for t in arckit_train],
            [ARCTask.from_arckit(t) for t in arckit_eval],
        )

    except ImportError as e:
        raise ImportError(
            "arckit is required for loading ARC datasets. "
            "Install with: pip install arckit"
        ) from e


def load_arc_tasks_from_json(path: str | Path) -> list[ARCTask]:
    """Load ARC tasks from a JSON file.

    Supports two formats:
    1. Single task: {"train": [...], "test": [...]}
    2. Multiple tasks: {"task_id": {"train": [...], "test": [...]}, ...}

    Args:
        path: Path to JSON file.

    Returns:
        List of ARCTask objects.

    Raises:
        FileNotFoundError: If file doesn't exist.
        json.JSONDecodeError: If file is not valid JSON.

    Example:
        ```python
        tasks = load_arc_tasks_from_json("my_tasks.json")
        ```
    """
    path = Path(path)

    with open(path) as f:
        data = json.load(f)

    tasks = []

    # Check if single task or multiple tasks
    if "train" in data:
        # Single task format
        task_id = path.stem  # Use filename as ID
        task = ARCTask.from_dict({"id": task_id, **data})
        tasks.append(task)
    else:
        # Multiple tasks format (keyed by task ID)
        for task_id, task_data in data.items():
            task = ARCTask.from_dict({"id": task_id, **task_data})
            tasks.append(task)

    return tasks


def load_arc_tasks_from_directory(
    directory: str | Path,
    pattern: str = "*.json",
) -> list[ARCTask]:
    """Load all ARC tasks from JSON files in a directory.

    Args:
        directory: Directory containing JSON task files.
        pattern: Glob pattern for task files.

    Returns:
        List of ARCTask objects from all matching files.

    Example:
        ```python
        tasks = load_arc_tasks_from_directory("./arc_tasks/")
        ```
    """
    directory = Path(directory)
    tasks = []

    for json_file in sorted(directory.glob(pattern)):
        try:
            file_tasks = load_arc_tasks_from_json(json_file)
            tasks.extend(file_tasks)
        except Exception as e:
            logger.warning(f"Failed to load {json_file}: {e}")

    return tasks


def find_task_by_id(
    task_id: str,
    dataset_name: str = "arc",
) -> ARCTask | None:
    """Find a specific task by ID in an arckit dataset.

    Args:
        task_id: The task ID to find (e.g., "007bbfb7").
        dataset_name: Which dataset to search.

    Returns:
        ARCTask if found, None otherwise.

    Example:
        ```python
        task = find_task_by_id("007bbfb7")
        if task:
            print(f"Found task with {len(task.train)} training examples")
        ```
    """
    try:
        train_tasks, eval_tasks = load_arc_dataset(dataset_name)

        # Search training tasks
        for task in train_tasks:
            if task.id == task_id:
                return task

        # Search evaluation tasks
        for task in eval_tasks:
            if task.id == task_id:
                return task

        return None

    except ImportError:
        logger.warning("arckit not available, cannot search datasets")
        return None


def clear_dataset_cache() -> None:
    """Clear the dataset cache.

    Useful for freeing memory or forcing reload of datasets.
    """
    _dataset_cache.clear()


__all__ = [
    "clear_dataset_cache",
    "find_task_by_id",
    "load_arc_dataset",
    "load_arc_tasks_from_directory",
    "load_arc_tasks_from_json",
]
