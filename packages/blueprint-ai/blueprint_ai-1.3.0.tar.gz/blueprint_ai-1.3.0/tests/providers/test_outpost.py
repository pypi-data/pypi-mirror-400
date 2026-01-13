"""Tests for Outpost provider."""

import pytest
import sys
from unittest.mock import patch, MagicMock

from blueprint.providers.base import CredentialsError, GenerationError
from blueprint.providers.outpost import (
    OutpostProvider,
    DEFAULT_SSM_INSTANCE,
    AGENT_CLAUDE,
    AGENT_CODEX,
    AGENT_GEMINI,
    AGENT_GROK,
    AGENT_AIDER,
    DEFAULT_AGENT,
    AVAILABLE_AGENTS,
)


class TestOutpostProvider:
    """Tests for OutpostProvider class."""

    @pytest.fixture
    def mock_boto3(self):
        """Mock the boto3 module."""
        mock = MagicMock()
        with patch.dict(sys.modules, {"boto3": mock}):
            yield mock

    def test_init_with_defaults(self, mock_boto3):
        """Provider initializes with default values."""
        provider = OutpostProvider()
        assert provider._ssm_instance == DEFAULT_SSM_INSTANCE
        assert provider._agent == DEFAULT_AGENT
        assert provider._region == "us-east-1"

    def test_init_with_custom_agent(self, mock_boto3):
        """Provider accepts custom agent."""
        provider = OutpostProvider(agent=AGENT_CODEX)
        assert provider._agent == AGENT_CODEX

    def test_init_with_invalid_agent(self, mock_boto3):
        """Provider rejects invalid agent."""
        with pytest.raises(ValueError) as exc_info:
            OutpostProvider(agent="invalid")
        assert "Unknown agent" in str(exc_info.value)

    def test_init_with_ssm_instance(self, mock_boto3):
        """Provider accepts custom SSM instance."""
        provider = OutpostProvider(ssm_instance="mi-custom")
        assert provider._ssm_instance == "mi-custom"

    def test_init_with_aws_profile(self, mock_boto3):
        """Provider passes AWS profile to session."""
        OutpostProvider(aws_profile="myprofile")
        mock_boto3.Session.assert_called_with(
            region_name="us-east-1",
            profile_name="myprofile",
        )

    def test_get_model_name(self, mock_boto3):
        """get_model_name returns agent identifier."""
        provider = OutpostProvider(agent=AGENT_GEMINI)
        assert provider.get_model_name() == "outpost:gemini"

    def test_env_var_name(self):
        """env_var_name returns OUTPOST_SSM_INSTANCE."""
        assert OutpostProvider.env_var_name() == "OUTPOST_SSM_INSTANCE"

    def test_from_env_with_default(self, mock_boto3, monkeypatch):
        """from_env uses default SSM instance."""
        monkeypatch.delenv("OUTPOST_SSM_INSTANCE", raising=False)
        monkeypatch.delenv("AWS_PROFILE", raising=False)

        # Mock successful AWS access
        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.return_value = {}
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider.from_env()
        assert provider._ssm_instance == DEFAULT_SSM_INSTANCE

    def test_from_env_with_custom_instance(self, mock_boto3, monkeypatch):
        """from_env uses OUTPOST_SSM_INSTANCE if set."""
        monkeypatch.setenv("OUTPOST_SSM_INSTANCE", "mi-custom-instance")

        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.return_value = {}
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider.from_env()
        assert provider._ssm_instance == "mi-custom-instance"

    def test_from_env_with_aws_profile(self, mock_boto3, monkeypatch):
        """from_env passes AWS_PROFILE to session."""
        monkeypatch.setenv("AWS_PROFILE", "testprofile")

        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.return_value = {}
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        OutpostProvider.from_env()

        mock_boto3.Session.assert_called_with(
            region_name="us-east-1",
            profile_name="testprofile",
        )

    def test_from_env_credential_error(self, mock_boto3, monkeypatch):
        """from_env raises CredentialsError on AWS failure."""
        monkeypatch.delenv("OUTPOST_SSM_INSTANCE", raising=False)

        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.side_effect = Exception("No credentials")
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        with pytest.raises(CredentialsError) as exc_info:
            OutpostProvider.from_env()
        assert "Cannot access AWS SSM" in str(exc_info.value)

    def test_generate_completion_success(self, mock_boto3):
        """generate_completion returns agent response."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()

        # Mock send_command
        mock_ssm.send_command.return_value = {
            "Command": {"CommandId": "cmd-123"}
        }

        # Mock get_command_invocation
        mock_ssm.get_command_invocation.return_value = {
            "Status": "Success",
            "StandardOutputContent": "Hello from Outpost!",
        }

        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider()
        result = provider.generate_completion("Say hello")

        assert result == "Hello from Outpost!"
        mock_ssm.send_command.assert_called_once()

    def test_generate_completion_with_agent_override(self, mock_boto3):
        """generate_completion can override agent."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()

        mock_ssm.send_command.return_value = {
            "Command": {"CommandId": "cmd-123"}
        }
        mock_ssm.get_command_invocation.return_value = {
            "Status": "Success",
            "StandardOutputContent": "Response",
        }

        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider(agent=AGENT_CLAUDE)
        provider.generate_completion("Prompt", agent=AGENT_CODEX)

        # Check the command used codex script
        call_args = mock_ssm.send_command.call_args
        command = call_args[1]["Parameters"]["commands"][0]
        assert "dispatch-codex.sh" in command

    def test_generate_completion_failure(self, mock_boto3):
        """generate_completion raises GenerationError on failure."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()

        mock_ssm.send_command.return_value = {
            "Command": {"CommandId": "cmd-123"}
        }
        mock_ssm.get_command_invocation.return_value = {
            "Status": "Failed",
            "StandardErrorContent": "Something went wrong",
        }

        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider()

        with pytest.raises(GenerationError) as exc_info:
            provider.generate_completion("Test")
        assert "Failed" in str(exc_info.value)

    def test_generate_completion_invalid_agent(self, mock_boto3):
        """generate_completion raises error for invalid agent override."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider()

        with pytest.raises(GenerationError) as exc_info:
            provider.generate_completion("Test", agent="invalid_agent")
        assert "Unknown agent" in str(exc_info.value)

    def test_validate_credentials_success(self, mock_boto3):
        """validate_credentials returns True on success."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.return_value = {}
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider()
        assert provider.validate_credentials() is True

    def test_validate_credentials_failure(self, mock_boto3):
        """validate_credentials returns False on failure."""
        mock_session = MagicMock()
        mock_ssm = MagicMock()
        mock_ssm.describe_instance_information.side_effect = Exception("Auth error")
        mock_session.client.return_value = mock_ssm
        mock_boto3.Session.return_value = mock_session

        provider = OutpostProvider()
        assert provider.validate_credentials() is False

    def test_repr(self, mock_boto3):
        """__repr__ returns readable string."""
        provider = OutpostProvider(agent=AGENT_CLAUDE)
        repr_str = repr(provider)
        assert "OutpostProvider" in repr_str
        assert "outpost:claude" in repr_str


class TestAgentConstants:
    """Tests for agent constants."""

    def test_all_agents_defined(self):
        """All agent constants are defined."""
        assert AGENT_CLAUDE == "claude"
        assert AGENT_CODEX == "codex"
        assert AGENT_GEMINI == "gemini"
        assert AGENT_GROK == "grok"
        assert AGENT_AIDER == "aider"

    def test_default_agent_is_claude(self):
        """DEFAULT_AGENT is claude."""
        assert DEFAULT_AGENT == AGENT_CLAUDE

    def test_available_agents_list(self):
        """AVAILABLE_AGENTS contains all agents."""
        assert len(AVAILABLE_AGENTS) == 5
        assert AGENT_CLAUDE in AVAILABLE_AGENTS
        assert AGENT_CODEX in AVAILABLE_AGENTS
        assert AGENT_GEMINI in AVAILABLE_AGENTS
        assert AGENT_GROK in AVAILABLE_AGENTS
        assert AGENT_AIDER in AVAILABLE_AGENTS


class TestDefaultSSMInstance:
    """Tests for SSM instance configuration."""

    def test_default_instance_is_outpost_prod(self):
        """DEFAULT_SSM_INSTANCE points to outpost-prod."""
        assert DEFAULT_SSM_INSTANCE == "mi-0bbd8fed3f0650ddb"
