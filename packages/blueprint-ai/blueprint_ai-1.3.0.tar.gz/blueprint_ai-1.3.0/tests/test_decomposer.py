"""Tests for the goal decomposer.

These tests verify the decomposer can break down goals into atomic tasks
with proper structure and dependencies.

Updated for v1.3.0: Multi-provider support via provider registry.
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from blueprint.generator.decomposer import (
    GoalDecomposer,
    decompose_goal,
    DecompositionError,
)
from blueprint.providers.base import ProviderBase


class MockProvider(ProviderBase):
    """Mock provider for testing."""

    def __init__(self, response: str = '[{"task_id": "T1", "name": "Test", "dependencies": [], "acceptance_criteria": ["Done"]}]'):
        self.response = response
        self.generate_calls = []

    def generate_completion(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7, **kwargs) -> str:
        self.generate_calls.append({"prompt": prompt, "max_tokens": max_tokens})
        return self.response

    def get_model_name(self) -> str:
        return "mock-model"

    def validate_credentials(self) -> bool:
        return True

    @classmethod
    def from_env(cls) -> "MockProvider":
        return cls()

    @classmethod
    def env_var_name(cls) -> str:
        return "MOCK_API_KEY"


class TestGoalDecomposer:
    """Test suite for GoalDecomposer class."""

    def test_init_with_provider_instance(self):
        """Should accept a ProviderBase instance directly."""
        provider = MockProvider()
        decomposer = GoalDecomposer(provider=provider)
        assert decomposer.provider is provider

    def test_init_with_provider_name(self):
        """Should accept provider name and use registry."""
        with patch("blueprint.generator.decomposer.get_provider") as mock_get:
            mock_provider = MockProvider()
            mock_get.return_value = mock_provider
            decomposer = GoalDecomposer(provider="anthropic")
            assert decomposer.provider is mock_provider
            mock_get.assert_called_once_with("anthropic")

    def test_init_with_no_provider_uses_default(self):
        """Should use default provider from registry when none specified."""
        with patch("blueprint.generator.decomposer.get_provider") as mock_get:
            mock_provider = MockProvider()
            mock_get.return_value = mock_provider
            decomposer = GoalDecomposer()
            mock_get.assert_called_once_with()

    def test_init_raises_on_provider_error(self):
        """Should raise DecompositionError when provider fails."""
        from blueprint.providers.base import ProviderError
        with patch("blueprint.generator.decomposer.get_provider") as mock_get:
            mock_get.side_effect = ProviderError("No API key")
            with pytest.raises(DecompositionError, match="No provider configured"):
                GoalDecomposer()

    def test_legacy_params_emit_deprecation_warning(self):
        """Should emit deprecation warning for legacy api_key and model params."""
        provider = MockProvider()
        with pytest.warns(DeprecationWarning, match="api_key and model parameters are deprecated"):
            GoalDecomposer(provider=provider, api_key="old-key", model="old-model")

    def test_parse_response_extracts_json(self):
        """Should extract JSON array from response."""
        decomposer = GoalDecomposer.__new__(GoalDecomposer)

        response = '[{"task_id": "T1", "name": "Test"}]'
        result = decomposer._parse_response(response)

        assert len(result) == 1
        assert result[0]["task_id"] == "T1"

    def test_parse_response_handles_markdown_fencing(self):
        """Should handle response wrapped in markdown code blocks."""
        decomposer = GoalDecomposer.__new__(GoalDecomposer)

        response = '```json\n[{"task_id": "T1", "name": "Test"}]\n```'
        result = decomposer._parse_response(response)

        assert len(result) == 1
        assert result[0]["task_id"] == "T1"

    def test_validate_tasks_checks_required_fields(self):
        """Should validate that required fields are present."""
        decomposer = GoalDecomposer.__new__(GoalDecomposer)

        tasks = [{"task_id": "T1"}]  # Missing name, dependencies, acceptance_criteria

        with pytest.raises(DecompositionError, match="missing required fields"):
            decomposer._validate_tasks(tasks)

    def test_validate_tasks_checks_dependencies(self):
        """Should validate that dependencies reference existing tasks."""
        decomposer = GoalDecomposer.__new__(GoalDecomposer)

        tasks = [{
            "task_id": "T1",
            "name": "Test",
            "dependencies": ["T99"],  # Non-existent
            "acceptance_criteria": ["Done"]
        }]

        with pytest.raises(DecompositionError, match="unknown dependency"):
            decomposer._validate_tasks(tasks)

    def test_validate_tasks_sets_defaults(self):
        """Should set default values for optional fields."""
        decomposer = GoalDecomposer.__new__(GoalDecomposer)

        tasks = [{
            "task_id": "T1",
            "name": "Test",
            "dependencies": [],
            "acceptance_criteria": ["Done"]
        }]

        decomposer._validate_tasks(tasks)

        assert tasks[0]["estimated_sessions"] == 1
        assert tasks[0]["files_to_create"] == []
        assert tasks[0]["files_to_modify"] == []
        assert tasks[0]["requires_human"] is False

    def test_decompose_uses_provider(self):
        """Should use provider generate_completion for decomposition."""
        provider = MockProvider()
        decomposer = GoalDecomposer(provider=provider)

        tasks = decomposer.decompose("Build a REST API")

        assert len(provider.generate_calls) == 1
        assert "Build a REST API" in provider.generate_calls[0]["prompt"]
        assert len(tasks) == 1
        assert tasks[0].task_id == "T1"


class TestDecomposeGoalFunction:
    """Test suite for convenience function."""

    def test_decompose_goal_with_provider_instance(self):
        """Should accept provider instance directly."""
        provider = MockProvider()
        tasks = decompose_goal("Test goal", provider=provider)

        assert len(tasks) == 1
        assert tasks[0].task_id == "T1"

    def test_decompose_goal_with_provider_name(self):
        """Should accept provider name string."""
        with patch("blueprint.generator.decomposer.get_provider") as mock_get:
            mock_provider = MockProvider()
            mock_get.return_value = mock_provider
            tasks = decompose_goal("Test goal", provider="openai")

            mock_get.assert_called_once_with("openai")
            assert len(tasks) == 1


# Integration test - only runs if API key is available
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
class TestDecomposerIntegration:
    """Integration tests that require actual API access."""

    def test_real_decomposition_with_anthropic(self):
        """Test actual decomposition with Anthropic provider."""
        tasks = decompose_goal(
            "Build a simple hello world CLI in Python",
            provider="anthropic",
        )

        assert len(tasks) >= 2
        assert all(hasattr(t, "task_id") for t in tasks)
        assert all(hasattr(t, "name") for t in tasks)
        assert all(hasattr(t, "dependencies") for t in tasks)
