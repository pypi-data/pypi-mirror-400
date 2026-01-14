"""Trajectory analyzer for ATLAS learning pipeline.

Analyzes trajectories to extract learning signals using various
credit assignment strategies.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Protocol, runtime_checkable

from cognitive_core.config import LearningConfig
from cognitive_core.core.types import AnalysisResult, ErrorPattern, Trajectory
from cognitive_core.protocols.llm import LLM

logger = logging.getLogger("cognitive_core.learning.analyzer")


# =============================================================================
# Credit Assignment Strategies
# =============================================================================


@runtime_checkable
class CreditAssignmentStrategy(Protocol):
    """Strategy for assigning credit to trajectory steps.

    Credit assignment determines which steps in a trajectory were most
    responsible for the outcome. This is crucial for learning what actions
    to reinforce or avoid.
    """

    def compute_attribution(
        self,
        trajectory: Trajectory,
        llm: LLM | None = None,
    ) -> list[float]:
        """Compute attribution scores for each step.

        Args:
            trajectory: The trajectory to analyze.
            llm: Optional LLM for strategies that require it.

        Returns:
            List of attribution scores (0.0-1.0) for each step.
            Scores should sum to approximately 1.0.
        """
        ...


class SimpleCreditStrategy:
    """Last successful action gets highest credit, decay backwards.

    This is a simple heuristic strategy that assigns most credit to the
    final steps, with exponential decay going backwards. Based on the
    intuition that later actions are more directly responsible for the
    outcome.

    Example:
        For a 4-step trajectory: [0.125, 0.25, 0.5, 1.0] -> normalized to sum to 1.0
    """

    def compute_attribution(
        self,
        trajectory: Trajectory,
        llm: LLM | None = None,
    ) -> list[float]:
        """Compute attribution using exponential decay from last step.

        Args:
            trajectory: The trajectory to analyze.
            llm: Ignored for this strategy.

        Returns:
            List of attribution scores with decay pattern.
        """
        if not trajectory.steps:
            return []

        n_steps = len(trajectory.steps)

        # Exponential decay from last step: 2^0, 2^-1, 2^-2, ...
        # Last step gets 2^0 = 1.0, second-to-last gets 0.5, etc.
        raw_scores = [2.0 ** (i - n_steps + 1) for i in range(n_steps)]

        # Normalize to sum to 1.0
        total = sum(raw_scores)
        if total > 0:
            normalized = [score / total for score in raw_scores]
        else:
            # Edge case: distribute equally
            normalized = [1.0 / n_steps for _ in range(n_steps)]

        return normalized


class LLMCreditStrategy:
    """Use LLM to identify key steps and their contributions.

    Prompts an LLM to analyze the trajectory and identify which steps
    were most critical for the outcome, with reasoning.

    Example:
        ```python
        strategy = LLMCreditStrategy(llm)
        scores = strategy.compute_attribution(trajectory)
        ```
    """

    def __init__(self, llm: LLM) -> None:
        """Initialize with an LLM.

        Args:
            llm: LLM instance for analysis.
        """
        self._llm = llm

    def compute_attribution(
        self,
        trajectory: Trajectory,
        llm: LLM | None = None,
    ) -> list[float]:
        """Compute attribution by asking LLM to identify key steps.

        Args:
            trajectory: The trajectory to analyze.
            llm: Optional override LLM (uses instance LLM if not provided).

        Returns:
            List of attribution scores from LLM analysis.
        """
        if not trajectory.steps:
            return []

        active_llm = llm or self._llm
        n_steps = len(trajectory.steps)

        # Format steps for prompt
        steps_text = self._format_steps(trajectory)

        prompt = f"""Analyze this trajectory and identify the contribution of each step to the outcome.

Task: {trajectory.task.description}
Outcome: {"Success" if trajectory.outcome.success else "Failure"}
{f"Error: {trajectory.outcome.error_info}" if trajectory.outcome.error_info else ""}

Steps:
{steps_text}

For each step, assign a contribution score from 0.0 to 1.0 based on how important it was for the outcome.
- Higher scores for steps that were critical for success/failure
- Lower scores for routine or less impactful steps

Return ONLY a JSON object in this exact format:
{{"attributions": [{{"step": 0, "score": 0.5, "reason": "brief reason"}}]}}

