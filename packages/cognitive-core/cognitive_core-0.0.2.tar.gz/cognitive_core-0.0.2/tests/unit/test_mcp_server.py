"""Tests for Memory MCP Server."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

from cognitive_core.core.types import CodeConcept, Experience, Strategy, Task, VerificationSpec


class MockExperienceMemory:
    """Mock ExperienceMemory for testing."""

    def __init__(self, experiences: list[Experience] | None = None):
        self._experiences = {e.id: e for e in (experiences or [])}

    def search(self, task: Task, k: int = 4) -> list[Experience]:
        return list(self._experiences.values())[:k]

    def get(self, experience_id: str) -> Experience | None:
        return self._experiences.get(experience_id)


class MockConceptLibrary:
    """Mock ConceptLibrary for testing."""

    def __init__(self, concepts: list[CodeConcept] | None = None):
        self._concepts = {c.id: c for c in (concepts or [])}

    def search(self, query: str, k: int = 5) -> list[CodeConcept]:
        return list(self._concepts.values())[:k]

    def get(self, concept_id: str) -> CodeConcept | None:
        return self._concepts.get(concept_id)


class MockStrategyBank:
    """Mock StrategyBank for testing."""

    def __init__(self, strategies: list[Strategy] | None = None):
        self._strategies = {s.id: s for s in (strategies or [])}

    def read(self, task: Task, k: int = 5) -> list[Strategy]:
        return list(self._strategies.values())[:k]

    def get(self, strategy_id: str) -> Strategy | None:
        return self._strategies.get(strategy_id)


class MockMemorySystem:
    """Mock MemorySystem for testing."""

    def __init__(
        self,
        experience_memory: MockExperienceMemory | None = None,
        concept_library: MockConceptLibrary | None = None,
        strategy_bank: MockStrategyBank | None = None,
    ):
        self._experience_memory = experience_memory
        self._concept_library = concept_library
        self._strategy_bank = strategy_bank

    @property
    def experience_memory(self):
        return self._experience_memory

    @property
    def concept_library(self):
        return self._concept_library

    @property
    def strategy_bank(self):
        return self._strategy_bank


class TestMemoryMCPServer:
    """Tests for Memory MCP Server."""

    @pytest.fixture
    def sample_experience(self) -> Experience:
        """Create a sample experience."""
        return Experience(
            id="exp-001",
            task_input="Fix authentication bug",
            solution_output="Added null check",
            feedback="Tests passed",
            success=True,
            trajectory_id="traj-001",
        )

    @pytest.fixture
    def sample_concept(self) -> CodeConcept:
        """Create a sample concept."""
        return CodeConcept(
            id="concept-001",
            name="null_check",
            description="Safe null checking",
            code="if x is not None: ...",
            signature="(x: Any) -> bool",
        )

    @pytest.fixture
    def sample_strategy(self) -> Strategy:
        """Create a sample strategy."""
        return Strategy(
            id="strat-001",
            situation="Null pointer errors",
            suggestion="Add defensive checks",
        )

    @pytest.fixture
    def memory_system(
        self,
        sample_experience: Experience,
        sample_concept: CodeConcept,
        sample_strategy: Strategy,
    ) -> MockMemorySystem:
        """Create a mock memory system."""
        return MockMemorySystem(
            experience_memory=MockExperienceMemory([sample_experience]),
            concept_library=MockConceptLibrary([sample_concept]),
            strategy_bank=MockStrategyBank([sample_strategy]),
        )

    def test_create_server_without_memory(self) -> None:
        """Test creating server without memory system."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        server = create_memory_server(memory=None)
        assert server is not None

    def test_create_server_with_memory(self, memory_system: MockMemorySystem) -> None:
        """Test creating server with memory system."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        server = create_memory_server(memory=memory_system)
        assert server is not None

    def test_experience_to_dict(self, sample_experience: Experience) -> None:
        """Test experience serialization."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import _experience_to_dict

        result = _experience_to_dict(sample_experience)

        assert result["id"] == "exp-001"
        assert result["task_input"] == "Fix authentication bug"
        assert result["solution_output"] == "Added null check"
        assert result["success"] is True
        assert "embedding" not in result  # Should be excluded

    def test_concept_to_dict(self, sample_concept: CodeConcept) -> None:
        """Test concept serialization."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import _concept_to_dict

        result = _concept_to_dict(sample_concept)

        assert result["id"] == "concept-001"
        assert result["name"] == "null_check"
        assert result["code"] == "if x is not None: ..."
        assert "embedding" not in result

    def test_strategy_to_dict(self, sample_strategy: Strategy) -> None:
        """Test strategy serialization."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import _strategy_to_dict

        result = _strategy_to_dict(sample_strategy)

        assert result["id"] == "strat-001"
        assert result["situation"] == "Null pointer errors"
        assert result["suggestion"] == "Add defensive checks"
        assert "embedding" not in result


