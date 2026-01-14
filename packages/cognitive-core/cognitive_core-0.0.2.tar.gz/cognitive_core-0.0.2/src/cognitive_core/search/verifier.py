"""Verifier implementations for ATLAS (Pillar 2).

Verifiers validate candidate solutions and enable inference-time scaling.
Key insight from SWE-Gym: verification enables best-of-k scaling.

Domain implementations:
- SimpleVerifier: Delegates to Environment.verify()
- ExactMatchVerifier: String/value equality check
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cognitive_core.core.types import Outcome

if TYPE_CHECKING:
    from cognitive_core.core.types import Candidate, Task
    from cognitive_core.protocols.environment import Environment


class SimpleVerifier:
    """Basic verifier that delegates verification to an environment.

    This is the simplest verifier - it passes the candidate solution
    to the environment's verify method and returns the result.

    Example:
        ```python
        env = ARCEnvironment()
        verifier = SimpleVerifier(env)
        outcome = verifier.verify(task, candidate)
        ```
    """

    def __init__(self, env: Environment) -> None:
        """Initialize with an environment for verification.

        Args:
            env: Environment that implements the verify method
        """
        self._env = env

    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify by delegating to environment.

        Args:
            task: The original task (unused, kept for protocol compliance)
            candidate: The candidate to verify

        Returns:
            Outcome from environment verification
        """
        return self._env.verify(candidate.solution)

    def rank(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[tuple[Candidate, float]]:
        """Return candidates with their fitness scores.

        Default implementation that returns candidates sorted by their
        existing fitness scores.

        Args:
            task: The original task
            candidates: Candidates to rank

        Returns:
            List of (candidate, score) tuples, sorted by score descending
        """
        ranked = [(c, c.fitness or 0.0) for c in candidates]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def batch_verify(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[Outcome]:
        """Verify multiple candidates sequentially.

        Default implementation that calls verify() for each candidate.

        Args:
            task: The original task
            candidates: Candidates to verify

        Returns:
            List of outcomes in same order as candidates
        """
        return [self.verify(task, c) for c in candidates]

    @property
    def supports_partial_scoring(self) -> bool:
        """Whether this verifier supports partial scores.

        SimpleVerifier supports partial scoring since environments
        can return partial_score in their Outcome.

        Returns:
            True
        """
        return True


class ExactMatchVerifier:
    """Verifier that checks exact match against expected value.

    Compares the candidate's solution directly with the expected
    value from the task's verification spec.

    Example:
        ```python
        verifier = ExactMatchVerifier()
        # Task has verification.config["expected"] = "hello"
        # Candidate.solution = "hello" -> success=True
        outcome = verifier.verify(task, candidate)
        ```
    """

    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify by checking exact equality with expected value.

        Args:
            task: The task containing expected value in verification.config
            candidate: The candidate to verify

        Returns:
            Outcome with success=True if solution matches expected
        """
        expected = None
        if task.verification and task.verification.config:
            expected = task.verification.config.get("expected")

        success = candidate.solution == expected

        return Outcome(
            success=success,
            partial_score=1.0 if success else 0.0,
        )

    def rank(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[tuple[Candidate, float]]:
        """Return candidates with their fitness scores.

        Default implementation that returns candidates sorted by their
        existing fitness scores.

        Args:
            task: The original task
            candidates: Candidates to rank

        Returns:
            List of (candidate, score) tuples, sorted by score descending
        """
        ranked = [(c, c.fitness or 0.0) for c in candidates]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def batch_verify(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[Outcome]:
        """Verify multiple candidates sequentially.

        Default implementation that calls verify() for each candidate.

        Args:
            task: The original task
            candidates: Candidates to verify

        Returns:
            List of outcomes in same order as candidates
        """
        return [self.verify(task, c) for c in candidates]

    @property
    def supports_partial_scoring(self) -> bool:
        """Whether this verifier supports partial scores.

        ExactMatchVerifier only gives 0 or 1, so technically
        it supports partial scoring (just at extremes).

        Returns:
            True
        """
        return True
