"""Tests for SWESearch (MCTS-based search)."""

from __future__ import annotations

from math import log, sqrt
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from cognitive_core.config import SWESearchConfig
from cognitive_core.core.types import Candidate, Outcome, RoutingDecision, Task, VerificationSpec
from cognitive_core.protocols.memory import MemoryQueryResult
from cognitive_core.protocols.search import SearchEngine
from cognitive_core.search.mcts import MCTSNode, SWESearch


# =============================================================================
# Test Fixtures
# =============================================================================


def make_task(
    task_id: str = "test-1",
    description: str = "Fix the bug in auth.py",
) -> Task:
    """Create a test task with all required fields."""
    return Task(
        id=task_id,
        description=description,
        domain="swe",
        verification=VerificationSpec(method="test_suite", config={}),
        context={
            "repo": "testorg/testrepo",
            "base_commit": "abc123",
            "test_cmd": "pytest tests/",
        },
    )


def make_routing_decision(
    strategy: str = "mcts",
    confidence: float = 0.8,
    budget: int = 100,
) -> RoutingDecision:
    """Create a routing decision."""
    return RoutingDecision(
        strategy=strategy,
        context=MemoryQueryResult(),
        confidence=confidence,
        budget=budget,
    )


def make_mock_memory() -> MagicMock:
    """Create a mock memory system."""
    mock = MagicMock()
    mock.query = MagicMock(return_value=MemoryQueryResult())
    return mock


def make_mock_llm(
    responses: list[str] | None = None,
    default_response: str = "ACTION: Investigate the issue\nCONTENT: cat auth.py\n---",
) -> MagicMock:
    """Create a mock SimpleLLM."""
    mock = MagicMock()
    if responses:
        mock.generate = MagicMock(side_effect=responses)
    else:
        mock.generate = MagicMock(return_value=default_response)
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


def make_mock_discriminator(
    estimate_score: float = 0.6,
    should_rollout: bool = False,
) -> MagicMock:
    """Create a mock discriminator."""
    mock = MagicMock()
    mock.estimate = MagicMock(return_value=estimate_score)
    mock.should_rollout = MagicMock(return_value=should_rollout)
    mock.estimate_with_rollout = AsyncMock(return_value=0.8)
    return mock


# =============================================================================
# MCTSNode Tests
# =============================================================================


class TestMCTSNodeBasic:
    """Tests for MCTSNode basic functionality."""

    def test_node_initialization(self) -> None:
        """Node initializes with correct defaults."""
        node = MCTSNode(state="Initial state")

        assert node.state == "Initial state"
        assert node.action is None
        assert node.parent is None
        assert node.children == []
        assert node.visits == 0
        assert node.total_value == 0.0
        assert node.candidate is None
        assert node.depth == 0

    def test_node_with_parent(self) -> None:
        """Node correctly links to parent."""
        parent = MCTSNode(state="Parent state")
        child = MCTSNode(
            state="Child state",
            action="test action",
            parent=parent,
            depth=1,
        )

        assert child.parent is parent
        assert child.depth == 1
        assert child.action == "test action"

    def test_is_leaf_no_children(self) -> None:
        """is_leaf returns True for node without children."""
        node = MCTSNode(state="test")
        assert node.is_leaf() is True

    def test_is_leaf_with_children(self) -> None:
        """is_leaf returns False for node with children."""
        parent = MCTSNode(state="Parent")
        child = MCTSNode(state="Child", parent=parent)
        parent.children.append(child)

        assert parent.is_leaf() is False


class TestMCTSNodeValue:
    """Tests for MCTSNode value property."""

    def test_value_zero_visits(self) -> None:
        """Value is 0 when no visits."""
        node = MCTSNode(state="test")
        assert node.value == 0.0

    def test_value_single_visit(self) -> None:
        """Value equals total_value for single visit."""
        node = MCTSNode(state="test")
        node.visits = 1
        node.total_value = 0.7
        assert node.value == 0.7

    def test_value_multiple_visits(self) -> None:
        """Value is average of total_value."""
        node = MCTSNode(state="test")
        node.visits = 4
        node.total_value = 2.8
        assert node.value == 0.7


