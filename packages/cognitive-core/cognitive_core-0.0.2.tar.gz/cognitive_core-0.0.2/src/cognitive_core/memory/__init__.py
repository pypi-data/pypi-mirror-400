"""Memory systems for ATLAS (Pillar 1).

Three complementary memory types at different abstraction levels:
- StrategyBank: Abstract reasoning patterns (highest abstraction)
- ExperienceMemory: Task-level retrieval (medium abstraction)
- ConceptLibrary: Reusable code patterns (lowest abstraction)
"""

from cognitive_core.memory.concepts import ChromaConceptLibrary
from cognitive_core.memory.experience import ChromaExperienceMemory
from cognitive_core.memory.primitives import ARCPrimitiveLoader, SWEPrimitiveLoader
from cognitive_core.memory.storage import ChromaVectorStore, QueryResult, VectorStore
from cognitive_core.memory.system import MemorySystemImpl
from cognitive_core.memory.strategies import (
    # Experience protocols and implementations
    ExperienceExtractor,
    PassthroughRefineStrategy,
    RefineStrategy,
    SimpleExperienceExtractor,
    # Concept protocols
    CompositionStrategy,
    CompressionStrategy,
    ConceptDocumenter,
    PrimitiveLoader,
    # Strategy bank protocols and implementations
    EMASuccessUpdater,
    SimpleAverageUpdater,
    StrategyAbstractor,
    SuccessRateUpdater,
)

__all__ = [
    # Storage
    "ChromaConceptLibrary",
    "ChromaExperienceMemory",
    "ChromaVectorStore",
    "MemorySystemImpl",
    "QueryResult",
    "VectorStore",
    # Primitive loaders
    "ARCPrimitiveLoader",
    "SWEPrimitiveLoader",
    # Experience protocols
    "ExperienceExtractor",
    "RefineStrategy",
    # Experience implementations
    "SimpleExperienceExtractor",
    "PassthroughRefineStrategy",
    # Concept protocols
    "CompositionStrategy",
    "CompressionStrategy",
    "ConceptDocumenter",
    "PrimitiveLoader",
    # Strategy bank protocols
    "StrategyAbstractor",
    "SuccessRateUpdater",
    # Strategy bank implementations
    "EMASuccessUpdater",
    "SimpleAverageUpdater",
]
