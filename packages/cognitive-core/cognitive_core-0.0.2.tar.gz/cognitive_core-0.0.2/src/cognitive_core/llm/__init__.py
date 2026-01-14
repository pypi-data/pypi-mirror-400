"""LLM integration for ATLAS.

Protocol-based LLM interface for easy provider swapping.
Includes adapters for LiteLLM, Anthropic, and OpenAI.
"""

from cognitive_core.llm.simple import SimpleLLM, SimpleLLMError

__all__ = ["SimpleLLM", "SimpleLLMError"]
