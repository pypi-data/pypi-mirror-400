---
id: i-13t1
title: Phase 3 integration tests
priority: 2
created_at: '2026-01-08 00:05:03'
tags:
  - integration
  - memory
  - phase-3
  - testing
status: open
---
## Overview

Comprehensive integration tests for Phase 3 memory implementations.

## Scope

### File: `tests/integration/test_memory_integration.py`

**End-to-end flow tests:**

```python
class TestMemoryIntegration:
    """Integration tests for memory system."""
    
    @pytest.fixture
    def memory_system(self, tmp_path):
        """Create full memory system with ephemeral ChromaDB."""
        ...
    
    async def test_store_and_retrieve_experience(self, memory_system):
        """Store trajectory, retrieve by similar task."""
        ...
    
    async def test_store_success_creates_strategy(self, memory_system):
        """Successful trajectory creates strategy."""
        ...
    
    async def test_store_failure_no_strategy(self, memory_system):
        """Failed trajectory doesn't create strategy."""
        ...
    
    async def test_parallel_query(self, memory_system):
        """Query all components in parallel."""
        ...
    
    async def test_concept_search_includes_primitives(self, memory_system):
        """Concept search returns primitives."""
        ...
```

**Ablation test fixtures:**

```python
class TestAblationConfigurations:
    """Test various component combinations."""
    
    async def test_experience_only(self):
        """Memory system with only ExperienceMemory."""
        ...
    
    async def test_concepts_only(self):
        """Memory system with only ConceptLibrary."""
        ...
    
    async def test_strategies_only(self):
        """Memory system with only StrategyBank."""
        ...
    
    async def test_no_components(self):
        """Memory system with no components (edge case)."""
        ...
```

**Strategy swapping tests:**

```python
class TestStrategySwapping:
    """Test different strategy implementations."""
    
    async def test_simple_vs_llm_extractor(self):
        """Compare extraction strategies."""
        ...
    
    async def test_ema_vs_simple_average(self):
        """Compare success rate updaters."""
        ...
```

### File: `tests/integration/conftest.py`

Shared fixtures:
- `ephemeral_chroma` - temporary ChromaDB
- `mock_embedder` - deterministic embeddings for testing
- `sample_trajectories` - success and failure examples
- `sample_tasks` - various task types

## Testing Approach

- Use ephemeral ChromaDB (in-memory or temp directory)
- Use deterministic mock embedder for reproducibility
- Test real async behavior with pytest-asyncio
- Verify protocol compliance for all implementations

## Dependencies

- All Phase 3 implementation issues
- pytest-asyncio

## Acceptance Criteria

- [ ] End-to-end store/retrieve flow works
- [ ] Parallel queries execute correctly
- [ ] Ablation configurations work
- [ ] Strategy swapping works
- [ ] All integration tests pass
- [ ] Tests are deterministic and reproducible
