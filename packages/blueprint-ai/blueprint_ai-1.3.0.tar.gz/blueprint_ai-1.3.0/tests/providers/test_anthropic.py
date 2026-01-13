"""Tests for Anthropic provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from blueprint.providers.base import CredentialsError, GenerationError
from blueprint.providers.anthropic import (
    AnthropicProvider,
    MODEL_OPUS,
    MODEL_SONNET,
    DEFAULT_MODEL,
)


class TestAnthropicProvider:
    """Tests for AnthropicProvider class."""

    @pytest.fixture
    def mock_anthropic(self):
        """Mock the anthropic module."""
        with patch("anthropic.Anthropic") as mock:
            yield mock

    def test_init_with_api_key(self, mock_anthropic):
        """Provider initializes with API key."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider._api_key == "test-key"
        assert provider._model == DEFAULT_MODEL
        mock_anthropic.assert_called_once_with(api_key="test-key")

    def test_init_with_custom_model(self, mock_anthropic):
        """Provider accepts custom model."""
        provider = AnthropicProvider(api_key="test-key", model=MODEL_SONNET)
        assert provider._model == MODEL_SONNET

    def test_get_model_name(self, mock_anthropic):
        """get_model_name returns current model."""
        provider = AnthropicProvider(api_key="test-key", model=MODEL_OPUS)
        assert provider.get_model_name() == MODEL_OPUS

    def test_validate_credentials_with_key(self, mock_anthropic):
        """validate_credentials returns True with valid key."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.validate_credentials() is True

    def test_validate_credentials_empty_key(self, mock_anthropic):
        """validate_credentials returns False with empty key."""
        provider = AnthropicProvider(api_key="")
        assert provider.validate_credentials() is False

    def test_env_var_name(self):
        """env_var_name returns ANTHROPIC_API_KEY."""
        assert AnthropicProvider.env_var_name() == "ANTHROPIC_API_KEY"

    def test_from_env_with_key(self, mock_anthropic, monkeypatch):
        """from_env creates provider when env var set."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "env-test-key")
        provider = AnthropicProvider.from_env()
        assert provider._api_key == "env-test-key"

    def test_from_env_without_key(self, mock_anthropic, monkeypatch):
        """from_env raises CredentialsError when env var not set."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(CredentialsError) as exc_info:
            AnthropicProvider.from_env()
        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_generate_completion(self, mock_anthropic):
        """generate_completion returns model response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated response")]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        result = provider.generate_completion("Test prompt")

        assert result == "Generated response"
        mock_anthropic.return_value.messages.create.assert_called_once()

    def test_generate_completion_with_params(self, mock_anthropic):
        """generate_completion passes parameters correctly."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        provider.generate_completion(
            "Prompt",
            max_tokens=1000,
            temperature=0.5,
            model=MODEL_SONNET,
        )

        call_kwargs = mock_anthropic.return_value.messages.create.call_args[1]
        assert call_kwargs["max_tokens"] == 1000
        assert call_kwargs["model"] == MODEL_SONNET

    def test_generate_completion_with_system_prompt(self, mock_anthropic):
        """generate_completion handles system prompt."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        provider.generate_completion("Prompt", system="You are helpful")

        call_kwargs = mock_anthropic.return_value.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are helpful"

    def test_generate_completion_api_error(self, mock_anthropic):
        """generate_completion raises GenerationError on API failure."""
        mock_anthropic.return_value.messages.create.side_effect = Exception(
            "API Error"
        )

        provider = AnthropicProvider(api_key="test-key")

        # Disable retries for faster test
        with patch.object(
            provider,
            "_call_with_retry",
            side_effect=GenerationError("Anthropic API call failed: API Error"),
        ):
            with pytest.raises(GenerationError) as exc_info:
                provider.generate_completion("Test")
            assert "API Error" in str(exc_info.value)

    def test_repr(self, mock_anthropic):
        """__repr__ returns readable string."""
        provider = AnthropicProvider(api_key="test-key", model=MODEL_OPUS)
        repr_str = repr(provider)
        assert "AnthropicProvider" in repr_str
        assert MODEL_OPUS in repr_str


class TestModelConstants:
    """Tests for model constants."""

    def test_model_opus_defined(self):
        """MODEL_OPUS constant is defined."""
        assert MODEL_OPUS == "claude-opus-4-5-20251101"

    def test_model_sonnet_defined(self):
        """MODEL_SONNET constant is defined."""
        assert MODEL_SONNET == "claude-sonnet-4-5-20250929"

    def test_default_model_is_opus(self):
        """DEFAULT_MODEL is Opus."""
        assert DEFAULT_MODEL == MODEL_OPUS
