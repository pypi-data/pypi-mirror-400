"""Memory protocols for ATLAS (Pillar 1).

Three complementary memory types at different abstraction levels:
- StrategyBank: Abstract reasoning patterns (highest abstraction)
- ExperienceMemory: Task-level retrieval (medium abstraction)
- ConceptLibrary: Reusable code patterns (lowest abstraction)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import (
        CodeConcept,
        Experience,
        Strategy,
        Task,
        Trajectory,
    )


@runtime_checkable
class ExperienceMemory(Protocol):
    """Task-level retrieval of similar past experiences (ReMem-style).

    Stores and retrieves experiences based on embedding similarity.
    Implements the search-synthesize-evolve loop from ReMem.

    Key insight: (task, memory) → search → retrieved → synthesis → solution → evolve → updated_memory

    Example:
        ```python
        memory = ChromaExperienceMemory()
        exp_id = memory.store(trajectory)
        similar = memory.search(new_task, k=4)  # Default k=4 from ReMem
        ```
    """

    def store(self, trajectory: Trajectory) -> str:
        """Store a trajectory as an experience.

        Extracts relevant information from the trajectory and stores it
        with an embedding for later retrieval.

        Args:
            trajectory: The trajectory to store

        Returns:
            Unique experience ID
        """
        ...

    def search(self, task: Task, k: int = 4) -> list[Experience]:
        """Find similar experiences via embedding similarity.

        Default k=4 is from the ReMem paper.

        Args:
            task: The task to find similar experiences for
            k: Number of experiences to return

        Returns:
            List of similar experiences, sorted by similarity
        """
        ...

    def get(self, experience_id: str) -> Experience | None:
        """Get an experience by ID.

        Args:
            experience_id: The experience ID

        Returns:
            The experience, or None if not found
        """
        ...

    def refine(self, experiences: list[Experience]) -> list[Experience]:
        """ReMem-style refinement: exploit useful, prune noise, reorganize.

        Improves the quality of retrieved experiences by:
        - Merging similar experiences
        - Removing low-quality ones
        - Reorganizing for better retrieval

        Args:
            experiences: Experiences to refine

        Returns:
            Refined list of experiences
        """
        ...

    def prune(self, criteria: dict[str, Any]) -> int:
        """Remove low-value experiences.

        Criteria can include:
        - min_success_rate: Minimum success rate to keep
        - max_age_days: Maximum age in days
        - keep_diverse: Whether to preserve diversity

        Args:
            criteria: Pruning criteria

        Returns:
            Number of experiences removed
        """
        ...

    def __len__(self) -> int:
        """Number of stored experiences."""
        ...


@runtime_checkable
class ConceptLibrary(Protocol):
    """Reusable code patterns and compositions (Stitch/LILO-style).

    Stores and retrieves code concepts at different abstraction levels:
    - Primitives: Domain-specific base operations (loaded at init)
    - Learned: Extracted from trajectories via compression
    - Composed: Combinations of existing concepts

    Key insight: Stitch compression is 3-4 orders of magnitude faster than DreamCoder.

    Example:
        ```python
        library = ConceptLibrary(primitives=arc_primitives)
        library.add(learned_concept)
        relevant = library.search("rotate grid 90 degrees", k=5)
        composed = library.compose([concept1.id, concept2.id])
        ```
    """

    def add(self, concept: CodeConcept) -> str:
        """Add a concept to the library.

        Args:
            concept: The concept to add

        Returns:
            Unique concept ID
        """
        ...

    def search(self, query: str, k: int = 5) -> list[CodeConcept]:
        """Find relevant concepts by semantic similarity.

        Args:
            query: Natural language description of what's needed
            k: Number of concepts to return

        Returns:
            List of relevant concepts, sorted by similarity
        """
        ...

    def get(self, concept_id: str) -> CodeConcept | None:
        """Get a concept by ID.

        Args:
            concept_id: The concept ID

        Returns:
            The concept, or None if not found
        """
        ...

    def compose(self, concept_ids: list[str]) -> CodeConcept | None:
        """Compose multiple concepts into one.

        Creates a new concept that combines the functionality of
        the given concepts. Uses LLM for composition logic.

        Args:
            concept_ids: IDs of concepts to compose

        Returns:
            New composed concept, or None if composition fails
        """
        ...

    def compress(self, trajectories: list[Trajectory]) -> list[CodeConcept]:
        """Extract new concepts via Stitch compression.

        Uses anti-unification to find common patterns in successful
        trajectories, then applies LILO AutoDoc for naming.

        Args:
            trajectories: Trajectories to extract patterns from

        Returns:
            List of newly extracted concepts
        """
        ...

    def update_stats(self, concept_id: str, success: bool) -> None:
        """Update usage statistics for a concept.

        Args:
            concept_id: The concept ID
            success: Whether usage was successful
        """
        ...

    def __len__(self) -> int:
        """Number of concepts in the library."""
        ...


@runtime_checkable
class StrategyBank(Protocol):
    """Abstract reasoning patterns (ArcMemo-style).

    Stores high-level strategies that describe when and how to approach
    problems. Key insight from ArcMemo: concept-level beats instance-level
    at ALL compute scales.

    Instead of: "Task #123 had this exact solution"
    Use: "For tasks with symmetry patterns, check horizontal/vertical reflection"

    Example:
        ```python
        bank = StrategyBank()
        strategy = bank.write(successful_trajectory)
        applicable = bank.read(new_task, k=5)
        bank.update_stats(strategy.id, success=True)
        ```
    """

    def write(self, trajectory: Trajectory) -> Strategy | None:
        """Abstract a trajectory into a strategy.

        Extracts the high-level approach from a successful trajectory
        and generalizes it into a reusable strategy.

        Args:
            trajectory: Successful trajectory to abstract

        Returns:
            New strategy, or None if not abstractable
        """
        ...

    def read(self, task: Task, k: int = 5) -> list[Strategy]:
        """Find applicable strategies for a task.

        Args:
            task: The task to find strategies for
            k: Number of strategies to return

        Returns:
            List of applicable strategies, sorted by relevance
        """
        ...

    def get(self, strategy_id: str) -> Strategy | None:
        """Get a strategy by ID.

        Args:
            strategy_id: The strategy ID

        Returns:
            The strategy, or None if not found
        """
        ...

    def update_stats(self, strategy_id: str, success: bool) -> None:
        """Update usage statistics for a strategy.

        Args:
            strategy_id: The strategy ID
            success: Whether application was successful
        """
        ...

    def __len__(self) -> int:
        """Number of strategies in the bank."""
        ...


@runtime_checkable
class MemorySystem(Protocol):
    """Aggregator for all memory types.

    Provides a unified interface for querying and storing across
    all three memory types. Each component is optional for ablation studies.

    Example:
        ```python
        # Full system
        memory = MemorySystemImpl(
            experience=exp_memory,
            concepts=concept_lib,
            strategies=strategy_bank,
        )

        # Experience-only ablation
        memory = MemorySystemImpl(experience=exp_memory)

        # Query all components
        results = memory.query(task, k=5)
        ```
    """

    @property
    def experience_memory(self) -> ExperienceMemory | None:
        """Experience memory component (if available)."""
        ...

    @property
    def concept_library(self) -> ConceptLibrary | None:
        """Concept library component (if available)."""
        ...

    @property
    def strategy_bank(self) -> StrategyBank | None:
        """Strategy bank component (if available)."""
        ...

    def query(self, task: Task, k: int = 5) -> MemoryQueryResult:
        """Query all available memory components.

        Missing components return empty results (graceful degradation).

        Args:
            task: The task to query for
            k: Number of results per component

        Returns:
            Combined results from all components
        """
        ...

    def store(self, trajectory: Trajectory) -> dict[str, Any]:
        """Store in all available components.

        Args:
            trajectory: The trajectory to store

        Returns:
            Dict with IDs from each component that stored it
        """
        ...


class MemoryQueryResult:
    """Results from querying the memory system."""

    experiences: list[Experience]
    concepts: list[CodeConcept]
    strategies: list[Strategy]

    def __init__(
        self,
        experiences: list[Experience] | None = None,
        concepts: list[CodeConcept] | None = None,
        strategies: list[Strategy] | None = None,
    ) -> None:
        self.experiences = experiences or []
        self.concepts = concepts or []
        self.strategies = strategies or []

    def is_empty(self) -> bool:
        """Check if all results are empty."""
        return not (self.experiences or self.concepts or self.strategies)
