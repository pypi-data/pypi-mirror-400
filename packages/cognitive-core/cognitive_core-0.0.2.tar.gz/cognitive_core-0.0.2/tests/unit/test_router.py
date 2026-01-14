"""Tests for BasicTaskRouter and EnhancedTaskRouter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest

from pydantic import ValidationError

from cognitive_core.config import RouterConfig
from cognitive_core.core.types import (
    CodeConcept,
    Experience,
    RoutingDecision,
    Strategy,
    Task,
    VerificationSpec,
)
from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem
from cognitive_core.protocols.search import TaskRouter
from cognitive_core.search.router import BasicTaskRouter, EnhancedTaskRouter


def make_task(task_id: str = "test-1", description: str = "Test task") -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        description=description,
        domain="test",
        verification=VerificationSpec(method="exact_match"),
    )


def make_experience(
    exp_id: str = "exp-1",
    success: bool = True,
) -> Experience:
    """Create a test experience with all required fields."""
    return Experience(
        id=exp_id,
        task_input="Test input",
        solution_output="Test output",
        feedback="Test feedback",
        success=success,
        trajectory_id="traj-1",
        timestamp=datetime.now(timezone.utc),
    )


def make_concept(concept_id: str = "concept-1") -> CodeConcept:
    """Create a test concept with all required fields."""
    return CodeConcept(
        id=concept_id,
        name="Test Concept",
        description="Test description",
        code="def test(): pass",
        signature="() -> None",
    )


def make_strategy(strategy_id: str = "strategy-1") -> Strategy:
    """Create a test strategy with all required fields."""
    return Strategy(
        id=strategy_id,
        situation="When X happens",
        suggestion="Do Y",
    )


def make_mock_memory(
    experiences: list[Experience] | None = None,
    concepts: list[CodeConcept] | None = None,
    strategies: list[Strategy] | None = None,
) -> MagicMock:
    """Create a mock memory system with configured query results."""
    mock = MagicMock(spec=MemorySystem)
    result = MemoryQueryResult(
        experiences=experiences,
        concepts=concepts,
        strategies=strategies,
    )
    mock.query = MagicMock(return_value=result)
    return mock


class TestBasicTaskRouterProtocol:
    """Tests for protocol compliance."""

    def test_implements_protocol(self) -> None:
        """BasicTaskRouter implements TaskRouter protocol."""
        router = BasicTaskRouter()
        assert isinstance(router, TaskRouter)

    def test_has_route_method(self) -> None:
        """Has route method."""
        router = BasicTaskRouter()
        assert hasattr(router, "route")
        assert callable(router.route)


class TestBasicTaskRouterRoute:
    """Tests for route method."""

    def test_route_returns_routing_decision(self) -> None:
        """Route returns a RoutingDecision."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert isinstance(result, RoutingDecision)

    def test_route_always_returns_direct_strategy(self) -> None:
        """Route always returns 'direct' strategy."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "direct"

    def test_route_queries_memory_with_task(self) -> None:
        """Route queries memory with the task."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        router.route(task, memory)

        memory.query.assert_called_once_with(task, k=5)

    def test_route_includes_context_from_memory(self) -> None:
        """Route includes memory context in decision."""
        router = BasicTaskRouter()
        task = make_task()
        experiences = [make_experience()]
        memory = make_mock_memory(experiences=experiences)

        result = router.route(task, memory)

        assert result.context is not None
        assert result.context.experiences == experiences

    def test_route_returns_budget_5(self) -> None:
        """Route returns budget of 5."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.budget == 5


class TestBasicTaskRouterConfidence:
    """Tests for confidence estimation."""

    def test_confidence_zero_with_empty_memory(self) -> None:
        """Confidence is 0 with no experiences."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.confidence == 0.0

    def test_confidence_increases_with_experiences(self) -> None:
        """Confidence increases with more experiences."""
        router = BasicTaskRouter()
        task = make_task()

        # 1 experience = 0.2 confidence
        memory_1 = make_mock_memory(experiences=[make_experience(f"exp-{i}") for i in range(1)])
        result_1 = router.route(task, memory_1)
        assert result_1.confidence == pytest.approx(0.2, abs=0.01)

        # 3 experiences = 0.6 confidence
        memory_3 = make_mock_memory(experiences=[make_experience(f"exp-{i}") for i in range(3)])
        result_3 = router.route(task, memory_3)
        assert result_3.confidence == pytest.approx(0.6, abs=0.01)

        # 5 experiences = 1.0 confidence
        memory_5 = make_mock_memory(experiences=[make_experience(f"exp-{i}") for i in range(5)])
        result_5 = router.route(task, memory_5)
        assert result_5.confidence == pytest.approx(1.0, abs=0.01)

    def test_confidence_capped_at_1(self) -> None:
        """Confidence is capped at 1.0 with many experiences."""
        router = BasicTaskRouter()
        task = make_task()
        experiences = [make_experience(f"exp-{i}") for i in range(10)]
        memory = make_mock_memory(experiences=experiences)

        result = router.route(task, memory)

        assert result.confidence == 1.0

    def test_confidence_zero_with_only_concepts(self) -> None:
        """Confidence is 0 when only concepts are found (no experiences)."""
        router = BasicTaskRouter()
        task = make_task()
        concepts = [make_concept()]
        memory = make_mock_memory(concepts=concepts)

        result = router.route(task, memory)

        # Current implementation only considers experiences for confidence
        assert result.confidence == 0.0

    def test_confidence_zero_with_only_strategies(self) -> None:
        """Confidence is 0 when only strategies are found (no experiences)."""
        router = BasicTaskRouter()
        task = make_task()
        strategies = [make_strategy()]
        memory = make_mock_memory(strategies=strategies)

        result = router.route(task, memory)

        # Current implementation only considers experiences for confidence
        assert result.confidence == 0.0


