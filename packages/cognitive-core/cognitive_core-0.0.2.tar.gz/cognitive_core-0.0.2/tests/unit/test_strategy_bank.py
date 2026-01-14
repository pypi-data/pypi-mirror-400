"""Tests for ChromaStrategyBank implementation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from cognitive_core.core.types import Outcome, Step, Strategy, Task, Trajectory, VerificationSpec
from cognitive_core.memory.storage import QueryResult
from cognitive_core.memory.strategies.strategy_bank import (
    EMASuccessUpdater,
    SimpleAverageUpdater,
)
from cognitive_core.memory.strategy_bank import ChromaStrategyBank

if TYPE_CHECKING:
    pass


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_embedder() -> MagicMock:
    """Create a mock EmbeddingProvider."""
    embedder = MagicMock()
    embedder.encode.return_value = np.array([0.1, 0.2, 0.3] * 128)  # 384 dimensions
    embedder.dimension = 384
    embedder.model_name = "mock-embedder"
    return embedder


@pytest.fixture
def mock_vector_store() -> AsyncMock:
    """Create a mock VectorStore."""
    store = AsyncMock()
    store.add = AsyncMock()
    store.query = AsyncMock(
        return_value=QueryResult(ids=[], distances=[], metadatas=[], documents=[])
    )
    store.get = AsyncMock(return_value=[])
    store.delete = AsyncMock()
    store.count = AsyncMock(return_value=0)
    return store


@pytest.fixture
def mock_abstractor() -> AsyncMock:
    """Create a mock StrategyAbstractor."""
    abstractor = AsyncMock()
    abstractor.abstract = AsyncMock(return_value=None)
    return abstractor


@pytest.fixture
def strategy_bank(
    mock_embedder: MagicMock,
    mock_vector_store: AsyncMock,
    mock_abstractor: AsyncMock,
) -> ChromaStrategyBank:
    """Create a ChromaStrategyBank with mock dependencies."""
    return ChromaStrategyBank(
        embedder=mock_embedder,
        vector_store=mock_vector_store,
        abstractor=mock_abstractor,
    )


@pytest.fixture
def successful_trajectory() -> Trajectory:
    """Create a successful trajectory for testing."""
    task = Task(
        id="task-001",
        domain="test",
        description="Fix the authentication bug",
        context={},
        verification=VerificationSpec(method="test_suite"),
    )
    step = Step(
        thought="I need to check the auth function",
        action="Read",
        observation="Found the bug",
    )
    outcome = Outcome(success=True, partial_score=1.0)
    return Trajectory(
        task=task,
        steps=[step],
        outcome=outcome,
        agent_id="test-agent",
    )


@pytest.fixture
def failed_trajectory() -> Trajectory:
    """Create a failed trajectory for testing."""
    task = Task(
        id="task-002",
        domain="test",
        description="Fix the database bug",
        context={},
        verification=VerificationSpec(method="test_suite"),
    )
    step = Step(
        thought="Trying to fix it",
        action="Edit",
        observation="Made changes",
    )
    outcome = Outcome(success=False, error_info="Tests failed")
    return Trajectory(
        task=task,
        steps=[step],
        outcome=outcome,
        agent_id="test-agent",
    )


@pytest.fixture
def sample_strategy() -> Strategy:
    """Create a sample strategy for testing."""
    return Strategy(
        id="strat-001",
        situation="When encountering null pointer errors",
        suggestion="Add defensive null checks before dereferencing",
        parameters=[{"name": "variable", "type": "str"}],
        usage_count=5,
        success_rate=0.8,
    )


# =============================================================================
# Write Tests
# =============================================================================


class TestWrite:
    """Tests for ChromaStrategyBank.write method."""

    @pytest.mark.asyncio
    async def test_write_only_processes_successful_trajectories(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        sample_strategy: Strategy,
        mock_abstractor: AsyncMock,
        mock_vector_store: AsyncMock,
    ) -> None:
        """write should only process successful trajectories."""
        mock_abstractor.abstract.return_value = sample_strategy

        result = await strategy_bank.write(successful_trajectory)

        assert result is not None
        mock_abstractor.abstract.assert_called_once_with(successful_trajectory)
        mock_vector_store.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_returns_none_for_failed_trajectories(
        self,
        strategy_bank: ChromaStrategyBank,
        failed_trajectory: Trajectory,
        mock_abstractor: AsyncMock,
        mock_vector_store: AsyncMock,
    ) -> None:
        """write should return None for failed trajectories."""
        result = await strategy_bank.write(failed_trajectory)

        assert result is None
        mock_abstractor.abstract.assert_not_called()
        mock_vector_store.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_delegates_to_abstractor(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        sample_strategy: Strategy,
        mock_abstractor: AsyncMock,
    ) -> None:
        """write should delegate to abstractor for strategy extraction."""
        mock_abstractor.abstract.return_value = sample_strategy

        await strategy_bank.write(successful_trajectory)

        mock_abstractor.abstract.assert_called_once_with(successful_trajectory)

    @pytest.mark.asyncio
    async def test_write_returns_none_when_abstractor_returns_none(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        mock_abstractor: AsyncMock,
        mock_vector_store: AsyncMock,
    ) -> None:
        """write should return None if abstractor returns None."""
        mock_abstractor.abstract.return_value = None

        result = await strategy_bank.write(successful_trajectory)

        assert result is None
        mock_vector_store.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_stores_strategy_in_vector_store(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        sample_strategy: Strategy,
        mock_abstractor: AsyncMock,
        mock_vector_store: AsyncMock,
        mock_embedder: MagicMock,
    ) -> None:
        """write should store strategy in vector store with correct metadata."""
        mock_abstractor.abstract.return_value = sample_strategy

        result = await strategy_bank.write(successful_trajectory)

        assert result is not None

        # Verify vector store was called with correct arguments
        mock_vector_store.add.assert_called_once()
        call_args = mock_vector_store.add.call_args

        # Check that the situation was embedded
        mock_embedder.encode.assert_called_with(sample_strategy.situation)

        # Check metadata
        metadata = call_args.kwargs["metadatas"][0]
        assert metadata["usage_count"] == sample_strategy.usage_count
        assert metadata["success_rate"] == sample_strategy.success_rate
        assert metadata["source_task_id"] == successful_trajectory.task.id
        assert metadata["suggestion"] == sample_strategy.suggestion
        assert json.loads(metadata["parameters"]) == sample_strategy.parameters

        # Check document is the situation
        assert call_args.kwargs["documents"][0] == sample_strategy.situation

    @pytest.mark.asyncio
    async def test_write_generates_uuid_if_not_set(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        mock_abstractor: AsyncMock,
        mock_vector_store: AsyncMock,
    ) -> None:
        """write should generate a UUID for the strategy if not set."""
        strategy_without_id = Strategy(
            id="",
            situation="When X happens",
            suggestion="Do Y",
            parameters=[],
        )
        mock_abstractor.abstract.return_value = strategy_without_id

        result = await strategy_bank.write(successful_trajectory)

        assert result is not None
        assert result.id != ""
        assert len(result.id) == 32  # UUID hex length

    @pytest.mark.asyncio
    async def test_write_returns_strategy_with_embedding(
        self,
        strategy_bank: ChromaStrategyBank,
        successful_trajectory: Trajectory,
        sample_strategy: Strategy,
        mock_abstractor: AsyncMock,
        mock_embedder: MagicMock,
    ) -> None:
        """write should return strategy with embedding set."""
        mock_abstractor.abstract.return_value = sample_strategy

        result = await strategy_bank.write(successful_trajectory)

        assert result is not None
        assert result.embedding is not None
        np.testing.assert_array_equal(result.embedding, mock_embedder.encode.return_value)


# =============================================================================
# Read Tests
# =============================================================================


class TestRead:
    """Tests for ChromaStrategyBank.read method."""

    @pytest.mark.asyncio
    async def test_read_returns_sorted_by_relevance(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
        mock_embedder: MagicMock,
    ) -> None:
        """read should return strategies sorted by relevance (distance + success_rate)."""
        task = Task(
            id="task-001",
            domain="test",
            description="Fix a bug",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        # Strategy 1: low distance (0.1), low success rate (0.3) -> score = 0.1 - 0.3 = -0.2
        # Strategy 2: high distance (0.5), high success rate (0.9) -> score = 0.5 - 0.9 = -0.4
        # Strategy 2 should come first (lower combined score)
        mock_vector_store.query.return_value = QueryResult(
            ids=["strat-1", "strat-2"],
            distances=[0.1, 0.5],
            metadatas=[
                {"suggestion": "Suggestion 1", "success_rate": 0.3, "usage_count": 1, "parameters": "[]"},
                {"suggestion": "Suggestion 2", "success_rate": 0.9, "usage_count": 5, "parameters": "[]"},
            ],
            documents=["Situation 1", "Situation 2"],
        )

        results = await strategy_bank.read(task, k=5)

        assert len(results) == 2
        # Strategy 2 should come first (better combined score)
        assert results[0].id == "strat-2"
        assert results[1].id == "strat-1"

    @pytest.mark.asyncio
    async def test_read_reconstructs_strategy_objects(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """read should reconstruct Strategy objects from query results."""
        task = Task(
            id="task-001",
            domain="test",
            description="Fix a bug",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        mock_vector_store.query.return_value = QueryResult(
            ids=["strat-1"],
            distances=[0.2],
            metadatas=[
                {
                    "suggestion": "Do this thing",
                    "success_rate": 0.85,
                    "usage_count": 10,
                    "parameters": '[{"name": "var", "type": "str"}]',
                }
            ],
            documents=["When this situation occurs"],
        )

        results = await strategy_bank.read(task, k=5)

        assert len(results) == 1
        strategy = results[0]
        assert strategy.id == "strat-1"
        assert strategy.situation == "When this situation occurs"
        assert strategy.suggestion == "Do this thing"
        assert strategy.success_rate == 0.85
        assert strategy.usage_count == 10
        assert strategy.parameters == [{"name": "var", "type": "str"}]

    @pytest.mark.asyncio
    async def test_read_returns_empty_list_when_no_results(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """read should return empty list when no strategies found."""
        task = Task(
            id="task-001",
            domain="test",
            description="Something unique",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        mock_vector_store.query.return_value = QueryResult(
            ids=[], distances=[], metadatas=[], documents=[]
        )

        results = await strategy_bank.read(task, k=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_read_embeds_task_description(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
        mock_embedder: MagicMock,
    ) -> None:
        """read should embed the task description for query."""
        task = Task(
            id="task-001",
            domain="test",
            description="Fix the authentication bug",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        await strategy_bank.read(task, k=5)

        mock_embedder.encode.assert_called_with(task.description)


# =============================================================================
# Get Tests
# =============================================================================


class TestGet:
    """Tests for ChromaStrategyBank.get method."""

    @pytest.mark.asyncio
    async def test_get_retrieves_stored_strategy(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """get should retrieve a stored strategy by ID."""
        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {
                    "suggestion": "Do something",
                    "success_rate": 0.75,
                    "usage_count": 3,
                    "parameters": "[]",
                },
                "document": "When something happens",
                "embedding": [0.1, 0.2, 0.3],
            }
        ]

        result = await strategy_bank.get("strat-001")

        assert result is not None
        assert result.id == "strat-001"
        assert result.situation == "When something happens"
        assert result.suggestion == "Do something"
        assert result.success_rate == 0.75
        assert result.usage_count == 3

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_id(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """get should return None if strategy ID not found."""
        mock_vector_store.get.return_value = []

        result = await strategy_bank.get("nonexistent-id")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_includes_embedding_if_present(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """get should include embedding in returned strategy if present."""
        embedding_list = [0.1, 0.2, 0.3, 0.4]
        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {"suggestion": "Do X", "success_rate": 0.5, "usage_count": 0, "parameters": "[]"},
                "document": "When Y",
                "embedding": embedding_list,
            }
        ]

        result = await strategy_bank.get("strat-001")

        assert result is not None
        assert result.embedding is not None
        np.testing.assert_array_equal(result.embedding, np.array(embedding_list))


# =============================================================================
# Update Stats Tests
# =============================================================================


class TestUpdateStats:
    """Tests for ChromaStrategyBank.update_stats method."""

    @pytest.mark.asyncio
    async def test_update_stats_uses_success_updater(
        self,
        mock_embedder: MagicMock,
        mock_vector_store: AsyncMock,
        mock_abstractor: AsyncMock,
    ) -> None:
        """update_stats should use the configured success updater."""
        # Create a mock success updater
        mock_updater = MagicMock()
        mock_updater.update.return_value = (0.6, 11)

        bank = ChromaStrategyBank(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            abstractor=mock_abstractor,
            success_updater=mock_updater,
        )

        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {"success_rate": 0.5, "usage_count": 10, "suggestion": "X", "parameters": "[]"},
                "document": "When Y",
                "embedding": [0.1, 0.2],
            }
        ]

        await bank.update_stats("strat-001", success=True)

        mock_updater.update.assert_called_once_with(
            current_rate=0.5,
            current_count=10,
            success=True,
        )

    @pytest.mark.asyncio
    async def test_update_stats_with_ema_updater(
        self,
        mock_embedder: MagicMock,
        mock_vector_store: AsyncMock,
        mock_abstractor: AsyncMock,
    ) -> None:
        """update_stats should work correctly with EMA updater."""
        ema_updater = EMASuccessUpdater(alpha=0.1)

        bank = ChromaStrategyBank(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            abstractor=mock_abstractor,
            success_updater=ema_updater,
        )

        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {"success_rate": 0.5, "usage_count": 10, "suggestion": "X", "parameters": "[]"},
                "document": "When Y",
                "embedding": [0.1, 0.2],
            }
        ]

        await bank.update_stats("strat-001", success=True)

        # Verify delete and re-add were called
        mock_vector_store.delete.assert_called_once_with(ids=["strat-001"])
        mock_vector_store.add.assert_called_once()

        # Check the new metadata
        call_args = mock_vector_store.add.call_args
        new_metadata = call_args.kwargs["metadatas"][0]
        # EMA: 0.1 * 1.0 + 0.9 * 0.5 = 0.55
        assert new_metadata["success_rate"] == pytest.approx(0.55)
        assert new_metadata["usage_count"] == 11

    @pytest.mark.asyncio
    async def test_update_stats_with_simple_average_updater(
        self,
        mock_embedder: MagicMock,
        mock_vector_store: AsyncMock,
        mock_abstractor: AsyncMock,
    ) -> None:
        """update_stats should work correctly with SimpleAverage updater."""
        simple_updater = SimpleAverageUpdater()

        bank = ChromaStrategyBank(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            abstractor=mock_abstractor,
            success_updater=simple_updater,
        )

        # 4 successes out of 5 (rate = 0.8)
        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {"success_rate": 0.8, "usage_count": 5, "suggestion": "X", "parameters": "[]"},
                "document": "When Y",
                "embedding": [0.1, 0.2],
            }
        ]

        await bank.update_stats("strat-001", success=True)

        # Verify the new metadata
        call_args = mock_vector_store.add.call_args
        new_metadata = call_args.kwargs["metadatas"][0]
        # Simple average: 5 successes out of 6 = 0.833...
        assert new_metadata["success_rate"] == pytest.approx(5 / 6)
        assert new_metadata["usage_count"] == 6

    @pytest.mark.asyncio
    async def test_update_stats_does_nothing_for_missing_strategy(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """update_stats should do nothing if strategy not found."""
        mock_vector_store.get.return_value = []

        await strategy_bank.update_stats("nonexistent-id", success=True)

        mock_vector_store.delete.assert_not_called()
        mock_vector_store.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_stats_preserves_other_metadata(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """update_stats should preserve other metadata fields."""
        mock_vector_store.get.return_value = [
            {
                "id": "strat-001",
                "metadata": {
                    "success_rate": 0.5,
                    "usage_count": 10,
                    "suggestion": "Original suggestion",
                    "parameters": '[{"name": "x"}]',
                    "source_task_id": "task-001",
                },
                "document": "When something",
                "embedding": [0.1, 0.2],
            }
        ]

        await strategy_bank.update_stats("strat-001", success=True)

        call_args = mock_vector_store.add.call_args
        new_metadata = call_args.kwargs["metadatas"][0]

        assert new_metadata["suggestion"] == "Original suggestion"
        assert new_metadata["parameters"] == '[{"name": "x"}]'
        assert new_metadata["source_task_id"] == "task-001"


# =============================================================================
# __len__ Tests
# =============================================================================


class TestLen:
    """Tests for ChromaStrategyBank.__len__ method."""

    def test_len_returns_correct_count(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """__len__ should return count from vector store."""
        mock_vector_store.count.return_value = 42

        result = len(strategy_bank)

        assert result == 42

    def test_len_returns_zero_for_empty_store(
        self,
        strategy_bank: ChromaStrategyBank,
        mock_vector_store: AsyncMock,
    ) -> None:
        """__len__ should return 0 for empty store."""
        mock_vector_store.count.return_value = 0

        result = len(strategy_bank)

        assert result == 0


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestProtocolCompliance:
    """Test that ChromaStrategyBank satisfies StrategyBank protocol."""

    def test_implements_strategy_bank_protocol(
        self,
        strategy_bank: ChromaStrategyBank,
    ) -> None:
        """ChromaStrategyBank should implement StrategyBank protocol."""
        from cognitive_core.protocols.memory import StrategyBank

        assert isinstance(strategy_bank, StrategyBank)

    def test_has_required_methods(
        self,
        strategy_bank: ChromaStrategyBank,
    ) -> None:
        """ChromaStrategyBank should have all required protocol methods."""
        assert hasattr(strategy_bank, "write")
        assert hasattr(strategy_bank, "read")
        assert hasattr(strategy_bank, "get")
        assert hasattr(strategy_bank, "update_stats")
        assert hasattr(strategy_bank, "__len__")

        assert callable(strategy_bank.write)
        assert callable(strategy_bank.read)
        assert callable(strategy_bank.get)
        assert callable(strategy_bank.update_stats)


# =============================================================================
# Default Updater Tests
# =============================================================================


class TestDefaultSuccessUpdater:
    """Test that ChromaStrategyBank uses EMASuccessUpdater by default."""

    def test_uses_ema_updater_by_default(
        self,
        mock_embedder: MagicMock,
        mock_vector_store: AsyncMock,
        mock_abstractor: AsyncMock,
    ) -> None:
        """ChromaStrategyBank should use EMASuccessUpdater by default."""
        bank = ChromaStrategyBank(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            abstractor=mock_abstractor,
        )

        assert isinstance(bank._success_updater, EMASuccessUpdater)
