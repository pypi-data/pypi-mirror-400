"""Search protocols for ATLAS (Pillar 2).

Search is how to solve - the algorithms for finding solutions.
Different methods suit different task types:
- Direct: High-confidence memory match (~1 call)
- Evolutionary (Mind Evolution): Population-based (~100 calls)
- MCTS (SWE-Search): Tree search with UCB selection (~200 calls)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import Candidate, Outcome, RoutingDecision, Task
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemorySystem


@runtime_checkable
class TaskRouter(Protocol):
    """Decides which search strategy to use based on task and memory context.

    The router analyzes the task and available memory to determine:
    - Which search strategy to use
    - What concepts/experiences/strategies are relevant
    - How difficult the task likely is
    - What search budget to allocate

    Routing logic:
    | Condition                    | Strategy      | Rationale                    |
    |------------------------------|---------------|------------------------------|
    | High similarity + success    | adapt         | Modify existing solution     |
    | Clear strategy available     | direct        | Apply strategy directly      |
    | ARC domain                   | evolutionary  | Mind Evolution for fitness   |
    | SWE domain                   | mcts          | SWE-Search for edits         |
    | Unknown/low confidence       | evolutionary  | Default to population search |

    Example:
        ```python
        router = TaskRouter(llm=llm)
        decision = router.route(task, memory)
        if decision.strategy == "direct":
            # Use direct solver
        elif decision.strategy == "evolutionary":
            # Use Mind Evolution
        ```
    """

    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """Decide how to approach a task.

        Args:
            task: The task to route
            memory: Memory system to query for context

        Returns:
            RoutingDecision with strategy, relevant context, and budget
        """
        ...


@runtime_checkable
class SearchEngine(Protocol):
    """Search for candidate solutions.

    Base protocol for all search methods. Implementations include:
    - DirectSolver: For high-confidence memory matches
    - MindEvolutionSearch: Population-based evolutionary search
    - SWESearch: MCTS with UCB selection

    All search engines can operate with or without memory (for ablation).

    Example:
        ```python
        search = MindEvolutionSearch(llm=llm, memory=memory)
        candidates = search.search(task, routing, env)
        best = max(candidates, key=lambda c: c.fitness or 0)
        ```
    """

    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Search for candidate solutions.

        Args:
            task: The task to solve
            routing: Routing decision with strategy and context
            env: Environment for verification

        Returns:
            List of candidate solutions, potentially ranked by fitness
        """
        ...

    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine a candidate based on feedback.

        Used for iterative improvement after verification failures.

        Args:
            candidate: The candidate to refine
            feedback: Feedback from verification or LLM
            task: The original task

        Returns:
            Refined candidate
        """
        ...

    @property
    def name(self) -> str:
        """Name of this search method."""
        ...


@runtime_checkable
class Verifier(Protocol):
    """Verifies candidate solutions and enables inference-time scaling.

    Key insight from SWE-Gym: verification enables best-of-k scaling,
    improving results from 10% to 13.3% with best-of-8.

    Domain implementations:
    - ARC: Exact grid match on training examples
    - SWE: Execute tests in Docker sandbox

    Example:
        ```python
        verifier = ARCVerifier()
        outcome = verifier.verify(task, candidate)
        if not outcome.success:
            # Refine and try again
            refined = search.refine(candidate, outcome.error_info, task)
        ```
    """

    def verify(self, task: Task, candidate: Candidate) -> Outcome:
        """Verify a candidate solution.

        Args:
            task: The original task
            candidate: The candidate to verify

        Returns:
            Outcome with success status, partial score, and details
        """
        ...

    def rank(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[tuple[Candidate, float]]:
        """Rank candidates by estimated quality.

        Uses verification or a discriminator model to rank candidates
        without full verification (useful for pruning).

        Args:
            task: The original task
            candidates: Candidates to rank

        Returns:
            List of (candidate, score) tuples, sorted by score descending
        """
        ...

    def batch_verify(
        self,
        task: Task,
        candidates: list[Candidate],
    ) -> list[Outcome]:
        """Verify multiple candidates efficiently.

        Args:
            task: The original task
            candidates: Candidates to verify

        Returns:
            List of outcomes in same order as candidates
        """
        ...

    @property
    def supports_partial_scoring(self) -> bool:
        """Whether this verifier supports partial scores.

        Returns:
            True if verify() can return partial_score
        """
        ...
