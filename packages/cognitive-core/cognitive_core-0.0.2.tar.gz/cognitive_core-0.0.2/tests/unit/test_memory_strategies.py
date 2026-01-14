"""Tests for ATLAS memory strategy protocols and implementations."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from cognitive_core.memory.strategies import (
    # Experience protocols and implementations
    ExperienceExtractor,
    PassthroughRefineStrategy,
    RefineStrategy,
    SimpleExperienceExtractor,
    # Concept protocols
    CompositionStrategy,
    CompressionStrategy,
    ConceptDocumenter,
    PrimitiveLoader,
    # Strategy bank protocols and implementations
    EMASuccessUpdater,
    SimpleAverageUpdater,
    StrategyAbstractor,
    SuccessRateUpdater,
)

if TYPE_CHECKING:
    from cognitive_core.core.types import Experience, Trajectory


class TestProtocolCompliance:
    """Test that implementations satisfy their protocols using runtime_checkable."""

    def test_simple_experience_extractor_protocol_compliance(self) -> None:
        """SimpleExperienceExtractor should satisfy ExperienceExtractor protocol."""
        extractor = SimpleExperienceExtractor()
        assert isinstance(extractor, ExperienceExtractor)

    def test_passthrough_refine_strategy_protocol_compliance(self) -> None:
        """PassthroughRefineStrategy should satisfy RefineStrategy protocol."""
        strategy = PassthroughRefineStrategy()
        assert isinstance(strategy, RefineStrategy)

    def test_ema_success_updater_protocol_compliance(self) -> None:
        """EMASuccessUpdater should satisfy SuccessRateUpdater protocol."""
        updater = EMASuccessUpdater()
        assert isinstance(updater, SuccessRateUpdater)

    def test_simple_average_updater_protocol_compliance(self) -> None:
        """SimpleAverageUpdater should satisfy SuccessRateUpdater protocol."""
        updater = SimpleAverageUpdater()
        assert isinstance(updater, SuccessRateUpdater)


class TestSimpleExperienceExtractor:
    """Tests for SimpleExperienceExtractor implementation."""

    def test_extracts_task_description(self, sample_trajectory: Trajectory) -> None:
        """Should extract the task description from trajectory."""
        extractor = SimpleExperienceExtractor()
        result = extractor.extract(sample_trajectory)

        assert result == sample_trajectory.task.description
        assert result == "Fix the bug in the login function"

    def test_returns_string(self, sample_trajectory: Trajectory) -> None:
        """Should return a string suitable for embedding."""
        extractor = SimpleExperienceExtractor()
        result = extractor.extract(sample_trajectory)

        assert isinstance(result, str)
        assert len(result) > 0


class TestPassthroughRefineStrategy:
    """Tests for PassthroughRefineStrategy implementation."""

    def test_returns_experiences_unchanged(self, sample_experience: Experience) -> None:
        """Should return experiences without modification."""
        strategy = PassthroughRefineStrategy()
        experiences = [sample_experience]

        result = asyncio.run(strategy.refine(experiences))

        assert result == experiences
        assert len(result) == 1
        assert result[0] is sample_experience

    def test_empty_list_returns_empty(self) -> None:
        """Should return empty list when given empty list."""
        strategy = PassthroughRefineStrategy()

        result = asyncio.run(strategy.refine([]))

        assert result == []

    def test_multiple_experiences(self, sample_experience: Experience) -> None:
        """Should handle multiple experiences."""
        strategy = PassthroughRefineStrategy()
        # Create multiple experiences by using the same one multiple times
        experiences = [sample_experience, sample_experience, sample_experience]

        result = asyncio.run(strategy.refine(experiences))

        assert len(result) == 3
        assert result == experiences

    def test_with_context(self, sample_experience: Experience, sample_task) -> None:
        """Should work with optional context parameter."""
        strategy = PassthroughRefineStrategy()
        experiences = [sample_experience]

        result = asyncio.run(strategy.refine(experiences, context=sample_task))

        assert result == experiences


class TestEMASuccessUpdater:
    """Tests for EMASuccessUpdater implementation."""

    def test_default_alpha(self) -> None:
        """Default alpha should be 0.1."""
        updater = EMASuccessUpdater()
        assert updater.alpha == 0.1

    def test_custom_alpha(self) -> None:
        """Should accept custom alpha value."""
        updater = EMASuccessUpdater(alpha=0.2)
        assert updater.alpha == 0.2

    def test_success_increases_rate(self) -> None:
        """Success should increase the rate from baseline."""
        updater = EMASuccessUpdater(alpha=0.1)

        new_rate, new_count = updater.update(
            current_rate=0.5,
            current_count=10,
            success=True,
        )

        # EMA: 0.1 * 1.0 + 0.9 * 0.5 = 0.1 + 0.45 = 0.55
        assert new_rate == pytest.approx(0.55)
        assert new_count == 11

    def test_failure_decreases_rate(self) -> None:
        """Failure should decrease the rate from baseline."""
        updater = EMASuccessUpdater(alpha=0.1)

        new_rate, new_count = updater.update(
            current_rate=0.5,
            current_count=10,
            success=False,
        )

        # EMA: 0.1 * 0.0 + 0.9 * 0.5 = 0.0 + 0.45 = 0.45
        assert new_rate == pytest.approx(0.45)
        assert new_count == 11

    def test_first_observation_success(self) -> None:
        """First success from zero should give alpha * 1.0."""
        updater = EMASuccessUpdater(alpha=0.1)

        new_rate, new_count = updater.update(
            current_rate=0.0,
            current_count=0,
            success=True,
        )

        assert new_rate == pytest.approx(0.1)
        assert new_count == 1

    def test_high_alpha_more_responsive(self) -> None:
        """Higher alpha should make rate more responsive to new observations."""
        updater_low = EMASuccessUpdater(alpha=0.1)
        updater_high = EMASuccessUpdater(alpha=0.5)

        rate_low, _ = updater_low.update(0.5, 10, True)
        rate_high, _ = updater_high.update(0.5, 10, True)

        # Higher alpha should give higher rate after success
        assert rate_high > rate_low

    def test_ema_formula_correctness(self) -> None:
        """Verify EMA formula: new_rate = alpha * new_value + (1 - alpha) * old_rate."""
        updater = EMASuccessUpdater(alpha=0.3)

        new_rate, _ = updater.update(
            current_rate=0.7,
            current_count=5,
            success=True,
        )

        # EMA: 0.3 * 1.0 + 0.7 * 0.7 = 0.3 + 0.49 = 0.79
        expected = 0.3 * 1.0 + 0.7 * 0.7
        assert new_rate == pytest.approx(expected)


class TestSimpleAverageUpdater:
    """Tests for SimpleAverageUpdater implementation."""

    def test_first_success(self) -> None:
        """First observation as success should give rate of 1.0."""
        updater = SimpleAverageUpdater()

        new_rate, new_count = updater.update(
            current_rate=0.0,
            current_count=0,
            success=True,
        )

        assert new_rate == pytest.approx(1.0)
        assert new_count == 1

    def test_first_failure(self) -> None:
        """First observation as failure should give rate of 0.0."""
        updater = SimpleAverageUpdater()

        new_rate, new_count = updater.update(
            current_rate=0.0,
            current_count=0,
            success=False,
        )

        assert new_rate == pytest.approx(0.0)
        assert new_count == 1

    def test_running_average_calculation(self) -> None:
        """Should correctly compute running average."""
        updater = SimpleAverageUpdater()

        # Start with 4 successes out of 5 (rate = 0.8)
        new_rate, new_count = updater.update(
            current_rate=0.8,
            current_count=5,
            success=True,  # 5th success
        )

        # Now 5 successes out of 6 = 0.833...
        assert new_rate == pytest.approx(5 / 6)
        assert new_count == 6

    def test_adding_failure_to_perfect_record(self) -> None:
        """Adding failure to 100% record should decrease rate."""
        updater = SimpleAverageUpdater()

        new_rate, new_count = updater.update(
            current_rate=1.0,
            current_count=4,
            success=False,
        )

        # 4 successes out of 5
        assert new_rate == pytest.approx(0.8)
        assert new_count == 5

    def test_50_percent_rate(self) -> None:
        """Test maintaining 50% rate."""
        updater = SimpleAverageUpdater()

        # 5 successes out of 10
        new_rate, new_count = updater.update(
            current_rate=0.5,
            current_count=10,
            success=True,
        )

        # 6 successes out of 11
        assert new_rate == pytest.approx(6 / 11)
        assert new_count == 11

    def test_count_always_increments(self) -> None:
        """Count should always increment regardless of success/failure."""
        updater = SimpleAverageUpdater()

        _, count1 = updater.update(0.5, 10, True)
        _, count2 = updater.update(0.5, 10, False)

        assert count1 == 11
        assert count2 == 11

    def test_convergence_to_true_rate(self) -> None:
        """Simulate multiple observations to verify convergence."""
        updater = SimpleAverageUpdater()

        # Simulate 10 observations: 7 successes, 3 failures
        rate = 0.0
        count = 0
        successes = [True, True, False, True, True, False, True, True, True, False]

        for success in successes:
            rate, count = updater.update(rate, count, success)

        assert rate == pytest.approx(0.7)
        assert count == 10


class TestProtocolsAreRuntimeCheckable:
    """Verify all protocols are properly decorated with @runtime_checkable."""

    def test_experience_extractor_is_runtime_checkable(self) -> None:
        """ExperienceExtractor should be checkable at runtime."""

        class CustomExtractor:
            def extract(self, trajectory) -> str:
                return "custom"

        extractor = CustomExtractor()
        assert isinstance(extractor, ExperienceExtractor)

    def test_refine_strategy_is_runtime_checkable(self) -> None:
        """RefineStrategy should be checkable at runtime."""

        class CustomRefiner:
            async def refine(self, experiences, context=None):
                return experiences

        refiner = CustomRefiner()
        assert isinstance(refiner, RefineStrategy)

    def test_success_rate_updater_is_runtime_checkable(self) -> None:
        """SuccessRateUpdater should be checkable at runtime."""

        class CustomUpdater:
            def update(self, current_rate, current_count, success):
                return (current_rate, current_count + 1)

        updater = CustomUpdater()
        assert isinstance(updater, SuccessRateUpdater)

    def test_composition_strategy_is_runtime_checkable(self) -> None:
        """CompositionStrategy should be checkable at runtime."""

        class CustomComposer:
            async def compose(self, concepts):
                return None

        composer = CustomComposer()
        assert isinstance(composer, CompositionStrategy)

    def test_compression_strategy_is_runtime_checkable(self) -> None:
        """CompressionStrategy should be checkable at runtime."""

        class CustomCompressor:
            async def compress(self, trajectories):
                return []

        compressor = CustomCompressor()
        assert isinstance(compressor, CompressionStrategy)

    def test_concept_documenter_is_runtime_checkable(self) -> None:
        """ConceptDocumenter should be checkable at runtime."""

        class CustomDocumenter:
            async def document(self, concept, usage_examples):
                return concept

        documenter = CustomDocumenter()
        assert isinstance(documenter, ConceptDocumenter)

    def test_primitive_loader_is_runtime_checkable(self) -> None:
        """PrimitiveLoader should be checkable at runtime."""

        class CustomLoader:
            def load(self):
                return {}

        loader = CustomLoader()
        assert isinstance(loader, PrimitiveLoader)

    def test_strategy_abstractor_is_runtime_checkable(self) -> None:
        """StrategyAbstractor should be checkable at runtime."""

        class CustomAbstractor:
            async def abstract(self, trajectory):
                return None

        abstractor = CustomAbstractor()
        assert isinstance(abstractor, StrategyAbstractor)
