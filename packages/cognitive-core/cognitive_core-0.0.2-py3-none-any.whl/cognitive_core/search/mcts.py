"""MCTS-based search for SWE tasks.

SWESearch implements Monte Carlo Tree Search with:
- UCB selection for exploration/exploitation balance
- LLM-generated action expansion
- Hybrid value estimation (discriminator + selective rollout)

Reference: SWE-Search paper (MCTS for software engineering)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from math import log, sqrt
from typing import TYPE_CHECKING, Any

from cognitive_core.config import SWESearchConfig
from cognitive_core.core.types import Candidate

if TYPE_CHECKING:
    from cognitive_core.core.types import RoutingDecision, Task
    from cognitive_core.execution.executor import TaskExecutor
    from cognitive_core.llm.simple import SimpleLLM
    from cognitive_core.protocols.environment import Environment
    from cognitive_core.protocols.memory import MemorySystem
    from cognitive_core.search.discriminator import Discriminator

logger = logging.getLogger("cognitive_core.search.mcts")


@dataclass
class MCTSNode:
    """Node in the MCTS tree.

    Each node represents a state in the search tree. The tree is built
    incrementally via selection, expansion, simulation, and backpropagation.

    Attributes:
        state: Current state description (accumulated actions and observations)
        action: Action that led to this state (None for root)
        parent: Parent node (None for root)
        children: Child nodes from expansion
        visits: Number of times this node has been visited
        total_value: Sum of backpropagated values
        candidate: Candidate solution at this node (if leaf/terminal)
        depth: Depth in the tree (root = 0)
    """

    state: str
    action: str | None = None
    parent: MCTSNode | None = None
    children: list[MCTSNode] = field(default_factory=list)
    visits: int = 0
    total_value: float = 0.0
    candidate: Candidate | None = None
    depth: int = 0

    @property
    def value(self) -> float:
        """Average value (mean of backpropagated values)."""
        return self.total_value / max(self.visits, 1)

    def ucb_score(self, ucb_constant: float = 1.414) -> float:
        """Upper Confidence Bound score for selection.

        UCB = exploitation + exploration
            = value + c * sqrt(ln(parent.visits) / visits)

        Args:
            ucb_constant: Exploration constant (default: sqrt(2) ~ 1.414)

        Returns:
            UCB score (higher is better for selection)
        """
        if self.visits == 0:
            return float("inf")  # Prioritize unvisited nodes
        if self.parent is None or self.parent.visits == 0:
            return self.value

        exploitation = self.value
        exploration = ucb_constant * sqrt(log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, ucb_constant: float = 1.414) -> MCTSNode:
        """Select child with highest UCB score.

        Args:
            ucb_constant: Exploration constant for UCB

        Returns:
            Child node with highest UCB score

        Raises:
            ValueError: If node has no children
        """
        if not self.children:
            raise ValueError("Cannot select best child from node with no children")
        return max(self.children, key=lambda c: c.ucb_score(ucb_constant))

    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0


class SWESearch:
    """MCTS-based search for SWE tasks.

    Uses Monte Carlo Tree Search with:
    - UCB selection for exploration/exploitation balance
    - LLM-generated action expansion
    - Hybrid value estimation (discriminator + selective rollout)

    The algorithm:
    1. Initialize root with task state
    2. For each expansion (up to max_expansions):
       a. Select leaf via UCB traversal
       b. Expand with LLM-generated actions
       c. Estimate value (hybrid: discriminator + selective rollout)
       d. Backpropagate value to ancestors
    3. Return best path from root to leaf

    Cost: ~200-500 LLM calls per task (with hybrid value estimation)

    Example:
        ```python
        search = SWESearch(memory=memory, llm=llm, discriminator=discriminator)
        candidates = search.search(task, routing, env)
        ```
    """

    def __init__(
        self,
        memory: MemorySystem,
        llm: SimpleLLM,
        executor: TaskExecutor | None = None,
        discriminator: Discriminator | None = None,
        config: SWESearchConfig | None = None,
    ):
        """Initialize SWESearch.

        Args:
            memory: Memory system for context retrieval
            llm: SimpleLLM for action generation
            executor: Optional TaskExecutor for rollouts
            discriminator: Optional discriminator for value estimation
            config: Configuration (uses defaults if not provided)
        """
        self._memory = memory
        self._llm = llm
        self._executor = executor
        self._discriminator = discriminator
        self._config = config or SWESearchConfig()

    def search(
        self,
        task: Task,
        routing: RoutingDecision,
        env: Environment,
    ) -> list[Candidate]:
        """Run MCTS search.

        Args:
            task: The task to solve
            routing: Routing decision with strategy and context
            env: Environment for verification

        Returns:
            List of candidate solutions, ranked by fitness
        """
        logger.info(
            "SWESearch starting",
            extra={
                "task_id": task.id,
                "max_expansions": self._config.max_expansions,
                "max_depth": self._config.max_depth,
            },
        )

        root = self._create_root(task, env)

        for iteration in range(self._config.max_expansions):
            # Selection: traverse tree via UCB
            leaf = self._select(root)

            # Expansion: if visited before and not at max depth
            if leaf.visits > 0 and leaf.depth < self._config.max_depth:
                children = self._expand(leaf, task, env)
                if children:
                    leaf.children.extend(children)
                    leaf = children[0]  # Select first child for evaluation

            # Value estimation: hybrid approach
            value = self._estimate_value(leaf, task, env)

            # Backpropagation: update ancestors
            self._backpropagate(leaf, value)

            logger.debug(
                "MCTS iteration complete",
                extra={
                    "iteration": iteration,
                    "leaf_depth": leaf.depth,
                    "value": value,
                    "root_visits": root.visits,
                },
            )

            # Early termination on success
            if value >= 1.0:
                logger.info(
                    "Early termination: found successful path",
                    extra={"iteration": iteration},
                )
                break

        candidates = self._extract_best_candidates(root, task)
        logger.info(
            "SWESearch complete",
            extra={
                "task_id": task.id,
                "candidates": len(candidates),
                "total_visits": root.visits,
            },
        )
        return candidates

    def refine(
        self,
        candidate: Candidate,
        feedback: str,
        task: Task,
    ) -> Candidate:
        """Refine candidate via targeted action generation.

        Uses feedback to generate improved actions.

        Args:
            candidate: The candidate to refine
            feedback: Feedback from verification
            task: The original task

        Returns:
            Refined candidate
        """
        prompt = f"""You are refining a solution based on feedback.

