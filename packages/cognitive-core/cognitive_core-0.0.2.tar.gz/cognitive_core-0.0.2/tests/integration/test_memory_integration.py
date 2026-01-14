"""Integration tests for Phase 3 memory implementations."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest

from cognitive_core.core.types import (
    CodeConcept,
    Outcome,
    Step,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.memory.concepts import ChromaConceptLibrary
from cognitive_core.memory.experience import ChromaExperienceMemory
from cognitive_core.memory.primitives import ARCPrimitiveLoader, SWEPrimitiveLoader
from cognitive_core.memory.storage import ChromaVectorStore
from cognitive_core.memory.strategy_bank import ChromaStrategyBank
from cognitive_core.memory.strategies import EMASuccessUpdater, SimpleAverageUpdater
from cognitive_core.memory.system import MemorySystemImpl
from cognitive_core.protocols.memory import MemoryQueryResult

if TYPE_CHECKING:
    from tests.integration.conftest import DeterministicEmbedder, SimpleStrategyAbstractor


class TestMemoryIntegration:
    """End-to-end integration tests for memory system."""

    def test_store_and_retrieve_experience(
        self,
        full_memory_system: MemorySystemImpl,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Store trajectory, retrieve by similar task."""
        # Store the trajectory
        result = full_memory_system.store(sample_success_trajectory)

        # Verify experience was stored
        assert "experience_id" in result

        # Query with similar task
        query_result = full_memory_system.query(sample_similar_task, k=5)

        # Should retrieve the stored experience
        assert len(query_result.experiences) >= 1
        assert query_result.experiences[0].success is True

    def test_store_success_creates_strategy(
        self,
        full_memory_system: MemorySystemImpl,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Successful trajectory creates strategy."""
        # Store successful trajectory
        result = full_memory_system.store(sample_success_trajectory)

        # Verify strategy was created
        assert "strategy_id" in result

        # Query strategies
        query_result = full_memory_system.query(sample_similar_task, k=5)

        # Should have at least one strategy
        assert len(query_result.strategies) >= 1

    def test_store_failure_no_strategy(
        self,
        full_memory_system: MemorySystemImpl,
        sample_failure_trajectory: Trajectory,
    ) -> None:
        """Failed trajectory doesn't create strategy."""
        # Store failed trajectory
        result = full_memory_system.store(sample_failure_trajectory)

        # Should have experience but no strategy
        assert "experience_id" in result
        assert "strategy_id" not in result

    def test_parallel_query_returns_all_types(
        self,
        full_memory_system: MemorySystemImpl,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Query all components in parallel returns combined results."""
        # Store some data first
        full_memory_system.store(sample_success_trajectory)

        # Query all components
        result = full_memory_system.query(sample_similar_task, k=5)

        # Should return MemoryQueryResult with all components
        assert isinstance(result, MemoryQueryResult)
        assert hasattr(result, "experiences")
        assert hasattr(result, "concepts")
        assert hasattr(result, "strategies")

        # Experiences should have been stored
        assert len(result.experiences) >= 1

        # Concepts should include primitives (from ARC loader)
        assert len(result.concepts) >= 1

        # Strategies should exist from successful trajectory
        assert len(result.strategies) >= 1

    def test_concept_search_includes_primitives(
        self,
        concept_library: ChromaConceptLibrary,
        sample_different_task: Task,
    ) -> None:
        """Concept search returns primitives."""
        # Search for ARC-related concepts (should find primitives)
        concepts = asyncio.run(
            concept_library.search("rotate grid 90 degrees", k=5)
        )

        # Should find ARC primitives
        assert len(concepts) >= 1

        # At least one should be a primitive (arc_rotate_90)
        primitive_found = any(c.source == "primitive" for c in concepts)
        assert primitive_found

    def test_experience_memory_stores_both_success_and_failure(
        self,
        experience_memory: ChromaExperienceMemory,
        sample_success_trajectory: Trajectory,
        sample_failure_trajectory: Trajectory,
    ) -> None:
        """Experience memory stores both successful and failed trajectories."""
        # Store both trajectories
        success_id = experience_memory.store(sample_success_trajectory)
        failure_id = experience_memory.store(sample_failure_trajectory)

        # Both should have IDs
        assert success_id is not None
        assert failure_id is not None

        # Memory should have both
        assert len(experience_memory) == 2

        # Can retrieve both
        success_exp = experience_memory.get(success_id)
        failure_exp = experience_memory.get(failure_id)

        assert success_exp is not None
        assert success_exp.success is True

        assert failure_exp is not None
        assert failure_exp.success is False

    def test_strategy_bank_only_stores_success(
        self,
        strategy_bank: ChromaStrategyBank,
        sample_success_trajectory: Trajectory,
        sample_failure_trajectory: Trajectory,
    ) -> None:
        """Strategy bank only stores successful trajectories."""
        # Try to write both
        success_strategy = asyncio.run(
            strategy_bank.write(sample_success_trajectory)
        )
        failure_strategy = asyncio.run(
            strategy_bank.write(sample_failure_trajectory)
        )

        # Only success should create strategy
        assert success_strategy is not None
        assert failure_strategy is None

        # Bank should have one strategy
        assert len(strategy_bank) == 1

    def test_multiple_store_and_query_cycles(
        self,
        full_memory_system: MemorySystemImpl,
    ) -> None:
        """Multiple store/query cycles work correctly."""
        # Create multiple trajectories
        for i in range(5):
            trajectory = Trajectory(
                task=Task(
                    id=f"task-{i}",
                    domain="swe",
                    description=f"Fix bug number {i} in the codebase",
                    verification=VerificationSpec(method="test_suite"),
                ),
                steps=[
                    Step(
                        thought=f"Working on bug {i}",
                        action=f"fix_bug({i})",
                        observation="Bug fixed",
                    )
                ],
                outcome=Outcome(success=True),
                agent_id="test-agent",
                timestamp=datetime.now(timezone.utc),
            )
            full_memory_system.store(trajectory)

        # Query should return multiple experiences
        query_task = Task(
            id="query-task",
            domain="swe",
            description="Fix a bug in the system",
            verification=VerificationSpec(method="test_suite"),
        )
        result = full_memory_system.query(query_task, k=5)

        # Should have 5 experiences
        assert len(result.experiences) == 5


class TestAblationConfigurations:
    """Test various component combinations for ablation studies."""

    def test_experience_only(
        self,
        experience_memory: ChromaExperienceMemory,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Memory system with only ExperienceMemory."""
        system = MemorySystemImpl(experience=experience_memory)

        # Store
        result = system.store(sample_success_trajectory)
        assert "experience_id" in result
        assert "strategy_id" not in result

        # Query
        query_result = system.query(sample_similar_task, k=5)
        assert len(query_result.experiences) >= 1
        assert len(query_result.concepts) == 0
        assert len(query_result.strategies) == 0

    def test_concepts_only(
        self,
        concept_library: ChromaConceptLibrary,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Memory system with only ConceptLibrary."""
        system = MemorySystemImpl(concepts=concept_library)

        # Store (should not store anything since ConceptLibrary doesn't store trajectories)
        result = system.store(sample_success_trajectory)
        assert "experience_id" not in result
        assert "strategy_id" not in result

        # Query (should still find primitives)
        query_result = system.query(sample_similar_task, k=5)
        assert len(query_result.experiences) == 0
        assert len(query_result.concepts) >= 1  # From primitives
        assert len(query_result.strategies) == 0

    def test_strategies_only(
        self,
        strategy_bank: ChromaStrategyBank,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Memory system with only StrategyBank."""
        system = MemorySystemImpl(strategies=strategy_bank)

        # Store
        result = system.store(sample_success_trajectory)
        assert "experience_id" not in result
        assert "strategy_id" in result

        # Query
        query_result = system.query(sample_similar_task, k=5)
        assert len(query_result.experiences) == 0
        assert len(query_result.concepts) == 0
        assert len(query_result.strategies) >= 1

    def test_no_components(
        self,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Memory system with no components (edge case)."""
        system = MemorySystemImpl()

        # Store should return empty result
        result = system.store(sample_success_trajectory)
        assert result == {}

        # Query should return empty result
        query_result = system.query(sample_similar_task, k=5)
        assert query_result.is_empty()

    def test_experience_and_strategies_no_concepts(
        self,
        experience_memory: ChromaExperienceMemory,
        strategy_bank: ChromaStrategyBank,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Memory system with experience and strategies but no concepts."""
        system = MemorySystemImpl(
            experience=experience_memory,
            strategies=strategy_bank,
        )

        # Store
        result = system.store(sample_success_trajectory)
        assert "experience_id" in result
        assert "strategy_id" in result

        # Query
        query_result = system.query(sample_similar_task, k=5)
        assert len(query_result.experiences) >= 1
        assert len(query_result.concepts) == 0
        assert len(query_result.strategies) >= 1


class TestStrategySwapping:
    """Test different strategy implementations."""

    def test_ema_vs_simple_average_updater(
        self,
    ) -> None:
        """Compare EMA vs SimpleAverage success rate updaters."""
        ema = EMASuccessUpdater(alpha=0.3)
        simple = SimpleAverageUpdater()

        # Start with same initial state
        ema_rate, ema_count = 0.5, 0
        simple_rate, simple_count = 0.5, 0

        # Apply same sequence of updates
        updates = [True, True, False, True, False, True, True, True]

        for success in updates:
            ema_rate, ema_count = ema.update(ema_rate, ema_count, success)
            simple_rate, simple_count = simple.update(simple_rate, simple_count, success)

        # Both should have processed same number of updates
        assert ema_count == simple_count == 8

        # Simple average should be 6/8 = 0.75
        assert abs(simple_rate - 0.75) < 0.01

        # EMA will be different (more recent weighted)
        assert ema_rate != simple_rate

    def test_arc_vs_swe_primitives(
        self,
    ) -> None:
        """Compare ARC vs SWE primitive loaders."""
        arc = ARCPrimitiveLoader()
        swe = SWEPrimitiveLoader()

        arc_primitives = arc.load()
        swe_primitives = swe.load()

        # Both should load primitives
        assert len(arc_primitives) > 0
        assert len(swe_primitives) > 0

        # All ARC primitives should have arc_ prefix
        for concept_id in arc_primitives:
            assert concept_id.startswith("arc_")

        # All SWE primitives should have swe_ prefix
        for concept_id in swe_primitives:
            assert concept_id.startswith("swe_")

        # No overlap between the two
        arc_ids = set(arc_primitives.keys())
        swe_ids = set(swe_primitives.keys())
        assert arc_ids.isdisjoint(swe_ids)


class TestConceptLibraryWithDifferentLoaders:
    """Test ConceptLibrary with different primitive loaders."""

    def test_arc_primitives_searchable(
        self,
        embedder: "DeterministicEmbedder",
        ephemeral_chroma,
    ) -> None:
        """ARC primitives are searchable."""
        # Create isolated vector store for this test
        collection = ephemeral_chroma.create_collection(f"arc_test_{uuid.uuid4().hex[:8]}")
        vector_store = ChromaVectorStore(collection=collection)

        library = ChromaConceptLibrary(
            embedder=embedder,
            vector_store=vector_store,
            primitive_loader=ARCPrimitiveLoader(),
        )

        # Search for rotation-related concepts
        # Note: k=15 to cover all ARC primitives since DeterministicEmbedder
        # uses hash-based embeddings without semantic similarity
        concepts = asyncio.run(library.search("rotate grid", k=15))

        # Should find primitives (search includes both primitives and learned)
        assert len(concepts) >= 1

        # At least one should contain rotation-related terms
        rotation_found = any(
            "rotate" in c.name.lower() or "rotate" in c.description.lower()
            for c in concepts
        )
        assert rotation_found

    def test_swe_primitives_searchable(
        self,
        embedder: "DeterministicEmbedder",
        ephemeral_chroma,
    ) -> None:
        """SWE primitives are searchable."""
        collection = ephemeral_chroma.create_collection(f"swe_{uuid.uuid4().hex[:8]}")
        vector_store = ChromaVectorStore(collection=collection)

        library = ChromaConceptLibrary(
            embedder=embedder,
            vector_store=vector_store,
            primitive_loader=SWEPrimitiveLoader(),
        )

        # Search for file-related concepts
        # Note: k=15 to cover all SWE primitives since DeterministicEmbedder
        # uses hash-based embeddings without semantic similarity
        concepts = asyncio.run(library.search("read file", k=15))

        # Should find file primitives
        assert len(concepts) >= 1
        file_found = any("file" in c.name.lower() for c in concepts)
        assert file_found


class TestExperienceMemoryPruning:
    """Test experience memory pruning functionality."""

    def test_prune_by_max_age(
        self,
        experience_memory: ChromaExperienceMemory,
        sample_success_trajectory: Trajectory,
    ) -> None:
        """Prune experiences older than max_age_days."""
        # Store a trajectory
        experience_memory.store(sample_success_trajectory)
        assert len(experience_memory) == 1

        # Prune with very short max age (should not affect recent experience)
        removed = experience_memory.prune({"max_age_days": 1})
        assert removed == 0
        assert len(experience_memory) == 1

    def test_prune_failures(
        self,
        experience_memory: ChromaExperienceMemory,
        sample_success_trajectory: Trajectory,
        sample_failure_trajectory: Trajectory,
    ) -> None:
        """Prune failed experiences with min_success_rate > 0."""
        # Store both trajectories
        experience_memory.store(sample_success_trajectory)
        experience_memory.store(sample_failure_trajectory)
        assert len(experience_memory) == 2

        # Prune failures
        removed = experience_memory.prune({"min_success_rate": 0.5})
        assert removed == 1
        assert len(experience_memory) == 1


class TestStrategyBankStatsUpdates:
    """Test strategy bank statistics updates."""

    def test_update_stats_affects_retrieval(
        self,
        strategy_bank: ChromaStrategyBank,
        sample_success_trajectory: Trajectory,
        sample_similar_task: Task,
    ) -> None:
        """Updating stats affects strategy retrieval ranking."""
        # Create a strategy
        strategy = asyncio.run(strategy_bank.write(sample_success_trajectory))
        assert strategy is not None

        # Get initial success rate
        initial_strategy = asyncio.run(strategy_bank.get(strategy.id))
        initial_rate = initial_strategy.success_rate

        # Update with successes
        for _ in range(5):
            asyncio.run(strategy_bank.update_stats(strategy.id, success=True))

        # Get updated strategy
        updated_strategy = asyncio.run(strategy_bank.get(strategy.id))

        # Success rate should have increased
        assert updated_strategy.success_rate > initial_rate