Include all {n_steps} steps in order."""

        try:
            response = active_llm.generate(prompt, temperature=0.0)
            scores = self._parse_response(response, n_steps)
            return self._normalize_scores(scores)
        except Exception as e:
            logger.warning(f"LLM credit attribution failed: {e}, falling back to simple")
            # Fall back to simple strategy
            return SimpleCreditStrategy().compute_attribution(trajectory)

    def _format_steps(self, trajectory: Trajectory) -> str:
        """Format trajectory steps for the prompt."""
        lines = []
        for i, step in enumerate(trajectory.steps):
            thought_part = f"Thought: {step.thought}\n" if step.thought else ""
            lines.append(
                f"Step {i}:\n"
                f"{thought_part}"
                f"Action: {step.action}\n"
                f"Observation: {step.observation[:200]}..."
                if len(step.observation) > 200
                else f"Step {i}:\n{thought_part}Action: {step.action}\nObservation: {step.observation}"
            )
        return "\n\n".join(lines)

    def _parse_response(self, response: str, n_steps: int) -> list[float]:
        """Parse LLM response to extract attribution scores."""
        # Try to parse JSON
        try:
            # First try direct parse
            data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse JSON from response")
            else:
                raise ValueError("No JSON found in response")

        # Extract scores
        attributions = data.get("attributions", [])
        scores = [0.0] * n_steps

        for attr in attributions:
            step_idx = attr.get("step", -1)
            score = attr.get("score", 0.0)
            if 0 <= step_idx < n_steps:
                scores[step_idx] = float(score)

        return scores

    def _normalize_scores(self, scores: list[float]) -> list[float]:
        """Normalize scores to sum to 1.0."""
        total = sum(scores)
        if total > 0:
            return [s / total for s in scores]
        # If all zeros, use uniform distribution
        n = len(scores)
        return [1.0 / n for _ in range(n)] if n > 0 else []


class CounterfactualCreditStrategy:
    """Credit assignment via counterfactual reasoning.

    For each step, asks the LLM: "Would the outcome change if this step
    was removed?" Steps where removal would change the outcome get higher
    credit.

    This is more computationally expensive but provides deeper insight
    into causal relationships between actions and outcomes.
    """

    def __init__(self, llm: LLM) -> None:
        """Initialize with an LLM.

        Args:
            llm: LLM instance for counterfactual reasoning.
        """
        self._llm = llm

    def compute_attribution(
        self,
        trajectory: Trajectory,
        llm: LLM | None = None,
    ) -> list[float]:
        """Compute attribution via counterfactual analysis.

        Args:
            trajectory: The trajectory to analyze.
            llm: Optional override LLM (uses instance LLM if not provided).

        Returns:
            List of attribution scores based on counterfactual reasoning.
        """
        if not trajectory.steps:
            return []

        active_llm = llm or self._llm
        n_steps = len(trajectory.steps)

        # For efficiency, do batch counterfactual analysis
        steps_text = self._format_steps(trajectory)

        prompt = f"""Analyze this trajectory using counterfactual reasoning.

Task: {trajectory.task.description}
Final Outcome: {"Success" if trajectory.outcome.success else "Failure"}
{f"Error: {trajectory.outcome.error_info}" if trajectory.outcome.error_info else ""}

Steps:
{steps_text}

For each step, consider: "If this step was removed or done differently, would the final outcome change?"

Assign an importance score from 0.0 to 1.0:
- 1.0: Removing this step would definitely change the outcome
- 0.5: Removing this step might change the outcome
- 0.0: Removing this step would not change the outcome

Return ONLY a JSON object in this exact format:
{{"counterfactuals": [{{"step": 0, "importance": 0.8, "reasoning": "brief explanation"}}]}}

