"""Tests for ChromaExperienceMemory implementation."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from cognitive_core.core.types import Experience, Outcome, Step, Task, Trajectory, VerificationSpec
from cognitive_core.memory.experience import ChromaExperienceMemory
from cognitive_core.memory.storage import QueryResult
from cognitive_core.memory.strategies.experience import (
    PassthroughRefineStrategy,
    SimpleExperienceExtractor,
)


class MockEmbeddingProvider:
    """Mock embedding provider for testing."""

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    def encode(self, text: str) -> np.ndarray:
        """Return a deterministic embedding based on text hash."""
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(self._dimension).astype(np.float32)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts."""
        return np.array([self.encode(t) for t in texts])

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return "mock-embedder"


class MockVectorStore:
    """Mock vector store for testing."""

    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    async def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Add items to mock store."""
        for i, item_id in enumerate(ids):
            self._items[item_id] = {
                "id": item_id,
                "embedding": embeddings[i],
                "metadata": metadatas[i],
                "document": documents[i],
            }

    async def query(
        self,
        embedding: list[float],
        k: int,
        where: dict[str, Any] | None = None,
    ) -> QueryResult:
        """Query mock store - returns items in order added."""
        items = list(self._items.values())

        # Apply where filter if provided
        if where:
            filtered_items = []
            for item in items:
                match = True
                for key, value in where.items():
                    if item["metadata"].get(key) != value:
                        match = False
                        break
                if match:
                    filtered_items.append(item)
            items = filtered_items

        # Limit to k items
        items = items[:k]

        return QueryResult(
            ids=[item["id"] for item in items],
            distances=[0.1 * i for i in range(len(items))],
            metadatas=[item["metadata"] for item in items],
            documents=[item["document"] for item in items],
        )

    async def delete(self, ids: list[str]) -> None:
        """Delete items from mock store."""
        for item_id in ids:
            self._items.pop(item_id, None)

    async def get(self, ids: list[str]) -> list[dict[str, Any]]:
        """Get items by ID."""
        result = []
        for item_id in ids:
            if item_id in self._items:
                result.append(self._items[item_id])
        return result

    async def count(self) -> int:
        """Return number of items."""
        return len(self._items)


class TestChromaExperienceMemory:
    """Tests for ChromaExperienceMemory implementation."""

    @pytest.fixture
    def mock_embedder(self) -> MockEmbeddingProvider:
        """Create a mock embedding provider."""
        return MockEmbeddingProvider()

    @pytest.fixture
    def mock_vector_store(self) -> MockVectorStore:
        """Create a mock vector store."""
        return MockVectorStore()

    @pytest.fixture
    def memory(
        self, mock_embedder: MockEmbeddingProvider, mock_vector_store: MockVectorStore
    ) -> ChromaExperienceMemory:
        """Create a ChromaExperienceMemory instance for testing."""
        return ChromaExperienceMemory(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
        )

    @pytest.fixture
    def sample_trajectory(self) -> Trajectory:
        """Create a sample trajectory for testing."""
        task = Task(
            id="task-001",
            domain="test",
            description="Fix the authentication bug",
            context={"file": "auth.py"},
            verification=VerificationSpec(method="test_suite"),
        )
        step = Step(
            thought="I need to check the login function",
            action="Fixed null check in login()",
            observation="Tests now pass",
            metadata={"tool": "edit"},
        )
        outcome = Outcome(
            success=True,
            partial_score=1.0,
            verification_details={"tests_passed": 5},
        )
        return Trajectory(
            task=task,
            steps=[step],
            outcome=outcome,
            agent_id="test-agent",
        )

    @pytest.fixture
    def failed_trajectory(self) -> Trajectory:
        """Create a failed trajectory for testing."""
        task = Task(
            id="task-002",
            domain="test",
            description="Implement new feature",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )
        step = Step(
            thought="Trying to implement",
            action="Added incomplete code",
            observation="Tests fail",
            metadata={},
        )
        outcome = Outcome(
            success=False,
            partial_score=0.3,
            error_info="Tests failed: 2/5 passed",
        )
        return Trajectory(
            task=task,
            steps=[step],
            outcome=outcome,
            agent_id="test-agent",
        )

    def test_store_returns_valid_uuid(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that store returns a valid UUID."""
        exp_id = memory.store(sample_trajectory)

        # UUID hex is 32 characters
        assert len(exp_id) == 32
        # Should be valid hex
        int(exp_id, 16)

    def test_store_increments_count(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that store adds to the memory."""
        assert len(memory) == 0

        memory.store(sample_trajectory)
        assert len(memory) == 1

        memory.store(sample_trajectory)
        assert len(memory) == 2

    def test_search_returns_relevant_experiences(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that search returns relevant experiences."""
        # Store an experience
        memory.store(sample_trajectory)

        # Search with similar task
        search_task = Task(
            id="search-task",
            domain="test",
            description="Fix authentication issue",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        results = memory.search(search_task, k=4)

        assert len(results) == 1
        assert results[0].task_input == sample_trajectory.task.description
        assert results[0].success is True

    def test_search_returns_multiple_experiences(
        self,
        memory: ChromaExperienceMemory,
        sample_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test that search returns multiple experiences."""
        memory.store(sample_trajectory)
        memory.store(failed_trajectory)

        search_task = Task(
            id="search-task",
            domain="test",
            description="Fix a bug",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        results = memory.search(search_task, k=4)

        assert len(results) == 2

    def test_search_respects_k_limit(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that search respects the k limit."""
        # Store multiple experiences
        for _ in range(5):
            memory.store(sample_trajectory)

        search_task = Task(
            id="search-task",
            domain="test",
            description="Test task",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        results = memory.search(search_task, k=2)
        assert len(results) == 2

    def test_search_default_k_is_4(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that default k=4 (from ReMem paper)."""
        # Store 5 experiences
        for _ in range(5):
            memory.store(sample_trajectory)

        search_task = Task(
            id="search-task",
            domain="test",
            description="Test task",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        results = memory.search(search_task)
        assert len(results) == 4

    def test_get_retrieves_stored_experience(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that get retrieves a stored experience."""
        exp_id = memory.store(sample_trajectory)

        experience = memory.get(exp_id)

        assert experience is not None
        assert experience.id == exp_id
        assert experience.task_input == sample_trajectory.task.description
        assert experience.success is True

    def test_get_returns_none_for_missing_id(
        self, memory: ChromaExperienceMemory
    ) -> None:
        """Test that get returns None for non-existent ID."""
        result = memory.get("nonexistent-id")
        assert result is None

    def test_refine_delegates_to_strategy(
        self, mock_embedder: MockEmbeddingProvider, mock_vector_store: MockVectorStore
    ) -> None:
        """Test that refine delegates to the refine strategy."""
        # Create mock refine strategy
        mock_strategy = MagicMock()
        refined_experiences = [
            Experience(
                id="refined-1",
                task_input="Refined task",
                solution_output="Refined solution",
                feedback="Refined feedback",
                success=True,
                trajectory_id="traj-1",
            )
        ]
        mock_strategy.refine = AsyncMock(return_value=refined_experiences)

        memory = ChromaExperienceMemory(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            refine_strategy=mock_strategy,
        )

        input_experiences = [
            Experience(
                id="exp-1",
                task_input="Test task",
                solution_output="Test solution",
                feedback="Test feedback",
                success=True,
                trajectory_id="traj-1",
            )
        ]

        result = memory.refine(input_experiences)

        mock_strategy.refine.assert_called_once_with(input_experiences)
        assert result == refined_experiences

    def test_refine_with_passthrough_strategy(
        self, memory: ChromaExperienceMemory
    ) -> None:
        """Test refine with default passthrough strategy returns same experiences."""
        experiences = [
            Experience(
                id="exp-1",
                task_input="Test task",
                solution_output="Test solution",
                feedback="Test feedback",
                success=True,
                trajectory_id="traj-1",
            )
        ]

        result = memory.refine(experiences)

        assert result == experiences

    def test_prune_removes_old_experiences(
        self,
        mock_embedder: MockEmbeddingProvider,
    ) -> None:
        """Test that prune removes old experiences based on max_age_days."""
        # Create a store with old and new items
        mock_store = MockVectorStore()

        # Add items directly with controlled timestamps
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        new_timestamp = datetime.now(timezone.utc).isoformat()

        import asyncio

        asyncio.get_event_loop().run_until_complete(
            mock_store.add(
                ids=["old-exp", "new-exp"],
                embeddings=[[0.1] * 384, [0.2] * 384],
                metadatas=[
                    {"timestamp": old_timestamp, "success": True, "task_input": "old", "solution_output": "", "feedback": "", "trajectory_id": "t1"},
                    {"timestamp": new_timestamp, "success": True, "task_input": "new", "solution_output": "", "feedback": "", "trajectory_id": "t2"},
                ],
                documents=["old doc", "new doc"],
            )
        )

        memory = ChromaExperienceMemory(
            embedder=mock_embedder,
            vector_store=mock_store,
        )

        removed = memory.prune({"max_age_days": 5})

        assert removed == 1
        assert len(memory) == 1

    def test_prune_removes_failed_experiences(
        self,
        mock_embedder: MockEmbeddingProvider,
    ) -> None:
        """Test that prune removes failed experiences with min_success_rate."""
        mock_store = MockVectorStore()

        now = datetime.now(timezone.utc).isoformat()

        import asyncio

        asyncio.get_event_loop().run_until_complete(
            mock_store.add(
                ids=["success-exp", "failed-exp"],
                embeddings=[[0.1] * 384, [0.2] * 384],
                metadatas=[
                    {"timestamp": now, "success": True, "task_input": "success", "solution_output": "", "feedback": "", "trajectory_id": "t1"},
                    {"timestamp": now, "success": False, "task_input": "failed", "solution_output": "", "feedback": "", "trajectory_id": "t2"},
                ],
                documents=["success doc", "failed doc"],
            )
        )

        memory = ChromaExperienceMemory(
            embedder=mock_embedder,
            vector_store=mock_store,
        )

        removed = memory.prune({"min_success_rate": 0.5})

        assert removed == 1
        assert len(memory) == 1

    def test_prune_returns_zero_on_empty_store(
        self, memory: ChromaExperienceMemory
    ) -> None:
        """Test that prune returns 0 when store is empty."""
        removed = memory.prune({"max_age_days": 1})
        assert removed == 0

    def test_len_returns_correct_count(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that __len__ returns correct count."""
        assert len(memory) == 0

        memory.store(sample_trajectory)
        assert len(memory) == 1

        memory.store(sample_trajectory)
        memory.store(sample_trajectory)
        assert len(memory) == 3

    def test_store_preserves_success_status(
        self,
        memory: ChromaExperienceMemory,
        sample_trajectory: Trajectory,
        failed_trajectory: Trajectory,
    ) -> None:
        """Test that store preserves success/failure status."""
        success_id = memory.store(sample_trajectory)
        failure_id = memory.store(failed_trajectory)

        success_exp = memory.get(success_id)
        failure_exp = memory.get(failure_id)

        assert success_exp is not None
        assert success_exp.success is True

        assert failure_exp is not None
        assert failure_exp.success is False

    def test_store_with_custom_extractor(
        self, mock_embedder: MockEmbeddingProvider, mock_vector_store: MockVectorStore
    ) -> None:
        """Test store with custom extractor."""

        class CustomExtractor:
            def extract(self, trajectory: Trajectory) -> str:
                return f"CUSTOM: {trajectory.task.description}"

        memory = ChromaExperienceMemory(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            extractor=CustomExtractor(),
        )

        task = Task(
            id="task-001",
            domain="test",
            description="Test description",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )
        trajectory = Trajectory(
            task=task,
            steps=[],
            outcome=Outcome(success=True),
            agent_id="test",
        )

        memory.store(trajectory)

        # The embedding should be based on the custom extracted text
        # This is verified by checking the document stored in the mock store
        import asyncio

        items = asyncio.get_event_loop().run_until_complete(
            mock_vector_store.query([0.0] * 384, k=1)
        )
        assert "CUSTOM: Test description" in items.documents[0]

    def test_search_handles_empty_results(
        self, memory: ChromaExperienceMemory
    ) -> None:
        """Test that search handles empty results gracefully."""
        search_task = Task(
            id="search-task",
            domain="test",
            description="Test task",
            context={},
            verification=VerificationSpec(method="test_suite"),
        )

        results = memory.search(search_task)

        assert results == []

    def test_experience_has_correct_fields(
        self, memory: ChromaExperienceMemory, sample_trajectory: Trajectory
    ) -> None:
        """Test that stored experience has all correct fields."""
        exp_id = memory.store(sample_trajectory)
        experience = memory.get(exp_id)

        assert experience is not None
        assert experience.id == exp_id
        assert experience.task_input == sample_trajectory.task.description
        assert experience.solution_output == sample_trajectory.steps[-1].action
        assert experience.feedback == "Success"
        assert experience.success is True
        assert experience.trajectory_id == sample_trajectory.task.id
        assert isinstance(experience.timestamp, datetime)
