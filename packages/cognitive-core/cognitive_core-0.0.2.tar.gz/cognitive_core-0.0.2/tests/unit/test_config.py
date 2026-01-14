"""Tests for ATLAS configuration system."""

from __future__ import annotations

from pathlib import Path

import pytest

from cognitive_core.config import (
    ATLASConfig,
    EmbeddingConfig,
    ExecutorConfig,
    LearningConfig,
    MemoryConfig,
    MindEvolutionConfig,
    RouterConfig,
    StorageConfig,
    SWESearchConfig,
)


class TestExecutorConfig:
    """Tests for ExecutorConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ExecutorConfig()

        assert config.agent_type == "claude-code"
        assert config.reuse_sessions is False
        assert config.timeout_seconds == 300
        assert config.permission_mode == "auto-approve"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = ExecutorConfig(
            agent_type="codex",
            reuse_sessions=True,
            timeout_seconds=600,
            permission_mode="interactive",
        )

        assert config.agent_type == "codex"
        assert config.reuse_sessions is True
        assert config.timeout_seconds == 600
        assert config.permission_mode == "interactive"

    def test_permission_modes(self) -> None:
        """Test all valid permission modes."""
        for mode in ["auto-approve", "auto-deny", "callback", "interactive"]:
            config = ExecutorConfig(permission_mode=mode)
            assert config.permission_mode == mode


class TestMemoryConfig:
    """Tests for MemoryConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = MemoryConfig()

        assert config.max_experiences == 4
        assert config.max_strategies == 3
        assert config.max_concepts == 5
        assert config.max_context_tokens == 4000

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = MemoryConfig(
            max_experiences=10,
            max_strategies=5,
            max_concepts=8,
            max_context_tokens=8000,
        )

        assert config.max_experiences == 10
        assert config.max_strategies == 5
        assert config.max_concepts == 8
        assert config.max_context_tokens == 8000


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = EmbeddingConfig()

        assert config.model_name == "BAAI/bge-base-en-v1.5"
        assert config.device == "cpu"
        assert config.cache_enabled is True

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = EmbeddingConfig(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cuda",
            cache_enabled=False,
        )

        assert config.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.device == "cuda"
        assert config.cache_enabled is False

    def test_device_options(self) -> None:
        """Test all valid device options."""
        for device in ["cpu", "cuda", "mps"]:
            config = EmbeddingConfig(device=device)
            assert config.device == device


