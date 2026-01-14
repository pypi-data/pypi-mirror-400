---
id: i-4qsx
title: Implement light LLM adapter for simple prompts
priority: 1
created_at: '2026-01-08 02:11:19'
tags:
  - implementation
  - llm
  - phase-4
status: open
---
# Light LLM Adapter

Implements [[s-2uov|Phase 4: Minimal Solver]] LLM requirements.

## Goal

Create a lightweight LLM adapter for simple prompt-based operations. Most task execution uses ACP agents via TaskExecutor, but DirectSolver needs simple LLM calls for solution adaptation.

## Requirements

### 1. SimpleLLM Implementation

Implement the existing LLM protocol with a configurable backend:

```python
class SimpleLLM:
    """Lightweight LLM for simple prompt operations."""
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ) -> None:
        ...
    
    def generate(self, prompt: str, ...) -> str:
        """Generate text from prompt."""
        ...
    
    def extract_json(self, prompt: str, schema: dict) -> dict:
        """Generate and parse JSON response."""
        ...
```

### 2. Usage Context

Used by DirectSolver for:
- Adapting retrieved solutions to current task
- Simple text transformations
- Quick classification/routing decisions

NOT used for:
- Full task execution (use TaskExecutor + ACP agent)
- Complex multi-step reasoning

### 3. Configuration

- Support for model selection
- Temperature control
- Max tokens limit
- API key from environment

## Files

```
atlas/llm/
├── __init__.py
└── simple.py         # SimpleLLM implementation
```

## Tests

- SimpleLLM.generate() returns string
- SimpleLLM.extract_json() parses valid JSON
- Configuration respected
- Mock-based tests (no real API calls in unit tests)
