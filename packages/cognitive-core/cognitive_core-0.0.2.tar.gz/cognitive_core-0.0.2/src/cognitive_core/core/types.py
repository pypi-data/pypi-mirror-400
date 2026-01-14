"""Core data types for ATLAS.

These are the foundational data structures that all ATLAS components operate on.
All types are immutable after creation and support JSON serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class VerificationSpec(BaseModel):
    """Specification for how to verify task success."""

    model_config = ConfigDict(frozen=True)

    method: str = Field(description="Verification method: 'exact_match', 'test_suite', 'llm_judge'")
    config: dict[str, Any] = Field(default_factory=dict, description="Method-specific configuration")


class Step(BaseModel):
    """Single step in a trajectory following ReAct pattern."""

    model_config = ConfigDict(frozen=True)

    thought: str | None = Field(default=None, description="Agent's reasoning (if available)")
    action: str = Field(description="Action taken")
    observation: str = Field(description="Result/feedback from environment")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata: tool, duration_ms, tokens_used, files_modified, etc.",
    )
    attribution_score: float | None = Field(
        default=None,
        description="Computed during analysis: contribution to outcome (0.0-1.0)",
    )


class Outcome(BaseModel):
    """Result of a trajectory attempt."""

    model_config = ConfigDict(frozen=True)

    success: bool = Field(description="Whether the task was solved successfully")
    partial_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Partial credit score (0.0-1.0) for ranking and learning",
    )
    error_info: str | None = Field(default=None, description="Error details if failed")
    verification_details: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific verification results",
    )


class Task(BaseModel):
    """Domain-agnostic representation of work to be done."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: str = Field(description="Unique task identifier")
    domain: str = Field(
        description="Task domain (emergent via embeddings, e.g., 'arc', 'swe', 'frontend')"
    )
    description: str = Field(description="Natural language task description")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific context data",
    )
    verification: VerificationSpec = Field(description="How to verify success")
    embedding: np.ndarray | None = Field(
        default=None,
        description="Precomputed embedding for retrieval",
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate embedding dimension if provided."""
        if self.embedding is not None and self.embedding.ndim != 1:
            raise ValueError("Embedding must be 1-dimensional")


class Trajectory(BaseModel):
    """The atomic unit of learning. Immutable record of an agent's attempt at a task."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    task: Task = Field(description="The task being attempted")
    steps: list[Step] = Field(description="Sequence of steps taken")
    outcome: Outcome = Field(description="Result of the attempt")
    agent_id: str = Field(description="Identifier of the agent that produced this trajectory")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this was created")

    # Optional metadata
    llm_calls: int = Field(default=0, ge=0, description="Number of LLM API calls made")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used")
    wall_time_seconds: float = Field(default=0.0, ge=0.0, description="Wall clock time")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata: timing, step counts, etc.",
    )


# =============================================================================
# Memory Types
# =============================================================================


class Experience(BaseModel):
    """A stored experience from a trajectory, used for task-level retrieval."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: str = Field(description="Unique experience identifier")
    task_input: str = Field(description="Task description")
    solution_output: str = Field(description="Solution attempt")
    feedback: str = Field(description="Outcome/error info")
    success: bool = Field(description="Whether the attempt succeeded")
    embedding: np.ndarray | None = Field(default=None, description="Embedding for retrieval")
    trajectory_id: str = Field(description="Source trajectory ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CodeConcept(BaseModel):
    """Reusable code pattern extracted from trajectories."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: str = Field(description="Unique concept identifier")
    name: str = Field(description="Human-readable name (from AutoDoc)")
    description: str = Field(description="What the concept does")
    code: str = Field(description="The actual code pattern")
    signature: str = Field(description="Type signature")
    examples: list[tuple[str, str]] = Field(
        default_factory=list,
        description="(input, output) example pairs",
    )

    # Statistics
    usage_count: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    # Retrieval
    embedding: np.ndarray | None = Field(default=None)

    # Metadata
    source: str = Field(
        default="primitive",
        description="Origin: 'primitive', 'learned', or 'composed'",
    )