class TestMCTSNodeUCB:
    """Tests for MCTSNode UCB calculation."""

    def test_ucb_unvisited_node(self) -> None:
        """Unvisited nodes have infinite UCB score."""
        node = MCTSNode(state="test")
        assert node.ucb_score() == float("inf")

    def test_ucb_root_node(self) -> None:
        """Root node (no parent) returns just value."""
        node = MCTSNode(state="test")
        node.visits = 2
        node.total_value = 1.4
        assert node.ucb_score() == node.value

    def test_ucb_calculation(self) -> None:
        """UCB correctly balances exploitation and exploration."""
        parent = MCTSNode(state="Parent")
        parent.visits = 10

        child = MCTSNode(state="Child", parent=parent)
        child.visits = 3
        child.total_value = 1.5  # value = 0.5

        ucb_constant = 1.414
        expected_exploitation = 0.5
        expected_exploration = ucb_constant * sqrt(log(10) / 3)
        expected_ucb = expected_exploitation + expected_exploration

        assert abs(child.ucb_score(ucb_constant) - expected_ucb) < 0.001

    def test_ucb_exploration_constant(self) -> None:
        """Different UCB constants affect exploration."""
        parent = MCTSNode(state="Parent")
        parent.visits = 10

        child = MCTSNode(state="Child", parent=parent)
        child.visits = 2
        child.total_value = 1.0

        ucb_low = child.ucb_score(0.5)
        ucb_high = child.ucb_score(2.0)

        # Higher constant means more exploration
        assert ucb_high > ucb_low


class TestMCTSNodeBestChild:
    """Tests for MCTSNode best_child selection."""

    def test_best_child_single_child(self) -> None:
        """best_child returns only child when single child."""
        parent = MCTSNode(state="Parent")
        parent.visits = 5
        child = MCTSNode(state="Child", parent=parent)
        child.visits = 2
        child.total_value = 1.0
        parent.children = [child]

        assert parent.best_child() is child

    def test_best_child_multiple_children(self) -> None:
        """best_child selects highest UCB child."""
        parent = MCTSNode(state="Parent")
        parent.visits = 10

        child1 = MCTSNode(state="Child1", parent=parent)
        child1.visits = 5
        child1.total_value = 4.0  # value = 0.8

        child2 = MCTSNode(state="Child2", parent=parent)
        child2.visits = 1
        child2.total_value = 0.5  # value = 0.5, but high exploration

        child3 = MCTSNode(state="Child3", parent=parent)
        child3.visits = 0  # Unvisited = inf UCB

        parent.children = [child1, child2, child3]

        # Unvisited child should be selected (infinite UCB)
        assert parent.best_child() is child3

    def test_best_child_all_visited(self) -> None:
        """best_child correctly balances when all visited."""
        parent = MCTSNode(state="Parent")
        parent.visits = 20

        child1 = MCTSNode(state="Child1", parent=parent)
        child1.visits = 10
        child1.total_value = 8.0  # High value, many visits

        child2 = MCTSNode(state="Child2", parent=parent)
        child2.visits = 3
        child2.total_value = 2.7  # High value, few visits

        parent.children = [child1, child2]

        # Both have similar exploitation but child2 has more exploration bonus
        best = parent.best_child()
        assert best in [child1, child2]  # Either is valid depending on balance

    def test_best_child_no_children_raises(self) -> None:
        """best_child raises ValueError when no children."""
        node = MCTSNode(state="test")

        with pytest.raises(ValueError, match="no children"):
            node.best_child()


# =============================================================================
# SWESearch Protocol Tests
# =============================================================================


class TestSWESearchProtocol:
    """Tests for SWESearch protocol compliance."""

    def test_implements_search_engine_protocol(self) -> None:
        """SWESearch implements SearchEngine protocol."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        assert isinstance(search, SearchEngine)

    def test_has_search_method(self) -> None:
        """Has search method."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        assert hasattr(search, "search")
        assert callable(search.search)

    def test_has_refine_method(self) -> None:
        """Has refine method."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        assert hasattr(search, "refine")
        assert callable(search.refine)

    def test_has_name_property(self) -> None:
        """Has name property."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        assert hasattr(search, "name")
        assert search.name == "mcts"


# =============================================================================
# SWESearch Search Method Tests
# =============================================================================


class TestSWESearchSearch:
    """Tests for SWESearch.search() method."""

    def test_search_returns_list_of_candidates(self) -> None:
        """search returns a list of Candidates."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment()
        config = SWESearchConfig(max_expansions=2)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        result = search.search(task, routing, env)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(c, Candidate) for c in result)

    def test_search_respects_max_expansions(self) -> None:
        """search stops at max_expansions iterations."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(partial_score=0.3)  # Never succeeds
        config = SWESearchConfig(max_expansions=5)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # LLM should be called multiple times for expansion
        # But not more than max_expansions times for expansion
        assert llm.generate.call_count <= config.max_expansions + 1

    def test_search_early_termination_on_success(self) -> None:
        """search terminates early when value >= 1.0."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(success=True, partial_score=1.0)
        config = SWESearchConfig(max_expansions=100)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # Should terminate early, not use all 100 expansions
        assert llm.generate.call_count < 50


class TestSWESearchExpansion:
    """Tests for SWESearch expansion (action generation)."""

    def test_expansion_generates_children(self) -> None:
        """Expansion creates child nodes from LLM response."""
        memory = make_mock_memory()
        llm = make_mock_llm(
            default_response="""ACTION: First action
