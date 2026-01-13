"""Provider registry for multi-provider support.

This module implements a singleton registry pattern for managing LLM providers.
Providers can be registered at runtime, enabling plugin-style extensibility.

Usage:
    from blueprint.providers.registry import get_provider, list_providers

    # Get default provider (anthropic)
    provider = get_provider()

    # Get specific provider
    provider = get_provider("openai")

    # List available providers
    print(list_providers())  # ['anthropic', 'openai', ...]

Configuration:
    BLUEPRINT_PROVIDER: Override default provider selection
"""

import os
import threading
from typing import Type

from blueprint.providers.base import ProviderBase, CredentialsError


class ProviderNotFoundError(Exception):
    """Raised when requested provider is not registered."""

    pass


class ProviderRegistry:
    """Singleton registry for LLM providers.

    Thread-safe registry for registering and retrieving provider implementations.
    Providers are lazily instantiated on first access.

    Example:
        >>> registry = ProviderRegistry()
        >>> registry.register("my_provider", MyProviderClass)
        >>> provider = registry.get("my_provider")
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "ProviderRegistry":
        """Singleton pattern - return existing instance if available."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._providers: dict[str, Type[ProviderBase]] = {}
                    cls._instance._initialized = False
        return cls._instance

    def _ensure_initialized(self) -> None:
        """Lazy initialization of default providers."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Register default providers
            self._register_default_providers()
            self._initialized = True

    def _register_default_providers(self) -> None:
        """Register built-in providers."""
        # Always register Anthropic (default)
        try:
            from blueprint.providers.anthropic import AnthropicProvider

            self._providers["anthropic"] = AnthropicProvider
        except ImportError:
            pass  # anthropic package not installed

        # Register OpenAI if available
        try:
            from blueprint.providers.openai import OpenAIProvider

            self._providers["openai"] = OpenAIProvider
        except ImportError:
            pass  # openai package not installed

        # Register Google if available
        try:
            from blueprint.providers.google import GoogleProvider

            self._providers["google"] = GoogleProvider
        except ImportError:
            pass  # google-generativeai package not installed

        # Register Outpost if available
        try:
            from blueprint.providers.outpost import OutpostProvider

            self._providers["outpost"] = OutpostProvider
        except ImportError:
            pass  # boto3 not installed or outpost module not available

    def register(self, name: str, provider_class: Type[ProviderBase]) -> None:
        """Register a provider class.

        Args:
            name: Unique name for the provider (e.g., "anthropic", "openai").
            provider_class: Provider class implementing ProviderBase.

        Raises:
            TypeError: If provider_class doesn't inherit from ProviderBase.
        """
        if not issubclass(provider_class, ProviderBase):
            raise TypeError(
                f"Provider class must inherit from ProviderBase, got {provider_class}"
            )

        with self._lock:
            self._providers[name.lower()] = provider_class

    def get(self, name: str | None = None) -> ProviderBase:
        """Get a provider instance by name.

        Args:
            name: Provider name. If None, uses BLUEPRINT_PROVIDER env var
                  or defaults to "anthropic".

        Returns:
            Instantiated provider.

        Raises:
            ProviderNotFoundError: If provider is not registered.
            CredentialsError: If provider credentials are not configured.
        """
        self._ensure_initialized()

        # Determine provider name
        if name is None:
            name = os.environ.get("BLUEPRINT_PROVIDER", "anthropic")

        name = name.lower()

        if name not in self._providers:
            available = ", ".join(sorted(self._providers.keys()))
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. Available providers: {available}"
            )

        provider_class = self._providers[name]
        return provider_class.from_env()

    def get_class(self, name: str) -> Type[ProviderBase]:
        """Get provider class without instantiation.

        Args:
            name: Provider name.

        Returns:
            Provider class.

        Raises:
            ProviderNotFoundError: If provider is not registered.
        """
        self._ensure_initialized()
        name = name.lower()

        if name not in self._providers:
            available = ", ".join(sorted(self._providers.keys()))
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. Available providers: {available}"
            )

        return self._providers[name]

    def list_providers(self) -> list[str]:
        """List all registered provider names.

        Returns:
            Sorted list of provider names.
        """
        self._ensure_initialized()
        return sorted(self._providers.keys())

    def is_registered(self, name: str) -> bool:
        """Check if a provider is registered.

        Args:
            name: Provider name.

        Returns:
            True if provider is registered.
        """
        self._ensure_initialized()
        return name.lower() in self._providers

    def unregister(self, name: str) -> None:
        """Remove a provider from the registry.

        Args:
            name: Provider name to remove.

        Note:
            Silently ignores if provider doesn't exist.
        """
        with self._lock:
            self._providers.pop(name.lower(), None)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance.

        Primarily for testing purposes.
        """
        with cls._lock:
            cls._instance = None


# Module-level convenience functions


def get_provider(name: str | None = None) -> ProviderBase:
    """Get a provider instance by name.

    Args:
        name: Provider name (default: from BLUEPRINT_PROVIDER or "anthropic").

    Returns:
        Instantiated provider.

    Example:
        >>> provider = get_provider("anthropic")
        >>> response = provider.generate_completion("Hello!")
    """
    return ProviderRegistry().get(name)


def list_providers() -> list[str]:
    """List all registered providers.

    Returns:
        Sorted list of provider names.

    Example:
        >>> print(list_providers())
        ['anthropic', 'openai', 'google']
    """
    return ProviderRegistry().list_providers()


def register_provider(name: str, provider_class: Type[ProviderBase]) -> None:
    """Register a custom provider.

    Args:
        name: Unique name for the provider.
        provider_class: Provider class implementing ProviderBase.

    Example:
        >>> from blueprint.providers import ProviderBase, register_provider
        >>> class MyProvider(ProviderBase):
        ...     # implementation
        >>> register_provider("my_provider", MyProvider)
    """
    ProviderRegistry().register(name, provider_class)
