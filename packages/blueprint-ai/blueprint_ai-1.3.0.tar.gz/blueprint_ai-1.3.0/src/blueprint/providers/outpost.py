"""Outpost fleet provider implementation.

This module implements the ProviderBase interface using the Outpost fleet
dispatch system. No API key required - uses IAM role authentication.

Environment:
    OUTPOST_SSM_INSTANCE: SSM instance ID (default: mi-0bbd8fed3f0650ddb)
    AWS_PROFILE: Optional AWS profile for credentials

Supported Agents:
    - claude (default)
    - codex
    - gemini
    - grok
    - aider
"""

import os
from typing import Any

from blueprint.providers.base import (
    ProviderBase,
    CredentialsError,
    GenerationError,
)

# Default SSM instance (outpost-prod)
DEFAULT_SSM_INSTANCE = "mi-0bbd8fed3f0650ddb"

# Agent identifiers
AGENT_CLAUDE = "claude"
AGENT_CODEX = "codex"
AGENT_GEMINI = "gemini"
AGENT_GROK = "grok"
AGENT_AIDER = "aider"
DEFAULT_AGENT = AGENT_CLAUDE

AVAILABLE_AGENTS = [AGENT_CLAUDE, AGENT_CODEX, AGENT_GEMINI, AGENT_GROK, AGENT_AIDER]


class OutpostProvider(ProviderBase):
    """Outpost fleet provider implementation.

    Uses the Outpost SSM-based dispatch system to send prompts to various
    AI agents in the fleet. No API key required - uses IAM authentication.

    This provider is synchronous and waits for completion.

    Example:
        >>> provider = OutpostProvider.from_env()
        >>> response = provider.generate_completion("Hello, Outpost!")
        >>> print(response)
        "Hello! I'm running on the Outpost fleet..."

        >>> # With custom agent
        >>> provider = OutpostProvider(ssm_instance="mi-...", agent="codex")
        >>> response = provider.generate_completion("Write some code")
    """

    def __init__(
        self,
        ssm_instance: str = DEFAULT_SSM_INSTANCE,
        agent: str = DEFAULT_AGENT,
        aws_profile: str | None = None,
        region: str = "us-east-1",
        timeout_seconds: int = 600,
    ):
        """Initialize the Outpost provider.

        Args:
            ssm_instance: SSM instance ID for the Outpost server.
            agent: Agent to use (claude, codex, gemini, grok, aider).
            aws_profile: Optional AWS profile name.
            region: AWS region.
            timeout_seconds: Max wait time for response.
        """
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 package not installed. Install with: pip install boto3"
            )

        if agent not in AVAILABLE_AGENTS:
            raise ValueError(
                f"Unknown agent: {agent}. Available: {AVAILABLE_AGENTS}"
            )

        self._ssm_instance = ssm_instance
        self._agent = agent
        self._region = region
        self._timeout = timeout_seconds

        # Create boto3 session
        session_kwargs = {"region_name": region}
        if aws_profile:
            session_kwargs["profile_name"] = aws_profile

        self._session = boto3.Session(**session_kwargs)
        self._ssm = self._session.client("ssm")

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a completion using Outpost fleet.

        Args:
            prompt: The input prompt.
            max_tokens: Not used (agents handle their own limits).
            temperature: Not used (agents handle their own config).
            **kwargs: Additional arguments.
                - agent: Override the default agent for this call.
                - timeout: Override default timeout.

        Returns:
            Generated text response from stdout.

        Raises:
            GenerationError: If generation fails or times out.
        """
        agent = kwargs.pop("agent", self._agent)
        timeout = kwargs.pop("timeout", self._timeout)

        if agent not in AVAILABLE_AGENTS:
            raise GenerationError(f"Unknown agent: {agent}")

        # Build dispatch command
        command = self._build_dispatch_command(agent, prompt)

        try:
            # Send SSM command
            response = self._ssm.send_command(
                InstanceIds=[self._ssm_instance],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": [command]},
                TimeoutSeconds=timeout,
                Comment=f"Blueprint provider: {agent}",
            )

            command_id = response["Command"]["CommandId"]

            # Wait for completion
            import time
            start_time = time.time()

            while time.time() - start_time < timeout:
                result = self._ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=self._ssm_instance,
                )

                status = result.get("Status", "Pending")

                if status == "Success":
                    stdout = result.get("StandardOutputContent", "")
                    return self._extract_response(stdout)

                if status in ("Failed", "Cancelled", "TimedOut"):
                    stderr = result.get("StandardErrorContent", "")
                    raise GenerationError(
                        f"Outpost command failed: {status}. Error: {stderr[:500]}"
                    )

                time.sleep(5)

            raise GenerationError(f"Outpost command timed out after {timeout}s")

        except Exception as e:
            if isinstance(e, GenerationError):
                raise
            raise GenerationError(f"Outpost dispatch failed: {e}") from e

    def _build_dispatch_command(self, agent: str, prompt: str) -> str:
        """Build the SSM command for dispatching to an agent."""
        # Map agent to dispatch script
        dispatch_scripts = {
            "claude": "dispatch.sh",
            "codex": "dispatch-codex.sh",
            "gemini": "dispatch-gemini.sh",
            "grok": "dispatch-grok.sh",
            "aider": "dispatch-aider.sh",
        }

        script = dispatch_scripts.get(agent, "dispatch.sh")
        executor_path = "/home/ubuntu/claude-executor"

        # Escape prompt for shell
        escaped_prompt = prompt.replace("'", "'\\''")

        return f"""#!/bin/bash