Include all {n_steps} steps in order."""

        try:
            response = active_llm.generate(prompt, temperature=0.0)
            scores = self._parse_response(response, n_steps)
            return self._normalize_scores(scores)
        except Exception as e:
            logger.warning(f"Counterfactual analysis failed: {e}, falling back to simple")
            return SimpleCreditStrategy().compute_attribution(trajectory)

    def _format_steps(self, trajectory: Trajectory) -> str:
        """Format trajectory steps for the prompt."""
        lines = []
        for i, step in enumerate(trajectory.steps):
            thought_part = f"Thought: {step.thought}\n" if step.thought else ""
            obs = step.observation[:200] + "..." if len(step.observation) > 200 else step.observation
            lines.append(f"Step {i}:\n{thought_part}Action: {step.action}\nObservation: {obs}")
        return "\n\n".join(lines)

    def _parse_response(self, response: str, n_steps: int) -> list[float]:
        """Parse LLM response to extract importance scores."""
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse JSON from response")
            else:
                raise ValueError("No JSON found in response")

        counterfactuals = data.get("counterfactuals", [])
        scores = [0.0] * n_steps

        for cf in counterfactuals:
            step_idx = cf.get("step", -1)
            importance = cf.get("importance", 0.0)
            if 0 <= step_idx < n_steps:
                scores[step_idx] = float(importance)

        return scores

    def _normalize_scores(self, scores: list[float]) -> list[float]:
        """Normalize scores to sum to 1.0."""
        total = sum(scores)
        if total > 0:
            return [s / total for s in scores]
        n = len(scores)
        return [1.0 / n for _ in range(n)] if n > 0 else []


# =============================================================================
# Trajectory Analyzer
# =============================================================================


class TrajectoryAnalyzer:
    """Analyzes trajectories to extract learning signals.

    Combines credit assignment with pattern detection and abstractability
    assessment to produce comprehensive analysis results.

    Example:
        ```python
        strategy = LLMCreditStrategy(llm)
        analyzer = TrajectoryAnalyzer(credit_strategy=strategy, llm=llm)
        result = analyzer.analyze(trajectory)
        print(f"Key steps: {result.key_steps}")
        print(f"Abstractable: {result.abstractable}")
        ```
    """

    # Threshold for considering a step as "key" (high attribution)
    KEY_STEP_THRESHOLD = 0.15

    def __init__(
        self,
        credit_strategy: CreditAssignmentStrategy,
        llm: LLM,
    ) -> None:
        """Initialize the analyzer.

        Args:
            credit_strategy: Strategy for credit assignment.
            llm: LLM for abstractability assessment and error detection.
        """
        self._credit_strategy = credit_strategy
        self._llm = llm

    def analyze(self, trajectory: Trajectory) -> AnalysisResult:
        """Analyze a trajectory to identify key steps and patterns.

        Args:
            trajectory: The trajectory to analyze.

        Returns:
            AnalysisResult with attribution, key steps, patterns, etc.
        """
        # 1. Credit assignment
        step_attribution = self._credit_strategy.compute_attribution(
            trajectory, self._llm
        )

        # 2. Identify key steps (above threshold)
        key_steps = [
            i
            for i, score in enumerate(step_attribution)
            if score > self.KEY_STEP_THRESHOLD
        ]

        # 3. Detect error patterns (if failed)
        error_patterns: list[dict[str, Any]] = []
        if not trajectory.outcome.success:
            error_patterns = self._detect_error_patterns(trajectory)

        # 4. Assess abstractability
        abstractable = self._assess_abstractability(trajectory)

        # 5. Generate training examples (hindsight learning)
        training_examples = self._generate_training_examples(trajectory, key_steps)

        return AnalysisResult(
            success=trajectory.outcome.success,
            key_steps=key_steps,
            step_attribution=step_attribution,
            error_patterns=error_patterns,
            abstractable=abstractable,
            training_examples=training_examples,
        )

    def _detect_error_patterns(
        self, trajectory: Trajectory
    ) -> list[dict[str, Any]]:
        """Detect error patterns from a failed trajectory.

        Uses LLM to identify common error patterns and provide fixes.

        Args:
            trajectory: A failed trajectory.

        Returns:
            List of detected error patterns as dictionaries.
        """
        if trajectory.outcome.success:
            return []

        # Collect error information
        error_info = trajectory.outcome.error_info or "Unknown error"
        last_observation = (
            trajectory.steps[-1].observation if trajectory.steps else ""
        )

        prompt = f"""Analyze this failed trajectory to identify error patterns.

Task: {trajectory.task.description}
Error: {error_info}
Last observation: {last_observation[:500]}

Identify any common error patterns (e.g., null pointer, type mismatch, missing import).

Return ONLY a JSON object in this format:
{{"patterns": [{{"name": "pattern_name", "signature": "error_signature", "suggested_fix": "how to fix", "example": "example of error"}}]}}

If no clear patterns are found, return {{"patterns": []}}"""

        try:
            response = self._llm.generate(prompt, temperature=0.0)
            data = self._parse_json(response)
            patterns = data.get("patterns", [])

            # Convert to list of dicts
            return [
                {
                    "name": p.get("name", "unknown"),
                    "signature": p.get("signature", ""),
                    "suggested_fix": p.get("suggested_fix", ""),
                    "example": p.get("example", ""),
                }
                for p in patterns
            ]
        except Exception as e:
            logger.warning(f"Error pattern detection failed: {e}")
            return []

    def _assess_abstractability(self, trajectory: Trajectory) -> bool:
        """Use LLM to assess if trajectory is worth extracting patterns from.

        Considers novelty, generalizability, and complexity.

        Args:
            trajectory: The trajectory to assess.

        Returns:
            True if the trajectory is worth extracting patterns from.
        """
        if not trajectory.steps:
            return False

        # Brief summary for assessment
        steps_summary = "\n".join(
            f"- {step.action}" for step in trajectory.steps[:5]
        )
        if len(trajectory.steps) > 5:
            steps_summary += f"\n- ... ({len(trajectory.steps) - 5} more steps)"

        prompt = f"""Assess if this trajectory is worth extracting reusable patterns from.

