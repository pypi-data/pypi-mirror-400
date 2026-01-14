"""Mind Evolution search for ARC-style tasks.

Population-based evolutionary search that:
- Initializes population from memory + novel generation
- Evaluates fitness via environment verification
- Selects elites and generates children via mutation/crossover
- Uses LLM for mutation and crossover operations

Cost: ~100 LLM calls per task (population_size * generations / 2)
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any

from cognitive_core.config import MindEvolutionConfig
from cognitive_core.core.types import Candidate

if TYPE_CHECKING:
    from cognitive_core.core.types import Experience, RoutingDecision, Task
    from cognitive_core.llm.simple import SimpleLLM
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemorySystem

logger = logging.getLogger("cognitive_core.search.mind_evolution")


class MindEvolutionSearch:
    """Mind Evolution search for ARC-style tasks.

    Population-based evolutionary search that:
    - Initializes population from memory + novel generation
    - Evaluates fitness via environment verification
    - Selects elites and generates children via mutation/crossover
    - Uses LLM for mutation and crossover operations

    Example:
        ```python
        search = MindEvolutionSearch(memory=memory, llm=llm)
        candidates = search.search(task, routing, env)
        best = candidates[0]  # Already sorted by fitness
        ```
    """

    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        config: MindEvolutionConfig | None = None,
    ) -> None:
        """Initialize MindEvolutionSearch.

        Args:
            memory: Memory system for querying similar experiences.
            llm: SimpleLLM for mutation and crossover operations.
            config: Configuration for evolutionary search parameters.
        """
        self._memory = memory
        self._llm = llm
        self._config = config or MindEvolutionConfig()

    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Run evolutionary search.

        Algorithm:
        1. Initialize population (50% from memory, 50% novel)
        2. For each generation:
           a. Evaluate fitness for all candidates via env.verify()
           b. Select top 50% as elites
           c. Generate children via mutation/crossover
           d. Replace population
        3. Return best candidates

        Args:
            task: The task to solve.
            routing: Routing decision with strategy and context.
            env: Environment for verification.

        Returns:
            List of candidate solutions, sorted by fitness descending.
        """
        logger.info(
            "MindEvolutionSearch.search started",
            extra={
                "task_id": task.id,
                "population_size": self._config.population_size,
                "generations": self._config.generations,
            },
        )

        # Initialize population
        population = self._initialize_population(task, routing)

        # Run evolution
        for gen in range(self._config.generations):
            logger.debug(
                "Generation started",
                extra={"generation": gen, "population_size": len(population)},
            )

            # Evaluate fitness
            population = self._evaluate_fitness(population, env)

            # Check for success - any candidate with fitness >= 1.0
            successful = [c for c in population if (c.fitness or 0) >= 1.0]
            if successful:
                logger.info(
                    "Found successful candidates, early terminating",
                    extra={
                        "generation": gen,
                        "successful_count": len(successful),
                    },
                )
                return sorted(successful, key=lambda c: c.fitness or 0, reverse=True)

            # Selection - keep top elite_fraction
            elites = self._select_elites(population)

            # Log best fitness this generation
            best_fitness = max((c.fitness or 0) for c in elites) if elites else 0
            logger.debug(
                "Generation completed",
                extra={
                    "generation": gen,
                    "best_fitness": best_fitness,
                    "elite_count": len(elites),
                },
            )

            # Generate children to fill population
            children = self._generate_children(elites, task)

            # Replace population with elites + children
            population = elites + children

        # Final evaluation and return
        population = self._evaluate_fitness(population, env)
        sorted_population = sorted(
            population, key=lambda c: c.fitness or 0, reverse=True
        )

        logger.info(
            "MindEvolutionSearch.search completed",
            extra={
                "task_id": task.id,
                "best_fitness": sorted_population[0].fitness if sorted_population else 0,
                "candidates_returned": len(sorted_population),
            },
        )

        return sorted_population

    def refine(self, candidate: Candidate, feedback: str, task: Task) -> Candidate:
        """Refine via targeted mutation.

        Uses feedback to guide a mutation that addresses specific issues.

        Args:
            candidate: The candidate to refine.
            feedback: Feedback from verification or user.
            task: The original task.

        Returns:
            Refined candidate.
        """
        logger.info(
            "Refining candidate via targeted mutation",
            extra={"task_id": task.id, "source": candidate.source},
        )

        prompt = f"""Given an ARC-style task and feedback on a solution, improve the solution:

Task: {task.description}

Current solution:
{candidate.solution}

Feedback:
{feedback}

Generate an improved solution that addresses the feedback. Return only the improved solution.
"""

        try:
            refined_solution = self._llm.generate(
                prompt, temperature=self._config.mutation_temperature
            )

            return Candidate(
                solution=refined_solution,
                confidence=candidate.confidence * 0.9,
                reasoning=f"Refined based on feedback: {feedback[:100]}",
                source="refined",
                parent_ids=[str(id(candidate))],
            )
        except Exception as e:
            logger.warning(
                "LLM refinement failed",
                extra={"error": str(e)},
            )
            return candidate

    @property
    def name(self) -> str:
        """Name of this search method."""
        return "evolutionary"

    # =========================================================================
    # Population Initialization
    # =========================================================================

    def _initialize_population(
        self, task: Task, routing: RoutingDecision
    ) -> list[Candidate]:
        """Initialize from memory + novel generation.

        Initializes population with:
        - memory_init_fraction from adapted memory experiences
        - Remaining slots filled with novel generations

        Args:
            task: The task to solve.
            routing: Routing decision with context (may contain experiences).

        Returns:
            List of candidates forming the initial population.
        """
        population: list[Candidate] = []
        memory_count = int(self._config.population_size * self._config.memory_init_fraction)

        logger.debug(
            "Initializing population",
            extra={
                "population_size": self._config.population_size,
                "memory_count": memory_count,
            },
        )

        # From memory - adapt similar experiences
        experiences = self._get_experiences(task, routing)
        for exp in experiences[:memory_count]:
            adapted = self._adapt_from_experience(task, exp)
            population.append(adapted)

        logger.debug(
            "Adapted from memory",
            extra={"adapted_count": len(population)},
        )

        # Novel generation to fill remaining
        while len(population) < self._config.population_size:
            novel = self._generate_novel(task)
            population.append(novel)

        logger.debug(
            "Population initialized",
            extra={"final_size": len(population)},
        )

        return population

    def _get_experiences(
        self, task: Task, routing: RoutingDecision
    ) -> list[Experience]:
        """Get experiences from routing context or query memory.

        Args:
            task: The task to find experiences for.
            routing: Routing decision that may contain context.

        Returns:
            List of similar experiences.
        """
        # First check routing context
        if routing.context is not None:
            # Import here to avoid circular imports
            from cognitive_core.protocols.memory import MemoryQueryResult

            if isinstance(routing.context, MemoryQueryResult):
                if routing.context.experiences:
                    logger.debug(
                        "Using experiences from routing context",
                        extra={"count": len(routing.context.experiences)},
                    )
                    return routing.context.experiences

        # Fall back to querying memory directly
        logger.debug("Querying memory for experiences")
        result = self._memory.query(task)
        return result.experiences

    def _adapt_from_experience(self, task: Task, experience: Experience) -> Candidate:
        """Adapt a solution from an experience to the current task.

        Uses LLM to adapt the experience's solution to the new task.

        Args:
            task: The current task.
            experience: The experience with solution to adapt.

        Returns:
            Adapted candidate.
        """
        prompt = f"""Given a similar solved ARC task, adapt the solution for a new task:

Similar Task: {experience.task_input}
Solution: {experience.solution_output}

New Task: {task.description}

Adapt the solution approach for the new task. Return only the adapted solution.
"""

        try:
            adapted = self._llm.generate(
                prompt, temperature=self._config.mutation_temperature
            )
            return Candidate(
                solution=adapted,
                confidence=0.7 if experience.success else 0.4,
                reasoning=f"Adapted from experience {experience.id}",
                source="adapted",
                parent_ids=[experience.id],
            )
        except Exception as e:
            logger.warning(
                "LLM adaptation failed, using original solution",
                extra={"error": str(e), "experience_id": experience.id},
            )
            return Candidate(
                solution=experience.solution_output,
                confidence=0.5,
                reasoning=f"Direct from experience {experience.id} (adaptation failed)",
                source="adapted",
                parent_ids=[experience.id],
            )

    def _generate_novel(self, task: Task) -> Candidate:
        """Generate a novel solution for the task.

        Uses LLM to generate a fresh solution approach.

        Args:
            task: The task to solve.

        Returns:
            Novel candidate.
        """
        prompt = f"""Solve this ARC-style task:

{task.description}

Think about the pattern transformation from input to output grids.
Generate a solution that describes the transformation. Return only the solution.
"""

        try:
            solution = self._llm.generate(
                prompt, temperature=self._config.mutation_temperature + 0.2
            )
            return Candidate(
                solution=solution,
                confidence=0.5,
                reasoning="Novel generation",
                source="generated",
            )
        except Exception as e:
            logger.warning(
                "LLM novel generation failed",
                extra={"error": str(e)},
            )
            return Candidate(
                solution=f"Unable to generate: {e}",
                confidence=0.1,
                reasoning="Generation failed",
                source="generated",
            )

    # =========================================================================
    # Fitness Evaluation
    # =========================================================================

    def _evaluate_fitness(
        self, population: list[Candidate], env: Environment
    ) -> list[Candidate]:
        """Evaluate fitness for all candidates via environment verification.

        Args:
            population: List of candidates to evaluate.
            env: Environment for verification.

        Returns:
            List of candidates with fitness scores set.
        """
        evaluated = []
        for candidate in population:
            # Skip if already evaluated
            if candidate.fitness is not None:
                evaluated.append(candidate)
                continue

            outcome = env.verify(candidate.solution)

            # Create new candidate with fitness set (Candidate is immutable)
            evaluated_candidate = Candidate(
                solution=candidate.solution,
                confidence=candidate.confidence,
                reasoning=candidate.reasoning,
                source=candidate.source,
                fitness=outcome.partial_score if outcome.partial_score is not None else (1.0 if outcome.success else 0.0),
                trajectory=candidate.trajectory,
                parent_ids=candidate.parent_ids,
            )
            evaluated.append(evaluated_candidate)

        return evaluated

    # =========================================================================
    # Selection
    # =========================================================================

    def _select_elites(self, population: list[Candidate]) -> list[Candidate]:
        """Select top candidates as elites.

        Args:
            population: List of evaluated candidates.

        Returns:
            List of elite candidates (top elite_fraction).
        """
        # Sort by fitness descending
        sorted_pop = sorted(population, key=lambda c: c.fitness or 0, reverse=True)

        # Keep top elite_fraction
        elite_count = max(1, int(len(sorted_pop) * self._config.elite_fraction))
        elites = sorted_pop[:elite_count]

        return elites

    # =========================================================================
    # Child Generation (Mutation and Crossover)
    # =========================================================================

    def _generate_children(
        self, elites: list[Candidate], task: Task
    ) -> list[Candidate]:
        """Generate children via mutation and crossover.

        Args:
            elites: Elite candidates to use as parents.
            task: The task being solved.

        Returns:
            List of child candidates.
        """
        children: list[Candidate] = []
        children_needed = self._config.population_size - len(elites)

        while len(children) < children_needed:
            # Decide mutation or crossover
            if random.random() < self._config.crossover_rate and len(elites) >= 2:
                # Crossover
                parent1, parent2 = random.sample(elites, 2)
                child = self._crossover(parent1, parent2, task)
            else:
                # Mutation
                parent = random.choice(elites)
                child = self._mutate(parent, task)

            children.append(child)

        return children

    def _mutate(self, candidate: Candidate, task: Task) -> Candidate:
        """LLM-based mutation.

        Generates a variation of the candidate's solution.

        Args:
            candidate: The candidate to mutate.
            task: The task being solved.

        Returns:
            Mutated candidate.
        """
        prompt = f"""Given an ARC-style task, modify this solution approach:

Task: {task.description}

Current solution:
{candidate.solution}

Generate a variation - make a small but meaningful change while keeping the core idea.
Return only the modified solution.
"""

        try:
            mutated = self._llm.generate(
                prompt, temperature=self._config.mutation_temperature
            )
            return Candidate(
                solution=mutated,
                confidence=candidate.confidence * 0.9,
                reasoning="Mutated from parent",
                source="mutated",
                parent_ids=[str(id(candidate))],
            )
        except Exception as e:
            logger.warning(
                "LLM mutation failed",
                extra={"error": str(e)},
            )
            # Return parent unchanged if mutation fails
            return candidate

    def _crossover(
        self, parent1: Candidate, parent2: Candidate, task: Task
    ) -> Candidate:
        """LLM-based crossover.

        Combines ideas from two parent solutions.

        Args:
            parent1: First parent candidate.
            parent2: Second parent candidate.
            task: The task being solved.

        Returns:
            Crossover child candidate.
        """
        prompt = f"""Combine the best ideas from two solutions:

Task: {task.description}

Solution 1:
{parent1.solution}

Solution 2:
{parent2.solution}

Create a new solution combining the best aspects of both. Return only the combined solution.
"""

        try:
            child_solution = self._llm.generate(
                prompt, temperature=self._config.mutation_temperature
            )
            return Candidate(
                solution=child_solution,
                confidence=(parent1.confidence + parent2.confidence) / 2,
                reasoning="Crossover of two parents",
                source="crossover",
                parent_ids=[str(id(parent1)), str(id(parent2))],
            )
        except Exception as e:
            logger.warning(
                "LLM crossover failed, falling back to mutation",
                extra={"error": str(e)},
            )
            # Fall back to mutating parent1
            return self._mutate(parent1, task)
