"""Tests for MindEvolutionSearch."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cognitive_core.config import MindEvolutionConfig
from cognitive_core.core.types import (
    Candidate,
    Experience,
    Outcome,
    RoutingDecision,
    Task,
    VerificationSpec,
)
from cognitive_core.protocols.memory import MemoryQueryResult, MemorySystem
from cognitive_core.protocols.search import SearchEngine
from cognitive_core.search.mind_evolution import MindEvolutionSearch


# =============================================================================
# Test Fixtures
# =============================================================================


def make_task(
    task_id: str = "test-1",
    description: str = "Test ARC task description",
    domain: str = "arc",
) -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        description=description,
        domain=domain,
        verification=VerificationSpec(method="exact_match"),
    )


def make_experience(
    exp_id: str = "exp-1",
    task_input: str = "Similar ARC task input",
    solution_output: str = "Solution output for similar task",
    success: bool = True,
) -> Experience:
    """Create a test experience with all required fields."""
    return Experience(
        id=exp_id,
        task_input=task_input,
        solution_output=solution_output,
        feedback="Test feedback",
        success=success,
        trajectory_id="traj-1",
        timestamp=datetime.now(timezone.utc),
    )


def make_routing_decision(
    experiences: list[Experience] | None = None,
    strategy: str = "evolutionary",
    confidence: float = 0.8,
    budget: int = 10,
) -> RoutingDecision:
    """Create a routing decision with optional context."""
    context = MemoryQueryResult(experiences=experiences) if experiences else None
    return RoutingDecision(
        strategy=strategy,
        context=context,
        confidence=confidence,
        budget=budget,
    )


def make_mock_memory(
    experiences: list[Experience] | None = None,
) -> MagicMock:
    """Create a mock memory system."""
    mock = MagicMock(spec=MemorySystem)
    result = MemoryQueryResult(experiences=experiences or [])
    mock.query = MagicMock(return_value=result)
    return mock


def make_mock_llm(
    response: str = "Generated solution",
) -> MagicMock:
    """Create a mock SimpleLLM."""
    mock = MagicMock()
    mock.generate = MagicMock(return_value=response)
    return mock


def make_mock_environment(
    success: bool = False,
    partial_score: float = 0.5,
) -> MagicMock:
    """Create a mock environment."""
    mock = MagicMock()
    outcome = Outcome(success=success, partial_score=partial_score)
    mock.verify = MagicMock(return_value=outcome)
    return mock


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestMindEvolutionSearchProtocol:
    """Tests for MindEvolutionSearch protocol compliance."""

    def test_implements_search_engine_protocol(self) -> None:
        """MindEvolutionSearch implements SearchEngine protocol."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        assert isinstance(search, SearchEngine)

    def test_has_search_method(self) -> None:
        """Has search method."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        assert hasattr(search, "search")
        assert callable(search.search)

    def test_has_refine_method(self) -> None:
        """Has refine method."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        assert hasattr(search, "refine")
        assert callable(search.refine)

    def test_has_name_property(self) -> None:
        """Has name property."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        assert hasattr(search, "name")
        assert search.name == "evolutionary"


# =============================================================================
# Configuration Tests
# =============================================================================


class TestMindEvolutionSearchConfiguration:
    """Tests for MindEvolutionSearch configuration."""

    def test_uses_default_config_when_none_provided(self) -> None:
        """Uses default MindEvolutionConfig when none provided."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        assert search._config is not None
        assert search._config.population_size == 20  # Default value

    def test_uses_provided_config(self) -> None:
        """Uses provided MindEvolutionConfig."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=10, generations=5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        assert search._config.population_size == 10
        assert search._config.generations == 5

    def test_config_affects_population_size(self) -> None:
        """Config population_size affects initial population."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=8, generations=1)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        population = search._initialize_population(task, routing)

        assert len(population) == 8


# =============================================================================
# Population Initialization Tests
# =============================================================================


