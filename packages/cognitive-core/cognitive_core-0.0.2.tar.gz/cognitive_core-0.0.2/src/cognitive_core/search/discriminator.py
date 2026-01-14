"""Discriminator for solution quality estimation."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cognitive_core.core.types import Candidate, Task
    from cognitive_core.execution.executor import TaskExecutor
    from cognitive_core.llm.simple import SimpleLLM
    from cognitive_core.protocols.environment import Environment

logger = logging.getLogger("cognitive_core.search.discriminator")


class Discriminator:
    """Estimates solution quality for MCTS and pruning.

    Provides two estimation methods:
    1. Quick LLM estimate - Single call to estimate quality
    2. Agent rollout - Run partial execution for high-confidence estimate

    The hybrid approach uses quick estimates for all candidates,
    then expensive rollouts only for promising ones (top 10-20%).

    Example:
        ```python
        discriminator = Discriminator(llm=simple_llm, executor=executor)

        # Quick estimate
        score = discriminator.estimate(task, candidate)

        # If promising, do rollout
        if discriminator.should_rollout(score):
            score = await discriminator.estimate_with_rollout(task, candidate, env)
        ```
    """

    def __init__(
        self,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,
    ):
        """Initialize the Discriminator.

        Args:
            llm: SimpleLLM instance for quick quality estimation.
            executor: Optional TaskExecutor for agent rollouts.
        """
        self._llm = llm
        self._executor = executor

    def estimate(self, task: Task, candidate: Candidate) -> float:
        """Quick LLM-based quality estimation.

        Args:
            task: The task being solved
            candidate: Candidate solution to evaluate

        Returns:
            Estimated quality score (0.0-1.0)
        """
        prompt = f"""Evaluate the quality of this solution attempt.

Task: {task.description}

Solution/Approach:
{candidate.solution}

Reasoning: {candidate.reasoning}

Rate the likelihood this solution is correct from 0.0 to 1.0.
Consider: Does it address the problem? Is the approach sound? Any obvious errors?

Return ONLY a decimal number between 0.0 and 1.0.
"""

        try:
            response = self._llm.generate(prompt, temperature=0.0)
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except (ValueError, Exception) as e:
            logger.warning(f"Failed to parse discriminator score: {e}")
            return 0.5  # Default uncertain

    async def estimate_with_rollout(
        self,
        task: Task,
        candidate: Candidate,
        env: Environment,
        depth: int = 5,
    ) -> float:
        """Agent rollout for high-confidence estimation.

        Args:
            task: The task being solved
            candidate: Current candidate/state
            env: Environment for execution
            depth: Number of steps to roll out

        Returns:
            Estimated quality based on rollout outcome
        """
        if self._executor is None:
            logger.debug("No executor available, falling back to LLM estimate")
            return self.estimate(task, candidate)

        try:
            # Execute with limited steps
            trajectory = await self._executor.execute(task, env, max_steps=depth)

            if trajectory.outcome.success:
                return 1.0
            return trajectory.outcome.partial_score or 0.0

        except Exception as e:
            logger.warning(f"Rollout failed: {e}")
            return 0.0

    def should_rollout(self, score: float, threshold: float = 0.7) -> bool:
        """Decide if candidate warrants expensive rollout.

        Args:
            score: Quick estimate score
            threshold: Minimum score to trigger rollout

        Returns:
            True if rollout is warranted
        """
        return score >= threshold

    def batch_estimate(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[float]:
        """Estimate quality for multiple candidates.

        Args:
            task: The task being solved
            candidates: List of candidates to evaluate

        Returns:
            List of scores in same order as candidates
        """
        if not candidates:
            return []

        if len(candidates) <= 3:
            return [self.estimate(task, c) for c in candidates]

        # Batch prompt for efficiency
        prompt = f"""Evaluate these solution attempts for the task.

Task: {task.description}

Solutions:
"""
        for i, c in enumerate(candidates):
            sol_str = str(c.solution)[:200]
            prompt += f"\n[{i + 1}] {sol_str}...\n"

        prompt += """
Rate each from 0.0 to 1.0.
Format: 1: 0.X, 2: 0.X, 3: 0.X, ...
"""

        try:
            response = self._llm.generate(prompt, temperature=0.0)
            return self._parse_batch_scores(response, len(candidates))
        except Exception as e:
            logger.warning(f"Batch estimate failed: {e}")
            return [0.5] * len(candidates)

    def _parse_batch_scores(self, response: str, count: int) -> list[float]:
        """Parse batch score response."""
        scores = [0.5] * count

        # Try to parse "1: 0.8, 2: 0.6, ..." format (including negative numbers)
        matches = re.findall(r"(\d+):\s*(-?[\d.]+)", response)

        for idx_str, score_str in matches:
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < count:
                    scores[idx] = max(0.0, min(1.0, float(score_str)))
            except ValueError:
                continue

        return scores
