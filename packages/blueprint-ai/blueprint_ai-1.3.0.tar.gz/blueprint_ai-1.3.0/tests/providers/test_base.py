"""Tests for provider base class."""

import pytest

from blueprint.providers.base import (
    ProviderBase,
    ProviderError,
    CredentialsError,
    GenerationError,
)


class ConcreteProvider(ProviderBase):
    """Concrete implementation for testing."""

    def __init__(self, api_key: str = "test-key", model: str = "test-model"):
        self._api_key = api_key
        self._model = model

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        return f"Generated response for: {prompt[:50]}"

    def get_model_name(self) -> str:
        return self._model

    def validate_credentials(self) -> bool:
        return bool(self._api_key)

    @classmethod
    def from_env(cls) -> "ConcreteProvider":
        import os

        api_key = os.environ.get("TEST_API_KEY", "")
        if not api_key:
            raise CredentialsError("TEST_API_KEY not set")
        return cls(api_key=api_key)

    @classmethod
    def env_var_name(cls) -> str:
        return "TEST_API_KEY"


class TestProviderBase:
    """Tests for ProviderBase ABC."""

    def test_cannot_instantiate_abstract_class(self):
        """ProviderBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProviderBase()

    def test_concrete_implementation_works(self):
        """Concrete implementation can be instantiated."""
        provider = ConcreteProvider()
        assert provider is not None
        assert provider.get_model_name() == "test-model"

    def test_generate_completion(self):
        """generate_completion returns string."""
        provider = ConcreteProvider()
        result = provider.generate_completion("Test prompt")
        assert isinstance(result, str)
        assert "Test prompt" in result

    def test_generate_completion_with_kwargs(self):
        """generate_completion accepts kwargs."""
        provider = ConcreteProvider()
        result = provider.generate_completion(
            "Test prompt",
            max_tokens=1000,
            temperature=0.5,
            custom_param="value",
        )
        assert isinstance(result, str)

    def test_validate_credentials(self):
        """validate_credentials returns bool."""
        provider = ConcreteProvider(api_key="valid-key")
        assert provider.validate_credentials() is True

        provider_no_key = ConcreteProvider(api_key="")
        assert provider_no_key.validate_credentials() is False

    def test_env_var_name(self):
        """env_var_name returns string."""
        assert ConcreteProvider.env_var_name() == "TEST_API_KEY"

    def test_from_env_raises_without_key(self, monkeypatch):
        """from_env raises CredentialsError when env var not set."""
        monkeypatch.delenv("TEST_API_KEY", raising=False)
        with pytest.raises(CredentialsError):
            ConcreteProvider.from_env()

    def test_from_env_succeeds_with_key(self, monkeypatch):
        """from_env creates provider when env var is set."""
        monkeypatch.setenv("TEST_API_KEY", "my-test-key")
        provider = ConcreteProvider.from_env()
        assert provider.validate_credentials() is True

    def test_repr(self):
        """__repr__ returns readable string."""
        provider = ConcreteProvider(model="my-model")
        assert "ConcreteProvider" in repr(provider)
        assert "my-model" in repr(provider)


class TestProviderErrors:
    """Tests for provider error classes."""

    def test_provider_error_is_exception(self):
        """ProviderError inherits from Exception."""
        err = ProviderError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"

    def test_credentials_error_is_provider_error(self):
        """CredentialsError inherits from ProviderError."""
        err = CredentialsError("missing key")
        assert isinstance(err, ProviderError)
        assert isinstance(err, Exception)

    def test_generation_error_is_provider_error(self):
        """GenerationError inherits from ProviderError."""
        err = GenerationError("generation failed")
        assert isinstance(err, ProviderError)
        assert isinstance(err, Exception)
