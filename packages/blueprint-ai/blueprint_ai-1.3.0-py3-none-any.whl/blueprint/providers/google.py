"""Google Gemini provider implementation.

This module implements the ProviderBase interface for Google's Gemini models.

Environment:
    GOOGLE_API_KEY: Required for API access

Supported Models:
    - gemini-1.5-pro (default)
    - gemini-1.5-flash
    - gemini-pro
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
MODEL_GEMINI_15_PRO = "gemini-1.5-pro"
MODEL_GEMINI_15_FLASH = "gemini-1.5-flash"
MODEL_GEMINI_PRO = "gemini-pro"
DEFAULT_MODEL = MODEL_GEMINI_15_PRO

# Retry configuration
MAX_RETRIES = 3
RETRY_MIN_WAIT = 1  # seconds
RETRY_MAX_WAIT = 30  # seconds


class GoogleProvider(ProviderBase):
    """Google Gemini provider implementation.

    Uses the Google Generative AI SDK to communicate with Gemini models.
    Includes automatic retry with exponential backoff for resilience.

    Example:
        >>> provider = GoogleProvider.from_env()
        >>> response = provider.generate_completion("Hello, Gemini!")
        >>> print(response)
        "Hello! How can I help you today?"

        >>> # With custom model
        >>> provider = GoogleProvider(api_key="...", model=MODEL_GEMINI_15_FLASH)
        >>> response = provider.generate_completion("Quick question", max_tokens=100)
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
    ):
        """Initialize the Google provider.

        Args:
            api_key: Google API key.
            model: Model to use. Defaults to Gemini 1.5 Pro.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

        self._api_key = api_key
        self._model = model

        # Configure the API
        genai.configure(api_key=api_key)
        self._genai = genai
        self._client = genai.GenerativeModel(model)

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a completion using Gemini.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            **kwargs: Additional arguments passed to the API.
                - model: Override the default model for this call.
                - system: System instruction to use.

        Returns:
            Generated text response.

        Raises:
            GenerationError: If generation fails after retries.
        """
        model_name = kwargs.pop("model", self._model)
        system = kwargs.pop("system", None)

        # Use different client if model override specified
        if model_name != self._model:
            client = self._genai.GenerativeModel(model_name)
        else:
            client = self._client

        return self._call_with_retry(
            client=client,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
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
        client,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Make API call with automatic retry."""
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }

            # Build content with optional system instruction
            if system:
                full_prompt = f"{system}\n\n{prompt}"
            else:
                full_prompt = prompt

            response = client.generate_content(
                full_prompt,
                generation_config=generation_config,
            )

            return response.text

        except Exception as e:
            raise GenerationError(f"Google API call failed: {e}") from e

    def get_model_name(self) -> str:
        """Get the current model name."""
        return self._model

    def validate_credentials(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    @classmethod
    def from_env(cls) -> "GoogleProvider":
        """Create provider from GOOGLE_API_KEY environment variable.

        Returns:
            Configured GoogleProvider instance.

        Raises:
            CredentialsError: If GOOGLE_API_KEY is not set.
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise CredentialsError(
                "GOOGLE_API_KEY environment variable not set. "
                "Set it or pass api_key parameter directly."
            )
        return cls(api_key=api_key)

    @classmethod
    def env_var_name(cls) -> str:
        """Return the environment variable name for this provider."""
        return "GOOGLE_API_KEY"