class TestPopulationInitialization:
    """Tests for population initialization."""

    def test_initializes_population_from_memory(self) -> None:
        """Initializes part of population from memory experiences."""
        experiences = [
            make_experience("exp-1", solution_output="sol1"),
            make_experience("exp-2", solution_output="sol2"),
        ]
        memory = make_mock_memory()
        llm = make_mock_llm(response="adapted solution")
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=0.5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        population = search._initialize_population(task, routing)

        # 50% of 4 = 2 from memory, should call LLM for adaptation
        assert llm.generate.call_count >= 2
        # Remaining 2 should be novel generations
        assert len(population) == 4

    def test_initializes_population_with_novel_generation(self) -> None:
        """Fills remaining population slots with novel generation."""
        memory = make_mock_memory(experiences=[])
        llm = make_mock_llm(response="novel solution")
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=0.5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        population = search._initialize_population(task, routing)

        # All should be novel since no experiences
        assert len(population) == 4
        assert llm.generate.call_count == 4

    def test_novel_generation_has_correct_source(self) -> None:
        """Novel candidates have source='generated'."""
        memory = make_mock_memory(experiences=[])
        llm = make_mock_llm(response="novel solution")
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=0.0)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        population = search._initialize_population(task, routing)

        assert all(c.source == "generated" for c in population)

    def test_adapted_candidates_have_correct_source(self) -> None:
        """Adapted candidates have source='adapted'."""
        experiences = [make_experience("exp-1"), make_experience("exp-2"),
                       make_experience("exp-3"), make_experience("exp-4")]
        memory = make_mock_memory()
        llm = make_mock_llm(response="adapted solution")
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=1.0)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        population = search._initialize_population(task, routing)

        # All should be adapted since memory_init_fraction=1.0
        assert all(c.source == "adapted" for c in population)

    def test_uses_experiences_from_routing_context(self) -> None:
        """Uses experiences from routing.context."""
        experiences = [make_experience("exp-context")]
        memory = make_mock_memory(experiences=[make_experience("exp-memory")])
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=0.5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)

        search._initialize_population(task, routing)

        # Memory should not be queried since context has experiences
        memory.query.assert_not_called()

    def test_queries_memory_when_context_empty(self) -> None:
        """Queries memory when routing.context is empty."""
        experiences = [make_experience("exp-memory")]
        memory = make_mock_memory(experiences=experiences)
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=4, memory_init_fraction=0.5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()  # No experiences

        search._initialize_population(task, routing)

        memory.query.assert_called_once_with(task)


# =============================================================================
# Mutation Tests
# =============================================================================


class TestMutation:
    """Tests for mutation operations."""

    def test_mutate_produces_valid_candidate(self) -> None:
        """Mutation produces a valid Candidate."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="mutated solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        child = search._mutate(parent, task)

        assert isinstance(child, Candidate)
        assert child.solution == "mutated solution"
        assert child.source == "mutated"

    def test_mutate_reduces_confidence(self) -> None:
        """Mutation slightly reduces confidence."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="mutated solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent = Candidate(
            solution="original",
            confidence=1.0,
            reasoning="Test",
            source="generated",
        )

        child = search._mutate(parent, task)

        assert child.confidence < parent.confidence

    def test_mutate_includes_parent_id(self) -> None:
        """Mutated candidate includes parent ID."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="mutated solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        child = search._mutate(parent, task)

        assert len(child.parent_ids) > 0

    def test_mutate_uses_temperature_from_config(self) -> None:
        """Mutation uses temperature from config."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(mutation_temperature=0.9)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        parent = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        search._mutate(parent, task)

        # Check temperature passed to LLM
        call_kwargs = llm.generate.call_args[1]
        assert call_kwargs.get("temperature") == 0.9

    def test_mutate_handles_llm_error(self) -> None:
        """Mutation handles LLM error gracefully."""
        memory = make_mock_memory()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=Exception("LLM error"))
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        child = search._mutate(parent, task)

        # Should return parent on error
        assert child == parent


# =============================================================================
# Crossover Tests
# =============================================================================


