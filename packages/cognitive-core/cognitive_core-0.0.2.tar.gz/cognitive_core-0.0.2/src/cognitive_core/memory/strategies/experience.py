"""Strategy protocols for ExperienceMemory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import Experience, Task, Trajectory


@runtime_checkable
class ExperienceExtractor(Protocol):
    """Extracts searchable content from trajectory for embedding."""

    def extract(self, trajectory: Trajectory) -> str:
        """Return text to embed for similarity search."""
        ...


@runtime_checkable
class RefineStrategy(Protocol):
    """ReMem-style refinement: exploit useful, prune noise, reorganize."""

    async def refine(
        self,
        experiences: list[Experience],
        context: Task | None = None,
    ) -> list[Experience]:
        """Meta-reasoning over retrieved experiences."""
        ...


# Default implementations


class SimpleExperienceExtractor:
    """Extract task description only (default baseline)."""

    def extract(self, trajectory: Trajectory) -> str:
        """Return the task description from the trajectory."""
        return trajectory.task.description


class PassthroughRefineStrategy:
    """No-op refinement (baseline for ablation)."""

    async def refine(
        self,
        experiences: list[Experience],
        context: Task | None = None,
    ) -> list[Experience]:
        """Return experiences unchanged."""
        return experiences
