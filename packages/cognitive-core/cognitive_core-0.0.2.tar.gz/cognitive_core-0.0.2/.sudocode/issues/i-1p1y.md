---
id: i-1p1y
title: Implement LLM and infrastructure protocols
priority: 1
created_at: '2025-12-18 03:33:24'
tags:
  - embeddings
  - llm
  - phase-1
  - protocols
relationships:
  - from_id: i-1p1y
    from_uuid: e9f8efa9-2f1a-4544-8281-41a6ecf75de5
    from_type: issue
    to_id: i-4zj6
    to_uuid: f7fdaab5-ec46-410d-a60d-5350250ac750
    to_type: issue
    relationship_type: depends-on
    created_at: '2025-12-18 04:33:19'
    metadata: null
  - from_id: i-1p1y
    from_uuid: e9f8efa9-2f1a-4544-8281-41a6ecf75de5
    from_type: issue
    to_id: s-8fnx
    to_uuid: 7b5a1dd5-414a-4a57-902a-dee0988267f2
    to_type: spec
    relationship_type: implements
    created_at: '2025-12-18 04:33:19'
    metadata: null
status: closed
closed_at: '2025-12-18 04:33:19'
---
Define the foundational protocols for LLM interaction, embeddings, and vector storage.

## Files to Create
- `atlas/protocols/llm.py` (~30 lines)
- `atlas/protocols/embeddings.py` (~25 lines)
- `atlas/protocols/vector_index.py` (~30 lines)

## LLM Protocol
Everything depends on this:

```python
class LLM(Protocol):
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        ...
    
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Async generation"""
        ...
```

## EmbeddingProvider Protocol
```python
class EmbeddingProvider(Protocol):
    def encode(self, text: str) -> np.ndarray:
        """Encode single text to vector"""
        ...
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts, returns (n, dim) array"""
        ...
    
    @property
    def dimension(self) -> int:
        """Embedding dimension"""
        ...
```

## VectorIndex Protocol
```python
class VectorIndex(Protocol):
    def add(self, id: str, vector: np.ndarray, metadata: Dict) -> None:
        """Add vector with metadata"""
        ...
    
    def search(self, vector: np.ndarray, k: int) -> List[Tuple[str, float, Dict]]:
        """Find k nearest neighbors, returns (id, score, metadata)"""
        ...
    
    def delete(self, id: str) -> bool:
        """Remove by ID"""
        ...
    
    def __len__(self) -> int:
        """Number of vectors stored"""
        ...
```

## Design Requirements
- Use `typing.Protocol` with `@runtime_checkable`
- Support both sync and async for LLM
- VectorIndex should support metadata filtering (future)

## Acceptance Criteria
- [ ] All protocols defined with type hints
- [ ] Protocols can be used for isinstance() checks
- [ ] Clear docstrings for each method

Implements [[s-8fnx]]