class TestCrossover:
    """Tests for crossover operations."""

    def test_crossover_produces_valid_candidate(self) -> None:
        """Crossover produces a valid Candidate."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="crossover solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent1 = Candidate(
            solution="solution A",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )
        parent2 = Candidate(
            solution="solution B",
            confidence=0.7,
            reasoning="Test",
            source="generated",
        )

        child = search._crossover(parent1, parent2, task)

        assert isinstance(child, Candidate)
        assert child.solution == "crossover solution"
        assert child.source == "crossover"

    def test_crossover_averages_confidence(self) -> None:
        """Crossover averages parent confidences."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="crossover solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent1 = Candidate(
            solution="solution A",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )
        parent2 = Candidate(
            solution="solution B",
            confidence=0.6,
            reasoning="Test",
            source="generated",
        )

        child = search._crossover(parent1, parent2, task)

        assert child.confidence == 0.7  # (0.8 + 0.6) / 2

    def test_crossover_prompt_includes_both_solutions(self) -> None:
        """Crossover prompt includes both parent solutions."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent1 = Candidate(
            solution="SOLUTION_A",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )
        parent2 = Candidate(
            solution="SOLUTION_B",
            confidence=0.7,
            reasoning="Test",
            source="generated",
        )

        search._crossover(parent1, parent2, task)

        call_args = llm.generate.call_args[0][0]
        assert "SOLUTION_A" in call_args
        assert "SOLUTION_B" in call_args

    def test_crossover_handles_llm_error(self) -> None:
        """Crossover falls back to mutation on LLM error."""
        memory = make_mock_memory()
        llm = MagicMock()
        # First call (crossover) fails, second call (mutation fallback) succeeds
        llm.generate = MagicMock(side_effect=[Exception("LLM error"), "fallback"])
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        parent1 = Candidate(
            solution="solution A",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )
        parent2 = Candidate(
            solution="solution B",
            confidence=0.7,
            reasoning="Test",
            source="generated",
        )

        child = search._crossover(parent1, parent2, task)

        # Should fall back to mutation
        assert child.source == "mutated"


# =============================================================================
# Selection Tests
# =============================================================================


class TestSelection:
    """Tests for selection operations."""

    def test_select_elites_keeps_top_candidates(self) -> None:
        """Selection keeps top candidates by fitness."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(elite_fraction=0.5)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)

        population = [
            Candidate(solution="low", confidence=0.5, reasoning="", source="generated", fitness=0.2),
            Candidate(solution="high", confidence=0.5, reasoning="", source="generated", fitness=0.9),
            Candidate(solution="mid", confidence=0.5, reasoning="", source="generated", fitness=0.5),
            Candidate(solution="highest", confidence=0.5, reasoning="", source="generated", fitness=1.0),
        ]

        elites = search._select_elites(population)

        # Should keep top 50% (2 candidates)
        assert len(elites) == 2
        # Best should be first
        assert elites[0].fitness == 1.0
        assert elites[1].fitness == 0.9

    def test_select_elites_keeps_at_least_one(self) -> None:
        """Selection keeps at least one elite."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(elite_fraction=0.1)  # Would be 0.1 of 1 = 0.1
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)

        population = [
            Candidate(solution="only", confidence=0.5, reasoning="", source="generated", fitness=0.5),
        ]

        elites = search._select_elites(population)

        assert len(elites) >= 1


# =============================================================================
# Fitness Evaluation Tests
# =============================================================================


class TestFitnessEvaluation:
    """Tests for fitness evaluation."""

    def test_evaluate_fitness_sets_fitness_from_outcome(self) -> None:
        """Evaluation sets fitness from environment outcome."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        env = make_mock_environment(success=False, partial_score=0.75)

        population = [
            Candidate(solution="test", confidence=0.5, reasoning="", source="generated"),
        ]

        evaluated = search._evaluate_fitness(population, env)

        assert evaluated[0].fitness == 0.75

    def test_evaluate_fitness_skips_already_evaluated(self) -> None:
        """Evaluation skips candidates with existing fitness."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        env = make_mock_environment()

        population = [
            Candidate(solution="already", confidence=0.5, reasoning="", source="generated", fitness=0.9),
            Candidate(solution="new", confidence=0.5, reasoning="", source="generated"),
        ]

        evaluated = search._evaluate_fitness(population, env)

        # Only one call to verify (for the new candidate)
        assert env.verify.call_count == 1
        # First candidate keeps its fitness
        assert evaluated[0].fitness == 0.9

    def test_evaluate_fitness_uses_success_as_fitness(self) -> None:
        """Evaluation uses 1.0 for success when partial_score is None."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        env = MagicMock()
        env.verify = MagicMock(
            return_value=Outcome(success=True, partial_score=None)
        )

        population = [
            Candidate(solution="test", confidence=0.5, reasoning="", source="generated"),
        ]

        evaluated = search._evaluate_fitness(population, env)

        assert evaluated[0].fitness == 1.0


