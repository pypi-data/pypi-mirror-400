"""Modal account configuration.

Handles Modal API token and workspace configuration with support for:
- Multiple Modal accounts
- Environment variable defaults
- Explicit credential passing

Tiger Style:
- Frozen dataclass (immutable config)
- Explicit error handling
- Clear validation
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModalConfig:
    """Modal account configuration.

    Credentials can be provided explicitly or via environment variables.

    Environment variables (defaults):
    - MODAL_TOKEN_ID
    - MODAL_TOKEN_SECRET
    - MODAL_WORKSPACE (optional)

    Example (explicit credentials):
        config = ModalConfig(
            token_id="ak-abc123",
            token_secret="as-xyz789",
            workspace="my-team",
        )

    Example (environment variables):
        # Uses MODAL_TOKEN_ID, MODAL_TOKEN_SECRET from env
        config = ModalConfig.from_env()

    Example (mixed):
        # Override token but use default workspace
        config = ModalConfig(
            token_id="ak-abc123",
            token_secret="as-xyz789",
        )
    """

    token_id: str | None = None
    token_secret: str | None = None
    workspace: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration.

        At least one of token_id or MODAL_TOKEN_ID must be set.
        """
        # Get effective values (explicit or env)
        effective_token_id = self.token_id or os.getenv("MODAL_TOKEN_ID")
        effective_token_secret = self.token_secret or os.getenv("MODAL_TOKEN_SECRET")

        # Validate
        if not effective_token_id:
            raise ValueError(
                "Modal token_id not provided and MODAL_TOKEN_ID env var not set. "
                "Provide token_id explicitly or set MODAL_TOKEN_ID environment variable."
            )

        if not effective_token_secret:
            raise ValueError(
                "Modal token_secret not provided and MODAL_TOKEN_SECRET env var not set. "
                "Provide token_secret explicitly or set MODAL_TOKEN_SECRET environment variable."
            )

    @classmethod
    def from_env(cls) -> "ModalConfig":
        """Create config from environment variables only.

        Raises:
            ValueError: If required env vars not set

        Example:
            >>> config = ModalConfig.from_env()
            >>> # Uses MODAL_TOKEN_ID, MODAL_TOKEN_SECRET, MODAL_WORKSPACE from env
        """
        return cls(
            token_id=None,  # Will use env var
            token_secret=None,  # Will use env var
            workspace=None,  # Will use env var if set
        )

    def get_effective_token_id(self) -> str:
        """Get token ID (explicit or from env).

        Returns:
            Token ID string (guaranteed to exist after __post_init__)
        """
        token_id = self.token_id or os.getenv("MODAL_TOKEN_ID")
        assert token_id, "token_id should be validated in __post_init__"
        return token_id

    def get_effective_token_secret(self) -> str:
        """Get token secret (explicit or from env).

        Returns:
            Token secret string (guaranteed to exist after __post_init__)
        """
        token_secret = self.token_secret or os.getenv("MODAL_TOKEN_SECRET")
        assert token_secret, "token_secret should be validated in __post_init__"
        return token_secret

    def get_effective_workspace(self) -> str | None:
        """Get workspace (explicit or from env).

        Returns:
            Workspace string or None (workspace is optional)
        """
        return self.workspace or os.getenv("MODAL_WORKSPACE")

    def to_env_dict(self) -> dict[str, str]:
        """Export as environment variable dict for subprocess.

        Returns:
            Dict with MODAL_TOKEN_ID, MODAL_TOKEN_SECRET, MODAL_WORKSPACE (if set)

        Example:
            >>> config = ModalConfig(token_id="ak-xxx", token_secret="as-yyy")
            >>> env = config.to_env_dict()
            >>> # Use with subprocess
            >>> subprocess.run(..., env={**os.environ, **env})
        """
        env = {
            "MODAL_TOKEN_ID": self.get_effective_token_id(),
            "MODAL_TOKEN_SECRET": self.get_effective_token_secret(),
        }

        workspace = self.get_effective_workspace()
        if workspace:
            env["MODAL_WORKSPACE"] = workspace

        return env
