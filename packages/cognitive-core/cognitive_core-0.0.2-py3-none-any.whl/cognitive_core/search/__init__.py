"""Search methods for ATLAS (Pillar 2).

Search is how to solve - the algorithms for finding solutions.
Different methods suit different task types:
- Direct: High-confidence memory match (~1 call)
- Mind Evolution: Population-based evolutionary (~100 calls)
- SWE-Search: MCTS with UCB selection (~200 calls)
"""

from cognitive_core.search.direct import DirectSolver
from cognitive_core.search.discriminator import Discriminator
from cognitive_core.search.mcts import MCTSNode, SWESearch
from cognitive_core.search.mind_evolution import MindEvolutionSearch
from cognitive_core.search.router import BasicTaskRouter, EnhancedTaskRouter
from cognitive_core.search.verifier import ExactMatchVerifier, SimpleVerifier

__all__ = [
    "BasicTaskRouter",
    "DirectSolver",
    "Discriminator",
    "EnhancedTaskRouter",
    "ExactMatchVerifier",
    "MCTSNode",
    "MindEvolutionSearch",
    "SimpleVerifier",
    "SWESearch",
]
