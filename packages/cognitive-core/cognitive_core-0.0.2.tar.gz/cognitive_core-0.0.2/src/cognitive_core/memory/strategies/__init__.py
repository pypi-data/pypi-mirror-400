"""Strategy protocols for ATLAS memory components.

This module provides pluggable strategy protocols that enable experimentation
with different approaches for memory operations.
"""

from cognitive_core.memory.strategies.concepts import (
    CompositionStrategy,
    CompressionStrategy,
    ConceptDocumenter,
    PrimitiveLoader,
)
from cognitive_core.memory.strategies.experience import (
    ExperienceExtractor,
    PassthroughRefineStrategy,
    RefineStrategy,
    SimpleExperienceExtractor,
)
from cognitive_core.memory.strategies.strategy_bank import (
    EMASuccessUpdater,
    SimpleAverageUpdater,
    StrategyAbstractor,
    SuccessRateUpdater,
)

__all__ = [
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
