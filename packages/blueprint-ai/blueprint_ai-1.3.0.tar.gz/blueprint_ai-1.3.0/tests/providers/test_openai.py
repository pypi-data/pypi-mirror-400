"""Tests for OpenAI provider."""

import pytest
from unittest.mock import patch, MagicMock

from blueprint.providers.base import CredentialsError, GenerationError
from blueprint.providers.openai import (
    OpenAIProvider,
    MODEL_GPT4O,
    MODEL_GPT4_TURBO,
    MODEL_GPT4,
    MODEL_GPT35_TURBO,
    DEFAULT_MODEL,
)


class TestOpenAIProvider:
    """Tests for OpenAIProvider class."""

    @pytest.fixture
    def mock_openai(self):
        """Mock the openai module."""
        with patch("openai.OpenAI") as mock:
            yield mock

    def test_init_with_api_key(self, mock_openai):
        """Provider initializes with API key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider._api_key == "test-key"
        assert provider._model == DEFAULT_MODEL
        mock_openai.assert_called_once_with(api_key="test-key")

    def test_init_with_custom_model(self, mock_openai):
        """Provider accepts custom model."""
        provider = OpenAIProvider(api_key="test-key", model=MODEL_GPT35_TURBO)
        assert provider._model == MODEL_GPT35_TURBO

    def test_get_model_name(self, mock_openai):
        """get_model_name returns current model."""
        provider = OpenAIProvider(api_key="test-key", model=MODEL_GPT4)
        assert provider.get_model_name() == MODEL_GPT4

    def test_validate_credentials_with_key(self, mock_openai):
        """validate_credentials returns True with valid key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.validate_credentials() is True

    def test_validate_credentials_empty_key(self, mock_openai):
        """validate_credentials returns False with empty key."""
        provider = OpenAIProvider(api_key="")
        assert provider.validate_credentials() is False

    def test_env_var_name(self):
        """env_var_name returns OPENAI_API_KEY."""
        assert OpenAIProvider.env_var_name() == "OPENAI_API_KEY"

    def test_from_env_with_key(self, mock_openai, monkeypatch):
        """from_env creates provider when env var set."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")
        provider = OpenAIProvider.from_env()
        assert provider._api_key == "env-test-key"

    def test_from_env_without_key(self, mock_openai, monkeypatch):
        """from_env raises CredentialsError when env var not set."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(CredentialsError) as exc_info:
            OpenAIProvider.from_env()
        assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_generate_completion(self, mock_openai):
        """generate_completion returns model response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Generated response"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        result = provider.generate_completion("Test prompt")

        assert result == "Generated response"
        mock_openai.return_value.chat.completions.create.assert_called_once()

    def test_generate_completion_with_params(self, mock_openai):
        """generate_completion passes parameters correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        provider.generate_completion(
            "Prompt",
            max_tokens=1000,
            temperature=0.5,
            model=MODEL_GPT35_TURBO,
        )

        call_kwargs = mock_openai.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 1000
        assert call_kwargs["model"] == MODEL_GPT35_TURBO
        assert call_kwargs["temperature"] == 0.5

    def test_generate_completion_with_system_prompt(self, mock_openai):
        """generate_completion handles system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        provider.generate_completion("Prompt", system="You are helpful")

        call_kwargs = mock_openai.return_value.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful"

    def test_generate_completion_api_error(self, mock_openai):
        """generate_completion raises GenerationError on API failure."""
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        provider = OpenAIProvider(api_key="test-key")

        # Disable retries for faster test
        with patch.object(
            provider,
            "_call_with_retry",
            side_effect=GenerationError("OpenAI API call failed: API Error"),
        ):
            with pytest.raises(GenerationError) as exc_info:
                provider.generate_completion("Test")
            assert "API Error" in str(exc_info.value)

    def test_repr(self, mock_openai):
        """__repr__ returns readable string."""
        provider = OpenAIProvider(api_key="test-key", model=MODEL_GPT4O)
        repr_str = repr(provider)
        assert "OpenAIProvider" in repr_str
        assert MODEL_GPT4O in repr_str


class TestModelConstants:
    """Tests for model constants."""

    def test_model_gpt4o_defined(self):
        """MODEL_GPT4O constant is defined."""
        assert MODEL_GPT4O == "gpt-4o"

    def test_model_gpt4_turbo_defined(self):
        """MODEL_GPT4_TURBO constant is defined."""
        assert MODEL_GPT4_TURBO == "gpt-4-turbo"

    def test_model_gpt4_defined(self):
        """MODEL_GPT4 constant is defined."""
        assert MODEL_GPT4 == "gpt-4"

    def test_model_gpt35_turbo_defined(self):
        """MODEL_GPT35_TURBO constant is defined."""
        assert MODEL_GPT35_TURBO == "gpt-3.5-turbo"

    def test_default_model_is_gpt4o(self):
        """DEFAULT_MODEL is GPT-4o."""
        assert DEFAULT_MODEL == MODEL_GPT4O