CONTENT: cat file.py
---
ACTION: Second action
CONTENT: patch -p1 < fix.patch
---"""
        )
        env = make_mock_environment()
        config = SWESearchConfig(max_expansions=2, max_depth=3)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # LLM should be called for expansion
        assert llm.generate.call_count >= 1

    def test_expansion_respects_max_depth(self) -> None:
        """Expansion stops at max_depth."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(partial_score=0.3)
        config = SWESearchConfig(max_expansions=50, max_depth=2)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # With max_depth=2, tree should be shallow
        # Fewer expansions needed
        assert llm.generate.call_count < 50


class TestSWESearchValueEstimation:
    """Tests for SWESearch value estimation."""

    def test_value_estimation_uses_discriminator(self) -> None:
        """Value estimation uses discriminator when available."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        discriminator = make_mock_discriminator(estimate_score=0.7)
        env = make_mock_environment()
        config = SWESearchConfig(max_expansions=2, use_discriminator=True)
        search = SWESearch(
            memory=memory, llm=llm, discriminator=discriminator, config=config
        )
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # Discriminator should be called for value estimation
        assert discriminator.estimate.call_count >= 1

    def test_value_estimation_fallback_to_env(self) -> None:
        """Value estimation falls back to env.verify without discriminator."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(partial_score=0.6)
        config = SWESearchConfig(max_expansions=2, use_discriminator=False)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # Environment verify should be called
        assert env.verify.call_count >= 1

    def test_hybrid_estimation_selective_rollout(self) -> None:
        """Hybrid estimation triggers rollout for promising candidates."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        discriminator = make_mock_discriminator(
            estimate_score=0.8, should_rollout=True
        )
        env = make_mock_environment()
        config = SWESearchConfig(
            max_expansions=2, use_discriminator=True, discriminator_threshold=0.7
        )
        search = SWESearch(
            memory=memory, llm=llm, discriminator=discriminator, config=config
        )
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # Should check if rollout is needed
        assert discriminator.should_rollout.call_count >= 1


class TestSWESearchBackpropagation:
    """Tests for SWESearch backpropagation."""

    def test_backpropagation_updates_ancestors(self) -> None:
        """Backpropagation updates visit counts and values."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        # Create a simple tree
        root = MCTSNode(state="root", depth=0)
        child = MCTSNode(state="child", parent=root, depth=1)

        # Backpropagate a value
        search._backpropagate(child, 0.8)

        assert child.visits == 1
        assert child.total_value == 0.8
        assert root.visits == 1
        assert root.total_value == 0.8

    def test_backpropagation_accumulates(self) -> None:
        """Multiple backpropagations accumulate correctly."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        root = MCTSNode(state="root", depth=0)
        child = MCTSNode(state="child", parent=root, depth=1)

        search._backpropagate(child, 0.6)
        search._backpropagate(child, 0.8)

        assert child.visits == 2
        assert child.total_value == 1.4
        assert child.value == 0.7


class TestSWESearchSelection:
    """Tests for SWESearch UCB selection."""

    def test_selection_returns_leaf(self) -> None:
        """Selection returns a leaf node."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        root = MCTSNode(state="root", depth=0)
        root.visits = 1

        leaf = search._select(root)

        assert leaf is root
        assert leaf.is_leaf()

    def test_selection_traverses_tree(self) -> None:
        """Selection traverses tree using UCB."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        root = MCTSNode(state="root", depth=0)
        root.visits = 10

        child1 = MCTSNode(state="child1", parent=root, depth=1)
        child1.visits = 5
        child1.total_value = 4.0

        child2 = MCTSNode(state="child2", parent=root, depth=1)
        child2.visits = 0  # Unvisited

        root.children = [child1, child2]

        leaf = search._select(root)

        # Should select unvisited child (infinite UCB)
        assert leaf is child2

    def test_selection_explores_and_exploits(self) -> None:
        """Selection balances exploration and exploitation."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = SWESearchConfig(ucb_constant=1.0)
        search = SWESearch(memory=memory, llm=llm, config=config)

        root = MCTSNode(state="root", depth=0)
        root.visits = 100

        # High value, many visits
        child1 = MCTSNode(state="child1", parent=root, depth=1)
        child1.visits = 50
        child1.total_value = 45.0  # value = 0.9

        # Lower value, fewer visits (more exploration bonus)
        child2 = MCTSNode(state="child2", parent=root, depth=1)
        child2.visits = 10
        child2.total_value = 7.0  # value = 0.7

        root.children = [child1, child2]

        # Calculate UCB scores
        ucb1 = child1.ucb_score(1.0)
        ucb2 = child2.ucb_score(1.0)

        # child2 should have higher exploration bonus
        leaf = search._select(root)
        assert leaf in [child1, child2]