class TestStorageConfig:
    """Tests for StorageConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = StorageConfig()

        assert config.base_path == Path(".atlas")
        assert config.chroma_collection_prefix == ""
        assert config.distance_metric == "cosine"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = StorageConfig(
            base_path=Path("/custom/path"),
            chroma_collection_prefix="test_",
            distance_metric="l2",
        )

        assert config.base_path == Path("/custom/path")
        assert config.chroma_collection_prefix == "test_"
        assert config.distance_metric == "l2"

    def test_distance_metrics(self) -> None:
        """Test all valid distance metrics."""
        for metric in ["cosine", "l2", "ip"]:
            config = StorageConfig(distance_metric=metric)
            assert config.distance_metric == metric


class TestATLASConfig:
    """Tests for ATLASConfig."""

    def test_default_values(self) -> None:
        """Test default configuration with nested configs."""
        config = ATLASConfig()

        # Check all sub-configs are created with defaults
        assert isinstance(config.executor, ExecutorConfig)
        assert isinstance(config.memory, MemoryConfig)
        assert isinstance(config.embedding, EmbeddingConfig)
        assert isinstance(config.storage, StorageConfig)

        # Verify nested defaults
        assert config.executor.agent_type == "claude-code"
        assert config.memory.max_experiences == 4
        assert config.embedding.model_name == "BAAI/bge-base-en-v1.5"
        assert config.storage.base_path == Path(".atlas")

    def test_custom_nested_configs(self) -> None:
        """Test custom nested configuration values."""
        config = ATLASConfig(
            executor=ExecutorConfig(agent_type="codex", timeout_seconds=600),
            memory=MemoryConfig(max_experiences=10),
            embedding=EmbeddingConfig(device="cuda"),
            storage=StorageConfig(base_path=Path("/data")),
        )

        assert config.executor.agent_type == "codex"
        assert config.executor.timeout_seconds == 600
        assert config.memory.max_experiences == 10
        assert config.embedding.device == "cuda"
        assert config.storage.base_path == Path("/data")

    def test_partial_override(self) -> None:
        """Test partially overriding configuration."""
        config = ATLASConfig(
            executor=ExecutorConfig(timeout_seconds=120),
        )

        # Overridden value
        assert config.executor.timeout_seconds == 120
        # Default values preserved
        assert config.executor.agent_type == "claude-code"
        assert config.memory.max_experiences == 4

    def test_independence(self) -> None:
        """Test that configs are independent instances."""
        config1 = ATLASConfig()
        config2 = ATLASConfig()

        # Modify one config
        config1.executor.timeout_seconds  # Access to ensure created

        # They should be different instances
        assert config1.executor is not config2.executor
        assert config1.memory is not config2.memory


class TestMindEvolutionConfig:
    """Tests for MindEvolutionConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = MindEvolutionConfig()

        assert config.population_size == 20
        assert config.generations == 10
        assert config.elite_fraction == 0.5
        assert config.memory_init_fraction == 0.5
        assert config.mutation_temperature == 0.7
        assert config.crossover_rate == 0.3

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = MindEvolutionConfig(
            population_size=50,
            generations=20,
            elite_fraction=0.3,
            memory_init_fraction=0.8,
            mutation_temperature=1.2,
            crossover_rate=0.5,
        )

        assert config.population_size == 50
        assert config.generations == 20
        assert config.elite_fraction == 0.3
        assert config.memory_init_fraction == 0.8
        assert config.mutation_temperature == 1.2
        assert config.crossover_rate == 0.5

    def test_immutable(self) -> None:
        """Test that config is frozen (immutable)."""
        config = MindEvolutionConfig()

        with pytest.raises(Exception):  # Pydantic raises ValidationError
            config.population_size = 100

    def test_validation_population_size_min(self) -> None:
        """Test population_size minimum constraint."""
        with pytest.raises(Exception):
            MindEvolutionConfig(population_size=3)  # ge=4

    def test_validation_elite_fraction_bounds(self) -> None:
        """Test elite_fraction bounds constraints."""
        with pytest.raises(Exception):
            MindEvolutionConfig(elite_fraction=0.05)  # ge=0.1

        with pytest.raises(Exception):
            MindEvolutionConfig(elite_fraction=0.95)  # le=0.9

    def test_validation_crossover_rate_bounds(self) -> None:
        """Test crossover_rate bounds constraints."""
        with pytest.raises(Exception):
            MindEvolutionConfig(crossover_rate=-0.1)  # ge=0.0

        with pytest.raises(Exception):
            MindEvolutionConfig(crossover_rate=1.5)  # le=1.0