Task: {trajectory.task.description}
Outcome: {"Success" if trajectory.outcome.success else "Failure"}
Steps (summary):
{steps_summary}

Consider:
1. Novelty: Does this solve a common problem in an interesting way?
2. Generalizability: Could the approach apply to similar tasks?
3. Complexity: Is there enough substance to extract patterns?

Respond with ONLY a JSON object:
{{"abstractable": true, "reasoning": "brief explanation"}} or {{"abstractable": false, "reasoning": "brief explanation"}}"""

        try:
            response = self._llm.generate(prompt, temperature=0.0)
            data = self._parse_json(response)
            return bool(data.get("abstractable", False))
        except Exception as e:
            logger.warning(f"Abstractability assessment failed: {e}")
            # Default to True for successful trajectories with multiple steps
            return trajectory.outcome.success and len(trajectory.steps) >= 2

    def _generate_training_examples(
        self,
        trajectory: Trajectory,
        key_steps: list[int],
    ) -> list[dict[str, Any]]:
        """Generate training examples for hindsight learning.

        Creates input-output pairs from the trajectory that could be used
        for fine-tuning or in-context learning.

        Args:
            trajectory: The source trajectory.
            key_steps: Indices of key steps to focus on.

        Returns:
            List of training example dictionaries.
        """
        examples = []

        if not trajectory.steps:
            return examples

        # Create task-to-solution example
        if trajectory.outcome.success:
            # Full trajectory example
            solution_steps = [
                step.action for step in trajectory.steps
            ]
            examples.append({
                "type": "task_solution",
                "input": trajectory.task.description,
                "output": "\n".join(solution_steps),
                "weight": 1.0,
            })

            # Key step examples (higher weight)
            for idx in key_steps:
                if idx < len(trajectory.steps):
                    step = trajectory.steps[idx]
                    # Context from previous steps
                    context = "\n".join(
                        s.action for s in trajectory.steps[:idx]
                    )
                    examples.append({
                        "type": "key_step",
                        "input": f"Task: {trajectory.task.description}\nContext: {context}",
                        "output": step.action,
                        "weight": 2.0,  # Higher weight for key steps
                    })
        else:
            # For failures, create negative examples
            if trajectory.outcome.error_info:
                examples.append({
                    "type": "error",
                    "input": trajectory.task.description,
                    "output": f"Error: {trajectory.outcome.error_info}",
                    "weight": 1.0,
                })

        return examples

    def _parse_json(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            return {}


# =============================================================================
# Factory Function
# =============================================================================


def create_analyzer(
    config: LearningConfig,
    llm: LLM,
) -> TrajectoryAnalyzer:
    """Create TrajectoryAnalyzer based on config.

    Factory function that creates the appropriate credit strategy
    based on configuration and wires up the analyzer.

    Args:
        config: Learning configuration with credit_strategy setting.
        llm: LLM instance for strategies that require it.

    Returns:
        Configured TrajectoryAnalyzer.

    Raises:
        ValueError: If credit_strategy is unknown.

    Example:
        ```python
        config = LearningConfig(credit_strategy="llm")
        llm = SimpleLLM()
        analyzer = create_analyzer(config, llm)
        result = analyzer.analyze(trajectory)
        ```
    """
    strategy: CreditAssignmentStrategy

    if config.credit_strategy == "simple":
        strategy = SimpleCreditStrategy()
    elif config.credit_strategy == "llm":
        strategy = LLMCreditStrategy(llm)
    elif config.credit_strategy == "counterfactual":
        strategy = CounterfactualCreditStrategy(llm)
    else:
        raise ValueError(f"Unknown credit strategy: {config.credit_strategy}")

    return TrajectoryAnalyzer(credit_strategy=strategy, llm=llm)


__all__ = [
    "CreditAssignmentStrategy",
    "CounterfactualCreditStrategy",
    "LLMCreditStrategy",
    "SimpleCreditStrategy",
    "TrajectoryAnalyzer",
    "create_analyzer",
]
