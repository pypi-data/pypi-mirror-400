"""OpenAI GPT provider implementation.

This module implements the ProviderBase interface for OpenAI's GPT models.

Environment:
    OPENAI_API_KEY: Required for API access

Supported Models:
    - gpt-4o (default)
    - gpt-4-turbo
    - gpt-4
    - gpt-3.5-turbo
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
MODEL_GPT4O = "gpt-4o"
MODEL_GPT4_TURBO = "gpt-4-turbo"
MODEL_GPT4 = "gpt-4"
MODEL_GPT35_TURBO = "gpt-3.5-turbo"
DEFAULT_MODEL = MODEL_GPT4O

# Retry configuration
MAX_RETRIES = 3
RETRY_MIN_WAIT = 1  # seconds
RETRY_MAX_WAIT = 30  # seconds


class OpenAIProvider(ProviderBase):
    """OpenAI GPT provider implementation.

    Uses the OpenAI SDK to communicate with GPT models.
    Includes automatic retry with exponential backoff for resilience.

    Example:
        >>> provider = OpenAIProvider.from_env()
        >>> response = provider.generate_completion("Hello, GPT!")
        >>> print(response)
        "Hello! How can I assist you today?"

        >>> # With custom model
        >>> provider = OpenAIProvider(api_key="sk-...", model=MODEL_GPT35_TURBO)
        >>> response = provider.generate_completion("Quick question", max_tokens=100)
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
    ):
        """Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key.
            model: Model to use. Defaults to GPT-4o.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )

        self._api_key = api_key
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a completion using GPT.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0-2.0 for OpenAI).
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

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return self._call_with_retry(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
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
        temperature: float,
        messages: list[dict],
        **kwargs: Any,
    ) -> str:
        """Make API call with automatic retry."""
        try:
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            return response.choices[0].message.content

        except Exception as e:
            raise GenerationError(f"OpenAI API call failed: {e}") from e

    def get_model_name(self) -> str:
        """Get the current model name."""
        return self._model

    def validate_credentials(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    @classmethod
    def from_env(cls) -> "OpenAIProvider":
        """Create provider from OPENAI_API_KEY environment variable.

        Returns:
            Configured OpenAIProvider instance.

        Raises:
            CredentialsError: If OPENAI_API_KEY is not set.
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise CredentialsError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it or pass api_key parameter directly."
            )
        return cls(api_key=api_key)

    @classmethod
    def env_var_name(cls) -> str:
        """Return the environment variable name for this provider."""
        return "OPENAI_API_KEY"
