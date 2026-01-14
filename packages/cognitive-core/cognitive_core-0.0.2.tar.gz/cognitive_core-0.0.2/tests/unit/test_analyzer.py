"""Tests for TrajectoryAnalyzer and credit assignment strategies."""

from __future__ import annotations

import json
import math
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import (
    AnalysisResult,
    Outcome,
    Step,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.learning.analyzer import (
    CounterfactualCreditStrategy,
    CreditAssignmentStrategy,
    LLMCreditStrategy,
    SimpleCreditStrategy,
    TrajectoryAnalyzer,
    create_analyzer,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_task() -> Task:
    """Create a simple task for testing."""
    return Task(
        id="task-001",
        domain="test",
        description="Write a function to add two numbers",
        verification=VerificationSpec(method="test_suite"),
    )


@pytest.fixture
def simple_steps() -> list[Step]:
    """Create a simple list of steps."""
    return [
        Step(
            thought="I need to define a function",
            action="def add(a, b):",
            observation="Function defined",
        ),
        Step(
            thought="Now I need to add the numbers",
            action="    return a + b",
            observation="Return statement added",
        ),
        Step(
            thought="Let me test it",
            action="print(add(2, 3))",
            observation="5",
        ),
    ]


@pytest.fixture
def success_trajectory(simple_task: Task, simple_steps: list[Step]) -> Trajectory:
    """Create a successful trajectory."""
    return Trajectory(
        task=simple_task,
        steps=simple_steps,
        outcome=Outcome(success=True),
        agent_id="test-agent",
        timestamp=datetime.now(),
    )


@pytest.fixture
def failed_trajectory(simple_task: Task) -> Trajectory:
    """Create a failed trajectory."""
    steps = [
        Step(
            thought="I need to add numbers",
            action="def add(a, b):",
            observation="Function defined",
        ),
        Step(
            thought="Try calling with wrong types",
            action='add("hello", 5)',
            observation="TypeError: can only concatenate str (not \"int\") to str",
        ),
    ]
    return Trajectory(
        task=simple_task,
        steps=steps,
        outcome=Outcome(
            success=False,
            error_info="TypeError: can only concatenate str (not \"int\") to str",
        ),
        agent_id="test-agent",
        timestamp=datetime.now(),
    )


@pytest.fixture
def empty_trajectory(simple_task: Task) -> Trajectory:
    """Create an empty trajectory (no steps)."""
    return Trajectory(
        task=simple_task,
        steps=[],
        outcome=Outcome(success=False, error_info="No steps taken"),
        agent_id="test-agent",
        timestamp=datetime.now(),
    )


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create a mock LLM."""
    llm = MagicMock()
    llm.model_id = "mock-model"
    return llm


# =============================================================================
# SimpleCreditStrategy Tests
# =============================================================================


class TestSimpleCreditStrategy:
    """Tests for SimpleCreditStrategy."""

    def test_compute_attribution_empty_trajectory(
        self, empty_trajectory: Trajectory
    ) -> None:
        """Test that empty trajectory returns empty list."""
        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(empty_trajectory)

        assert result == []

    def test_compute_attribution_single_step(self, simple_task: Task) -> None:
        """Test attribution with single step."""
        trajectory = Trajectory(
            task=simple_task,
            steps=[Step(action="single action", observation="done")],
            outcome=Outcome(success=True),
            agent_id="test-agent",
        )

        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(trajectory)

        assert len(result) == 1
        assert result[0] == 1.0  # Only step gets all credit

    def test_compute_attribution_sums_to_one(
        self, success_trajectory: Trajectory
    ) -> None:
        """Test that attribution scores sum to approximately 1.0."""
        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(success_trajectory)

        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_compute_attribution_decay_pattern(
        self, success_trajectory: Trajectory
    ) -> None:
        """Test that later steps get higher attribution (decay pattern)."""
        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(success_trajectory)

        # Each step should have higher score than the previous
        # Pattern: [0.125, 0.25, 0.5] normalized = [0.143, 0.286, 0.571]
        assert result[0] < result[1] < result[2]

    def test_compute_attribution_ignores_llm_parameter(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that LLM parameter is ignored."""
        strategy = SimpleCreditStrategy()
        result1 = strategy.compute_attribution(success_trajectory)
        result2 = strategy.compute_attribution(success_trajectory, llm=mock_llm)

        assert result1 == result2
        mock_llm.generate.assert_not_called()

    def test_compute_attribution_four_steps(self, simple_task: Task) -> None:
        """Test specific decay pattern with 4 steps."""
        steps = [
            Step(action=f"action {i}", observation=f"obs {i}") for i in range(4)
        ]
        trajectory = Trajectory(
            task=simple_task,
            steps=steps,
            outcome=Outcome(success=True),
            agent_id="test-agent",
        )

        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(trajectory)

        # Raw scores: [0.125, 0.25, 0.5, 1.0]
        # Normalized: [0.0667, 0.1333, 0.2667, 0.5333]
        assert len(result) == 4
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

        # Verify exponential decay pattern
        expected_raw = [0.125, 0.25, 0.5, 1.0]
        expected_total = sum(expected_raw)
        expected_normalized = [r / expected_total for r in expected_raw]

        for actual, expected in zip(result, expected_normalized, strict=True):
            assert math.isclose(actual, expected, rel_tol=1e-9)

    def test_all_scores_in_valid_range(
        self, success_trajectory: Trajectory
    ) -> None:
        """Test that all scores are in 0.0-1.0 range."""
        strategy = SimpleCreditStrategy()
        result = strategy.compute_attribution(success_trajectory)

        for score in result:
            assert 0.0 <= score <= 1.0


# =============================================================================
# LLMCreditStrategy Tests
# =============================================================================


class TestLLMCreditStrategy:
    """Tests for LLMCreditStrategy."""

    def test_compute_attribution_empty_trajectory(
        self, empty_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that empty trajectory returns empty list."""
        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(empty_trajectory)

        assert result == []
        mock_llm.generate.assert_not_called()

    def test_compute_attribution_parses_llm_response(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that LLM response is parsed correctly."""
        mock_llm.generate.return_value = json.dumps({
            "attributions": [
                {"step": 0, "score": 0.2, "reason": "setup"},
                {"step": 1, "score": 0.3, "reason": "core logic"},
                {"step": 2, "score": 0.5, "reason": "verification"},
            ]
        })

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        assert len(result) == 3
        mock_llm.generate.assert_called_once()
        # Scores should be normalized
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_compute_attribution_normalizes_scores(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that scores are normalized to sum to 1.0."""
        # LLM returns non-normalized scores
        mock_llm.generate.return_value = json.dumps({
            "attributions": [
                {"step": 0, "score": 0.5, "reason": "a"},
                {"step": 1, "score": 0.5, "reason": "b"},
                {"step": 2, "score": 0.5, "reason": "c"},
            ]
        })

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)
        # Each should be 1/3 after normalization
        for score in result:
            assert math.isclose(score, 1 / 3, rel_tol=1e-9)

    def test_compute_attribution_with_override_llm(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that override LLM is used when provided."""
        override_llm = MagicMock()
        override_llm.generate.return_value = json.dumps({
            "attributions": [
                {"step": 0, "score": 0.1, "reason": "a"},
                {"step": 1, "score": 0.2, "reason": "b"},
                {"step": 2, "score": 0.7, "reason": "c"},
            ]
        })

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory, llm=override_llm)

        # Instance LLM should not be called
        mock_llm.generate.assert_not_called()
        override_llm.generate.assert_called_once()
        assert len(result) == 3

    def test_compute_attribution_fallback_on_error(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test fallback to SimpleCreditStrategy on error."""
        mock_llm.generate.side_effect = Exception("API Error")

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        # Should fall back to simple strategy
        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)
        # Verify decay pattern (simple strategy)
        assert result[0] < result[1] < result[2]

    def test_compute_attribution_fallback_on_invalid_json(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test fallback when LLM returns invalid JSON."""
        mock_llm.generate.return_value = "This is not valid JSON at all"

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        # Should fall back to simple strategy
        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_compute_attribution_handles_json_in_markdown(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test parsing JSON wrapped in markdown code block."""
        mock_llm.generate.return_value = """Here is the analysis:
```json
{"attributions": [
    {"step": 0, "score": 0.3, "reason": "x"},
    {"step": 1, "score": 0.3, "reason": "y"},
    {"step": 2, "score": 0.4, "reason": "z"}
]}
```"""

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_compute_attribution_missing_steps(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test handling when LLM omits some steps."""
        mock_llm.generate.return_value = json.dumps({
            "attributions": [
                {"step": 0, "score": 0.5, "reason": "first"},
                # Step 1 is missing
                {"step": 2, "score": 0.5, "reason": "last"},
            ]
        })

        strategy = LLMCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        assert len(result) == 3
        # Step 1 should be 0.0, then normalized
        # [0.5, 0.0, 0.5] -> [0.5, 0.0, 0.5] (sums to 1.0)
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_prompt_includes_task_and_outcome(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that prompt includes task description and outcome."""
        mock_llm.generate.return_value = json.dumps({
            "attributions": [
                {"step": 0, "score": 0.3, "reason": "a"},
                {"step": 1, "score": 0.3, "reason": "b"},
                {"step": 2, "score": 0.4, "reason": "c"},
            ]
        })

        strategy = LLMCreditStrategy(mock_llm)
        strategy.compute_attribution(success_trajectory)

        prompt = mock_llm.generate.call_args[0][0]
        assert "Write a function to add two numbers" in prompt
        assert "Success" in prompt


# =============================================================================
# CounterfactualCreditStrategy Tests
# =============================================================================


class TestCounterfactualCreditStrategy:
    """Tests for CounterfactualCreditStrategy."""

    def test_compute_attribution_empty_trajectory(
        self, empty_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that empty trajectory returns empty list."""
        strategy = CounterfactualCreditStrategy(mock_llm)
        result = strategy.compute_attribution(empty_trajectory)

        assert result == []
        mock_llm.generate.assert_not_called()

    def test_compute_attribution_parses_counterfactual_response(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test parsing counterfactual reasoning response."""
        mock_llm.generate.return_value = json.dumps({
            "counterfactuals": [
                {"step": 0, "importance": 0.3, "reasoning": "needed for setup"},
                {"step": 1, "importance": 0.9, "reasoning": "core logic"},
                {"step": 2, "importance": 0.5, "reasoning": "verification"},
            ]
        })

        strategy = CounterfactualCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)
        mock_llm.generate.assert_called_once()

    def test_prompt_asks_counterfactual_question(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that prompt asks about removing steps."""
        mock_llm.generate.return_value = json.dumps({
            "counterfactuals": [
                {"step": 0, "importance": 0.5, "reasoning": "a"},
                {"step": 1, "importance": 0.3, "reasoning": "b"},
                {"step": 2, "importance": 0.2, "reasoning": "c"},
            ]
        })

        strategy = CounterfactualCreditStrategy(mock_llm)
        strategy.compute_attribution(success_trajectory)

        prompt = mock_llm.generate.call_args[0][0]
        assert "removed" in prompt.lower() or "counterfactual" in prompt.lower()

    def test_compute_attribution_fallback_on_error(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test fallback to SimpleCreditStrategy on error."""
        mock_llm.generate.side_effect = Exception("API Error")

        strategy = CounterfactualCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory)

        # Should fall back to simple strategy
        assert len(result) == 3
        assert math.isclose(sum(result), 1.0, rel_tol=1e-9)

    def test_compute_attribution_with_override_llm(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that override LLM is used when provided."""
        override_llm = MagicMock()
        override_llm.generate.return_value = json.dumps({
            "counterfactuals": [
                {"step": 0, "importance": 0.2, "reasoning": "a"},
                {"step": 1, "importance": 0.4, "reasoning": "b"},
                {"step": 2, "importance": 0.4, "reasoning": "c"},
            ]
        })

        strategy = CounterfactualCreditStrategy(mock_llm)
        result = strategy.compute_attribution(success_trajectory, llm=override_llm)

        mock_llm.generate.assert_not_called()
        override_llm.generate.assert_called_once()
        assert len(result) == 3


# =============================================================================
# TrajectoryAnalyzer Tests
# =============================================================================


class TestTrajectoryAnalyzer:
    """Tests for TrajectoryAnalyzer."""

    @pytest.fixture
    def analyzer_with_simple_strategy(self, mock_llm: MagicMock) -> TrajectoryAnalyzer:
        """Create analyzer with simple credit strategy."""
        strategy = SimpleCreditStrategy()
        return TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

    @pytest.fixture
    def analyzer_with_llm_strategy(self, mock_llm: MagicMock) -> TrajectoryAnalyzer:
        """Create analyzer with LLM credit strategy."""
        # Set up default LLM responses
        mock_llm.generate.return_value = json.dumps({
            "abstractable": True,
            "reasoning": "Worth extracting",
        })
        strategy = LLMCreditStrategy(mock_llm)
        return TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

    def test_analyze_returns_analysis_result(
        self,
        success_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test that analyze returns an AnalysisResult."""
        result = analyzer_with_simple_strategy.analyze(success_trajectory)

        assert isinstance(result, AnalysisResult)

    def test_analyze_success_field(
        self,
        success_trajectory: Trajectory,
        failed_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test that success field reflects trajectory outcome."""
        success_result = analyzer_with_simple_strategy.analyze(success_trajectory)
        failure_result = analyzer_with_simple_strategy.analyze(failed_trajectory)

        assert success_result.success is True
        assert failure_result.success is False

    def test_analyze_step_attribution(
        self,
        success_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test that step_attribution is populated."""
        result = analyzer_with_simple_strategy.analyze(success_trajectory)

        assert len(result.step_attribution) == 3
        assert math.isclose(sum(result.step_attribution), 1.0, rel_tol=1e-9)

    def test_analyze_key_steps_above_threshold(
        self,
        success_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test that key_steps contains indices above threshold."""
        result = analyzer_with_simple_strategy.analyze(success_trajectory)

        # With simple strategy and 3 steps, later steps should be key
        # [0.143, 0.286, 0.571] - threshold is 0.15
        # Steps 1 and 2 should be key (> 0.15)
        assert 2 in result.key_steps  # Last step definitely key
        assert 1 in result.key_steps  # Second step should be key
        assert 0 not in result.key_steps  # First step should not be key

    def test_analyze_error_patterns_on_failure(
        self,
        failed_trajectory: Trajectory,
        mock_llm: MagicMock,
    ) -> None:
        """Test error pattern detection on failed trajectory."""
        mock_llm.generate.side_effect = [
            # First call: abstractability assessment
            json.dumps({"abstractable": False, "reasoning": "failure"}),
            # Second call: error pattern detection (if called)
            json.dumps({"patterns": [{"name": "type_error", "signature": "TypeError", "suggested_fix": "Check types", "example": "string + int"}]}),
        ]

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)
        result = analyzer.analyze(failed_trajectory)

        # Should have error patterns for failed trajectory
        # (exact content depends on LLM mock response)
        assert isinstance(result.error_patterns, list)

    def test_analyze_no_error_patterns_on_success(
        self,
        success_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test no error patterns on successful trajectory."""
        result = analyzer_with_simple_strategy.analyze(success_trajectory)

        assert result.error_patterns == []

    def test_analyze_abstractability_assessment(
        self,
        success_trajectory: Trajectory,
        mock_llm: MagicMock,
    ) -> None:
        """Test abstractability assessment."""
        mock_llm.generate.return_value = json.dumps({
            "abstractable": True,
            "reasoning": "Novel approach worth extracting",
        })

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)
        result = analyzer.analyze(success_trajectory)

        assert isinstance(result.abstractable, bool)

    def test_analyze_training_examples_for_success(
        self,
        success_trajectory: Trajectory,
        mock_llm: MagicMock,
    ) -> None:
        """Test training examples generated for successful trajectory."""
        mock_llm.generate.return_value = json.dumps({
            "abstractable": True,
            "reasoning": "Worth it",
        })

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)
        result = analyzer.analyze(success_trajectory)

        assert isinstance(result.training_examples, list)
        assert len(result.training_examples) > 0

        # Should have task_solution example
        types = [ex["type"] for ex in result.training_examples]
        assert "task_solution" in types

    def test_analyze_empty_trajectory(
        self,
        empty_trajectory: Trajectory,
        analyzer_with_simple_strategy: TrajectoryAnalyzer,
    ) -> None:
        """Test analyzing empty trajectory."""
        result = analyzer_with_simple_strategy.analyze(empty_trajectory)

        assert result.success is False
        assert result.step_attribution == []
        assert result.key_steps == []
        assert result.abstractable is False  # Empty trajectory not abstractable


class TestTrajectoryAnalyzerErrorPatterns:
    """Tests for error pattern detection."""

    def test_detect_error_patterns_success_returns_empty(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that successful trajectory returns no error patterns."""
        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        patterns = analyzer._detect_error_patterns(success_trajectory)

        assert patterns == []

    def test_detect_error_patterns_parses_llm_response(
        self, failed_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test parsing of LLM error pattern response."""
        mock_llm.generate.return_value = json.dumps({
            "patterns": [
                {
                    "name": "type_error",
                    "signature": "TypeError",
                    "suggested_fix": "Check input types",
                    "example": "mixing str and int",
                },
            ]
        })

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        patterns = analyzer._detect_error_patterns(failed_trajectory)

        assert len(patterns) == 1
        assert patterns[0]["name"] == "type_error"
        assert patterns[0]["suggested_fix"] == "Check input types"

    def test_detect_error_patterns_handles_llm_error(
        self, failed_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test graceful handling of LLM errors."""
        mock_llm.generate.side_effect = Exception("API Error")

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        patterns = analyzer._detect_error_patterns(failed_trajectory)

        assert patterns == []


class TestTrajectoryAnalyzerAbstractability:
    """Tests for abstractability assessment."""

    def test_assess_abstractability_empty_trajectory(
        self, empty_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test that empty trajectory is not abstractable."""
        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        result = analyzer._assess_abstractability(empty_trajectory)

        assert result is False
        mock_llm.generate.assert_not_called()

    def test_assess_abstractability_parses_llm_response(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test parsing of LLM abstractability response."""
        mock_llm.generate.return_value = json.dumps({
            "abstractable": True,
            "reasoning": "Novel pattern worth extracting",
        })

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        result = analyzer._assess_abstractability(success_trajectory)

        assert result is True

    def test_assess_abstractability_false_response(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test handling of non-abstractable response."""
        mock_llm.generate.return_value = json.dumps({
            "abstractable": False,
            "reasoning": "Too simple to extract patterns",
        })

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        result = analyzer._assess_abstractability(success_trajectory)

        assert result is False

    def test_assess_abstractability_fallback_on_error(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test fallback when LLM fails."""
        mock_llm.generate.side_effect = Exception("API Error")

        strategy = SimpleCreditStrategy()
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=mock_llm)

        # Should default to True for successful trajectory with steps
        result = analyzer._assess_abstractability(success_trajectory)

        assert result is True


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateAnalyzer:
    """Tests for create_analyzer factory function."""

    def test_create_analyzer_simple_strategy(self, mock_llm: MagicMock) -> None:
        """Test creating analyzer with simple strategy."""
        config = LearningConfig(credit_strategy="simple")
        analyzer = create_analyzer(config, mock_llm)

        assert isinstance(analyzer, TrajectoryAnalyzer)
        assert isinstance(analyzer._credit_strategy, SimpleCreditStrategy)

    def test_create_analyzer_llm_strategy(self, mock_llm: MagicMock) -> None:
        """Test creating analyzer with LLM strategy."""
        config = LearningConfig(credit_strategy="llm")
        analyzer = create_analyzer(config, mock_llm)

        assert isinstance(analyzer, TrajectoryAnalyzer)
        assert isinstance(analyzer._credit_strategy, LLMCreditStrategy)

    def test_create_analyzer_counterfactual_strategy(
        self, mock_llm: MagicMock
    ) -> None:
        """Test creating analyzer with counterfactual strategy."""
        config = LearningConfig(credit_strategy="counterfactual")
        analyzer = create_analyzer(config, mock_llm)

        assert isinstance(analyzer, TrajectoryAnalyzer)
        assert isinstance(analyzer._credit_strategy, CounterfactualCreditStrategy)

    def test_create_analyzer_unknown_strategy_raises(
        self, mock_llm: MagicMock
    ) -> None:
        """Test that unknown strategy raises ValueError."""
        # Need to bypass pydantic validation
        config = LearningConfig(credit_strategy="llm")
        # Manually set to invalid value
        object.__setattr__(config, "credit_strategy", "unknown")

        with pytest.raises(ValueError, match="Unknown credit strategy"):
            create_analyzer(config, mock_llm)

    def test_create_analyzer_default_config(self, mock_llm: MagicMock) -> None:
        """Test creating analyzer with default config."""
        config = LearningConfig()  # Default is "llm"
        analyzer = create_analyzer(config, mock_llm)

        assert isinstance(analyzer._credit_strategy, LLMCreditStrategy)


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestCreditAssignmentStrategyProtocol:
    """Tests for CreditAssignmentStrategy protocol compliance."""

    def test_simple_strategy_is_protocol_compliant(self) -> None:
        """Test SimpleCreditStrategy implements protocol."""
        strategy = SimpleCreditStrategy()
        assert isinstance(strategy, CreditAssignmentStrategy)

    def test_llm_strategy_is_protocol_compliant(
        self, mock_llm: MagicMock
    ) -> None:
        """Test LLMCreditStrategy implements protocol."""
        strategy = LLMCreditStrategy(mock_llm)
        assert isinstance(strategy, CreditAssignmentStrategy)

    def test_counterfactual_strategy_is_protocol_compliant(
        self, mock_llm: MagicMock
    ) -> None:
        """Test CounterfactualCreditStrategy implements protocol."""
        strategy = CounterfactualCreditStrategy(mock_llm)
        assert isinstance(strategy, CreditAssignmentStrategy)


# =============================================================================
# Integration-like Tests
# =============================================================================


class TestAnalyzerIntegration:
    """Integration-like tests for the analyzer."""

    def test_full_analysis_workflow(
        self, success_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test complete analysis workflow."""
        # Configure mock for all LLM calls
        mock_llm.generate.side_effect = [
            # Attribution (for LLM strategy)
            json.dumps({
                "attributions": [
                    {"step": 0, "score": 0.2, "reason": "setup"},
                    {"step": 1, "score": 0.3, "reason": "logic"},
                    {"step": 2, "score": 0.5, "reason": "verify"},
                ]
            }),
            # Abstractability
            json.dumps({
                "abstractable": True,
                "reasoning": "Good pattern",
            }),
        ]

        config = LearningConfig(credit_strategy="llm")
        analyzer = create_analyzer(config, mock_llm)
        result = analyzer.analyze(success_trajectory)

        # Verify complete result
        assert result.success is True
        assert len(result.step_attribution) == 3
        assert math.isclose(sum(result.step_attribution), 1.0, rel_tol=1e-9)
        assert len(result.key_steps) > 0
        assert result.error_patterns == []
        assert result.abstractable is True
        assert len(result.training_examples) > 0

    def test_failure_analysis_workflow(
        self, failed_trajectory: Trajectory, mock_llm: MagicMock
    ) -> None:
        """Test analysis workflow for failed trajectory."""
        mock_llm.generate.side_effect = [
            # Error patterns
            json.dumps({
                "patterns": [
                    {
                        "name": "type_error",
                        "signature": "TypeError",
                        "suggested_fix": "Type check",
                        "example": "str + int",
                    }
                ]
            }),
            # Abstractability
            json.dumps({
                "abstractable": False,
                "reasoning": "Failure pattern",
            }),
        ]

        config = LearningConfig(credit_strategy="simple")
        analyzer = create_analyzer(config, mock_llm)
        result = analyzer.analyze(failed_trajectory)

        assert result.success is False
        assert len(result.step_attribution) == 2
        assert len(result.error_patterns) > 0
