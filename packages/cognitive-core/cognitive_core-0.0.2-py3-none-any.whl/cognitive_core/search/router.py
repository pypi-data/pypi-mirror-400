"""TaskRouter implementations for ATLAS.

The router decides which search strategy to use based on task and memory context.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from cognitive_core.config import RouterConfig
from cognitive_core.core.types import RoutingDecision

if TYPE_CHECKING:
    from cognitive_core.core.types import Experience, Task
    from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem

logger = logging.getLogger("cognitive_core.search.router")


class BasicTaskRouter:
    """Basic router that always routes to DirectSolver.

    This is the Phase 4 minimal implementation that:
    - Queries memory for relevant context
    - Estimates confidence based on memory results
    - Always routes to the "direct" strategy

    Future versions will implement more sophisticated routing logic
    based on task domain, memory similarity, and success patterns.

    Example:
        ```python
        router = BasicTaskRouter()
        decision = router.route(task, memory)
        # decision.strategy is always "direct"
        ```
    """

    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """Route task - v1 always uses direct strategy.

        Args:
            task: The task to route
            memory: Memory system to query for context

        Returns:
            RoutingDecision with strategy="direct" and relevant context
        """
        # Query memory for context
        context = memory.query(task, k=5)

        # Estimate confidence based on whether we found similar experiences
        confidence = self._estimate_confidence(context)

        # v1: Always use direct strategy
        return RoutingDecision(
            strategy="direct",
            context=context,
            confidence=confidence,
            budget=5,
        )

    def _estimate_confidence(self, context: MemoryQueryResult | None) -> float:
        """Estimate confidence based on memory results.

        Uses a simple heuristic: confidence scales with the number of
        experiences found, up to a maximum of 5 experiences = 100% confidence.

        Args:
            context: Memory query result

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if context is None or context.is_empty():
            return 0.0
        # Simple heuristic: confidence based on number of experiences found
        return min(1.0, len(context.experiences) / 5.0)