class TestBasicTaskRouterEmptyMemory:
    """Tests for handling empty/minimal memory."""

    def test_works_with_empty_memory_result(self) -> None:
        """Router works when memory returns empty results."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "direct"
        assert result.confidence == 0.0
        assert result.budget == 5
        assert result.context is not None
        assert result.context.is_empty()

    def test_works_with_different_task_domains(self) -> None:
        """Router works with various task domains."""
        router = BasicTaskRouter()
        memory = make_mock_memory()

        domains = ["arc", "swe", "frontend", "backend", "unknown"]
        for domain in domains:
            task = Task(
                id=f"task-{domain}",
                domain=domain,
                description=f"Test task for {domain}",
                verification=VerificationSpec(method="test_suite"),
            )
            result = router.route(task, memory)
            # v1 always returns direct regardless of domain
            assert result.strategy == "direct"


class TestBasicTaskRouterEdgeCases:
    """Tests for edge cases and error handling."""

    def test_context_is_memory_query_result(self) -> None:
        """Context in result is the MemoryQueryResult from query."""
        router = BasicTaskRouter()
        task = make_task()
        experiences = [make_experience()]
        concepts = [make_concept()]
        strategies = [make_strategy()]
        memory = make_mock_memory(
            experiences=experiences,
            concepts=concepts,
            strategies=strategies,
        )

        result = router.route(task, memory)

        assert isinstance(result.context, MemoryQueryResult)
        assert result.context.experiences == experiences
        assert result.context.concepts == concepts
        assert result.context.strategies == strategies

    def test_routing_decision_is_immutable(self) -> None:
        """RoutingDecision is frozen/immutable."""
        router = BasicTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        with pytest.raises((AttributeError, TypeError, ValidationError)):
            result.strategy = "evolutionary"

    def test_multiple_routes_independent(self) -> None:
        """Multiple route calls are independent."""
        router = BasicTaskRouter()
        task1 = make_task("task-1", "First task")
        task2 = make_task("task-2", "Second task")

        experiences_1 = [make_experience("exp-1")]
        experiences_2 = [make_experience(f"exp-{i}") for i in range(5)]

        memory1 = make_mock_memory(experiences=experiences_1)
        memory2 = make_mock_memory(experiences=experiences_2)

        result1 = router.route(task1, memory1)
        result2 = router.route(task2, memory2)

        # Both return direct strategy
        assert result1.strategy == "direct"
        assert result2.strategy == "direct"

        # But different confidences based on experience count
        assert result1.confidence == pytest.approx(0.2, abs=0.01)
        assert result2.confidence == pytest.approx(1.0, abs=0.01)


class TestEstimateConfidence:
    """Tests for _estimate_confidence method."""

    def test_estimate_confidence_none_context(self) -> None:
        """Returns 0 for None context."""
        router = BasicTaskRouter()
        result = router._estimate_confidence(None)
        assert result == 0.0

    def test_estimate_confidence_empty_context(self) -> None:
        """Returns 0 for empty context."""
        router = BasicTaskRouter()
        context = MemoryQueryResult()
        result = router._estimate_confidence(context)
        assert result == 0.0

    def test_estimate_confidence_scaling(self) -> None:
        """Confidence scales linearly with experience count up to 5."""
        router = BasicTaskRouter()

        for n in range(6):
            experiences = [make_experience(f"exp-{i}") for i in range(n)]
            context = MemoryQueryResult(experiences=experiences)
            expected = min(1.0, n / 5.0)
            result = router._estimate_confidence(context)
            assert result == pytest.approx(expected, abs=0.001)


# =============================================================================
# EnhancedTaskRouter Tests
# =============================================================================


def make_task_with_domain(
    task_id: str = "test-1",
    description: str = "Test task",
    domain: str = "test",
    embedding: np.ndarray | None = None,
) -> Task:
    """Create a test task with domain and optional embedding."""
    return Task(
        id=task_id,
        description=description,
        domain=domain,
        verification=VerificationSpec(method="exact_match"),
        embedding=embedding,
    )


def make_experience_with_embedding(
    exp_id: str = "exp-1",
    success: bool = True,
    task_input: str = "Test input",
    embedding: np.ndarray | None = None,
) -> Experience:
    """Create a test experience with optional embedding."""
    return Experience(
        id=exp_id,
        task_input=task_input,
        solution_output="Test output",
        feedback="Test feedback",
        success=success,
        trajectory_id="traj-1",
        timestamp=datetime.now(timezone.utc),
        embedding=embedding,
    )


class TestEnhancedTaskRouterProtocol:
    """Tests for protocol compliance."""

    def test_implements_protocol(self) -> None:
        """EnhancedTaskRouter implements TaskRouter protocol."""
        router = EnhancedTaskRouter()
        assert isinstance(router, TaskRouter)

    def test_has_route_method(self) -> None:
        """Has route method."""
        router = EnhancedTaskRouter()
        assert hasattr(router, "route")
        assert callable(router.route)

    def test_default_config(self) -> None:
        """Uses default RouterConfig when not provided."""
        router = EnhancedTaskRouter()
        assert router.config is not None
        assert isinstance(router.config, RouterConfig)
        assert router.config.similarity_threshold == 0.9

    def test_custom_config(self) -> None:
        """Accepts custom RouterConfig."""
        config = RouterConfig(similarity_threshold=0.85, default_strategy="direct")
        router = EnhancedTaskRouter(config=config)
        assert router.config.similarity_threshold == 0.85
        assert router.config.default_strategy == "direct"


class TestEnhancedTaskRouterRoute:
    """Tests for route method."""

    def test_route_returns_routing_decision(self) -> None:
        """Route returns a RoutingDecision."""
        router = EnhancedTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert isinstance(result, RoutingDecision)

    def test_route_queries_memory_with_task(self) -> None:
        """Route queries memory with the task."""
        router = EnhancedTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        router.route(task, memory)

        memory.query.assert_called_once_with(task, k=10)

    def test_route_includes_context(self) -> None:
        """Route includes memory context in decision."""
        router = EnhancedTaskRouter()
        task = make_task()
        experiences = [make_experience()]
        memory = make_mock_memory(experiences=experiences)

        result = router.route(task, memory)

        assert result.context is not None
        assert result.context.experiences == experiences


class TestEnhancedTaskRouterDomainRouting:
    """Tests for domain-based routing."""

    def test_routes_arc_to_evolutionary(self) -> None:
        """Routes ARC domain to evolutionary strategy."""
        router = EnhancedTaskRouter()
        task = make_task_with_domain(domain="arc")
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "evolutionary"

    def test_routes_swe_to_mcts(self) -> None:
        """Routes SWE domain to mcts strategy."""
        router = EnhancedTaskRouter()
        task = make_task_with_domain(domain="swe")
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "mcts"

    def test_routes_unknown_to_default(self) -> None:
        """Routes unknown domain to default strategy."""
        router = EnhancedTaskRouter()
        task = make_task_with_domain(domain="unknown")
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "evolutionary"  # Default

    def test_domain_routing_case_insensitive(self) -> None:
        """Domain routing is case insensitive."""
        router = EnhancedTaskRouter()

        task_arc = make_task_with_domain(domain="ARC")
        task_swe = make_task_with_domain(domain="SWE")
        memory = make_mock_memory()

        assert router.route(task_arc, memory).strategy == "evolutionary"
        assert router.route(task_swe, memory).strategy == "mcts"

    def test_custom_domain_strategies(self) -> None:
        """Custom domain strategies can be configured."""
        config = RouterConfig(arc_strategy="mcts", swe_strategy="evolutionary")
        router = EnhancedTaskRouter(config=config)

        task_arc = make_task_with_domain(domain="arc")
        task_swe = make_task_with_domain(domain="swe")
        memory = make_mock_memory()

        assert router.route(task_arc, memory).strategy == "mcts"
        assert router.route(task_swe, memory).strategy == "evolutionary"

    def test_domain_routing_disabled(self) -> None:
        """Domain routing can be disabled."""
        config = RouterConfig(use_domain_routing=False, default_strategy="direct")
        router = EnhancedTaskRouter(config=config)

        task = make_task_with_domain(domain="arc")
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.strategy == "direct"


class TestEnhancedTaskRouterAdaptRouting:
    """Tests for adapt routing based on similarity."""

    def test_routes_to_adapt_with_high_similarity_and_success(self) -> None:
        """Routes to adapt when similarity >= threshold and success exists."""
        router = EnhancedTaskRouter(config=RouterConfig(similarity_threshold=0.9))

        # Create task and experience with same embedding
        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(
            description="solve this problem",
            embedding=embedding,
        )
        experience = make_experience_with_embedding(
            success=True,
            task_input="solve this problem",  # Same for high text similarity
            embedding=embedding,
        )
        memory = make_mock_memory(experiences=[experience])

        result = router.route(task, memory)

        assert result.strategy == "adapt"

    def test_no_adapt_without_success(self) -> None:
        """Does not route to adapt without successful experience."""
        router = EnhancedTaskRouter()

        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(embedding=embedding)
        experience = make_experience_with_embedding(
            success=False,  # No success
            embedding=embedding,
        )
        memory = make_mock_memory(experiences=[experience])

        result = router.route(task, memory)

        assert result.strategy != "adapt"

    def test_no_adapt_with_low_similarity(self) -> None:
        """Does not route to adapt with low similarity."""
        router = EnhancedTaskRouter(config=RouterConfig(similarity_threshold=0.9))

        # Different embeddings = low similarity
        task = make_task_with_domain(embedding=np.array([1.0, 0.0, 0.0]))
        experience = make_experience_with_embedding(
            success=True,
            embedding=np.array([0.0, 1.0, 0.0]),  # Orthogonal = 0 similarity
        )
        memory = make_mock_memory(experiences=[experience])

        result = router.route(task, memory)

        assert result.strategy != "adapt"


class TestEnhancedTaskRouterStrategyMatch:
    """Tests for strategy-based routing."""

    def test_routes_to_direct_with_strategy_match(self) -> None:
        """Routes to direct when strategy matches task."""
        router = EnhancedTaskRouter()

        # Create task and strategy with overlapping words
        task = make_task_with_domain(description="When grid has symmetry apply rotation")
        strategy = Strategy(
            id="strat-1",
            situation="When grid has symmetry patterns",  # Overlapping words
            suggestion="Check for rotation",
        )
        memory = make_mock_memory(strategies=[strategy])

        result = router.route(task, memory)

        assert result.strategy == "direct"

    def test_no_direct_without_strategy_match(self) -> None:
        """Does not route to direct without strategy match."""
        router = EnhancedTaskRouter()

        task = make_task_with_domain(description="solve complex algorithm")
        strategy = Strategy(
            id="strat-1",
            situation="different topic entirely",  # No overlap
            suggestion="Do something",
        )
        memory = make_mock_memory(strategies=[strategy])

        result = router.route(task, memory)

        # Falls through to domain routing or default
        assert result.strategy != "direct"


class TestEnhancedTaskRouterSimilarity:
    """Tests for similarity calculation."""

    def test_cosine_similarity_identical_vectors(self) -> None:
        """Cosine similarity of identical vectors is 1.0."""
        router = EnhancedTaskRouter()
        vec = np.array([1.0, 2.0, 3.0])

        result = router._cosine_similarity(vec, vec)

        assert result == pytest.approx(1.0, abs=0.001)

    def test_cosine_similarity_orthogonal_vectors(self) -> None:
        """Cosine similarity of orthogonal vectors is 0.0."""
        router = EnhancedTaskRouter()
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])

        result = router._cosine_similarity(vec1, vec2)

        assert result == pytest.approx(0.0, abs=0.001)

    def test_cosine_similarity_zero_vector(self) -> None:
        """Cosine similarity with zero vector is 0.0."""
        router = EnhancedTaskRouter()
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([0.0, 0.0, 0.0])

        result = router._cosine_similarity(vec1, vec2)

        assert result == 0.0

    def test_text_similarity_identical(self) -> None:
        """Text similarity of identical strings is 1.0."""
        router = EnhancedTaskRouter()

        result = router._text_similarity("hello world", "hello world")

        assert result == pytest.approx(1.0, abs=0.001)

    def test_text_similarity_no_overlap(self) -> None:
        """Text similarity with no word overlap is 0.0."""
        router = EnhancedTaskRouter()

        result = router._text_similarity("hello world", "foo bar")

        assert result == pytest.approx(0.0, abs=0.001)

    def test_text_similarity_partial_overlap(self) -> None:
        """Text similarity with partial overlap is between 0 and 1."""
        router = EnhancedTaskRouter()

        result = router._text_similarity("hello world", "hello there")

        # 1 word overlap ("hello") out of 3 unique words
        assert 0.0 < result < 1.0
        assert result == pytest.approx(1 / 3, abs=0.001)

    def test_text_similarity_empty_string(self) -> None:
        """Text similarity with empty string is 0.0."""
        router = EnhancedTaskRouter()

        assert router._text_similarity("", "hello") == 0.0
        assert router._text_similarity("hello", "") == 0.0
        assert router._text_similarity("", "") == 0.0

    def test_text_similarity_case_insensitive(self) -> None:
        """Text similarity is case insensitive."""
        router = EnhancedTaskRouter()

        result = router._text_similarity("Hello World", "HELLO WORLD")

        assert result == pytest.approx(1.0, abs=0.001)

    def test_uses_embedding_when_available(self) -> None:
        """Uses embedding similarity when both have embeddings."""
        router = EnhancedTaskRouter()

        # Create identical embeddings but different text
        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(
            description="completely different text",
            embedding=embedding,
        )
        experience = make_experience_with_embedding(
            task_input="no overlap at all",
            embedding=embedding,
        )

        similarity = router._calculate_similarity(task, experience)

        # Should use embedding (1.0) not text (0.0)
        assert similarity == pytest.approx(1.0, abs=0.001)

    def test_falls_back_to_text_without_embeddings(self) -> None:
        """Falls back to text similarity without embeddings."""
        router = EnhancedTaskRouter()

        task = make_task_with_domain(description="hello world")
        experience = make_experience_with_embedding(
            task_input="hello world",
            embedding=None,
        )

        similarity = router._calculate_similarity(task, experience)

        assert similarity == pytest.approx(1.0, abs=0.001)


class TestEnhancedTaskRouterBudget:
    """Tests for budget estimation."""

    def test_budget_for_adapt(self) -> None:
        """Adapt strategy has low budget."""
        router = EnhancedTaskRouter()

        budget = router._estimate_budget("adapt", 0.0)

        assert budget == 5

    def test_budget_for_direct(self) -> None:
        """Direct strategy has low budget."""
        router = EnhancedTaskRouter()

        budget = router._estimate_budget("direct", 0.0)

        assert budget == 10

    def test_budget_for_evolutionary(self) -> None:
        """Evolutionary strategy has medium budget."""
        router = EnhancedTaskRouter()

        budget = router._estimate_budget("evolutionary", 0.0)

        assert budget == 100

    def test_budget_for_mcts(self) -> None:
        """MCTS strategy has high budget."""
        router = EnhancedTaskRouter()

        budget = router._estimate_budget("mcts", 0.0)

        assert budget == 200

    def test_budget_reduced_for_high_similarity(self) -> None:
        """Budget is reduced for high similarity."""
        router = EnhancedTaskRouter()

        # High similarity (>0.8) = 50% budget
        budget_high = router._estimate_budget("evolutionary", 0.9)
        assert budget_high == 50  # 100 * 0.5

        # Medium similarity (>0.5) = 75% budget
        budget_med = router._estimate_budget("evolutionary", 0.7)
        assert budget_med == 75  # 100 * 0.75

        # Low similarity = full budget
        budget_low = router._estimate_budget("evolutionary", 0.3)
        assert budget_low == 100


class TestEnhancedTaskRouterConfidence:
    """Tests for confidence estimation."""

    def test_confidence_zero_with_empty_memory(self) -> None:
        """Confidence is 0 with empty memory."""
        router = EnhancedTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        assert result.confidence == 0.0

    def test_confidence_increases_with_similarity(self) -> None:
        """Confidence increases with similarity."""
        router = EnhancedTaskRouter()

        # Similar text = higher similarity = higher confidence
        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(
            description="test task",
            embedding=embedding,
        )
        experience = make_experience_with_embedding(
            success=False,
            task_input="test task",
            embedding=embedding,
        )
        memory = make_mock_memory(experiences=[experience])

        result = router.route(task, memory)

        # similarity=1.0 * 0.5 = 0.5 base confidence
        assert result.confidence >= 0.5

    def test_confidence_bonus_for_success(self) -> None:
        """Confidence gets bonus for successful experiences."""
        router = EnhancedTaskRouter()

        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(
            description="test task",
            embedding=embedding,
        )
        experience = make_experience_with_embedding(
            success=True,
            task_input="test task",
            embedding=embedding,
        )
        memory = make_mock_memory(experiences=[experience])

        result = router.route(task, memory)

        # similarity=1.0 * 0.5 + success=0.3 = 0.8
        assert result.confidence >= 0.8

    def test_confidence_bonus_for_strategies(self) -> None:
        """Confidence gets bonus for available strategies."""
        router = EnhancedTaskRouter()
        task = make_task()
        strategies = [make_strategy()]
        memory = make_mock_memory(strategies=strategies)

        result = router.route(task, memory)

        # Has strategies = +0.1 bonus
        assert result.confidence >= 0.1

    def test_confidence_capped_at_1(self) -> None:
        """Confidence is capped at 1.0."""
        router = EnhancedTaskRouter()

        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(
            description="test",
            embedding=embedding,
        )
        experience = make_experience_with_embedding(
            success=True,
            task_input="test",
            embedding=embedding,
        )
        strategies = [make_strategy()]
        memory = make_mock_memory(experiences=[experience], strategies=strategies)

        result = router.route(task, memory)

        assert result.confidence <= 1.0


class TestEnhancedTaskRouterEdgeCases:
    """Tests for edge cases."""

    def test_routing_decision_is_immutable(self) -> None:
        """RoutingDecision is frozen/immutable."""
        router = EnhancedTaskRouter()
        task = make_task()
        memory = make_mock_memory()

        result = router.route(task, memory)

        with pytest.raises((AttributeError, TypeError, ValidationError)):
            result.strategy = "evolutionary"

    def test_multiple_routes_independent(self) -> None:
        """Multiple route calls are independent."""
        router = EnhancedTaskRouter()

        task_arc = make_task_with_domain(domain="arc")
        task_swe = make_task_with_domain(domain="swe")
        memory = make_mock_memory()

        result_arc = router.route(task_arc, memory)
        result_swe = router.route(task_swe, memory)

        assert result_arc.strategy == "evolutionary"
        assert result_swe.strategy == "mcts"

    def test_unknown_strategy_default_budget(self) -> None:
        """Unknown strategy gets default budget."""
        router = EnhancedTaskRouter()

        budget = router._estimate_budget("unknown_strategy", 0.0)

        assert budget == 100  # Default

    def test_empty_experiences_list(self) -> None:
        """Handles empty experiences list."""
        router = EnhancedTaskRouter()
        task = make_task()

        result = router._calculate_max_similarity(task, [])

        assert result == 0.0

    def test_is_similar_enough_threshold(self) -> None:
        """_is_similar_enough uses 0.5 threshold."""
        router = EnhancedTaskRouter()

        embedding = np.array([1.0, 0.0, 0.0])
        task = make_task_with_domain(embedding=embedding)

        # Same embedding = 1.0 similarity >= 0.5
        exp_similar = make_experience_with_embedding(embedding=embedding)
        assert router._is_similar_enough(task, exp_similar)

        # Orthogonal = 0.0 similarity < 0.5
        exp_different = make_experience_with_embedding(
            embedding=np.array([0.0, 1.0, 0.0])
        )
        assert not router._is_similar_enough(task, exp_different)
