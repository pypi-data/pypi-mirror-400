"""Learning engine for ATLAS (Pillar 3).

Learning is how to improve - extracting knowledge from trajectories
to update memory and optionally fine-tune models.
"""

from cognitive_core.learning.analyzer import (
    CounterfactualCreditStrategy,
    CreditAssignmentStrategy,
    LLMCreditStrategy,
    SimpleCreditStrategy,
    TrajectoryAnalyzer,
    create_analyzer,
)
from cognitive_core.learning.extractor import (
    AbstractionExtractor,
    CombinedPatternExtractor,
    LLMPatternExtractor,
    PatternExtractor,
    TextPatternExtractor,
    create_extractor,
)
from cognitive_core.learning.hindsight import HindsightLearner
from cognitive_core.learning.pipeline import LearningPipeline, create_learning_pipeline

__all__ = [
    # Credit assignment strategies
    "CounterfactualCreditStrategy",
    "CreditAssignmentStrategy",
    "LLMCreditStrategy",
    "SimpleCreditStrategy",
    # Trajectory analysis
    "TrajectoryAnalyzer",
    "create_analyzer",
    # Pattern extractors
    "PatternExtractor",
    "LLMPatternExtractor",
    "TextPatternExtractor",
    "CombinedPatternExtractor",
    # Abstraction extractor
    "AbstractionExtractor",
    "create_extractor",
    # Hindsight learning
    "HindsightLearner",
    # Learning pipeline
    "LearningPipeline",
    "create_learning_pipeline",
]
