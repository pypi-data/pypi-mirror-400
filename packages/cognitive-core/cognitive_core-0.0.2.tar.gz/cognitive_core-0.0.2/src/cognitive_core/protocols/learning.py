"""Learning protocols for ATLAS (Pillar 3).

Learning is how to improve - extracting knowledge from trajectories
to update memory and optionally fine-tune models.

Data flow:
    Trajectories → TrajectoryAnalyzer → AnalysisResult
                                           ↓
                                    AbstractionExtractor → CodeConcepts, Strategies
                                           ↓
                                    Memory Update
                                           ↓
                                    HindsightLearner → Training Data → Fine-tune
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import (
        AnalysisResult,
        CodeConcept,
        FinetuneResult,
        Strategy,
        Trajectory,
    )


@runtime_checkable
class TrajectoryAnalyzer(Protocol):
    """Extract learning signals from trajectories.

    Analyzes trajectories to identify:
    - Key steps that contributed to success/failure
    - Error patterns for learning
    - Whether the trajectory is worth abstracting
    - Training examples for hindsight learning

    Credit assignment methods:
    - Simple: Last successful action gets credit
    - LLM-based: Ask LLM to identify key steps
    - Counterfactual: Would removing this step change outcome?

    Example:
        ```python
        analyzer = LLMTrajectoryAnalyzer(llm=llm)
        result = analyzer.analyze(trajectory)
        if result.abstractable:
            # Extract patterns
            concepts = extractor.extract_code_patterns([trajectory])
        ```
    """

    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Full analysis of a trajectory.

        Args:
            trajectory: The trajectory to analyze

        Returns:
            AnalysisResult with key steps, attribution, patterns, etc.
        """
        ...

    def attribute_outcome(
        self,
        trajectory: Trajectory,
    ) -> list[tuple[int, float]]:
        """Credit assignment: which steps contributed to outcome.

        Args:
            trajectory: The trajectory to analyze

        Returns:
            List of (step_index, contribution_score) tuples
        """
        ...

    def extract_error_patterns(
        self,
        trajectories: list[Trajectory],
    ) -> list[dict[str, Any]]:
        """Find common error patterns across failed trajectories.

        Args:
            trajectories: Failed trajectories to analyze

        Returns:
            List of error pattern descriptions
        """
        ...


@runtime_checkable
class AbstractionExtractor(Protocol):
    """Extract reusable patterns from trajectories.

    Two main extraction methods:
    - Code patterns: Stitch-style compression (3-4x faster than DreamCoder)
    - Strategies: ArcMemo-style abstraction (concept > instance at all scales)

    Also provides AutoDoc for generating human-readable documentation
    (LILO-style) to help LLMs interpret abstractions.

    Example:
        ```python
        extractor = StitchAbstractionExtractor(llm=llm)

        # Extract code patterns
        concepts = extractor.extract_code_patterns(successful_trajectories)

        # Extract strategies
        strategies = extractor.extract_strategies(successful_trajectories)

        # Document a concept
        documented = extractor.auto_document(concept)
        ```
    """

    def extract_code_patterns(
        self,
        trajectories: list[Trajectory],
    ) -> list[CodeConcept]:
        """Extract reusable code patterns using Stitch compression.

        Process:
        1. Parse successful code to AST
        2. Find common subtrees via anti-unification
        3. Score by MDL (compression benefit)
        4. Extract top-k as CodeConcepts

        Args:
            trajectories: Trajectories to extract patterns from

        Returns:
            List of newly extracted code concepts
        """
        ...

    def extract_strategies(
        self,
        trajectories: list[Trajectory],
    ) -> list[Strategy]:
        """Extract abstract reasoning patterns (ArcMemo-style).

        Process:
        1. Identify successful trajectory
        2. Abstract task description → situation
        3. Abstract solution approach → suggestion
        4. Extract typed parameters

        Args:
            trajectories: Trajectories to extract strategies from

        Returns:
            List of extracted strategies
        """
        ...

    def auto_document(self, concept: CodeConcept) -> CodeConcept:
        """Generate human-readable documentation (LILO AutoDoc).

        Uses LLM to generate:
        - Concise name (snake_case)
        - One-sentence description
        - Type signature
        - When to use this pattern

        Args:
            concept: Concept to document

        Returns:
            Same concept with updated name, description, signature
        """
        ...


