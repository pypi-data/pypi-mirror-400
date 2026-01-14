"""Shared pytest fixtures for integration tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Generator

import chromadb
import numpy as np
import pytest

from cognitive_core.core.types import (
    CodeConcept,
    Outcome,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)
from cognitive_core.memory.concepts import ChromaConceptLibrary
from cognitive_core.memory.experience import ChromaExperienceMemory
from cognitive_core.memory.primitives import ARCPrimitiveLoader
from cognitive_core.memory.storage import ChromaVectorStore
from cognitive_core.memory.strategy_bank import ChromaStrategyBank
from cognitive_core.memory.system import MemorySystemImpl
from cognitive_core.protocols.embeddings import EmbeddingProvider


class DeterministicEmbedder(EmbeddingProvider):
    """Deterministic embedder for reproducible tests.

    Creates embeddings based on hash of text, ensuring same text
    produces same embedding every time.
    """

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def encode(self, text: str) -> np.ndarray:
        """Generate deterministic embedding from text."""
        # Use hash of text as seed for reproducibility
        seed = hash(text) % (2**32)
        rng = np.random.RandomState(seed)
        embedding = rng.randn(self._dimension).astype(np.float32)
        # Normalize to unit vector
        return embedding / (np.linalg.norm(embedding) + 1e-8)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Batch encode texts."""
        return np.array([self.encode(text) for text in texts])


class SimpleStrategyAbstractor:
    """Simple strategy abstractor for testing."""

    async def abstract(self, trajectory: Trajectory) -> Strategy | None:
        """Create a simple strategy from trajectory."""
        if not trajectory.outcome.success:
            return None

        return Strategy(
            id=f"strategy-{uuid.uuid4().hex[:8]}",
            situation=f"When working on: {trajectory.task.description[:50]}",
            suggestion=f"Apply the approach used for {trajectory.task.domain} tasks",
            parameters=[],
            usage_count=0,
            success_rate=0.5,
        )


@pytest.fixture
def embedder() -> DeterministicEmbedder:
    """Create deterministic embedder."""
    return DeterministicEmbedder(dimension=384)


@pytest.fixture
def ephemeral_chroma() -> Generator[chromadb.Client, None, None]:
    """Create ephemeral ChromaDB client."""
    client = chromadb.Client()
    yield client


@pytest.fixture
def experience_vector_store(ephemeral_chroma: chromadb.Client) -> ChromaVectorStore:
    """Create vector store for experiences."""
    collection_name = f"experiences_{uuid.uuid4().hex[:8]}"
    collection = ephemeral_chroma.create_collection(collection_name)
    return ChromaVectorStore(collection=collection)


@pytest.fixture
def concept_vector_store(ephemeral_chroma: chromadb.Client) -> ChromaVectorStore:
    """Create vector store for concepts."""
    collection_name = f"concepts_{uuid.uuid4().hex[:8]}"
    collection = ephemeral_chroma.create_collection(collection_name)
    return ChromaVectorStore(collection=collection)


@pytest.fixture
def strategy_vector_store(ephemeral_chroma: chromadb.Client) -> ChromaVectorStore:
    """Create vector store for strategies."""
    collection_name = f"strategies_{uuid.uuid4().hex[:8]}"
    collection = ephemeral_chroma.create_collection(collection_name)
    return ChromaVectorStore(collection=collection)


@pytest.fixture
def experience_memory(
    embedder: DeterministicEmbedder,
    experience_vector_store: ChromaVectorStore,
) -> ChromaExperienceMemory:
    """Create experience memory."""
    return ChromaExperienceMemory(
        embedder=embedder,
        vector_store=experience_vector_store,
    )


@pytest.fixture
def concept_library(
    embedder: DeterministicEmbedder,
    concept_vector_store: ChromaVectorStore,
) -> ChromaConceptLibrary:
    """Create concept library with ARC primitives."""
    return ChromaConceptLibrary(
        embedder=embedder,
        vector_store=concept_vector_store,
        primitive_loader=ARCPrimitiveLoader(),
    )


@pytest.fixture
def strategy_bank(
    embedder: DeterministicEmbedder,
    strategy_vector_store: ChromaVectorStore,
) -> ChromaStrategyBank:
    """Create strategy bank."""
    return ChromaStrategyBank(
        embedder=embedder,
        vector_store=strategy_vector_store,
        abstractor=SimpleStrategyAbstractor(),
    )


@pytest.fixture
def full_memory_system(
    experience_memory: ChromaExperienceMemory,
    concept_library: ChromaConceptLibrary,
    strategy_bank: ChromaStrategyBank,
) -> MemorySystemImpl:
    """Create full memory system with all components."""
    return MemorySystemImpl(
        experience=experience_memory,
        concepts=concept_library,
        strategies=strategy_bank,
    )


@pytest.fixture
def sample_success_trajectory() -> Trajectory:
    """Create a successful trajectory for testing."""
    return Trajectory(
        task=Task(
            id="task-success-001",
            domain="swe",
            description="Fix the authentication bug in login.py",
            context={"file": "login.py"},
            verification=VerificationSpec(method="test_suite"),
        ),
        steps=[
            Step(
                thought="I need to check the login function",
                action="read_file('login.py')",
                observation="def login(user, password): ...",
            ),
            Step(
                thought="Found the bug - missing null check",
                action="edit_file('login.py', add_null_check)",
                observation="File updated",
            ),
            Step(
                thought="Running tests to verify",
                action="run_tests()",
                observation="All tests passed",
            ),
        ],
        outcome=Outcome(
            success=True,
            partial_score=1.0,
            verification_details={"tests_passed": 5},
        ),
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_failure_trajectory() -> Trajectory:
    """Create a failed trajectory for testing."""
    return Trajectory(
        task=Task(
            id="task-failure-001",
            domain="swe",
            description="Fix the database connection error",
            context={"file": "db.py"},
            verification=VerificationSpec(method="test_suite"),
        ),
        steps=[
            Step(
                thought="I need to check the database module",
                action="read_file('db.py')",
                observation="def connect(): ...",
            ),
            Step(
                thought="Attempting to fix connection",
                action="edit_file('db.py', fix_connection)",
                observation="File updated",
            ),
        ],
        outcome=Outcome(
            success=False,
            partial_score=0.3,
            error_info="Connection still fails: timeout error",
        ),
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_similar_task() -> Task:
    """Create a task similar to sample_success_trajectory."""
    return Task(
        id="task-similar-001",
        domain="swe",
        description="Fix the authentication bug in auth.py",
        context={"file": "auth.py"},
        verification=VerificationSpec(method="test_suite"),
    )


@pytest.fixture
def sample_different_task() -> Task:
    """Create a task different from sample trajectories."""
    return Task(
        id="task-different-001",
        domain="arc",
        description="Rotate the grid 90 degrees clockwise",
        context={"grid_size": "3x3"},
        verification=VerificationSpec(method="exact_match"),
    )
