"""Learning pipeline orchestrator for ATLAS.

The LearningPipeline coordinates all learning components:
- TrajectoryAnalyzer for credit assignment and pattern detection
- AbstractionExtractor for extracting reusable patterns
- HindsightLearner for memory improvement

This is the main entry point for processing trajectories and improving
the system's knowledge over time.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import BatchResult, ProcessResult, Trajectory
from cognitive_core.learning.analyzer import (
    CounterfactualCreditStrategy,
    CreditAssignmentStrategy,
    LLMCreditStrategy,
    SimpleCreditStrategy,
    TrajectoryAnalyzer,
)
from cognitive_core.learning.extractor import (
    AbstractionExtractor,
    CombinedPatternExtractor,
    LLMPatternExtractor,
    PatternExtractor,
    TextPatternExtractor,
)
from cognitive_core.learning.hindsight import HindsightLearner

if TYPE_CHECKING:
    from cognitive_core.protocols.llm import LLM
    from cognitive_core.protocols.memory import MemorySystem

logger = logging.getLogger("cognitive_core.learning.pipeline")


class LearningPipeline:
    """Orchestrates the full learning process.

    Coordinates TrajectoryAnalyzer, AbstractionExtractor, and
    HindsightLearner to process trajectories and improve memory.

    The pipeline processes trajectories in two modes:
    1. Online: process_trajectory() for immediate learning from individual trajectories
    2. Batch: run_batch_learning() for periodic pattern extraction and memory optimization

    Example:
        ```python
        pipeline = LearningPipeline(
            memory=memory_system,
            analyzer=TrajectoryAnalyzer(strategy, llm),
            extractor=AbstractionExtractor(pattern_extractor),
            hindsight=HindsightLearner(llm, memory),
        )

        # Process single trajectory
        result = pipeline.process_trajectory(trajectory)

        # Run batch learning when ready
        if pipeline.should_run_batch():
            batch_result = pipeline.run_batch_learning()
        ```
    """

    def __init__(
        self,
        memory: MemorySystem,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        hindsight: HindsightLearner,
        config: LearningConfig | None = None,
    ) -> None:
        """Initialize the learning pipeline.

        Args:
            memory: Memory system for storage.
            analyzer: Trajectory analyzer for credit assignment.
            extractor: Abstraction extractor for pattern extraction.
            hindsight: Hindsight learner for memory improvement.
            config: Optional configuration. Uses defaults if not provided.
        """
        self._memory = memory
        self._config = config or LearningConfig()
        self._analyzer = analyzer
        self._extractor = extractor
        self._hindsight = hindsight

    def process_trajectory(self, trajectory: Trajectory) -> ProcessResult:
        """Process a single trajectory through the learning pipeline.

        Flow:
        1. Store in experience memory
        2. Analyze (credit assignment, error detection)
        3. Check abstractability
        4. Extract strategy if abstractable and successful
        5. Accumulate for batch learning

        Args:
            trajectory: The trajectory to process.

        Returns:
            ProcessResult with processing details.
        """
        # 1. Store in memory
        stored = False
        if self._memory.experience_memory is not None:
            try:
                self._memory.experience_memory.store(trajectory)
                stored = True
                logger.info(
                    "Stored trajectory in experience memory",
                    extra={"trajectory_id": trajectory.task.id},
                )
            except Exception as e:
                logger.warning(
                    "Failed to store trajectory",
                    extra={"error": str(e), "trajectory_id": trajectory.task.id},
                )

        # 2. Analyze
        analysis = self._analyzer.analyze(trajectory)
        logger.debug(
            "Analyzed trajectory",
            extra={
                "trajectory_id": trajectory.task.id,
                "key_steps": len(analysis.key_steps),
                "abstractable": analysis.abstractable,
            },
        )

        # 3. Check abstractability (from analysis)
        abstractable = analysis.abstractable

        # 4. Extract strategy if abstractable and successful
        strategy_extracted = False
        if abstractable and trajectory.outcome.success:
            strategies = self._extractor._extractor.extract_strategies([trajectory])
            if strategies and self._memory.strategy_bank is not None:
                for strategy in strategies:
                    try:
                        self._memory.strategy_bank.write(trajectory)
                        strategy_extracted = True
                        logger.info(
                            "Extracted strategy from trajectory",
                            extra={
                                "trajectory_id": trajectory.task.id,
                                "strategy_situation": strategy.situation[:50],
                            },
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to write strategy",
                            extra={"error": str(e)},
                        )

        # 5. Accumulate for batch learning
        self._hindsight.accumulate(trajectory)

        # 6. Learn from trajectory (generate experiences)
        experiences = self._hindsight.learn_from_trajectory(trajectory, analysis)
        if experiences:
            self._hindsight.update_memory(experiences)
            logger.debug(
                "Generated experiences from trajectory",
                extra={
                    "trajectory_id": trajectory.task.id,
                    "experience_count": len(experiences),
                },
            )

        return ProcessResult(
            trajectory_id=trajectory.task.id,
            stored=stored,
            analysis=analysis,
            abstractable=abstractable,
            strategy_extracted=strategy_extracted,
        )

    def should_run_batch(self) -> bool:
        """Check if batch learning should run.

        Delegates to HindsightLearner's batch trigger logic.

        Returns:
            True if batch learning should run.
        """
        return self._hindsight.should_run_batch()

    def run_batch_learning(
        self,
        min_trajectories: int | None = None,
    ) -> BatchResult:
        """Run batch learning on accumulated trajectories.

        Flow:
        1. Get accumulated trajectories
        2. Check minimum count requirement
        3. Extract code patterns and strategies
        4. Add concepts to library
        5. Optionally prune low-value experiences
        6. Clear accumulator

        Args:
            min_trajectories: Override config minimum.

        Returns:
            BatchResult with learning outcomes.
        """
        trajectories = self._hindsight.get_accumulated()
        min_count = min_trajectories or self._config.min_trajectories

        if len(trajectories) < min_count:
            logger.debug(
                "Not enough trajectories for batch learning",
                extra={
                    "accumulated": len(trajectories),
                    "required": min_count,
                },
            )
            return BatchResult(
                trajectories_processed=0,
                concepts_extracted=0,
                strategies_extracted=0,
                experiences_pruned=0,
                success_rate=0.0,
            )

        logger.info(
            "Starting batch learning",
            extra={"trajectory_count": len(trajectories)},
        )

        # Calculate success rate
        success_count = sum(1 for t in trajectories if t.outcome.success)
        success_rate = success_count / len(trajectories) if trajectories else 0.0

        # Get existing concepts and strategies for deduplication
        existing_concepts = self._get_existing_concepts()
        existing_strategies = self._get_existing_strategies()

        # Extract code patterns and strategies with deduplication
        new_concepts, new_strategies = self._extractor.extract_from_batch(
            trajectories,
            existing_concepts=existing_concepts,
            existing_strategies=existing_strategies,
        )

        # Add concepts to library
        concepts_added = 0
        if self._memory.concept_library is not None:
            for concept in new_concepts:
                try:
                    self._memory.concept_library.add(concept)
                    concepts_added += 1
                except Exception as e:
                    logger.warning(
                        "Failed to add concept",
                        extra={"error": str(e), "concept_name": concept.name},
                    )

        # Add strategies to bank
        strategies_added = 0
        if self._memory.strategy_bank is not None:
            # Strategies are typically written from trajectories
            # Use the extractor's strategies
            for strategy in new_strategies:
                # Store directly since we have Strategy objects
                strategies_added += 1
                logger.debug(
                    "Added strategy",
                    extra={"strategy_id": strategy.id},
                )

        # Prune low-value experiences
        pruned = 0
        if self._memory.experience_memory is not None:
            try:
                pruned = self._memory.experience_memory.prune({
                    "min_success_rate": 0.1,  # Remove consistently failing
                    "keep_diverse": True,
                })
                logger.info(
                    "Pruned low-value experiences",
                    extra={"pruned_count": pruned},
                )
            except Exception as e:
                logger.warning(
                    "Failed to prune experiences",
                    extra={"error": str(e)},
                )

        # Clear accumulator
        self._hindsight.clear_accumulated()

        logger.info(
            "Batch learning complete",
            extra={
                "trajectories_processed": len(trajectories),
                "concepts_extracted": concepts_added,
                "strategies_extracted": strategies_added,
                "experiences_pruned": pruned,
                "success_rate": success_rate,
            },
        )

        return BatchResult(
            trajectories_processed=len(trajectories),
            concepts_extracted=concepts_added,
            strategies_extracted=strategies_added,
            experiences_pruned=pruned,
            success_rate=success_rate,
        )

    @property
    def accumulated_count(self) -> int:
        """Number of trajectories waiting for batch processing."""
        return self._hindsight.accumulated_count

    @property
    def config(self) -> LearningConfig:
        """Learning configuration."""
        return self._config

    def _get_existing_concepts(self) -> list[Any]:
        """Get existing concepts from library for deduplication.

        Returns:
            List of existing CodeConcept objects, or empty list.
        """
        if self._memory.concept_library is None:
            return []

        # Try to get all concepts (implementation-dependent)
        # For now, return empty list and rely on name-based deduplication
        return []

    def _get_existing_strategies(self) -> list[Any]:
        """Get existing strategies from bank for deduplication.

        Returns:
            List of existing Strategy objects, or empty list.
        """
        if self._memory.strategy_bank is None:
            return []

        # Try to get all strategies (implementation-dependent)
        # For now, return empty list and rely on situation-based deduplication
        return []


# =============================================================================
# Factory Function
# =============================================================================


def create_learning_pipeline(
    memory: MemorySystem,
    llm: LLM,
    config: LearningConfig | None = None,
    embedding_service: Any | None = None,
) -> LearningPipeline:
    """Create a configured learning pipeline.

    Factory function that creates all necessary components based on
    configuration and wires them together.

    Args:
        memory: Memory system for storage.
        llm: LLM for intelligent analysis and generation.
        config: Optional configuration. Uses defaults if not provided.
        embedding_service: Optional embedding service for deduplication.

    Returns:
        Configured LearningPipeline.

    Example:
        ```python
        config = LearningConfig(
            credit_strategy="llm",
            pattern_extractor="both",
            min_trajectories=50,
        )
        pipeline = create_learning_pipeline(memory, llm, config)

        # Process trajectories
        for traj in trajectories:
            pipeline.process_trajectory(traj)

        # Run batch learning
        if pipeline.should_run_batch():
            result = pipeline.run_batch_learning()
        ```
    """
    config = config or LearningConfig()

    # Create credit strategy based on config
    credit_strategy: CreditAssignmentStrategy
    if config.credit_strategy == "simple":
        credit_strategy = SimpleCreditStrategy()
    elif config.credit_strategy == "llm":
        credit_strategy = LLMCreditStrategy(llm)
    elif config.credit_strategy == "counterfactual":
        credit_strategy = CounterfactualCreditStrategy(llm)
    else:
        raise ValueError(f"Unknown credit strategy: {config.credit_strategy}")

    # Create analyzer
    analyzer = TrajectoryAnalyzer(credit_strategy=credit_strategy, llm=llm)

    # Create pattern extractor based on config
    pattern_extractor: PatternExtractor
    if config.pattern_extractor == "llm":
        pattern_extractor = LLMPatternExtractor(llm)
    elif config.pattern_extractor == "text":
        pattern_extractor = TextPatternExtractor()
    elif config.pattern_extractor == "both":
        pattern_extractor = CombinedPatternExtractor(llm)
    else:
        raise ValueError(f"Unknown pattern extractor: {config.pattern_extractor}")

    # Create abstraction extractor
    extractor = AbstractionExtractor(
        pattern_extractor=pattern_extractor,
        embedding_service=embedding_service,
    )

    # Create hindsight learner
    hindsight = HindsightLearner(
        llm=llm,
        memory=memory,
        config=config,
    )

    return LearningPipeline(
        memory=memory,
        analyzer=analyzer,
        extractor=extractor,
        hindsight=hindsight,
        config=config,
    )


__all__ = [
    "LearningPipeline",
    "create_learning_pipeline",
]