@runtime_checkable
class HindsightLearner(Protocol):
    """Learn from trajectories to improve future performance.

    Two modes:
    - SOAR-style: Fine-tune on own traces (overcomes performance plateaus)
    - SAGE-style: Training-free, memory-only improvement

    SOAR key insights:
    - Separate sampling and refinement data
    - Weight successful examples higher
    - Cross-model diversity helps

    Example:
        ```python
        learner = SOARHindsightLearner(
            base_model="claude-3-haiku",
            min_trajectories=100,
        )

        if learner.should_finetune():
            data = learner.prepare_training_data(trajectories)
            result = learner.finetune(data)
        ```
    """

    def prepare_training_data(
        self,
        trajectories: list[Trajectory],
    ) -> dict[str, Any]:
        """Convert trajectories to training format.

        SOAR-style separation:
        - sampling_data: Learn to generate good initial solutions (2x weight)
        - refinement_data: Learn to refine based on feedback (1.5x weight)
        - error_data: Learn from failures (1x weight)

        Args:
            trajectories: Trajectories to convert

        Returns:
            Dict with 'sampling', 'refinement', and 'metadata' keys
        """
        ...

    def should_finetune(self) -> bool:
        """Check if enough data has accumulated for fine-tuning.

        Considers:
        - Number of accumulated trajectories (>= 100)
        - Time since last fine-tune (>= 24 hours)
        - Quality threshold met

        Returns:
            True if fine-tuning should be triggered
        """
        ...

    def finetune(self, training_data: dict[str, Any]) -> FinetuneResult:
        """Execute fine-tuning.

        Args:
            training_data: Data from prepare_training_data()

        Returns:
            FinetuneResult with success status, model path, metrics
        """
        ...

    def accumulate(self, trajectory: Trajectory) -> None:
        """Accumulate a trajectory for future fine-tuning.

        Args:
            trajectory: Trajectory to add to the buffer
        """
        ...

    @property
    def accumulated_count(self) -> int:
        """Number of trajectories accumulated since last fine-tune."""
        ...


@runtime_checkable
class LearningPipeline(Protocol):
    """Orchestrates the full learning process.

    Combines analyzer, extractor, and hindsight learner into
    a unified pipeline that processes trajectories and updates memory.

    Example:
        ```python
        pipeline = LearningPipelineImpl(
            memory=memory,
            analyzer=analyzer,
            extractor=extractor,
            hindsight=hindsight_learner,  # optional
        )

        # Process single trajectory
        result = pipeline.process_trajectory(trajectory)

        # Run batch learning
        if len(pipeline.trajectory_buffer) >= 50:
            batch_result = pipeline.run_batch_learning()
        ```
    """

    def process_trajectory(self, trajectory: Trajectory) -> dict[str, Any]:
        """Process a single trajectory through the full pipeline.

        Steps:
        1. Store in experience memory
        2. Analyze trajectory
        3. Extract strategy if abstractable
        4. Accumulate for batch processing

        Args:
            trajectory: Trajectory to process

        Returns:
            Dict with processing results (IDs, analysis, etc.)
        """
        ...

    def run_batch_learning(self, min_trajectories: int = 50) -> dict[str, Any]:
        """Run batch learning on accumulated trajectories.

        Steps:
        1. Extract code patterns via Stitch
        2. Extract strategies
        3. Maybe fine-tune if threshold met
        4. Prune low-value experiences
        5. Clear buffer

        Args:
            min_trajectories: Minimum trajectories required

        Returns:
            Dict with learning results (new concepts, fine-tune status, etc.)
        """
        ...

    @property
    def trajectory_buffer(self) -> list[Trajectory]:
        """Current buffer of unprocessed trajectories."""
        ...