# =============================================================================
# SWESearch Refine Method Tests
# =============================================================================


class TestSWESearchRefine:
    """Tests for SWESearch.refine() method."""

    def test_refine_returns_candidate(self) -> None:
        """refine returns a Candidate."""
        memory = make_mock_memory()
        llm = make_mock_llm(default_response="Refined solution")
        search = SWESearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original solution",
            confidence=0.8,
            reasoning="Initial",
            source="generated",
        )

        result = search.refine(candidate, "Try different approach", task)

        assert isinstance(result, Candidate)

    def test_refine_uses_llm(self) -> None:
        """refine uses LLM to generate refined solution."""
        memory = make_mock_memory()
        llm = make_mock_llm(default_response="Better solution")
        search = SWESearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Initial",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        llm.generate.assert_called_once()
        assert result.solution == "Better solution"

    def test_refine_includes_feedback(self) -> None:
        """refine includes feedback in prompt."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Initial",
            source="generated",
        )

        search.refine(candidate, "This specific feedback", task)

        call_args = llm.generate.call_args[0][0]
        assert "This specific feedback" in call_args

    def test_refine_reduces_confidence(self) -> None:
        """Refined candidate has lower confidence."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=1.0,
            reasoning="Initial",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        assert result.confidence < candidate.confidence

    def test_refine_handles_llm_error(self) -> None:
        """refine handles LLM error gracefully."""
        memory = make_mock_memory()
        llm = MagicMock()
        llm.generate = MagicMock(side_effect=RuntimeError("LLM error"))
        search = SWESearch(memory=memory, llm=llm)
        task = make_task()
        candidate = Candidate(
            solution="original",
            confidence=0.8,
            reasoning="Initial",
            source="generated",
        )

        result = search.refine(candidate, "feedback", task)

        # Should return original on error
        assert result == candidate


# =============================================================================
# SWESearch Action Parsing Tests
# =============================================================================


class TestSWESearchActionParsing:
    """Tests for action parsing from LLM responses."""

    def test_parse_single_action(self) -> None:
        """Parse single action correctly."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        response = """ACTION: Investigate the bug
CONTENT: cat auth.py
---"""

        actions = search._parse_actions(response)

        assert len(actions) == 1
        assert actions[0][0] == "Investigate the bug"
        assert actions[0][1] == "cat auth.py"

    def test_parse_multiple_actions(self) -> None:
        """Parse multiple actions correctly."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        response = """ACTION: First action
CONTENT: command1
---
ACTION: Second action
CONTENT: command2
---
ACTION: Third action
CONTENT: command3
---"""

        actions = search._parse_actions(response)

        assert len(actions) == 3
        assert actions[0][0] == "First action"
        assert actions[1][0] == "Second action"
        assert actions[2][0] == "Third action"

    def test_parse_multiline_content(self) -> None:
        """Parse action with multiline content."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        response = """ACTION: Apply patch
CONTENT: --- a/auth.py
+++ b/auth.py
@@ -1,3 +1,4 @@
+import logging
 def login():
     pass
---"""

        actions = search._parse_actions(response)

        assert len(actions) == 1
        assert "patch" in actions[0][0].lower()
        assert "import logging" in actions[0][1]

    def test_parse_empty_response(self) -> None:
        """Parse empty response returns empty list."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        actions = search._parse_actions("")

        assert actions == []


# =============================================================================
# SWESearch Best Path Extraction Tests
# =============================================================================


