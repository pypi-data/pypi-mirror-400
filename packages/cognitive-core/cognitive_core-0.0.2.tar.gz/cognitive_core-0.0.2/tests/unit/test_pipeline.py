"""Tests for ATLAS learning pipeline orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import (
    AnalysisResult,
    BatchResult,
    CodeConcept,
    Experience,
    Outcome,
    ProcessResult,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.learning.analyzer import SimpleCreditStrategy, TrajectoryAnalyzer
from cognitive_core.learning.extractor import AbstractionExtractor, TextPatternExtractor
from cognitive_core.learning.hindsight import HindsightLearner
from cognitive_core.learning.pipeline import LearningPipeline, create_learning_pipeline


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create a mock LLM."""
    llm = MagicMock()
    llm.generate.return_value = '{"abstractable": true, "reasoning": "test"}'
    llm.extract_json.return_value = []
    return llm


@pytest.fixture
def mock_memory_system() -> MagicMock:
    """Create a mock memory system."""
    memory = MagicMock()

    # Mock experience memory
    exp_memory = MagicMock()
    exp_memory.store.return_value = "exp-123"
    exp_memory.search.return_value = []
    exp_memory.prune.return_value = 0
    exp_memory.__len__ = MagicMock(return_value=0)
    memory.experience_memory = exp_memory

    # Mock concept library
    concept_lib = MagicMock()
    concept_lib.add.return_value = "concept-123"
    concept_lib.search.return_value = []
    concept_lib.__len__ = MagicMock(return_value=0)
    memory.concept_library = concept_lib

    # Mock strategy bank
    strategy_bank = MagicMock()
    strategy_bank.write.return_value = MagicMock(id="strategy-123")
    strategy_bank.read.return_value = []
    strategy_bank.__len__ = MagicMock(return_value=0)
    memory.strategy_bank = strategy_bank

    return memory


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task."""
    return Task(
        id="task-001",
        domain="test",
        description="Fix the login bug in the authentication module",
        context={"file": "auth.py"},
        verification=VerificationSpec(method="test_suite"),
    )


@pytest.fixture
def sample_steps() -> list[Step]:
    """Create sample trajectory steps."""
    return [
        Step(
            thought="First, I'll read the auth file",
            action="Read auth.py",
            observation="File contents: ...",
        ),
        Step(
            thought="I see the bug, fixing it now",
            action="Edit auth.py line 42",
            observation="File updated successfully",
        ),
        Step(
            thought="Running tests to verify",
            action="Run pytest auth_test.py",
            observation="All tests passed",
        ),
    ]


@pytest.fixture
def successful_trajectory(sample_task: Task, sample_steps: list[Step]) -> Trajectory:
    """Create a successful trajectory."""
    return Trajectory(
        task=sample_task,
        steps=sample_steps,
        outcome=Outcome(success=True, partial_score=1.0),
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def failed_trajectory(sample_task: Task, sample_steps: list[Step]) -> Trajectory:
    """Create a failed trajectory."""
    return Trajectory(
        task=sample_task,
        steps=sample_steps[:2],  # Incomplete steps
        outcome=Outcome(
            success=False,
            partial_score=0.3,
            error_info="Test failed: authentication error",
        ),
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def analyzer(mock_llm: MagicMock) -> TrajectoryAnalyzer:
    """Create a trajectory analyzer."""
    return TrajectoryAnalyzer(
        credit_strategy=SimpleCreditStrategy(),
        llm=mock_llm,
    )


@pytest.fixture
def extractor() -> AbstractionExtractor:
    """Create an abstraction extractor."""
    return AbstractionExtractor(
        pattern_extractor=TextPatternExtractor(),
        embedding_service=None,
    )


@pytest.fixture
def hindsight(mock_llm: MagicMock, mock_memory_system: MagicMock) -> HindsightLearner:
    """Create a hindsight learner."""
    return HindsightLearner(
        llm=mock_llm,
        memory=mock_memory_system,
        config=LearningConfig(min_trajectories=2),
    )


@pytest.fixture
def pipeline(
    mock_memory_system: MagicMock,
    analyzer: TrajectoryAnalyzer,
    extractor: AbstractionExtractor,
    hindsight: HindsightLearner,
) -> LearningPipeline:
    """Create a learning pipeline."""
    return LearningPipeline(
        memory=mock_memory_system,
        analyzer=analyzer,
        extractor=extractor,
        hindsight=hindsight,
        config=LearningConfig(min_trajectories=2),
    )


# =============================================================================
# LearningPipeline Tests
# =============================================================================


class TestLearningPipelineInit:
    """Tests for LearningPipeline initialization."""

    def test_init_with_all_components(
        self,
        mock_memory_system: MagicMock,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        hindsight: HindsightLearner,
    ) -> None:
        """Test initialization with all components."""
        config = LearningConfig(min_trajectories=10)
        pipeline = LearningPipeline(
            memory=mock_memory_system,
            analyzer=analyzer,
            extractor=extractor,
            hindsight=hindsight,
            config=config,
        )

        assert pipeline._memory is mock_memory_system
        assert pipeline._analyzer is analyzer
        assert pipeline._extractor is extractor
        assert pipeline._hindsight is hindsight
        assert pipeline._config.min_trajectories == 10

    def test_init_with_default_config(
        self,
        mock_memory_system: MagicMock,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        hindsight: HindsightLearner,
    ) -> None:
        """Test initialization without config uses defaults."""
        pipeline = LearningPipeline(
            memory=mock_memory_system,
            analyzer=analyzer,
            extractor=extractor,
            hindsight=hindsight,
        )

        assert pipeline._config.min_trajectories == 50  # Default


class TestProcessTrajectory:
    """Tests for process_trajectory method."""

    def test_process_successful_trajectory(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test processing a successful trajectory."""
        result = pipeline.process_trajectory(successful_trajectory)

        assert isinstance(result, ProcessResult)
        assert result.trajectory_id == "task-001"
        assert result.stored is True
        assert result.analysis is not None
        assert result.analysis.success is True

    def test_process_failed_trajectory(
        self,
        pipeline: LearningPipeline,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test processing a failed trajectory."""
        result = pipeline.process_trajectory(failed_trajectory)

        assert isinstance(result, ProcessResult)
        assert result.trajectory_id == "task-001"
        assert result.stored is True
        assert result.analysis is not None
        assert result.analysis.success is False

    def test_process_stores_in_experience_memory(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test that process_trajectory stores in experience memory."""
        pipeline.process_trajectory(successful_trajectory)

        mock_memory_system.experience_memory.store.assert_called_once_with(
            successful_trajectory
        )

    def test_process_accumulates_for_batch(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that trajectories are accumulated for batch learning."""
        assert pipeline.accumulated_count == 0

        pipeline.process_trajectory(successful_trajectory)

        assert pipeline.accumulated_count == 1

    def test_process_handles_missing_experience_memory(
        self,
        mock_memory_system: MagicMock,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        hindsight: HindsightLearner,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test processing when experience memory is None."""
        mock_memory_system.experience_memory = None
        pipeline = LearningPipeline(
            memory=mock_memory_system,
            analyzer=analyzer,
            extractor=extractor,
            hindsight=hindsight,
        )

        result = pipeline.process_trajectory(successful_trajectory)

        assert result.stored is False
        assert result.analysis is not None

    def test_process_handles_store_error(
        self,
        pipeline: LearningPipeline,
        mock_memory_system: MagicMock,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test processing handles store errors gracefully."""
        mock_memory_system.experience_memory.store.side_effect = Exception("Store failed")

        result = pipeline.process_trajectory(successful_trajectory)

        assert result.stored is False
        assert result.analysis is not None  # Analysis still works


class TestShouldRunBatch:
    """Tests for should_run_batch method."""

    def test_should_run_batch_not_enough_trajectories(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test should_run_batch returns False when not enough trajectories."""
        pipeline.process_trajectory(successful_trajectory)

        assert pipeline.accumulated_count == 1
        assert pipeline.should_run_batch() is False  # min_trajectories=2

    def test_should_run_batch_enough_trajectories(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test should_run_batch returns True when enough trajectories."""
        # Process two trajectories (min_trajectories=2)
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)

        assert pipeline.accumulated_count == 2
        assert pipeline.should_run_batch() is True


class TestRunBatchLearning:
    """Tests for run_batch_learning method."""

    def test_run_batch_learning_not_enough_trajectories(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test run_batch_learning with insufficient trajectories."""
        pipeline.process_trajectory(successful_trajectory)

        result = pipeline.run_batch_learning()

        assert isinstance(result, BatchResult)
        assert result.trajectories_processed == 0
        assert result.concepts_extracted == 0
        assert result.strategies_extracted == 0

    def test_run_batch_learning_success(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test successful batch learning."""
        # Accumulate enough trajectories
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)

        result = pipeline.run_batch_learning()

        assert isinstance(result, BatchResult)
        assert result.trajectories_processed == 2
        assert result.success_rate == 1.0  # Both successful

    def test_run_batch_learning_clears_accumulator(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that batch learning clears the accumulator."""
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)
        assert pipeline.accumulated_count == 2

        pipeline.run_batch_learning()

        assert pipeline.accumulated_count == 0

    def test_run_batch_learning_with_min_override(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test run_batch_learning with min_trajectories override."""
        pipeline.process_trajectory(successful_trajectory)

        # Override to require only 1
        result = pipeline.run_batch_learning(min_trajectories=1)

        assert result.trajectories_processed == 1

    def test_run_batch_learning_mixed_success_rate(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test batch learning with mixed success/failure."""
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(failed_trajectory)

        result = pipeline.run_batch_learning()

        assert result.trajectories_processed == 2
        assert result.success_rate == 0.5  # 1 success, 1 failure

    def test_run_batch_learning_prunes_experiences(
        self,
        pipeline: LearningPipeline,
        mock_memory_system: MagicMock,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test that batch learning prunes experiences."""
        mock_memory_system.experience_memory.prune.return_value = 5

        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)

        result = pipeline.run_batch_learning()

        assert result.experiences_pruned == 5
        mock_memory_system.experience_memory.prune.assert_called_once()


class TestAccumulatedCount:
    """Tests for accumulated_count property."""

    def test_accumulated_count_initially_zero(
        self,
        pipeline: LearningPipeline,
    ) -> None:
        """Test accumulated_count is zero initially."""
        assert pipeline.accumulated_count == 0

    def test_accumulated_count_increments(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test accumulated_count increments with each trajectory."""
        pipeline.process_trajectory(successful_trajectory)
        assert pipeline.accumulated_count == 1

        pipeline.process_trajectory(successful_trajectory)
        assert pipeline.accumulated_count == 2


class TestConfig:
    """Tests for config property."""

    def test_config_property(
        self,
        pipeline: LearningPipeline,
    ) -> None:
        """Test config property returns configuration."""
        assert pipeline.config.min_trajectories == 2


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateLearningPipeline:
    """Tests for create_learning_pipeline factory function."""

    def test_create_with_default_config(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with default configuration."""
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
        )

        assert isinstance(pipeline, LearningPipeline)
        assert pipeline.config.credit_strategy == "llm"  # Default
        assert pipeline.config.pattern_extractor == "llm"  # Default

    def test_create_with_simple_credit_strategy(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with simple credit strategy."""
        config = LearningConfig(credit_strategy="simple")
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.credit_strategy == "simple"

    def test_create_with_llm_credit_strategy(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with LLM credit strategy."""
        config = LearningConfig(credit_strategy="llm")
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.credit_strategy == "llm"

    def test_create_with_counterfactual_credit_strategy(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with counterfactual credit strategy."""
        config = LearningConfig(credit_strategy="counterfactual")
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.credit_strategy == "counterfactual"

    def test_create_with_text_pattern_extractor(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with text pattern extractor."""
        config = LearningConfig(pattern_extractor="text")
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.pattern_extractor == "text"

    def test_create_with_combined_pattern_extractor(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with combined pattern extractor."""
        config = LearningConfig(pattern_extractor="both")
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.pattern_extractor == "both"

    def test_create_with_embedding_service(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with embedding service for deduplication."""
        mock_embedding = MagicMock()
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            embedding_service=mock_embedding,
        )

        assert isinstance(pipeline, LearningPipeline)

    def test_create_with_custom_min_trajectories(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory with custom min_trajectories."""
        config = LearningConfig(min_trajectories=100)
        pipeline = create_learning_pipeline(
            memory=mock_memory_system,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.config.min_trajectories == 100

    def test_create_invalid_credit_strategy_raises(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory raises for invalid credit strategy."""
        # We need to bypass validation to test the factory
        config = MagicMock()
        config.credit_strategy = "invalid"
        config.pattern_extractor = "llm"
        config.min_trajectories = 50

        with pytest.raises(ValueError, match="Unknown credit strategy"):
            create_learning_pipeline(
                memory=mock_memory_system,
                llm=mock_llm,
                config=config,
            )

    def test_create_invalid_pattern_extractor_raises(
        self,
        mock_llm: MagicMock,
        mock_memory_system: MagicMock,
    ) -> None:
        """Test factory raises for invalid pattern extractor."""
        config = MagicMock()
        config.credit_strategy = "simple"
        config.pattern_extractor = "invalid"
        config.min_trajectories = 50

        with pytest.raises(ValueError, match="Unknown pattern extractor"):
            create_learning_pipeline(
                memory=mock_memory_system,
                llm=mock_llm,
                config=config,
            )


# =============================================================================
# Integration Tests
# =============================================================================


class TestPipelineIntegration:
    """Integration tests for the learning pipeline."""

    def test_full_pipeline_flow(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test complete pipeline flow: process, accumulate, batch."""
        # Process multiple trajectories
        result1 = pipeline.process_trajectory(successful_trajectory)
        assert result1.stored is True

        result2 = pipeline.process_trajectory(failed_trajectory)
        assert result2.stored is True

        # Verify accumulation
        assert pipeline.accumulated_count == 2

        # Run batch learning
        batch_result = pipeline.run_batch_learning()

        # Verify results
        assert batch_result.trajectories_processed == 2
        assert batch_result.success_rate == 0.5
        assert pipeline.accumulated_count == 0

    def test_multiple_batch_cycles(
        self,
        pipeline: LearningPipeline,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test multiple batch learning cycles."""
        # First cycle
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)
        batch1 = pipeline.run_batch_learning()
        assert batch1.trajectories_processed == 2

        # Second cycle
        pipeline.process_trajectory(successful_trajectory)
        pipeline.process_trajectory(successful_trajectory)
        batch2 = pipeline.run_batch_learning()
        assert batch2.trajectories_processed == 2

    def test_pipeline_with_no_memory_components(
        self,
        mock_llm: MagicMock,
        analyzer: TrajectoryAnalyzer,
        extractor: AbstractionExtractor,
        successful_trajectory: Trajectory,
    ) -> None:
        """Test pipeline with no memory components (ablation)."""
        mock_memory = MagicMock()
        mock_memory.experience_memory = None
        mock_memory.concept_library = None
        mock_memory.strategy_bank = None

        hindsight = HindsightLearner(
            llm=mock_llm,
            memory=mock_memory,
            config=LearningConfig(min_trajectories=1),
        )

        pipeline = LearningPipeline(
            memory=mock_memory,
            analyzer=analyzer,
            extractor=extractor,
            hindsight=hindsight,
            config=LearningConfig(min_trajectories=1),
        )

        # Should still work, just without storage
        result = pipeline.process_trajectory(successful_trajectory)
        assert result.stored is False
        assert result.analysis is not None

        # Batch learning should work
        batch_result = pipeline.run_batch_learning()
        assert batch_result.trajectories_processed == 1