Task: {task.description}

Current solution:
{candidate.solution}

Feedback: {feedback}

Generate an improved solution that addresses the feedback.
Return the complete improved solution:
"""

        try:
            refined_solution = self._llm.generate(prompt)
            return Candidate(
                solution=refined_solution,
                confidence=candidate.confidence * 0.9,
                reasoning=f"Refined based on feedback: {feedback[:100]}",
                source="adapted",
                fitness=None,
                parent_ids=[str(id(candidate))],
            )
        except Exception as e:
            logger.warning("Refinement failed", extra={"error": str(e)})
            return candidate

    @property
    def name(self) -> str:
        """Name of this search method."""
        return "mcts"

    def _create_root(self, task: Task, env: Environment) -> MCTSNode:
        """Create root node for the search tree.

        Args:
            task: The task to solve
            env: Environment (for initial state)

        Returns:
            Root MCTSNode
        """
        initial_state = f"""Task: {task.description}

Context:
{self._format_context(task)}

Starting state: Ready to investigate and fix the issue.
"""
        return MCTSNode(state=initial_state, depth=0)

    def _format_context(self, task: Task) -> str:
        """Format task context for state description."""
        context = task.context or {}
        parts = []
        if repo := context.get("repo"):
            parts.append(f"Repository: {repo}")
        if base_commit := context.get("base_commit"):
            parts.append(f"Base commit: {base_commit}")
        if test_cmd := context.get("test_cmd"):
            parts.append(f"Test command: {test_cmd}")
        return "\n".join(parts) if parts else "No additional context"

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select leaf node via UCB traversal.

        Traverses the tree, selecting children with highest UCB score
        until reaching a leaf or unvisited node.

        Args:
            node: Starting node (typically root)

        Returns:
            Selected leaf node
        """
        current = node
        while not current.is_leaf() and current.visits > 0:
            current = current.best_child(self._config.ucb_constant)
        return current

    def _expand(
        self,
        node: MCTSNode,
        task: Task,
        env: Environment,
    ) -> list[MCTSNode]:
        """Expand node with LLM-generated actions.

        Generates 2-3 promising next actions using the LLM.

        Args:
            node: Node to expand
            task: The task being solved
            env: Environment for context

        Returns:
            List of child nodes
        """
        prompt = f"""You are debugging a software issue.

Task: {task.description}

Current state:
{node.state}

What are 2-3 promising next actions? Format each as:
ACTION: <description>
CONTENT: <patch or command>
---
"""

        try:
            response = self._llm.generate(prompt)
            actions = self._parse_actions(response)
        except Exception as e:
            logger.warning("LLM expansion failed", extra={"error": str(e)})
            return []

        children = []
        for action, content in actions:
            new_state = f"{node.state}\n\nAction: {action}\n{content}"
            child = MCTSNode(
                state=new_state,
                action=content,
                parent=node,
                depth=node.depth + 1,
            )
            children.append(child)

        logger.debug(
            "Expanded node",
            extra={"parent_depth": node.depth, "num_children": len(children)},
        )
        return children

    def _parse_actions(self, response: str) -> list[tuple[str, str]]:
        """Parse LLM response into action tuples.

        Expected format:
        ACTION: <description>
        CONTENT: <patch or command>
        ---

        Args:
            response: LLM response text

        Returns:
            List of (action_description, content) tuples
        """
        actions = []
        # Split by standalone --- delimiter (on its own line or at end)
        # This avoids splitting on --- within unified diffs
        parts = re.split(r"\n---\s*(?:\n|$)", response)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Extract ACTION and CONTENT
            action_match = re.search(r"ACTION:\s*(.+?)(?=\nCONTENT:|$)", part, re.DOTALL)
            content_match = re.search(r"CONTENT:\s*(.+)", part, re.DOTALL)

            if action_match:
                action = action_match.group(1).strip()
                content = content_match.group(1).strip() if content_match else ""
                actions.append((action, content))

        return actions

    def _estimate_value(
        self,
        node: MCTSNode,
        task: Task,
        env: Environment,
    ) -> float:
        """Hybrid value estimation: discriminator + selective rollout.

        1. Use discriminator for quick estimate
        2. If promising (above threshold), do agent rollout
        3. Fallback to environment verification

        Args:
            node: Node to evaluate
            task: The task being solved
            env: Environment for verification

        Returns:
            Estimated value (0.0 to 1.0)
        """
        candidate = self._node_to_candidate(node)
        node.candidate = candidate  # Store for later extraction

        if self._discriminator and self._config.use_discriminator:
            # Quick LLM-based estimate
            quick_score = self._discriminator.estimate(task, candidate)

            # If promising, do expensive rollout
            if self._discriminator.should_rollout(
                quick_score, self._config.discriminator_threshold
            ):
                try:
                    import asyncio

                    try:
                        loop = asyncio.get_running_loop()
                        # Already in async context - fall back to quick score
                        return quick_score
                    except RuntimeError:
                        # No running loop - safe to use asyncio.run
                        return asyncio.run(
                            self._discriminator.estimate_with_rollout(
                                task, candidate, env, depth=self._config.rollout_depth
                            )
                        )
                except Exception as e:
                    logger.warning(
                        "Rollout failed, using quick score",
                        extra={"error": str(e)},
                    )
                    return quick_score
            return quick_score

        # Fallback: direct verification
        try:
            outcome = env.verify(candidate.solution)
            return outcome.partial_score or 0.0
        except Exception as e:
            logger.warning("Verification failed", extra={"error": str(e)})
            return 0.0

    def _node_to_candidate(self, node: MCTSNode) -> Candidate:
        """Convert node to candidate solution.

        Extracts the solution from the accumulated actions in the node's state.

        Args:
            node: Node to convert

        Returns:
            Candidate with solution and metadata
        """
        # Extract solution from actions
        solution = self._extract_solution(node)

        return Candidate(
            solution=solution,
            confidence=0.5 + (0.5 * node.value) if node.visits > 0 else 0.5,
            reasoning=f"MCTS path at depth {node.depth}",
            source="generated",
            fitness=node.value if node.visits > 0 else None,
        )

    def _extract_solution(self, node: MCTSNode) -> str:
        """Extract solution from node's accumulated state.

        Args:
            node: Node to extract from

        Returns:
            Solution string (patch or final action)
        """
        # Get the action from this node or traverse to find meaningful content
        if node.action:
            return node.action

        # If no action, return the state difference from root
        parts = node.state.split("\n\nAction:")
        if len(parts) > 1:
            return "\n\nAction:".join(parts[1:])
        return node.state

    def _backpropagate(self, node: MCTSNode, value: float) -> None:
        """Backpropagate value to ancestors.

        Updates visit counts and total values for all nodes
        from the given node back to the root.

        Args:
            node: Starting node
            value: Value to backpropagate
        """
        current: MCTSNode | None = node
        while current is not None:
            current.visits += 1
            current.total_value += value
            current = current.parent

    def _extract_best_candidates(
        self,
        root: MCTSNode,
        task: Task,
    ) -> list[Candidate]:
        """Extract best candidates from the search tree.

        Follows highest-value paths and collects candidates.

        Args:
            root: Root of the search tree
            task: The task (for metadata)

        Returns:
            List of candidates sorted by fitness
        """
        candidates = []
        visited = set()

        def collect_candidates(node: MCTSNode) -> None:
            """Recursively collect candidates from tree."""
            node_id = id(node)
            if node_id in visited:
                return
            visited.add(node_id)

            # Add candidate if it has been evaluated
            if node.candidate and node.visits > 0:
                candidates.append(node.candidate)

            # Recurse into children
            for child in node.children:
                collect_candidates(child)

        collect_candidates(root)

        # Sort by fitness (highest first)
        candidates.sort(key=lambda c: c.fitness or 0.0, reverse=True)

        # If no candidates with fitness, create one from best path
        if not candidates:
            best_path = self._get_best_path(root)
            if best_path:
                leaf = best_path[-1]
                candidates.append(self._node_to_candidate(leaf))

        logger.debug(
            "Extracted candidates",
            extra={"count": len(candidates)},
        )
        return candidates

    def _get_best_path(self, root: MCTSNode) -> list[MCTSNode]:
        """Get the best path from root to leaf.

        Follows the highest average value children.

        Args:
            root: Root of the search tree

        Returns:
            List of nodes from root to best leaf
        """
        path = [root]
        current = root

        while current.children:
            # Select best child by average value
            best = max(
                current.children, key=lambda c: c.value if c.visits > 0 else -float("inf")
            )
            path.append(best)
            current = best

        return path
