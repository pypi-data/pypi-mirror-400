"""Multi-provider abstraction layer for Blueprint.

This module provides a pluggable provider system allowing Blueprint to use
different LLM backends for goal decomposition and other generation tasks.

Supported Providers:
- anthropic: Anthropic Claude (default)
- openai: OpenAI GPT models
- google: Google Gemini models
- outpost: Outpost fleet dispatch (no API key required)

Usage:
    # Use default provider (anthropic)
    from blueprint.providers import get_provider
    provider = get_provider()

    # Use specific provider
    provider = get_provider("openai")

    # List available providers
    from blueprint.providers import list_providers
    print(list_providers())

Configuration:
    BLUEPRINT_PROVIDER: Override default provider selection
    ANTHROPIC_API_KEY: Required for anthropic provider
    OPENAI_API_KEY: Required for openai provider
    GOOGLE_API_KEY: Required for google provider
"""

from blueprint.providers.base import (
    ProviderBase,
    ProviderError,
    CredentialsError,
    GenerationError,
)

# Registry imports are deferred to avoid circular dependencies
# Import them explicitly when needed:
# from blueprint.providers.registry import ProviderRegistry, get_provider, list_providers

__all__ = [
    "ProviderBase",
    "ProviderError",
    "CredentialsError",
    "GenerationError",
]