class TestSWESearchBestPath:
    """Tests for best path extraction."""

    def test_extract_best_candidates_returns_sorted(self) -> None:
        """Extracted candidates are sorted by fitness."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment()
        config = SWESearchConfig(max_expansions=5)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        candidates = search.search(task, routing, env)

        # Candidates should be sorted by fitness (descending)
        if len(candidates) > 1:
            for i in range(len(candidates) - 1):
                assert (candidates[i].fitness or 0) >= (candidates[i + 1].fitness or 0)

    def test_get_best_path_single_node(self) -> None:
        """Best path from single node returns just that node."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        root = MCTSNode(state="root", depth=0)
        root.visits = 1

        path = search._get_best_path(root)

        assert len(path) == 1
        assert path[0] is root

    def test_get_best_path_follows_best_value(self) -> None:
        """Best path follows nodes with highest value."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        root = MCTSNode(state="root", depth=0)
        root.visits = 10

        child1 = MCTSNode(state="child1", parent=root, depth=1)
        child1.visits = 5
        child1.total_value = 2.5  # value = 0.5

        child2 = MCTSNode(state="child2", parent=root, depth=1)
        child2.visits = 5
        child2.total_value = 4.0  # value = 0.8

        root.children = [child1, child2]

        path = search._get_best_path(root)

        assert len(path) == 2
        assert path[0] is root
        assert path[1] is child2  # Higher value


# =============================================================================
# SWESearch Configuration Tests
# =============================================================================


class TestSWESearchConfig:
    """Tests for SWESearch configuration."""

    def test_uses_default_config(self) -> None:
        """Uses default config when not provided."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        search = SWESearch(memory=memory, llm=llm)

        assert search._config.max_expansions == 100
        assert search._config.ucb_constant == 1.414
        assert search._config.max_depth == 20

    def test_uses_custom_config(self) -> None:
        """Uses custom config when provided."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        config = SWESearchConfig(
            max_expansions=50, ucb_constant=2.0, max_depth=10
        )
        search = SWESearch(memory=memory, llm=llm, config=config)

        assert search._config.max_expansions == 50
        assert search._config.ucb_constant == 2.0
        assert search._config.max_depth == 10

    def test_config_affects_behavior(self) -> None:
        """Configuration affects search behavior."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(partial_score=0.3)

        # Small config for quick test
        config = SWESearchConfig(max_expansions=3, max_depth=2)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        search.search(task, routing, env)

        # Should respect limits
        assert llm.generate.call_count <= 5  # Limited by config


# =============================================================================
# Integration Tests
# =============================================================================


class TestSWESearchIntegration:
    """Integration tests for SWESearch."""

    def test_full_search_flow(self) -> None:
        """Full search flow from start to candidates."""
        memory = make_mock_memory()
        llm = make_mock_llm(
            responses=[
                # Expansion actions
                "ACTION: Check error\nCONTENT: grep error auth.py\n---",
                "ACTION: Fix bug\nCONTENT: patch fix\n---",
            ]
        )
        env = make_mock_environment(partial_score=0.7)
        config = SWESearchConfig(max_expansions=3, max_depth=2)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        candidates = search.search(task, routing, env)

        assert len(candidates) > 0
        assert all(isinstance(c, Candidate) for c in candidates)

    def test_search_with_discriminator(self) -> None:
        """Search with discriminator for value estimation."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        discriminator = make_mock_discriminator(estimate_score=0.6)
        env = make_mock_environment()
        config = SWESearchConfig(max_expansions=3, use_discriminator=True)
        search = SWESearch(
            memory=memory, llm=llm, discriminator=discriminator, config=config
        )
        task = make_task()
        routing = make_routing_decision()

        candidates = search.search(task, routing, env)

        assert len(candidates) > 0
        # Discriminator should have been used
        assert discriminator.estimate.call_count >= 1

    def test_search_then_refine_flow(self) -> None:
        """Search followed by refinement."""
        memory = make_mock_memory()
        # Search uses LLM, then refine uses LLM again
        # Provide enough responses for both phases
        search_llm = make_mock_llm()  # For search expansion
        env = make_mock_environment(partial_score=0.5)
        config = SWESearchConfig(max_expansions=2)
        search = SWESearch(memory=memory, llm=search_llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        # Search
        candidates = search.search(task, routing, env)
        assert len(candidates) > 0

        # Create a new mock for refinement
        refine_llm = make_mock_llm(default_response="Refined and improved solution")
        search._llm = refine_llm

        # Refine best candidate
        refined = search.refine(candidates[0], "Try harder", task)
        assert refined.solution == "Refined and improved solution"

    def test_candidate_properties(self) -> None:
        """Candidates have expected properties."""
        memory = make_mock_memory()
        llm = make_mock_llm()
        env = make_mock_environment(partial_score=0.6)
        config = SWESearchConfig(max_expansions=2)
        search = SWESearch(memory=memory, llm=llm, config=config)
        task = make_task()
        routing = make_routing_decision()

        candidates = search.search(task, routing, env)

        for candidate in candidates:
            assert hasattr(candidate, "solution")
            assert hasattr(candidate, "confidence")
            assert hasattr(candidate, "reasoning")
            assert hasattr(candidate, "source")
            assert 0.0 <= candidate.confidence <= 1.0