class Strategy(BaseModel):
    """Abstract reasoning pattern (ArcMemo-style)."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: str = Field(description="Unique strategy identifier")
    situation: str = Field(description="When to apply this strategy")
    suggestion: str = Field(description="What to do")
    parameters: list[dict[str, str]] = Field(
        default_factory=list,
        description="Typed parameters for the strategy",
    )

    # Statistics
    usage_count: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.5, ge=0.0, le=1.0)

    # Retrieval
    embedding: np.ndarray | None = Field(default=None)


# =============================================================================
# Search Types
# =============================================================================


class Candidate(BaseModel):
    """A candidate solution from search."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    solution: Any = Field(description="Domain-specific solution")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this solution")
    reasoning: str = Field(description="Explanation of the solution")
    source: str = Field(description="Origin: 'generated', 'adapted', 'retrieved'")
    fitness: float | None = Field(default=None, description="Fitness score from evaluation")
    trajectory: Trajectory | None = Field(
        default=None,
        description="Source trajectory for this candidate (if available)",
    )
    parent_ids: list[str] = Field(
        default_factory=list,
        description="IDs of parent candidates (for evolutionary search)",
    )


class RoutingDecision(BaseModel):
    """Result of routing a task to a search strategy."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    strategy: str = Field(
        description="Search strategy: 'direct', 'evolutionary', 'mcts', 'adapt'"
    )
    context: Any = Field(
        default=None,
        description="Retrieved experiences/strategies (MemoryQueryResult)",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="0-1 confidence in strategy choice",
    )
    budget: int = Field(
        default=5,
        ge=1,
        description="Max iterations/calls for search",
    )


# =============================================================================
# Learning Types
# =============================================================================


class AnalysisResult(BaseModel):
    """Result of trajectory analysis."""

    model_config = ConfigDict(frozen=True)

    success: bool = Field(description="Whether the trajectory succeeded")
    key_steps: list[int] = Field(description="Indices of critical steps")
    step_attribution: list[float] = Field(description="Credit per step")
    error_patterns: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Detected failure modes",
    )
    abstractable: bool = Field(description="Whether patterns are worth extracting")
    training_examples: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Examples for hindsight learning",
    )


class FinetuneResult(BaseModel):
    """Result of a fine-tuning operation."""

    model_config = ConfigDict(frozen=True)

    success: bool = Field(description="Whether fine-tuning succeeded")
    model_path: str | None = Field(default=None, description="Path to fine-tuned model")
    metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Training metrics",
    )


class ErrorPattern(BaseModel):
    """Detected error pattern from trajectory analysis.

    Represents a recurring error pattern found across multiple failed
    trajectories, with suggested fixes.

    Example:
        ```python
        pattern = ErrorPattern(
            name="null_pointer_dereference",
            signature="AttributeError: 'NoneType' has no attribute",
            frequency=5,
            suggested_fix="Add null check before accessing attribute",
            examples=["obj.method() where obj is None"],
        )
        ```
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Pattern name, e.g., 'null_pointer_dereference'")
    signature: str = Field(description="Pattern signature or regex for matching")
    frequency: int = Field(default=1, ge=1, description="How often this pattern was seen")
    suggested_fix: str = Field(description="Recommended resolution for this error")
    examples: list[str] = Field(
        default_factory=list,
        description="Example occurrences of this error",
    )


class ProcessResult(BaseModel):
    """Result of processing a single trajectory through the learning pipeline.

    Tracks what happened when a trajectory was analyzed and stored.

    Attributes:
        trajectory_id: ID of the processed trajectory
        stored: Whether the trajectory was stored in memory
        analysis: The analysis result (if analysis was performed)
        abstractable: Whether the trajectory was deemed worth extracting
        strategy_extracted: Whether a strategy was extracted and stored
    """

    model_config = ConfigDict(frozen=True)

    trajectory_id: str = Field(description="ID of the processed trajectory")
    stored: bool = Field(description="Whether trajectory was stored in memory")
    analysis: AnalysisResult | None = Field(
        default=None,
        description="Analysis result if performed",
    )
    abstractable: bool = Field(
        default=False,
        description="Whether trajectory is worth extracting patterns from",
    )
    strategy_extracted: bool = Field(
        default=False,
        description="Whether a strategy was extracted and stored",
    )


class BatchResult(BaseModel):
    """Result of batch learning on accumulated trajectories.

    Summarizes what was learned and extracted during batch processing.

    Attributes:
        trajectories_processed: Number of trajectories in the batch
        concepts_extracted: Number of code concepts extracted
        strategies_extracted: Number of strategies extracted
        experiences_pruned: Number of low-value experiences removed
        success_rate: Fraction of successful trajectories in batch
    """

    model_config = ConfigDict(frozen=True)

    trajectories_processed: int = Field(
        ge=0,
        description="Number of trajectories processed",
    )
    concepts_extracted: int = Field(
        ge=0,
        description="Number of code concepts extracted",
    )
    strategies_extracted: int = Field(
        ge=0,
        description="Number of strategies extracted",
    )
    experiences_pruned: int = Field(
        ge=0,
        description="Number of low-value experiences removed",
    )
    success_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction of successful trajectories",
    )
