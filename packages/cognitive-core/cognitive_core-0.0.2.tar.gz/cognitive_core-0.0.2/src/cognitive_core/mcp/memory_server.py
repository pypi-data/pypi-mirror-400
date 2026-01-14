"""Memory MCP Server for exposing ATLAS memory as agent tools.

Uses FastMCP to create an MCP server with memory search tools.
Agents can use these tools mid-execution to query additional context.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from cognitive_core.core.types import CodeConcept, Experience, Strategy, Task
    from cognitive_core.protocols.memory import MemorySystem

logger = logging.getLogger("cognitive_core.mcp")


def create_memory_server(memory: MemorySystem | None = None) -> FastMCP:
    """Create MCP server with memory tools.

    Args:
        memory: The ATLAS memory system to expose. If None, tools return empty results.

    Returns:
        FastMCP server instance with memory tools.

    Example:
        ```python
        from cognitive_core.mcp import create_memory_server
        from cognitive_core.memory import MemorySystemImpl

        memory = MemorySystemImpl(...)
        server = create_memory_server(memory)

        # Run as standalone
        server.run()
        ```
    """
    try:
        from fastmcp import FastMCP
    except ImportError as e:
        raise ImportError(
            "fastmcp is required for the MCP server. "
            "Install with: pip install fastmcp"
        ) from e

    mcp = FastMCP("atlas-memory")
    _memory = memory

    @mcp.tool()
    def memory_search_experiences(query: str, k: int = 4) -> list[dict[str, Any]]:
        """Search for similar past experiences.

        Finds experiences from past task attempts that are similar to your current
        situation. Use this when you want to learn from how similar tasks were
        approached before.

        Args:
            query: Natural language description of what you're looking for.
                   Example: "fix authentication bug" or "implement sorting algorithm"
            k: Number of results to return (default: 4, max: 10)

        Returns:
            List of relevant experiences, each containing:
            - task_input: What the task was
            - solution_output: How it was approached
            - feedback: The outcome/result
            - success: Whether it succeeded
        """
        if _memory is None or _memory.experience_memory is None:
            logger.debug("Experience memory not available")
            return []

        # Clamp k to reasonable bounds
        k = max(1, min(k, 10))

        # Create a minimal task for querying
        from cognitive_core.core.types import Task, VerificationSpec

        task = Task(
            id="query",
            domain="unknown",
            description=query,
            verification=VerificationSpec(method="none"),
        )

        try:
            experiences = _memory.experience_memory.search(task, k=k)
            return [_experience_to_dict(exp) for exp in experiences]
        except Exception as e:
            logger.warning("Failed to search experiences", extra={"error": str(e)})
            return []

    @mcp.tool()
    def memory_search_concepts(query: str, k: int = 5) -> list[dict[str, Any]]:
        """Search for relevant code patterns and concepts.

        Finds reusable code patterns that might help with your current task.
        These are abstracted from successful past solutions.

        Args:
            query: Natural language description of what you need.
                   Example: "rotate grid 90 degrees" or "parse JSON safely"
            k: Number of results to return (default: 5, max: 10)

        Returns:
            List of relevant concepts, each containing:
            - name: Human-readable name
            - description: What the concept does
            - code: The actual code pattern
            - signature: Type signature
            - success_rate: How often it leads to success
        """
        if _memory is None or _memory.concept_library is None:
            logger.debug("Concept library not available")
            return []

        k = max(1, min(k, 10))

        try:
            concepts = _memory.concept_library.search(query, k=k)
            return [_concept_to_dict(concept) for concept in concepts]
        except Exception as e:
            logger.warning("Failed to search concepts", extra={"error": str(e)})
            return []

    @mcp.tool()
    def memory_search_strategies(query: str, k: int = 3) -> list[dict[str, Any]]:
        """Search for applicable high-level strategies.

        Finds abstract reasoning patterns that describe when and how to approach
        certain types of problems. These are generalized insights from past successes.

        Args:
            query: Natural language description of your situation.
                   Example: "task with symmetry patterns" or "debugging memory leak"
            k: Number of results to return (default: 3, max: 10)

        Returns:
            List of applicable strategies, each containing:
            - situation: When to apply this strategy
            - suggestion: What to do
            - success_rate: How often it works
        """
        if _memory is None or _memory.strategy_bank is None:
            logger.debug("Strategy bank not available")
            return []

        k = max(1, min(k, 10))

        # Create a minimal task for querying
        from cognitive_core.core.types import Task, VerificationSpec

        task = Task(
            id="query",
            domain="unknown",
            description=query,
            verification=VerificationSpec(method="none"),
        )

        try:
            strategies = _memory.strategy_bank.read(task, k=k)
            return [_strategy_to_dict(strategy) for strategy in strategies]
        except Exception as e:
            logger.warning("Failed to search strategies", extra={"error": str(e)})
            return []

    @mcp.tool()
    def memory_get_concept(concept_id: str) -> dict[str, Any] | None:
        """Get a specific code concept by ID.

        Retrieves full details of a concept you've seen referenced elsewhere.
        Use this when you have a concept ID and want to see its code and details.

        Args:
            concept_id: The unique concept identifier (e.g., "concept-abc123")

        Returns:
            The concept details if found, or None if not found.
            Contains: name, description, code, signature, examples, usage_count, success_rate
        """
        if _memory is None or _memory.concept_library is None:
            logger.debug("Concept library not available")
            return None

        try:
            concept = _memory.concept_library.get(concept_id)
            return _concept_to_dict(concept) if concept else None
        except Exception as e:
            logger.warning(
                "Failed to get concept",
                extra={"concept_id": concept_id, "error": str(e)},
            )
            return None

    @mcp.tool()
    def memory_get_experience(experience_id: str) -> dict[str, Any] | None:
        """Get a specific experience by ID.

        Retrieves full details of an experience you've seen referenced elsewhere.

        Args:
            experience_id: The unique experience identifier

        Returns:
            The experience details if found, or None if not found.
        """
        if _memory is None or _memory.experience_memory is None:
            logger.debug("Experience memory not available")
            return None

        try:
            experience = _memory.experience_memory.get(experience_id)
            return _experience_to_dict(experience) if experience else None
        except Exception as e:
            logger.warning(
                "Failed to get experience",
                extra={"experience_id": experience_id, "error": str(e)},
            )
            return None

    @mcp.tool()
    def memory_get_strategy(strategy_id: str) -> dict[str, Any] | None:
        """Get a specific strategy by ID.

        Retrieves full details of a strategy you've seen referenced elsewhere.

        Args:
            strategy_id: The unique strategy identifier

        Returns:
            The strategy details if found, or None if not found.
        """
        if _memory is None or _memory.strategy_bank is None:
            logger.debug("Strategy bank not available")
            return None

        try:
            strategy = _memory.strategy_bank.get(strategy_id)
            return _strategy_to_dict(strategy) if strategy else None
        except Exception as e:
            logger.warning(
                "Failed to get strategy",
                extra={"strategy_id": strategy_id, "error": str(e)},
            )
            return None

    logger.info("Memory MCP server created", extra={"tools": 6})
    return mcp


def _experience_to_dict(exp: Experience) -> dict[str, Any]:
    """Convert Experience to JSON-serializable dict.

    Omits embeddings and internal fields for cleaner output.
    """
    return {
        "id": exp.id,
        "task_input": exp.task_input,
        "solution_output": exp.solution_output,
        "feedback": exp.feedback,
        "success": exp.success,
        "trajectory_id": exp.trajectory_id,
        "timestamp": exp.timestamp.isoformat() if isinstance(exp.timestamp, datetime) else str(exp.timestamp),
        "metadata": exp.metadata,
    }


def _concept_to_dict(concept: CodeConcept) -> dict[str, Any]:
    """Convert CodeConcept to JSON-serializable dict.

    Includes code and examples for agent use.
    """
    return {
        "id": concept.id,
        "name": concept.name,
        "description": concept.description,
        "code": concept.code,
        "signature": concept.signature,
        "examples": concept.examples,
        "usage_count": concept.usage_count,
        "success_rate": concept.success_rate,
        "source": concept.source,
    }


def _strategy_to_dict(strategy: Strategy) -> dict[str, Any]:
    """Convert Strategy to JSON-serializable dict."""
    return {
        "id": strategy.id,
        "situation": strategy.situation,
        "suggestion": strategy.suggestion,
        "parameters": strategy.parameters,
        "usage_count": strategy.usage_count,
        "success_rate": strategy.success_rate,
    }


# Allow running as standalone server
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ATLAS Memory MCP Server")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    args = parser.parse_args()

    # Create server without memory (will return empty results)
    # In production, you'd pass in a real MemorySystem
    server = create_memory_server(memory=None)
    print(f"Starting ATLAS Memory MCP Server on {args.host}:{args.port}")
    print("Note: Running without memory system (tools will return empty results)")
    server.run()
