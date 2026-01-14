"""LLM protocol for ATLAS.

Protocol-based LLM interface for easy provider swapping.
Everything in ATLAS depends on this interface.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLM(Protocol):
    """Language model interface.

    This is the foundational protocol that almost everything depends on.
    Implementations can wrap LiteLLM, Anthropic, OpenAI, or local models.

    Example:
        ```python
        llm = LiteLLMAdapter(model="claude-3-5-sonnet-20241022")
        response = llm.generate("What is 2 + 2?")
        ```
    """

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            **kwargs: Provider-specific arguments

        Returns:
            Generated text
        """
        ...

    async def agenerate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Async version of generate.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            **kwargs: Provider-specific arguments

        Returns:
            Generated text
        """
        ...

    @property
    def model_id(self) -> str:
        """Model identifier.

        Returns:
            String identifying the model (e.g., "claude-3-5-sonnet-20241022")
        """
        ...
