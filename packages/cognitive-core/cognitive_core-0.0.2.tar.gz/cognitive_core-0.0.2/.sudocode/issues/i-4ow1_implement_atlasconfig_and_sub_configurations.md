---
id: i-4ow1
title: Implement ATLASConfig and sub-configurations
priority: 0
created_at: '2026-01-07 08:55:54'
tags:
  - config
  - infrastructure
  - phase-2
status: open
---
# Implement ATLASConfig and sub-configurations

Implements: [[s-7xs8|Phase 2: Infrastructure Layer]]

## Scope

Create the centralized configuration system with dataclass-based configs.

## Files to Create

- `src/atlas/config.py`

## Implementation

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ExecutorConfig:
    """TaskExecutor configuration."""
    agent_type: str = "claude-code"
    reuse_sessions: bool = False
    timeout_seconds: int = 300
    permission_mode: str = "auto-approve"

@dataclass
class MemoryConfig:
    """Memory context limits for prompts."""
    max_experiences: int = 4
    max_strategies: int = 3
    max_concepts: int = 5
    max_context_tokens: int = 4000

@dataclass
class EmbeddingConfig:
    """Embedding provider configuration."""
    model_name: str = "BAAI/bge-base-en-v1.5"
    device: str = "cpu"
    cache_enabled: bool = True

@dataclass
class StorageConfig:
    """Storage and persistence configuration."""
    base_path: Path = field(default_factory=lambda: Path(".atlas"))
    chroma_collection_prefix: str = ""
    distance_metric: str = "cosine"

@dataclass
class ATLASConfig:
    """Root configuration for ATLAS."""
    executor: ExecutorConfig = field(default_factory=ExecutorConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
```

## Acceptance Criteria

- [ ] All config dataclasses implemented with defaults
- [ ] Configs are importable from `atlas.config`
- [ ] Type hints are complete
- [ ] Unit tests for default values and custom values
