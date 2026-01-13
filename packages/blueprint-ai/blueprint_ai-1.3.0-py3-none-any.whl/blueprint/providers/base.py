"""Abstract base class for LLM providers.

This module defines the ProviderBase ABC that all provider implementations
must inherit from. Keeps the interface minimal to avoid leaky abstractions.

Design Principles:
- Minimal interface: only essential methods
- Provider-specific features via **kwargs
- Clear error hierarchy
- Type hints for all methods
"""

from abc import ABC, abstractmethod
from typing import Any


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


class CredentialsError(ProviderError):
    """Raised when credentials are missing or invalid."""

    pass


class GenerationError(ProviderError):
    """Raised when generation fails."""

    pass


class ProviderBase(ABC):
    """Abstract base class for LLM providers.

    All provider implementations must inherit from this class and implement
    the abstract methods defined here.

    Example:
        >>> class MyProvider(ProviderBase):
        ...     def generate_completion(self, prompt, max_tokens=4096, **kwargs):
        ...         # Implementation here
        ...         return "Generated text"
        ...
        ...     def get_model_name(self):
        ...         return "my-model-v1"
        ...
        ...     def validate_credentials(self):
        ...         return True
        ...
        ...     @classmethod
        ...     def from_env(cls):
        ...         return cls()
        ...
        ...     @classmethod
        ...     def env_var_name(cls):
        ...         return "MY_API_KEY"
    """

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            prompt: The input prompt to send to the model.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0-1.0).
            **kwargs: Provider-specific options (model selection, etc.)

        Returns:
            The generated text response.

        Raises:
            GenerationError: If generation fails.
            CredentialsError: If credentials are invalid.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name/identifier of the model being used.

        Returns:
            Model identifier string (e.g., "claude-opus-4-5-20251101").
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured.

        Returns:
            True if credentials are valid, False otherwise.

        Note:
            This should perform a lightweight validation (e.g., check env var exists).
            For full validation, make a test API call.
        """
        pass

    @classmethod
    @abstractmethod
    def from_env(cls) -> "ProviderBase":
        """Create a provider instance from environment variables.

        Returns:
            Configured provider instance.

        Raises:
            CredentialsError: If required environment variables are not set.

        Example:
            >>> provider = AnthropicProvider.from_env()
            >>> # Uses ANTHROPIC_API_KEY from environment
        """
        pass

    @classmethod
    @abstractmethod
    def env_var_name(cls) -> str:
        """Get the name of the primary environment variable for this provider.

        Returns:
            Environment variable name (e.g., "ANTHROPIC_API_KEY").

        Note:
            Used by the registry for auto-detection of available providers.
        """
        pass

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(model={self.get_model_name()})"
