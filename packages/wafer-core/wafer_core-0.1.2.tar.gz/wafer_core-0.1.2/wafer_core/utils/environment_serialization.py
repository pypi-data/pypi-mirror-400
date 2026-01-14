"""Serialization utilities for GPU benchmark environments.

Pure functions for serializing/deserializing environment state,
particularly deployment state reconstruction.

Tiger Style:
- Pure functions only (no classes, no state)
- Explicit inputs/outputs
- Centralized serialization logic
"""

from typing import Any

from wafer_core.utils.kernel_utils.deployment import (
    DeploymentConfig,
    DeploymentState,
    PythonEnvState,
)


def reconstruct_deployment_state(data: dict) -> DeploymentState:
    """Reconstruct DeploymentState from serialized dict.

    Handles nested dataclass reconstruction (config, env_state).

    Args:
        data: Serialized deployment state dict with keys:
            - workspace_path: str
            - env_state: dict (serialized PythonEnvState)
            - config: dict (serialized DeploymentConfig)

    Returns:
        Reconstructed DeploymentState instance

    Example:
        >>> data = {
        ...     "workspace_path": "/path/to/workspace",
        ...     "env_state": {"python_version": "3.10", ...},
        ...     "config": {"ssh_target": "user@host:22", ...},
        ... }
        >>> state = reconstruct_deployment_state(data)
        >>> assert isinstance(state, DeploymentState)
    """
    # Reconstruct nested dataclasses from dicts
    env_state = PythonEnvState(**data["env_state"])
    config = DeploymentConfig(**data["config"])

    return DeploymentState(
        workspace_path=data["workspace_path"],
        env_state=env_state,
        config=config,
    )


def serialize_deployment_state(state: DeploymentState) -> dict:
    """Serialize DeploymentState to dict.

    Inverse of reconstruct_deployment_state.

    Args:
        state: DeploymentState to serialize

    Returns:
        Dict suitable for JSON serialization

    Example:
        >>> from pathlib import Path
        >>> config = DeploymentConfig(ssh_target="user@host:22", ssh_key="~/.ssh/id_rsa", gpu_id=0)
        >>> env_state = PythonEnvState(python_version="3.10")
        >>> state = DeploymentState(workspace_path=Path("/workspace"), env_state=env_state, config=config)
        >>> data = serialize_deployment_state(state)
        >>> assert "workspace_path" in data
    """
    return {
        "workspace_path": str(state.workspace_path),
        "env_state": vars(state.env_state) if hasattr(state.env_state, "__dict__") else state.env_state,
        "config": vars(state.config) if hasattr(state.config, "__dict__") else state.config,
    }


def serialize_environment_checkpoint(
    sample_data: dict,
    ssh_target: str,
    ssh_key: str,
    gpu_ids: list[int],
    deployment_state: DeploymentState | None,
    workspace_dir: str | None,
    additional_data: dict[str, Any] | None = None,
) -> dict:
    """Create environment checkpoint for serialization.

    Packages all environment state into a dict suitable for checkpointing.

    Args:
        sample_data: Problem/sample data dict
        ssh_target: SSH connection string (user@host:port)
        ssh_key: Path to SSH key
        gpu_ids: List of GPU IDs
        deployment_state: Remote deployment state (or None)
        workspace_dir: Remote workspace directory path (or None)
        additional_data: Optional benchmark-specific data

    Returns:
        Checkpoint dict with all environment state

    Example:
        >>> checkpoint = serialize_environment_checkpoint(
        ...     sample_data={"problem_id": "p1"},
        ...     ssh_target="user@host:22",
        ...     ssh_key="~/.ssh/id_rsa",
        ...     gpu_ids=[0],
        ...     deployment_state=None,
        ...     workspace_dir=None,
        ... )
        >>> assert "sample_data" in checkpoint
    """
    checkpoint = {
        "sample_data": sample_data,
        "ssh_target": ssh_target,
        "ssh_key": ssh_key,
        "gpu_ids": gpu_ids,
        "workspace_dir": workspace_dir,
    }

    # Add deployment state if available
    if deployment_state is not None:
        checkpoint["deployment_state"] = serialize_deployment_state(deployment_state)

    # Add any additional benchmark-specific data
    if additional_data:
        checkpoint.update(additional_data)

    return checkpoint


def deserialize_environment_checkpoint(data: dict) -> dict:
    """Deserialize environment checkpoint.

    Reconstructs deployment state if present.

    Args:
        data: Serialized checkpoint dict

    Returns:
        Checkpoint dict with reconstructed objects

    Example:
        >>> data = {"sample_data": {...}, "deployment_state": {...}}
        >>> checkpoint = deserialize_environment_checkpoint(data)
        >>> if "deployment_state" in checkpoint:
        ...     assert isinstance(checkpoint["deployment_state"], DeploymentState)
    """
    checkpoint = dict(data)

    # Reconstruct deployment state if present
    if "deployment_state" in checkpoint and checkpoint["deployment_state"] is not None:
        checkpoint["deployment_state"] = reconstruct_deployment_state(checkpoint["deployment_state"])

    return checkpoint