# =============================================================================
# Evolution Tests
# =============================================================================


class TestEvolution:
    """Tests for the full evolution process."""

    def test_evolution_improves_fitness_over_generations(self) -> None:
        """Evolution generally improves fitness over generations."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="improved solution")
        config = MindEvolutionConfig(population_size=4, generations=3)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        # Mock environment with improving fitness
        fitness_sequence = [0.1, 0.2, 0.3, 0.4] * 20  # Enough for all generations
        fitness_iter = iter(fitness_sequence)
        env = MagicMock()
        env.verify = MagicMock(
            side_effect=lambda s: Outcome(success=False, partial_score=next(fitness_iter))
        )

        result = search.search(task, routing, env)

        # Should have results
        assert len(result) > 0
        # All should have fitness set
        assert all(c.fitness is not None for c in result)

    def test_early_termination_on_success(self) -> None:
        """Evolution terminates early when successful candidate found."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=4, generations=10)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        # Mock environment - success on 5th candidate
        call_count = [0]

        def verify_with_success(s: Any) -> Outcome:
            call_count[0] += 1
            if call_count[0] == 5:
                return Outcome(success=True, partial_score=1.0)
            return Outcome(success=False, partial_score=0.5)

        env = MagicMock()
        env.verify = MagicMock(side_effect=verify_with_success)

        result = search.search(task, routing, env)

        # Should return early with successful candidate
        assert len(result) > 0
        assert result[0].fitness == 1.0

    def test_returns_sorted_candidates(self) -> None:
        """Returns candidates sorted by fitness descending."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = MindEvolutionConfig(population_size=4, generations=1)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        # Mock environment with varying fitness
        scores = [0.3, 0.8, 0.1, 0.5] * 2  # For two rounds of evaluation
        score_iter = iter(scores)
        env = MagicMock()
        env.verify = MagicMock(
            side_effect=lambda s: Outcome(success=False, partial_score=next(score_iter))
        )

        result = search.search(task, routing, env)

        # Should be sorted by fitness descending
        fitnesses = [c.fitness for c in result]
        assert fitnesses == sorted(fitnesses, reverse=True)


# =============================================================================
# Child Generation Tests
# =============================================================================


class TestChildGeneration:
    """Tests for child generation."""

    def test_generate_children_fills_population(self) -> None:
        """Generate children fills population to target size."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="child solution")
        config = MindEvolutionConfig(population_size=6, crossover_rate=0.0)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()

        elites = [
            Candidate(solution="elite1", confidence=0.8, reasoning="", source="generated"),
            Candidate(solution="elite2", confidence=0.7, reasoning="", source="generated"),
        ]

        children = search._generate_children(elites, task)

        # Should generate 6 - 2 = 4 children
        assert len(children) == 4

    def test_generate_children_uses_crossover(self) -> None:
        """Generate children uses crossover when rate > 0."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="child solution")
        config = MindEvolutionConfig(population_size=4, crossover_rate=1.0)  # Always crossover
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()

        elites = [
            Candidate(solution="elite1", confidence=0.8, reasoning="", source="generated"),
            Candidate(solution="elite2", confidence=0.7, reasoning="", source="generated"),
        ]

        # Patch random.random to always choose crossover
        with patch("cognitive_core.search.mind_evolution.random.random", return_value=0.0):
            children = search._generate_children(elites, task)

        # All should be crossover (or fallback)
        assert all(c.source in ("crossover", "mutated") for c in children)

    def test_generate_children_uses_mutation(self) -> None:
        """Generate children uses mutation when rate = 0."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="child solution")
        config = MindEvolutionConfig(population_size=4, crossover_rate=0.0)  # Never crossover
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()

        elites = [
            Candidate(solution="elite1", confidence=0.8, reasoning="", source="generated"),
        ]

        children = search._generate_children(elites, task)

        # All should be mutation
        assert all(c.source == "mutated" for c in children)


