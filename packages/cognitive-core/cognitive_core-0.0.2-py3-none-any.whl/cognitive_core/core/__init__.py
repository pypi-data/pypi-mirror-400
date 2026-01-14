"""Core data structures for ATLAS.

These are the foundational "atoms" that all ATLAS components operate on.
"""

from cognitive_core.core.types import (
    AnalysisResult,
    BatchResult,
    Candidate,
    CodeConcept,
    ErrorPattern,
    Experience,
    FinetuneResult,
    Outcome,
    ProcessResult,
    RoutingDecision,
    Step,
    Strategy,
    Task,
    Trajectory,
    VerificationSpec,
)

__all__ = [
    # Primary types
    "Trajectory",
    "Task",
    "Step",
    "Outcome",
    # Memory types
    "Experience",
    "CodeConcept",
    "Strategy",
    # Search types
    "Candidate",
    "RoutingDecision",
    "VerificationSpec",
    # Learning types
    "AnalysisResult",
    "BatchResult",
    "ErrorPattern",
    "FinetuneResult",
    "ProcessResult",
]
