"""Protocol definitions for ATLAS components.

All protocols use typing.Protocol for structural subtyping.
Components depend on protocols, not concrete implementations.

Usage:
    from cognitive_core.protocols import LLM, ExperienceMemory, SearchEngine

    class MyLLM:
        def generate(self, prompt: str, **kwargs) -> str:
            ...

    assert isinstance(MyLLM(), LLM)  # Works with @runtime_checkable
"""

# Infrastructure protocols
from cognitive_core.protocols.agent import Agent
from cognitive_core.protocols.embeddings import EmbeddingProvider
from cognitive_core.protocols.environment import Environment
from cognitive_core.protocols.llm import LLM
from cognitive_core.protocols.vector_index import VectorIndex

# Learning protocols (Pillar 3)
from cognitive_core.protocols.learning import (
    AbstractionExtractor,
    HindsightLearner,
    LearningPipeline,
    TrajectoryAnalyzer,
)

# Memory protocols (Pillar 1)
from cognitive_core.protocols.memory import (
    ConceptLibrary,
    ExperienceMemory,
    MemoryQueryResult,
    MemorySystem,
    StrategyBank,
)

# Search protocols (Pillar 2)
from cognitive_core.protocols.search import (
    SearchEngine,
    TaskRouter,
    Verifier,
)

__all__ = [
    # Infrastructure
    "LLM",
    "EmbeddingProvider",
    "VectorIndex",
    "Environment",
    "Agent",
    # Memory (Pillar 1)
    "ExperienceMemory",
    "ConceptLibrary",
    "StrategyBank",
    "MemorySystem",
    "MemoryQueryResult",
    # Search (Pillar 2)
    "TaskRouter",
    "SearchEngine",
    "Verifier",
    # Learning (Pillar 3)
    "TrajectoryAnalyzer",
    "AbstractionExtractor",
    "HindsightLearner",
    "LearningPipeline",
]