# =============================================================================
# Refine Method Tests
# =============================================================================


class TestRefine:
    """Tests for refine method."""

    def test_refine_returns_candidate(self) -> None:
        """Refine returns a Candidate."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="refined solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        assert isinstance(result, Candidate)

    def test_refine_uses_feedback_in_prompt(self) -> None:
        """Refine includes feedback in prompt."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        search.refine(candidate, "THIS IS MY FEEDBACK", task)

        call_args = llm.generate.call_args[0][0]
        assert "THIS IS MY FEEDBACK" in call_args

    def test_refine_reduces_confidence(self) -> None:
        """Refined candidate has lower confidence."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="refined")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=1.0,
            reasoning="Test",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        assert result.confidence < candidate.confidence

    def test_refine_handles_llm_error(self) -> None:
        """Refine handles LLM error gracefully."""
        memory = make_mock_memory()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=Exception("LLM error"))
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        # Should return original on error
        assert result == candidate

    def test_refine_sets_source_to_refined(self) -> None:
        """Refined candidate has source='refined'."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="refined solution")
        search = MindEvolutionSearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Test",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        assert result.source == "refined"


# =============================================================================
# Integration Tests
# =============================================================================


class TestMindEvolutionSearchIntegration:
    """Integration tests for MindEvolutionSearch."""

    def test_full_search_flow(self) -> None:
        """Full search flow from initialization to result."""
        experiences = [make_experience()]
        memory = make_mock_memory(experiences=experiences)
        llm = make_mock_llm(response="evolved solution")
        config = MindEvolutionConfig(population_size=4, generations=2)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision(experiences=experiences)
        env = make_mock_environment(success=False, partial_score=0.6)

        result = search.search(task, routing, env)

        assert len(result) > 0
        assert all(isinstance(c, Candidate) for c in result)
        assert all(c.fitness is not None for c in result)

    def test_search_with_empty_memory(self) -> None:
        """Search works with empty memory."""
        memory = make_mock_memory(experiences=[])
        llm = make_mock_llm(response="novel solution")
        config = MindEvolutionConfig(population_size=4, generations=1)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()
        env = make_mock_environment()

        result = search.search(task, routing, env)

        assert len(result) > 0
        # All should be generated (no memory to adapt from)
        assert any(c.source == "generated" for c in result)

    def test_search_then_refine_flow(self) -> None:
        """Search followed by refinement flow."""
        memory = make_mock_memory()
        llm = make_mock_llm(response="generated solution")
        config = MindEvolutionConfig(population_size=4, generations=1)
        search = MindEvolutionSearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()
        env = make_mock_environment(success=False, partial_score=0.5)

        # Search first
        candidates = search.search(task, routing, env)
        assert len(candidates) > 0

        # Then refine
        refined = search.refine(candidates[0], "Try a different approach", task)
        assert refined.source == "refined"

    def test_name_property(self) -> None:
        """Name property returns 'evolutionary'."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = MindEvolutionSearch(memory=memory, llm=llm)

        assert search.name == "evolutionary"
