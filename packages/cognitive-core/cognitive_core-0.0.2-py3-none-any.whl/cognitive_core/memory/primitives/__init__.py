"""Domain-specific primitive loaders for ATLAS.

Primitive loaders provide domain-specific code concepts that serve as
the foundational building blocks for the ConceptLibrary.
"""

from cognitive_core.memory.primitives.arc import ARCPrimitiveLoader
from cognitive_core.memory.primitives.swe import SWEPrimitiveLoader

__all__ = [
    "ARCPrimitiveLoader",
    "SWEPrimitiveLoader",
]
