"""Tests for Google provider."""

import pytest
import sys
from unittest.mock import patch, MagicMock

from blueprint.providers.base import CredentialsError, GenerationError
from blueprint.providers.google import (
    GoogleProvider,
    MODEL_GEMINI_15_PRO,
    MODEL_GEMINI_15_FLASH,
    MODEL_GEMINI_PRO,
    DEFAULT_MODEL,
)


class TestGoogleProvider:
    """Tests for GoogleProvider class."""

    @pytest.fixture
    def mock_genai(self):
        """Mock the google.generativeai module."""
        mock = MagicMock()
        with patch.dict(sys.modules, {"google.generativeai": mock}):
            yield mock

    def test_init_with_api_key(self, mock_genai):
        """Provider initializes with API key."""
        provider = GoogleProvider(api_key="test-key")
        assert provider._api_key == "test-key"
        assert provider._model == DEFAULT_MODEL
        mock_genai.configure.assert_called_once_with(api_key="test-key")
        mock_genai.GenerativeModel.assert_called_once_with(DEFAULT_MODEL)

    def test_init_with_custom_model(self, mock_genai):
        """Provider accepts custom model."""
        provider = GoogleProvider(api_key="test-key", model=MODEL_GEMINI_15_FLASH)
        assert provider._model == MODEL_GEMINI_15_FLASH

    def test_get_model_name(self, mock_genai):
        """get_model_name returns current model."""
        provider = GoogleProvider(api_key="test-key", model=MODEL_GEMINI_PRO)
        assert provider.get_model_name() == MODEL_GEMINI_PRO

    def test_validate_credentials_with_key(self, mock_genai):
        """validate_credentials returns True with valid key."""
        provider = GoogleProvider(api_key="test-key")
        assert provider.validate_credentials() is True

    def test_validate_credentials_empty_key(self, mock_genai):
        """validate_credentials returns False with empty key."""
        provider = GoogleProvider(api_key="")
        assert provider.validate_credentials() is False

    def test_env_var_name(self):
        """env_var_name returns GOOGLE_API_KEY."""
        assert GoogleProvider.env_var_name() == "GOOGLE_API_KEY"

    def test_from_env_with_key(self, mock_genai, monkeypatch):
        """from_env creates provider when env var set."""
        monkeypatch.setenv("GOOGLE_API_KEY", "env-test-key")
        provider = GoogleProvider.from_env()
        assert provider._api_key == "env-test-key"

    def test_from_env_without_key(self, mock_genai, monkeypatch):
        """from_env raises CredentialsError when env var not set."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        with pytest.raises(CredentialsError) as exc_info:
            GoogleProvider.from_env()
        assert "GOOGLE_API_KEY" in str(exc_info.value)

    def test_generate_completion(self, mock_genai):
        """generate_completion returns model response."""
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        provider = GoogleProvider(api_key="test-key")
        result = provider.generate_completion("Test prompt")

        assert result == "Generated response"
        mock_genai.GenerativeModel.return_value.generate_content.assert_called_once()

    def test_generate_completion_with_params(self, mock_genai):
        """generate_completion passes parameters correctly."""
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        provider = GoogleProvider(api_key="test-key")
        provider.generate_completion("Prompt", max_tokens=1000, temperature=0.5)

        call_args = mock_genai.GenerativeModel.return_value.generate_content.call_args
        generation_config = call_args[1]["generation_config"]
        assert generation_config["max_output_tokens"] == 1000
        assert generation_config["temperature"] == 0.5

    def test_generate_completion_with_system_prompt(self, mock_genai):
        """generate_completion handles system prompt."""
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        provider = GoogleProvider(api_key="test-key")
        provider.generate_completion("Prompt", system="You are helpful")

        call_args = mock_genai.GenerativeModel.return_value.generate_content.call_args
        prompt_sent = call_args[0][0]
        assert "You are helpful" in prompt_sent
        assert "Prompt" in prompt_sent

    def test_generate_completion_api_error(self, mock_genai):
        """generate_completion raises GenerationError on API failure."""
        provider = GoogleProvider(api_key="test-key")

        with patch.object(
            provider,
            "_call_with_retry",
            side_effect=GenerationError("Google API call failed: API Error"),
        ):
            with pytest.raises(GenerationError) as exc_info:
                provider.generate_completion("Test")
            assert "API Error" in str(exc_info.value)

    def test_repr(self, mock_genai):
        """__repr__ returns readable string."""
        provider = GoogleProvider(api_key="test-key", model=MODEL_GEMINI_15_PRO)
        repr_str = repr(provider)
        assert "GoogleProvider" in repr_str
        assert MODEL_GEMINI_15_PRO in repr_str


class TestModelConstants:
    """Tests for model constants."""

    def test_model_gemini_15_pro_defined(self):
        """MODEL_GEMINI_15_PRO constant is defined."""
        assert MODEL_GEMINI_15_PRO == "gemini-1.5-pro"

    def test_model_gemini_15_flash_defined(self):
        """MODEL_GEMINI_15_FLASH constant is defined."""
        assert MODEL_GEMINI_15_FLASH == "gemini-1.5-flash"

    def test_model_gemini_pro_defined(self):
        """MODEL_GEMINI_PRO constant is defined."""
        assert MODEL_GEMINI_PRO == "gemini-pro"

    def test_default_model_is_gemini_15_pro(self):
        """DEFAULT_MODEL is Gemini 1.5 Pro."""
        assert DEFAULT_MODEL == MODEL_GEMINI_15_PRO