class EnhancedTaskRouter:
    """Smart task routing based on task characteristics and memory analysis.

    EnhancedTaskRouter implements Phase 5 routing logic that:
    1. Analyzes memory for similar experiences and success patterns
    2. Calculates similarity using embeddings or text heuristics
    3. Routes based on configurable thresholds and domain rules

    Routing Priority:
    1. High similarity + success → 'adapt' (reuse known solution)
    2. Strategy match → 'direct' (apply known strategy)
    3. Domain-based → 'evolutionary' for ARC, 'mcts' for SWE
    4. Default → configurable fallback (usually 'evolutionary')

    Example:
        ```python
        router = EnhancedTaskRouter(config=RouterConfig(similarity_threshold=0.85))
        decision = router.route(task, memory)
        # decision.strategy could be 'adapt', 'direct', 'evolutionary', or 'mcts'
        ```
    """

    def __init__(self, config: RouterConfig | None = None) -> None:
        """Initialize EnhancedTaskRouter.

        Args:
            config: Router configuration. If not provided, uses defaults.
        """
        self._config = config or RouterConfig()

    @property
    def config(self) -> RouterConfig:
        """Router configuration."""
        return self._config

    def route(self, task: Task, memory: MemorySystem) -> RoutingDecision:
        """Route task to appropriate search strategy.

        Decision process:
        1. Query memory for similar experiences
        2. Calculate similarity and check for success patterns
        3. Apply routing rules based on config
        4. Return decision with context and estimated budget

        Args:
            task: The task to route
            memory: Memory system to query for context

        Returns:
            RoutingDecision with strategy, context, confidence, and budget
        """
        logger.debug(
            "EnhancedTaskRouter.route started",
            extra={"task_id": task.id, "domain": task.domain},
        )

        # Analyze memory
        context, similarity, has_success = self._analyze_memory(task, memory)

        # Select strategy
        strategy = self._select_strategy(task, similarity, has_success, context)

        # Estimate confidence and budget
        confidence = self._estimate_confidence(similarity, has_success, context)
        budget = self._estimate_budget(strategy, similarity)

        logger.info(
            "Task routed",
            extra={
                "task_id": task.id,
                "strategy": strategy,
                "confidence": confidence,
                "budget": budget,
                "similarity": similarity,
                "has_success": has_success,
            },
        )

        return RoutingDecision(
            strategy=strategy,
            context=context,
            confidence=confidence,
            budget=budget,
        )

    def _analyze_memory(
        self,
        task: Task,
        memory: MemorySystem,
    ) -> tuple[MemoryQueryResult, float, bool]:
        """Analyze memory for routing decision.

        Queries memory for similar experiences and analyzes:
        - Maximum similarity score
        - Whether similar successful experiences exist

        Args:
            task: The task to analyze
            memory: Memory system to query

        Returns:
            Tuple of (context, max_similarity, has_successful_similar)
        """
        # Query memory for context
        context = memory.query(task, k=10)

        if context.is_empty():
            logger.debug("Empty memory, no similar experiences found")
            return context, 0.0, False

        # Calculate similarity scores
        max_similarity = self._calculate_max_similarity(task, context.experiences)

        # Check for successful similar experiences
        has_success = any(
            exp.success and self._is_similar_enough(task, exp)
            for exp in context.experiences
        )

        logger.debug(
            "Memory analyzed",
            extra={
                "num_experiences": len(context.experiences),
                "max_similarity": max_similarity,
                "has_success": has_success,
            },
        )

        return context, max_similarity, has_success

    def _calculate_max_similarity(
        self,
        task: Task,
        experiences: list[Experience],
    ) -> float:
        """Calculate maximum similarity to past experiences.

        Uses embedding cosine similarity when available,
        falls back to text-based heuristics.

        Args:
            task: The current task
            experiences: Past experiences to compare against

        Returns:
            Maximum similarity score (0.0 to 1.0)
        """
        if not experiences:
            return 0.0

        max_sim = 0.0
        for exp in experiences:
            sim = self._calculate_similarity(task, exp)
            max_sim = max(max_sim, sim)

        return max_sim

    def _calculate_similarity(self, task: Task, experience: Experience) -> float:
        """Calculate similarity between a task and an experience.

        Args:
            task: The current task
            experience: An experience to compare

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Try embedding similarity first
        if task.embedding is not None and experience.embedding is not None:
            return self._cosine_similarity(task.embedding, experience.embedding)

        # Fall back to text similarity
        return self._text_similarity(task.description, experience.task_input)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity (0.0 to 1.0, clipped)
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = float(np.dot(a, b) / (norm_a * norm_b))
        # Clip to [0, 1] range
        return max(0.0, min(1.0, similarity))

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard similarity on words.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0

        # Tokenize to words (simple whitespace split, lowercase)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _is_similar_enough(self, task: Task, experience: Experience) -> bool:
        """Check if an experience is similar enough for adaptation.

        Uses a lower threshold (0.5) than the routing threshold to identify
        potentially useful experiences.

        Args:
            task: The current task
            experience: An experience to check

        Returns:
            True if similar enough
        """
        similarity = self._calculate_similarity(task, experience)
        return similarity >= 0.5  # Lower threshold for "similar enough"

    def _select_strategy(
        self,
        task: Task,
        similarity: float,
        has_success: bool,
        context: MemoryQueryResult,
    ) -> str:
        """Select search strategy based on analysis.

        Priority order:
        1. High similarity + success → 'adapt'
        2. Strategy match → 'direct'
        3. Domain routing → domain-specific
        4. Default → configured default

        Args:
            task: The task being routed
            similarity: Maximum similarity score
            has_success: Whether successful similar experiences exist
            context: Memory query results

        Returns:
            Strategy name
        """
        # Check for high-similarity adapt case
        if similarity >= self._config.similarity_threshold and has_success:
            logger.debug(
                "Routing to 'adapt' based on high similarity + success",
                extra={"similarity": similarity},
            )
            return "adapt"

        # Check for strategy matches
        if context.strategies and self._has_strategy_match(task, context):
            logger.debug("Routing to 'direct' based on strategy match")
            return "direct"

        # Domain-based routing
        if self._config.use_domain_routing:
            domain = task.domain.lower() if task.domain else ""
            if domain == "arc":
                logger.debug("Routing to 'evolutionary' based on ARC domain")
                return self._config.arc_strategy
            elif domain == "swe":
                logger.debug("Routing to 'mcts' based on SWE domain")
                return self._config.swe_strategy

        # Default
        logger.debug(f"Routing to default strategy: {self._config.default_strategy}")
        return self._config.default_strategy

    def _has_strategy_match(self, task: Task, context: MemoryQueryResult) -> bool:
        """Check if there's a matching strategy for this task.

        A strategy matches if its situation description is similar to the task.

        Args:
            task: The task being routed
            context: Memory query results with strategies

        Returns:
            True if a matching strategy exists
        """
        if not context.strategies:
            return False

        # Check if any strategy's situation matches the task
        for strategy in context.strategies:
            if strategy.situation:
                similarity = self._text_similarity(task.description, strategy.situation)
                if similarity >= 0.3:  # Lower threshold for strategy matching
                    return True

        return False

    def _estimate_confidence(
        self,
        similarity: float,
        has_success: bool,
        context: MemoryQueryResult,
    ) -> float:
        """Estimate confidence in routing decision.

        Confidence is based on:
        - Similarity score (50% weight)
        - Past success (30% bonus)
        - Strategy availability (10% bonus)

        Args:
            similarity: Maximum similarity score
            has_success: Whether successful similar experiences exist
            context: Memory query results

        Returns:
            Confidence score (0.0 to 1.0)
        """
        base = similarity * 0.5

        if has_success:
            base += 0.3

        if context.strategies:
            base += 0.1

        return min(1.0, base)

    def _estimate_budget(self, strategy: str, similarity: float) -> int:
        """Estimate LLM call budget for strategy.

        Higher similarity = lower budget (easier task).

        Args:
            strategy: Selected strategy
            similarity: Similarity score

        Returns:
            Estimated budget (number of LLM calls)
        """
        base_budgets = {
            "adapt": 5,
            "direct": 10,
            "evolutionary": 100,
            "mcts": 200,
        }

        base = base_budgets.get(strategy, 100)

        # Reduce budget for high similarity
        if similarity > 0.8:
            return max(1, int(base * 0.5))
        elif similarity > 0.5:
            return max(1, int(base * 0.75))

        return base
