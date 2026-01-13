"""Tests for provider registry."""

import pytest
from unittest.mock import patch, MagicMock

from blueprint.providers.base import ProviderBase, CredentialsError
from blueprint.providers.registry import (
    ProviderRegistry,
    ProviderNotFoundError,
    get_provider,
    list_providers,
    register_provider,
)


class MockProvider(ProviderBase):
    """Mock provider for testing."""

    def __init__(self, api_key: str = "mock-key"):
        self._api_key = api_key

    def generate_completion(self, prompt, max_tokens=4096, temperature=0.7, **kwargs):
        return f"Mock response for: {prompt}"

    def get_model_name(self):
        return "mock-model"

    def validate_credentials(self):
        return bool(self._api_key)

    @classmethod
    def from_env(cls):
        import os

        key = os.environ.get("MOCK_API_KEY", "")
        if not key:
            raise CredentialsError("MOCK_API_KEY not set")
        return cls(api_key=key)

    @classmethod
    def env_var_name(cls):
        return "MOCK_API_KEY"


class TestProviderRegistry:
    """Tests for ProviderRegistry class."""

    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry before each test."""
        ProviderRegistry.reset()
        yield
        ProviderRegistry.reset()

    def test_singleton_pattern(self):
        """Registry is a singleton."""
        registry1 = ProviderRegistry()
        registry2 = ProviderRegistry()
        assert registry1 is registry2

    def test_register_provider(self):
        """Can register a provider class."""
        registry = ProviderRegistry()
        registry.register("mock", MockProvider)
        assert registry.is_registered("mock")

    def test_register_requires_provider_base(self):
        """Registration requires ProviderBase subclass."""
        registry = ProviderRegistry()

        class NotAProvider:
            pass

        with pytest.raises(TypeError):
            registry.register("bad", NotAProvider)

    def test_get_registered_provider(self, monkeypatch):
        """Can get a registered provider instance."""
        monkeypatch.setenv("MOCK_API_KEY", "test-key")
        registry = ProviderRegistry()
        registry.register("mock", MockProvider)

        provider = registry.get("mock")
        assert isinstance(provider, MockProvider)
        assert provider._api_key == "test-key"

    def test_get_unknown_provider(self):
        """Getting unknown provider raises error."""
        registry = ProviderRegistry()
        with pytest.raises(ProviderNotFoundError) as exc_info:
            registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_get_default_provider(self, monkeypatch):
        """Default provider is anthropic when no BLUEPRINT_PROVIDER set."""
        monkeypatch.delenv("BLUEPRINT_PROVIDER", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        registry = ProviderRegistry()

        # Mock the anthropic import
        with patch(
            "blueprint.providers.registry.ProviderRegistry._register_default_providers"
        ):
            registry._providers["anthropic"] = MockProvider
            monkeypatch.setenv("MOCK_API_KEY", "test-key")

            # Since we mocked anthropic with MockProvider, we need to handle both keys
            class FakeAnthropicProvider(MockProvider):
                @classmethod
                def from_env(cls):
                    return cls(api_key="test-key")

            registry._providers["anthropic"] = FakeAnthropicProvider
            registry._initialized = True

            provider = registry.get(None)
            assert isinstance(provider, FakeAnthropicProvider)

    def test_get_provider_from_env_var(self, monkeypatch):
        """BLUEPRINT_PROVIDER env var selects provider."""
        monkeypatch.setenv("BLUEPRINT_PROVIDER", "mock")
        monkeypatch.setenv("MOCK_API_KEY", "env-key")

        registry = ProviderRegistry()
        registry.register("mock", MockProvider)
        registry._initialized = True

        provider = registry.get(None)
        assert isinstance(provider, MockProvider)

    def test_list_providers(self):
        """list_providers returns sorted list."""
        registry = ProviderRegistry()
        registry.register("zzz_provider", MockProvider)
        registry.register("aaa_provider", MockProvider)
        registry._initialized = True

        providers = registry.list_providers()
        assert providers == sorted(providers)
        assert "aaa_provider" in providers
        assert "zzz_provider" in providers

    def test_get_class(self):
        """get_class returns provider class without instantiation."""
        registry = ProviderRegistry()
        registry.register("mock", MockProvider)
        registry._initialized = True

        cls = registry.get_class("mock")
        assert cls is MockProvider

    def test_unregister(self):
        """Can unregister a provider."""
        registry = ProviderRegistry()
        registry.register("mock", MockProvider)
        assert registry.is_registered("mock")

        registry.unregister("mock")
        assert not registry.is_registered("mock")

    def test_unregister_nonexistent(self):
        """Unregistering nonexistent provider is silent."""
        registry = ProviderRegistry()
        registry.unregister("nonexistent")  # Should not raise

    def test_case_insensitive(self, monkeypatch):
        """Provider names are case-insensitive."""
        monkeypatch.setenv("MOCK_API_KEY", "test-key")
        registry = ProviderRegistry()
        registry.register("Mock", MockProvider)
        registry._initialized = True

        assert registry.is_registered("MOCK")
        assert registry.is_registered("mock")
        assert registry.is_registered("Mock")


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry before each test."""
        ProviderRegistry.reset()
        yield
        ProviderRegistry.reset()

    def test_get_provider_function(self, monkeypatch):
        """get_provider function works correctly."""
        monkeypatch.setenv("MOCK_API_KEY", "test-key")
        register_provider("mock", MockProvider)
        ProviderRegistry()._initialized = True

        provider = get_provider("mock")
        assert isinstance(provider, MockProvider)

    def test_list_providers_function(self):
        """list_providers function works correctly."""
        register_provider("test_provider", MockProvider)
        ProviderRegistry()._initialized = True

        providers = list_providers()
        assert "test_provider" in providers

    def test_register_provider_function(self):
        """register_provider function works correctly."""
        register_provider("custom", MockProvider)
        ProviderRegistry()._initialized = True

        assert ProviderRegistry().is_registered("custom")


class TestProviderNotFoundError:
    """Tests for ProviderNotFoundError."""

    def test_error_message_includes_provider_name(self):
        """Error message includes the missing provider name."""
        ProviderRegistry.reset()
        registry = ProviderRegistry()
        registry._initialized = True

        with pytest.raises(ProviderNotFoundError) as exc_info:
            registry.get("missing_provider")

        assert "missing_provider" in str(exc_info.value)

    def test_error_message_lists_available(self):
        """Error message lists available providers."""
        ProviderRegistry.reset()
        registry = ProviderRegistry()
        registry.register("available", MockProvider)
        registry._initialized = True

        with pytest.raises(ProviderNotFoundError) as exc_info:
            registry.get("missing")

        assert "available" in str(exc_info.value)
