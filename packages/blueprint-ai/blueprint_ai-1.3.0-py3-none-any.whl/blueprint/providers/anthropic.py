"""Anthropic Claude provider implementation.

This module implements the ProviderBase interface for Anthropic's Claude models.
It extracts and refactors the existing Anthropic integration from decomposer.py.

Environment:
    ANTHROPIC_API_KEY: Required for API access

Supported Models:
    - claude-opus-4-5-20251101 (default)
    - claude-sonnet-4-5-20250929
"""

import os
from typing import Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from blueprint.providers.base import (
    ProviderBase,
    CredentialsError,
    GenerationError,
)

# Model identifiers
MODEL_OPUS = "claude-opus-4-5-20251101"
MODEL_SONNET = "claude-sonnet-4-5-20250929"
DEFAULT_MODEL = MODEL_OPUS

# Retry configuration (matches decomposer.py)
MAX_RETRIES = 3
RETRY_MIN_WAIT = 1  # seconds
RETRY_MAX_WAIT = 30  # seconds


class AnthropicProvider(ProviderBase):
    """Anthropic Claude provider implementation.

    Uses the Anthropic SDK to communicate with Claude models.
    Includes automatic retry with exponential backoff for resilience.

    Example:
        >>> provider = AnthropicProvider.from_env()
        >>> response = provider.generate_completion("Hello, Claude!")
        >>> print(response)
        "Hello! I'm Claude, an AI assistant..."

        >>> # With custom model
        >>> provider = AnthropicProvider(api_key="sk-...", model=MODEL_SONNET)
        >>> response = provider.generate_completion("Quick question", max_tokens=100)
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
    ):
        """Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key.
            model: Model to use. Defaults to Opus 4.5.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        self._api_key = api_key
        self._model = model
        self._client = Anthropic(api_key=api_key)

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a completion using Claude.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            **kwargs: Additional arguments passed to the API.
                - model: Override the default model for this call.
                - system: System prompt to prepend.

        Returns:
            Generated text response.

        Raises:
            GenerationError: If generation fails after retries.
        """
        model = kwargs.pop("model", self._model)
        system = kwargs.pop("system", None)

        messages = [{"role": "user", "content": prompt}]

        return self._call_with_retry(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            system=system,
            **kwargs,
        )

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    def _call_with_retry(
        self,
        model: str,
        max_tokens: int,
        messages: list[dict],
        system: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Make API call with automatic retry."""
        try:
            api_kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system:
                api_kwargs["system"] = system

            response = self._client.messages.create(**api_kwargs)
            return response.content[0].text

        except Exception as e:
            raise GenerationError(f"Anthropic API call failed: {e}") from e

    def get_model_name(self) -> str:
        """Get the current model name."""
        return self._model

    def validate_credentials(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    @classmethod
    def from_env(cls) -> "AnthropicProvider":
        """Create provider from ANTHROPIC_API_KEY environment variable.

        Returns:
            Configured AnthropicProvider instance.

        Raises:
            CredentialsError: If ANTHROPIC_API_KEY is not set.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise CredentialsError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Set it or pass api_key parameter directly."
            )
        return cls(api_key=api_key)

    @classmethod
    def env_var_name(cls) -> str:
        """Return the environment variable name for this provider."""
        return "ANTHROPIC_API_KEY"
