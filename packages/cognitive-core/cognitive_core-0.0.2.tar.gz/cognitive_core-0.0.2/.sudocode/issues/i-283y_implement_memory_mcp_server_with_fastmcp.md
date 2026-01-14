---
id: i-283y
title: Implement Memory MCP Server with FastMCP
priority: 1
created_at: '2026-01-07 08:55:55'
tags:
  - fastmcp
  - mcp
  - memory
  - phase-2
status: open
---
# Implement Memory MCP Server

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Create MCP server that exposes ATLAS memory as tools for agents using FastMCP.

## Files to Create

- `src/atlas/mcp/__init__.py`
- `src/atlas/mcp/memory_server.py`

## Dependencies

- `fastmcp` package

## Tools to Expose

| Tool | Description |
|------|-------------|
| `memory_search_experiences` | Find similar past experiences |
| `memory_search_concepts` | Find relevant code patterns |
| `memory_search_strategies` | Find applicable strategies |
| `memory_get_concept` | Get specific concept by ID |

## Implementation

```python
from fastmcp import FastMCP
from atlas.protocols.memory import MemorySystem

def create_memory_server(memory: MemorySystem) -> FastMCP:
    """Create MCP server with memory tools."""
    
    mcp = FastMCP("atlas-memory")
    
    @mcp.tool()
    def memory_search_experiences(query: str, k: int = 4) -> list[dict]:
        """Search for similar past experiences.
        
        Args:
            query: Natural language description of what you're looking for
            k: Number of results to return (default: 4)
        
        Returns:
            List of relevant experiences with task, solution, and outcome
        """
        if memory.experience_memory is None:
            return []
        experiences = memory.experience_memory.search_by_text(query, k=k)
        return [_experience_to_dict(exp) for exp in experiences]
    
    @mcp.tool()
    def memory_search_concepts(query: str, k: int = 5) -> list[dict]:
        """Search for relevant code patterns and concepts."""
        if memory.concept_library is None:
            return []
        concepts = memory.concept_library.search(query, k=k)
        return [_concept_to_dict(c) for c in concepts]
    
    @mcp.tool()
    def memory_search_strategies(query: str, k: int = 3) -> list[dict]:
        """Search for applicable high-level strategies."""
        if memory.strategy_bank is None:
            return []
        strategies = memory.strategy_bank.read_by_text(query, k=k)
        return [_strategy_to_dict(s) for s in strategies]
    
    @mcp.tool()
    def memory_get_concept(concept_id: str) -> dict | None:
        """Get a specific code concept by ID."""
        if memory.concept_library is None:
            return None
        concept = memory.concept_library.get(concept_id)
        return _concept_to_dict(concept) if concept else None
    
    return mcp

def _experience_to_dict(exp) -> dict:
    ...

def _concept_to_dict(concept) -> dict:
    ...

def _strategy_to_dict(strategy) -> dict:
    ...
```

## Notes

- Memory system may not be fully implemented yet (Phase 3)
- For now, tools should gracefully return empty results if memory components are None
- Server should be runnable standalone for testing

## Acceptance Criteria

- [ ] FastMCP server created with all 4 tools
- [ ] Tools have proper docstrings (shown to agents)
- [ ] Graceful handling when memory components are None
- [ ] Returns properly serialized dicts
- [ ] Can run server standalone for testing
- [ ] Unit tests for tool functions
