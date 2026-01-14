"""Target configuration for pluggable execution targets.

Tiger Style:
- Frozen dataclasses for immutable config
- Explicit over implicit
- No classes with methods (pure data)

Types of targets:
- BaremetalTarget: Physical GPU server (SSH access, NCU support)
- VMTarget: Virtual machine with GPU (SSH access, no NCU)
- ModalTarget: Serverless execution (Phase 5 - not implemented yet)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer_core.utils.kernel_utils.deployment import DeploymentConfig


@dataclass(frozen=True)
class BaremetalTarget:
    """Configuration for baremetal GPU server.

    Baremetal servers typically have:
    - Full privileged access (can run NCU profiling)
    - Consistent hardware (good for benchmarks)
    - SSH access via wafer_core.ssh

    Example (venv execution):
        target = BaremetalTarget(
            name="vultr-baremetal",
            ssh_target="chiraag@45.76.244.62:22",
            ssh_key="~/.ssh/id_ed25519",
            gpu_ids=[6, 7],  # Multiple GPUs for failover
            ncu_available=True,
        )

    Example (Docker execution - Modal-like):
        target = BaremetalTarget(
            name="vultr-docker",
            ssh_target="chiraag@45.76.244.62:22",
            ssh_key="~/.ssh/id_ed25519",
            gpu_ids=[6, 7],
            docker_image="nvcr.io/nvidia/cutlass:4.3-devel",
            pip_packages=["triton", "ninja", "nvidia-cutlass-dsl==4.3.0.dev0"],
            torch_package="torch>=2.8.0",
            torch_index_url="https://download.pytorch.org/whl/nightly/cu128",
        )
    """

    name: str
    ssh_target: str  # Format: user@host:port
    ssh_key: str  # Path to SSH private key
    gpu_ids: list[int]  # List of GPU IDs to try (in order)
    gpu_type: str = "B200"
    compute_capability: str = "10.0"
    ncu_available: bool = True  # Baremetal typically has NCU

    # Docker execution config (Modal-like). If docker_image is set, run in container.
    docker_image: str | None = None  # Docker image to use (e.g., "nvcr.io/nvidia/cutlass:4.3-devel")
    pip_packages: tuple[str, ...] = ()  # Packages to install via uv pip install
    torch_package: str | None = None  # Torch package spec (e.g., "torch>=2.8.0")
    torch_index_url: str | None = None  # Custom index for torch (e.g., PyTorch nightly)

    def __post_init__(self) -> None:
        """Validate configuration."""
        assert len(self.gpu_ids) > 0, "Must specify at least one GPU ID"
        assert ":" in self.ssh_target, f"ssh_target must include port (user@host:port), got: {self.ssh_target}"
        # If torch_index_url is set, torch_package must also be set
        if self.torch_index_url:
            assert self.torch_package, "torch_package must be set when torch_index_url is provided"


@dataclass(frozen=True)
class VMTarget:
    """Configuration for VM with GPU.

    VMs typically have:
    - Limited privileged access (no NCU profiling)
    - Less consistent hardware than baremetal
    - SSH access via wafer_core.ssh
    - Good for cheap/fast correctness checks

    Example (venv execution):
        target = VMTarget(
            name="lambda-vm",
            ssh_target="ubuntu@150.136.217.70:22",
            ssh_key="~/.ssh/lambda-mac",
            gpu_ids=[7],
            ncu_available=False,
        )

    Example (Docker execution - Modal-like):
        target = VMTarget(
            name="lambda-docker",
            ssh_target="ubuntu@150.136.217.70:22",
            ssh_key="~/.ssh/lambda-mac",
            gpu_ids=[7],
            docker_image="nvcr.io/nvidia/pytorch:24.01-py3",
            pip_packages=["triton", "ninja"],
        )
    """

    name: str
    ssh_target: str  # Format: user@host:port
    ssh_key: str  # Path to SSH private key
    gpu_ids: list[int]  # List of GPU IDs to try (in order)
    gpu_type: str = "B200"
    compute_capability: str = "10.0"
    ncu_available: bool = False  # VMs typically don't have NCU

    # Docker execution config (Modal-like). If docker_image is set, run in container.
    docker_image: str | None = None  # Docker image to use (e.g., "nvcr.io/nvidia/pytorch:24.01-py3")
    pip_packages: tuple[str, ...] = ()  # Packages to install via uv pip install
    torch_package: str | None = None  # Torch package spec (e.g., "torch>=2.8.0")
    torch_index_url: str | None = None  # Custom index for torch (e.g., PyTorch nightly)

    def __post_init__(self) -> None:
        """Validate configuration."""
        assert len(self.gpu_ids) > 0, "Must specify at least one GPU ID"
        assert ":" in self.ssh_target, f"ssh_target must include port (user@host:port), got: {self.ssh_target}"
        # If torch_index_url is set, torch_package must also be set
        if self.torch_index_url:
            assert self.torch_package, "torch_package must be set when torch_index_url is provided"


@dataclass(frozen=True)
class ModalTarget:
    """Configuration for Modal serverless execution.

    Modal provides:
    - On-demand GPU instances (no persistent SSH)
    - Fast cold starts (~10-15 seconds)
    - Good for parallel execution
    - No NCU profiling support
    - Pay-per-use (availability determined by plan/credits)

    Example:
        target = ModalTarget(
            name="modal-b200",
            modal_app_name="kernel-eval-b200",
            gpu_type="B200",
            gpu_arch="blackwell",  # Fallback to any Blackwell
            timeout_seconds=600,
        )

    Example with explicit credentials:
        target = ModalTarget(
            name="modal-b200",
            modal_app_name="kernel-eval-b200",
            modal_token_id="ak-xxx",
            modal_token_secret="as-yyy",
            modal_workspace="my-team",
        )
    """

    name: str
    modal_app_name: str  # Modal app identifier (e.g., "kernel-eval-b200")

    # Modal account configuration (optional - uses env vars if not provided)
    modal_token_id: str | None = None  # Modal API token ID (or MODAL_TOKEN_ID env var)
    modal_token_secret: str | None = None  # Modal token secret (or MODAL_TOKEN_SECRET env var)
    modal_workspace: str | None = None  # Optional workspace name (or MODAL_WORKSPACE env var)

    # GPU requirements
    gpu_type: str = "B200"  # Preferred GPU type
    gpu_arch: str | None = None  # Fallback: any GPU in this arch (e.g., "blackwell")
    compute_capability: str = "10.0"

    # Modal-specific settings
    timeout_seconds: int = 600  # Max execution time
    cpu_count: int = 4  # CPUs for kernel compilation
    memory_gb: int = 16  # Memory for compilation/execution

    # Modal doesn't support NCU profiling (no privileged access)
    ncu_available: bool = False

    def __post_init__(self) -> None:
        """Validate configuration."""
        import os

        assert self.modal_app_name, "modal_app_name cannot be empty"
        assert self.timeout_seconds > 0, "timeout_seconds must be positive"
        assert self.cpu_count > 0, "cpu_count must be positive"
        assert self.memory_gb > 0, "memory_gb must be positive"

        # Fail fast: Check if Modal credentials are available
        # Priority order:
        # 1. Explicit credentials in config
        # 2. Environment variables
        # 3. Modal's default auth (~/.modal.toml or modal.token_flow)

        has_explicit = self.modal_token_id and self.modal_token_secret
        has_env = os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")

        # Check if Modal has default credentials configured (~/.modal.toml)
        # Don't import modal here to avoid trio/asyncio conflicts
        has_modal_auth = os.path.exists(os.path.expanduser("~/.modal.toml"))

        assert has_explicit or has_env or has_modal_auth, (
            f"ModalTarget '{self.name}' requires credentials. "
            "Either:\n"
            "  1. Run: modal token new (sets up default auth)\n"
            "  2. Set environment variables: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET\n"
            "  3. Pass credentials explicitly: ModalTarget(modal_token_id='...', modal_token_secret='...')\n"
            "\n"
            "Get credentials from: https://modal.com/settings"
        )


# Union type for target configs (Phase 5: VM + Baremetal + Modal)
TargetConfig = BaremetalTarget | VMTarget | ModalTarget


# Type guard functions for pattern matching
def is_baremetal_target(target: TargetConfig) -> bool:
    """Check if target is baremetal."""
    return isinstance(target, BaremetalTarget)


def is_vm_target(target: TargetConfig) -> bool:
    """Check if target is VM."""
    return isinstance(target, VMTarget)


def is_modal_target(target: TargetConfig) -> bool:
    """Check if target is Modal."""
    return isinstance(target, ModalTarget)


def target_to_deployment_config(target: TargetConfig, gpu_id: int) -> DeploymentConfig:
    """Convert target to DeploymentConfig with specific GPU.

    Tiger Style: Pure function instead of method on frozen dataclass.

    Args:
        target: Target configuration (VM or Baremetal)
        gpu_id: Specific GPU ID to use (must be from target.gpu_ids)

    Returns:
        DeploymentConfig ready for setup_deployment()

    Example:
        >>> target = BaremetalTarget(
        ...     name="vultr",
        ...     ssh_target="user@host:22",
        ...     ssh_key="~/.ssh/key",
        ...     gpu_ids=[6, 7],
        ... )
        >>> config = target_to_deployment_config(target, gpu_id=7)
        >>> config.gpu_id
        7
    """
    from wafer_core.utils.kernel_utils.deployment import DeploymentConfig

    # Type narrowing: Only SSH-based targets supported (not Modal)
    assert not isinstance(
        target, ModalTarget
    ), f"target_to_deployment_config only supports SSH targets, got {type(target).__name__}"

    return DeploymentConfig(
        ssh_target=target.ssh_target,
        ssh_key=target.ssh_key,
        gpu_id=gpu_id,
    )