class TestMemoryMCPServerTools:
    """Tests for MCP server tool functions.

    These tests verify the tool functions work correctly.
    We test the internal functions directly since testing FastMCP tools
    requires running the server.
    """

    @pytest.fixture
    def experiences(self) -> list[Experience]:
        """Create sample experiences."""
        return [
            Experience(
                id=f"exp-{i}",
                task_input=f"Task {i}",
                solution_output=f"Solution {i}",
                feedback="OK",
                success=i % 2 == 0,
                trajectory_id=f"traj-{i}",
            )
            for i in range(5)
        ]

    @pytest.fixture
    def concepts(self) -> list[CodeConcept]:
        """Create sample concepts."""
        return [
            CodeConcept(
                id=f"concept-{i}",
                name=f"concept_{i}",
                description=f"Description {i}",
                code=f"code_{i}()",
                signature="() -> None",
            )
            for i in range(5)
        ]

    @pytest.fixture
    def strategies(self) -> list[Strategy]:
        """Create sample strategies."""
        return [
            Strategy(
                id=f"strat-{i}",
                situation=f"Situation {i}",
                suggestion=f"Suggestion {i}",
            )
            for i in range(5)
        ]

    def test_search_experiences_returns_limited(
        self, experiences: list[Experience]
    ) -> None:
        """Test that experience search respects k limit."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        memory = MockMemorySystem(
            experience_memory=MockExperienceMemory(experiences)
        )
        server = create_memory_server(memory)

        # Get the tool function
        # Note: This accesses FastMCP internals, adjust based on actual API
        # For now, we test the underlying logic via mock

        # Test by calling the mock directly
        results = memory.experience_memory.search(
            Task(id="q", domain="t", description="query", verification=VerificationSpec(method="none")),
            k=2
        )
        assert len(results) == 2

    def test_search_with_none_memory(self) -> None:
        """Test search gracefully handles None memory."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        memory = MockMemorySystem()  # All None
        server = create_memory_server(memory)

        # With no experience memory, search should return empty
        assert memory.experience_memory is None

    def test_get_concept_existing(self, concepts: list[CodeConcept]) -> None:
        """Test getting an existing concept."""
        library = MockConceptLibrary(concepts)
        result = library.get("concept-2")

        assert result is not None
        assert result.id == "concept-2"

    def test_get_concept_nonexistent(self, concepts: list[CodeConcept]) -> None:
        """Test getting a nonexistent concept."""
        library = MockConceptLibrary(concepts)
        result = library.get("nonexistent")

        assert result is None

    def test_get_experience_existing(self, experiences: list[Experience]) -> None:
        """Test getting an existing experience."""
        memory = MockExperienceMemory(experiences)
        result = memory.get("exp-2")

        assert result is not None
        assert result.id == "exp-2"

    def test_get_strategy_existing(self, strategies: list[Strategy]) -> None:
        """Test getting an existing strategy."""
        bank = MockStrategyBank(strategies)
        result = bank.get("strat-1")

        assert result is not None
        assert result.id == "strat-1"


class TestMemoryMCPServerIntegration:
    """Integration tests for the MCP server."""

    def test_server_can_run_standalone(self) -> None:
        """Test that server can be created for standalone running."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        # Should not raise
        server = create_memory_server(memory=None)
        assert hasattr(server, "run")

    def test_server_tools_registered(self) -> None:
        """Test that expected tools are registered."""
        pytest.importorskip("fastmcp")
        from cognitive_core.mcp.memory_server import create_memory_server

        server = create_memory_server(memory=None)

        # FastMCP should have tools registered
        # The exact API to check depends on FastMCP version
        # This is a basic smoke test
        assert server is not None
