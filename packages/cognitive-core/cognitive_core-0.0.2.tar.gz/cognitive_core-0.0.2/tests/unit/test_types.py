"""Tests for ATLAS core types."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cognitive_core.core.types import (
    AnalysisResult,
    BatchResult,
    ErrorPattern,
    ProcessResult,
)


class TestErrorPattern:
    """Tests for ErrorPattern."""

    def test_create_error_pattern(self) -> None:
        """Test creating an ErrorPattern with all fields."""
        pattern = ErrorPattern(
            name="null_pointer_dereference",
            signature="AttributeError: 'NoneType' has no attribute",
            frequency=5,
            suggested_fix="Add null check before accessing attribute",
            examples=["obj.method() where obj is None"],
        )

        assert pattern.name == "null_pointer_dereference"
        assert pattern.signature == "AttributeError: 'NoneType' has no attribute"
        assert pattern.frequency == 5
        assert pattern.suggested_fix == "Add null check before accessing attribute"
        assert pattern.examples == ["obj.method() where obj is None"]

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        pattern = ErrorPattern(
            name="test_error",
            signature=".*Error.*",
            suggested_fix="Fix the error",
        )

        assert pattern.frequency == 1
        assert pattern.examples == []

    def test_immutable(self) -> None:
        """Test that ErrorPattern is frozen (immutable)."""
        pattern = ErrorPattern(
            name="test",
            signature="test",
            suggested_fix="fix",
        )

        with pytest.raises((AttributeError, ValidationError)):
            pattern.name = "modified"

    def test_frequency_minimum(self) -> None:
        """Test frequency must be >= 1."""
        with pytest.raises(ValidationError):
            ErrorPattern(
                name="test",
                signature="test",
                frequency=0,
                suggested_fix="fix",
            )

    def test_multiple_examples(self) -> None:
        """Test with multiple examples."""
        pattern = ErrorPattern(
            name="key_error",
            signature="KeyError",
            suggested_fix="Check if key exists before accessing",
            examples=[
                "dict['missing_key']",
                "data.get('key') without default",
                "accessing undefined config",
            ],
        )

        assert len(pattern.examples) == 3


class TestProcessResult:
    """Tests for ProcessResult."""

    def test_create_process_result(self) -> None:
        """Test creating a ProcessResult with all fields."""
        analysis = AnalysisResult(
            success=True,
            key_steps=[0, 2, 4],
            step_attribution=[0.2, 0.1, 0.3, 0.1, 0.3],
            abstractable=True,
        )

        result = ProcessResult(
            trajectory_id="traj-123",
            stored=True,
            analysis=analysis,
            abstractable=True,
            strategy_extracted=True,
        )

        assert result.trajectory_id == "traj-123"
        assert result.stored is True
        assert result.analysis is not None
        assert result.analysis.success is True
        assert result.abstractable is True
        assert result.strategy_extracted is True

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        result = ProcessResult(
            trajectory_id="traj-123",
            stored=True,
        )

        assert result.analysis is None
        assert result.abstractable is False
        assert result.strategy_extracted is False

    def test_immutable(self) -> None:
        """Test that ProcessResult is frozen (immutable)."""
        result = ProcessResult(
            trajectory_id="traj-123",
            stored=True,
        )

        with pytest.raises((AttributeError, ValidationError)):
            result.stored = False

    def test_without_analysis(self) -> None:
        """Test ProcessResult without analysis."""
        result = ProcessResult(
            trajectory_id="traj-456",
            stored=False,
            analysis=None,
            abstractable=False,
            strategy_extracted=False,
        )

        assert result.trajectory_id == "traj-456"
        assert result.stored is False
        assert result.analysis is None


class TestBatchResult:
    """Tests for BatchResult."""

    def test_create_batch_result(self) -> None:
        """Test creating a BatchResult with all fields."""
        result = BatchResult(
            trajectories_processed=100,
            concepts_extracted=5,
            strategies_extracted=3,
            experiences_pruned=10,
            success_rate=0.75,
        )

        assert result.trajectories_processed == 100
        assert result.concepts_extracted == 5
        assert result.strategies_extracted == 3
        assert result.experiences_pruned == 10
        assert result.success_rate == 0.75

    def test_immutable(self) -> None:
        """Test that BatchResult is frozen (immutable)."""
        result = BatchResult(
            trajectories_processed=50,
            concepts_extracted=2,
            strategies_extracted=1,
            experiences_pruned=5,
            success_rate=0.6,
        )

        with pytest.raises((AttributeError, ValidationError)):
            result.trajectories_processed = 100

    def test_zero_values(self) -> None:
        """Test BatchResult with zero values."""
        result = BatchResult(
            trajectories_processed=0,
            concepts_extracted=0,
            strategies_extracted=0,
            experiences_pruned=0,
            success_rate=0.0,
        )

        assert result.trajectories_processed == 0
        assert result.concepts_extracted == 0
        assert result.strategies_extracted == 0
        assert result.experiences_pruned == 0
        assert result.success_rate == 0.0

    def test_validation_non_negative_counts(self) -> None:
        """Test that counts must be non-negative."""
        with pytest.raises(ValidationError):
            BatchResult(
                trajectories_processed=-1,
                concepts_extracted=0,
                strategies_extracted=0,
                experiences_pruned=0,
                success_rate=0.5,
            )

    def test_validation_success_rate_bounds(self) -> None:
        """Test success_rate bounds (0.0 to 1.0)."""
        with pytest.raises(ValidationError):
            BatchResult(
                trajectories_processed=10,
                concepts_extracted=0,
                strategies_extracted=0,
                experiences_pruned=0,
                success_rate=-0.1,
            )

        with pytest.raises(ValidationError):
            BatchResult(
                trajectories_processed=10,
                concepts_extracted=0,
                strategies_extracted=0,
                experiences_pruned=0,
                success_rate=1.5,
            )

    def test_perfect_success_rate(self) -> None:
        """Test BatchResult with 100% success rate."""
        result = BatchResult(
            trajectories_processed=50,
            concepts_extracted=10,
            strategies_extracted=5,
            experiences_pruned=0,
            success_rate=1.0,
        )

        assert result.success_rate == 1.0
