"""Strategy protocols for ConceptLibrary."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import CodeConcept, Trajectory


@runtime_checkable
class CompositionStrategy(Protocol):
    """Combines multiple concepts into a new composed concept."""

    async def compose(self, concepts: list[CodeConcept]) -> CodeConcept | None:
        """Compose concepts into a new one. Returns None if not possible."""
        ...


@runtime_checkable
class CompressionStrategy(Protocol):
    """Extracts new concepts from trajectories (Stitch/LILO-style)."""

    async def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """Extract reusable patterns from successful trajectories."""
        ...


@runtime_checkable
class ConceptDocumenter(Protocol):
    """Generates documentation for concepts (LILO AutoDoc)."""

    async def document(
        self,
        concept: CodeConcept,
        usage_examples: list[tuple[str, str]],
    ) -> CodeConcept:
        """Add name, description, signature, usage guidance."""
        ...


@runtime_checkable
class PrimitiveLoader(Protocol):
    """Loads domain-specific primitive concepts."""

    def load(self) -> dict[str, CodeConcept]:
        """Return dict mapping concept_id to CodeConcept."""
        ...