cd {executor_path}
if [ -f "{script}" ]; then
    ./{script} /tmp/blueprint-provider '{escaped_prompt}'
else
    echo "Agent script not found: {script}"
    exit 1
fi
"""

    def _extract_response(self, stdout: str) -> str:
        """Extract the actual response from stdout.

        The dispatch scripts may include setup/teardown output.
        We look for the agent's actual response.
        """
        # For now, return the full stdout
        # Could be enhanced to parse specific markers
        return stdout.strip()

    def get_model_name(self) -> str:
        """Get the current agent name."""
        return f"outpost:{self._agent}"

    def validate_credentials(self) -> bool:
        """Check if AWS credentials are available.

        Returns True if we can create an SSM client.
        """
        try:
            # Try to describe instance - lightweight credential check
            self._ssm.describe_instance_information(MaxResults=1)
            return True
        except Exception:
            return False

    @classmethod
    def from_env(cls) -> "OutpostProvider":
        """Create provider from environment variables.

        Uses OUTPOST_SSM_INSTANCE if set, otherwise default.
        AWS credentials come from environment, profile, or IAM role.

        Returns:
            Configured OutpostProvider instance.

        Raises:
            CredentialsError: If AWS credentials cannot be found.
        """
        ssm_instance = os.environ.get("OUTPOST_SSM_INSTANCE", DEFAULT_SSM_INSTANCE)
        aws_profile = os.environ.get("AWS_PROFILE")

        try:
            import boto3
        except ImportError:
            raise CredentialsError(
                "boto3 package not installed. Install with: pip install boto3"
            )

        provider = cls(
            ssm_instance=ssm_instance,
            aws_profile=aws_profile,
        )

        # Validate we can access AWS
        try:
            provider._ssm.describe_instance_information(MaxResults=1)
        except Exception as e:
            raise CredentialsError(
                f"Cannot access AWS SSM. Check credentials. Error: {e}"
            )

        return provider

    @classmethod
    def env_var_name(cls) -> str:
        """Return the environment variable name for this provider.

        Note: Outpost uses IAM roles, not API keys.
        This returns the SSM instance var for consistency.
        """
        return "OUTPOST_SSM_INSTANCE"