class TestSWESearchConfig:
    """Tests for SWESearchConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SWESearchConfig()

        assert config.max_expansions == 100
        assert config.ucb_constant == 1.414
        assert config.max_depth == 20
        assert config.rollout_depth == 5
        assert config.use_discriminator is True
        assert config.discriminator_threshold == 0.7

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = SWESearchConfig(
            max_expansions=200,
            ucb_constant=2.0,
            max_depth=30,
            rollout_depth=10,
            use_discriminator=False,
            discriminator_threshold=0.5,
        )

        assert config.max_expansions == 200
        assert config.ucb_constant == 2.0
        assert config.max_depth == 30
        assert config.rollout_depth == 10
        assert config.use_discriminator is False
        assert config.discriminator_threshold == 0.5

    def test_immutable(self) -> None:
        """Test that config is frozen (immutable)."""
        config = SWESearchConfig()

        with pytest.raises(Exception):
            config.max_expansions = 500

    def test_validation_max_expansions_min(self) -> None:
        """Test max_expansions minimum constraint."""
        with pytest.raises(Exception):
            SWESearchConfig(max_expansions=0)  # ge=1

    def test_validation_discriminator_threshold_bounds(self) -> None:
        """Test discriminator_threshold bounds constraints."""
        with pytest.raises(Exception):
            SWESearchConfig(discriminator_threshold=-0.1)  # ge=0.0

        with pytest.raises(Exception):
            SWESearchConfig(discriminator_threshold=1.5)  # le=1.0


class TestRouterConfig:
    """Tests for RouterConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RouterConfig()

        assert config.similarity_threshold == 0.9
        assert config.use_domain_routing is True
        assert config.default_strategy == "evolutionary"
        assert config.arc_strategy == "evolutionary"
        assert config.swe_strategy == "mcts"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RouterConfig(
            similarity_threshold=0.8,
            use_domain_routing=False,
            default_strategy="mcts",
            arc_strategy="beam_search",
            swe_strategy="evolutionary",
        )

        assert config.similarity_threshold == 0.8
        assert config.use_domain_routing is False
        assert config.default_strategy == "mcts"
        assert config.arc_strategy == "beam_search"
        assert config.swe_strategy == "evolutionary"

    def test_immutable(self) -> None:
        """Test that config is frozen (immutable)."""
        config = RouterConfig()

        with pytest.raises(Exception):
            config.similarity_threshold = 0.5

    def test_validation_similarity_threshold_bounds(self) -> None:
        """Test similarity_threshold bounds constraints."""
        with pytest.raises(Exception):
            RouterConfig(similarity_threshold=-0.1)  # ge=0.0

        with pytest.raises(Exception):
            RouterConfig(similarity_threshold=1.5)  # le=1.0


class TestLearningConfig:
    """Tests for LearningConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = LearningConfig()

        assert config.credit_strategy == "llm"
        assert config.pattern_extractor == "llm"
        assert config.min_trajectories == 50
        assert config.min_hours_since_last is None
        assert config.min_success_rate is None

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = LearningConfig(
            credit_strategy="simple",
            pattern_extractor="both",
            min_trajectories=100,
            min_hours_since_last=24.0,
            min_success_rate=0.6,
        )

        assert config.credit_strategy == "simple"
        assert config.pattern_extractor == "both"
        assert config.min_trajectories == 100
        assert config.min_hours_since_last == 24.0
        assert config.min_success_rate == 0.6

    def test_immutable(self) -> None:
        """Test that config is frozen (immutable)."""
        config = LearningConfig()

        with pytest.raises(Exception):
            config.credit_strategy = "simple"

    def test_credit_strategy_options(self) -> None:
        """Test all valid credit strategy options."""
        for strategy in ["simple", "llm", "counterfactual"]:
            config = LearningConfig(credit_strategy=strategy)
            assert config.credit_strategy == strategy

    def test_invalid_credit_strategy(self) -> None:
        """Test invalid credit strategy is rejected."""
        with pytest.raises(Exception):
            LearningConfig(credit_strategy="invalid")

    def test_pattern_extractor_options(self) -> None:
        """Test all valid pattern extractor options."""
        for extractor in ["llm", "text", "both"]:
            config = LearningConfig(pattern_extractor=extractor)
            assert config.pattern_extractor == extractor

    def test_invalid_pattern_extractor(self) -> None:
        """Test invalid pattern extractor is rejected."""
        with pytest.raises(Exception):
            LearningConfig(pattern_extractor="invalid")

    def test_validation_min_trajectories_min(self) -> None:
        """Test min_trajectories minimum constraint."""
        with pytest.raises(Exception):
            LearningConfig(min_trajectories=0)  # ge=1

    def test_validation_min_hours_since_last(self) -> None:
        """Test min_hours_since_last non-negative constraint."""
        with pytest.raises(Exception):
            LearningConfig(min_hours_since_last=-1.0)  # ge=0.0

    def test_validation_min_success_rate_bounds(self) -> None:
        """Test min_success_rate bounds constraints."""
        with pytest.raises(Exception):
            LearningConfig(min_success_rate=-0.1)  # ge=0.0

        with pytest.raises(Exception):
            LearningConfig(min_success_rate=1.5)  # le=1.0

    def test_optional_fields_can_be_none(self) -> None:
        """Test optional fields accept None explicitly."""
        config = LearningConfig(
            min_hours_since_last=None,
            min_success_rate=None,
        )

        assert config.min_hours_since_last is None
        assert config.min_success_rate is None
