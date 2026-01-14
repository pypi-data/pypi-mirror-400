"""ATLAS configuration system.

Centralized dataclass-based configuration with sensible defaults.
All components use these configs for consistent behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


@dataclass
class ExecutorConfig:
    """TaskExecutor configuration.

    Attributes:
        agent_type: ACP agent type to use (claude-code, codex, gemini, opencode)
        reuse_sessions: If True, reuse agent handle across tasks (new session per task)
        timeout_seconds: Maximum time for task execution
        permission_mode: How to handle agent permission requests
    """

    agent_type: str = "claude-code"
    reuse_sessions: bool = False
    timeout_seconds: int = 300
    permission_mode: Literal["auto-approve", "auto-deny", "callback", "interactive"] = (
        "auto-approve"
    )


@dataclass
class MemoryConfig:
    """Memory context limits for prompts.

    Controls how much memory context is included in agent prompts.
    Defaults are based on research papers (ReMem uses k=4 for experiences).

    Attributes:
        max_experiences: Maximum similar experiences to include
        max_strategies: Maximum applicable strategies to include
        max_concepts: Maximum code concepts to include
        max_context_tokens: Token limit for memory context section
    """

    max_experiences: int = 4  # From ReMem paper
    max_strategies: int = 3
    max_concepts: int = 5
    max_context_tokens: int = 4000


@dataclass
class EmbeddingConfig:
    """Embedding provider configuration.

    Attributes:
        model_name: Sentence transformer model to use
        device: Device for inference (cpu, cuda, mps)
        cache_enabled: Whether to cache embeddings in memory
    """

    model_name: str = "BAAI/bge-base-en-v1.5"  # Validated in ReMem paper
    device: Literal["cpu", "cuda", "mps"] = "cpu"
    cache_enabled: bool = True


@dataclass
class StorageConfig:
    """Storage and persistence configuration.

    Attributes:
        base_path: Base directory for ATLAS data (project-local)
        chroma_collection_prefix: Prefix for ChromaDB collections (useful for testing)
        distance_metric: Distance metric for vector similarity
    """

    base_path: Path = field(default_factory=lambda: Path(".atlas"))
    chroma_collection_prefix: str = ""
    distance_metric: Literal["cosine", "l2", "ip"] = "cosine"

    def __post_init__(self) -> None:
        """Ensure base_path is a Path object."""
        if isinstance(self.base_path, str):
            self.base_path = Path(self.base_path)


class MindEvolutionConfig(BaseModel):
    """Configuration for Mind Evolution search."""

    model_config = ConfigDict(frozen=True)

    population_size: int = Field(default=20, ge=4, description="Population size")
    generations: int = Field(default=10, ge=1, description="Number of generations")
    elite_fraction: float = Field(
        default=0.5, ge=0.1, le=0.9, description="Fraction of elites to keep"
    )
    memory_init_fraction: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Fraction initialized from memory"
    )
    mutation_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature for mutation"
    )
    crossover_rate: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Probability of crossover"
    )


class SWESearchConfig(BaseModel):
    """Configuration for SWE-Search (MCTS)."""

    model_config = ConfigDict(frozen=True)

    max_expansions: int = Field(default=100, ge=1, description="Max tree expansions")
    ucb_constant: float = Field(
        default=1.414, ge=0.0, description="UCB exploration constant"
    )
    max_depth: int = Field(default=20, ge=1, description="Max tree depth")
    rollout_depth: int = Field(default=5, ge=1, description="Rollout simulation depth")
    use_discriminator: bool = Field(
        default=True, description="Use discriminator for value estimation"
    )
    discriminator_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Threshold for agent rollout"
    )


class RouterConfig(BaseModel):
    """Configuration for task routing."""

    model_config = ConfigDict(frozen=True)

    similarity_threshold: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Threshold for adapt strategy"
    )
    use_domain_routing: bool = Field(
        default=True, description="Route by task domain"
    )
    default_strategy: str = Field(
        default="evolutionary", description="Default strategy when uncertain"
    )
    arc_strategy: str = Field(
        default="evolutionary", description="Strategy for ARC domain"
    )
    swe_strategy: str = Field(default="mcts", description="Strategy for SWE domain")


class LearningConfig(BaseModel):
    """Configuration for the learning pipeline.

    Controls how trajectories are analyzed and patterns are extracted.

    Attributes:
        credit_strategy: Credit assignment method ('simple', 'llm', 'counterfactual')
        pattern_extractor: Pattern extraction method ('llm', 'text', 'both')
        min_trajectories: Minimum trajectories required for batch learning
        min_hours_since_last: Optional time-based trigger (hours since last batch)
        min_success_rate: Optional quality threshold for batch learning
    """

    model_config = ConfigDict(frozen=True)

    credit_strategy: Literal["simple", "llm", "counterfactual"] = Field(
        default="llm",
        description="Credit assignment strategy",
    )
    pattern_extractor: Literal["llm", "text", "both"] = Field(
        default="llm",
        description="Pattern extraction method",
    )
    min_trajectories: int = Field(
        default=50,
        ge=1,
        description="Minimum trajectories for batch learning",
    )
    min_hours_since_last: float | None = Field(
        default=None,
        ge=0.0,
        description="Optional time-based trigger (hours)",
    )
    min_success_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional quality threshold",
    )


@dataclass
class ATLASConfig:
    """Root configuration for ATLAS.

    Aggregates all sub-configurations into a single object.
    Use this as the primary configuration interface.

    Example:
        ```python
        # Default config
        config = ATLASConfig()

        # Custom config
        config = ATLASConfig(
            executor=ExecutorConfig(agent_type="codex", timeout_seconds=600),
            storage=StorageConfig(base_path=Path("/tmp/atlas")),
        )
        ```
    """

    executor: ExecutorConfig = field(default_factory=ExecutorConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


# Convenience exports
__all__ = [
    "ATLASConfig",
    "EmbeddingConfig",
    "ExecutorConfig",
    "LearningConfig",
    "MemoryConfig",
    "MindEvolutionConfig",
    "RouterConfig",
    "StorageConfig",
    "SWESearchConfig",
]
