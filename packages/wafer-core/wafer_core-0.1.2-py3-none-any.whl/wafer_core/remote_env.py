"""Python environment setup for remote machines.

Replaces kerbal.python_env with minimal internal implementation.
Sets up Python venv with uv and installs packages.

Usage (sync):
    from wafer_core.ssh import SSHClient
    from wafer_core.remote_env import setup_python_env, PythonEnvState

    client = SSHClient("root@gpu:22", ssh_key_path="~/.ssh/id_rsa")
    state = setup_python_env(
        client,
        workspace="/workspace/project",
        requirements=["torch>=2.0", "triton"],
    )
    result = client.exec(f"{state.venv_python} train.py")

Usage (async):
    from wafer_core.async_ssh import AsyncSSHClient
    from wafer_core.remote_env import async_setup_python_env, PythonEnvState

    async with AsyncSSHClient("root@gpu:22", "~/.ssh/id_rsa") as client:
        state = await async_setup_python_env(
            client,
            workspace="/workspace/project",
            requirements=["torch>=2.0", "triton"],
        )
        result = await client.exec(f"{state.venv_python} train.py")
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer_core.async_ssh import AsyncSSHClient
    from wafer_core.ssh import SSHClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PythonEnvState:
    """Immutable state of a configured Python environment.

    Attributes:
        venv_python: Absolute path to venv Python binary
        venv_bin: Absolute path to venv bin directory
        workspace: Absolute path to workspace root
        env_vars: Pre-computed environment variables
    """

    venv_python: str
    venv_bin: str
    workspace: str
    env_vars: dict[str, str]


def setup_python_env(
    client: "SSHClient",
    workspace: str,
    requirements: list[str],
    python_version: str = ">=3.10",
    venv_path: str = ".venv",
    index_url: str | None = None,
) -> PythonEnvState:
    """Setup Python environment with dependencies.

    Args:
        client: SSHClient instance
        workspace: Absolute path to workspace on remote
        requirements: pip packages like ["torch>=2.0", "triton"]
        python_version: Python version requirement
        venv_path: Venv location relative to workspace
        index_url: Custom package index URL (e.g., for ROCm torch)

    Returns:
        PythonEnvState with paths and env vars

    Example:
        state = setup_python_env(
            client,
            workspace="/workspace/project",
            requirements=["torch>=2.4.0", "triton"],
        )

        # With custom index for ROCm:
        state = setup_python_env(
            client,
            workspace="/workspace/project",
            requirements=["torch", "torchvision"],
            index_url="https://download.pytorch.org/whl/rocm6.2",
        )
    """
    assert client is not None, "client cannot be None"
    assert workspace, "workspace must be non-empty"
    assert requirements, "requirements must be non-empty"

    logger.debug(f"Setting up python environment in {workspace}")

    # Expand workspace path
    workspace = client.expand_path(workspace)

    # Verify workspace exists
    result = client.exec(f"test -d {workspace}")
    assert result.exit_code == 0, f"Workspace does not exist: {workspace}"

    venv_full_path = f"{workspace}/{venv_path}"

    # Step 1: Ensure uv is installed
    _ensure_uv(client)

    # Step 2: Create venv
    _create_venv(client, workspace, venv_full_path, python_version)

    # Step 3: Install requirements
    _install_packages(client, venv_full_path, requirements, index_url)

    # Step 4: Verify venv works
    _verify_venv(client, venv_full_path)

    logger.info("Python environment ready")

    # Build state
    venv_python = f"{venv_full_path}/bin/python"
    venv_bin = f"{venv_full_path}/bin"

    env_vars = {
        "PATH": f"{venv_bin}:$PATH",
        "PYTHONUNBUFFERED": "1",
    }

    return PythonEnvState(
        venv_python=venv_python,
        venv_bin=venv_bin,
        workspace=workspace,
        env_vars=env_vars,
    )


def _ensure_uv(client: "SSHClient") -> None:
    """Ensure uv is installed."""
    result = client.exec("command -v uv")
    if result.exit_code == 0:
        logger.debug("uv already installed")
        return

    logger.debug("Installing uv...")
    install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    result = client.exec(install_cmd)
    assert result.exit_code == 0, f"uv installation failed: {result.stderr}"
    logger.debug("uv installed")


def _create_venv(
    client: "SSHClient",
    workspace: str,
    venv_full_path: str,
    python_version: str,
) -> None:
    """Create venv using uv."""
    logger.debug("Creating virtual environment...")

    # Generate minimal pyproject.toml for uv
    pyproject_toml = f"""[project]
name = "remote-env"
version = "0.1.0"
requires-python = "{python_version}"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
"""

    # Write pyproject.toml
    write_cmd = f"cat > {workspace}/pyproject.toml << 'EOF'\n{pyproject_toml}\nEOF"
    result = client.exec(write_cmd)
    assert result.exit_code == 0, f"Failed to write pyproject.toml: {result.stderr}"

    # Create venv with uv, specifying Python version
    py_version_num = python_version.lstrip(">=<~")
    cmd = f"""
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    cd {workspace}
    uv venv {venv_full_path} --python {py_version_num}
    """
    result = client.exec(cmd)
    assert result.exit_code == 0, f"venv creation failed: {result.stderr}"

    logger.debug(f"Virtual environment created at {venv_full_path}")


def _install_packages(
    client: "SSHClient",
    venv_full_path: str,
    requirements: list[str],
    index_url: str | None = None,
) -> None:
    """Install pip packages into venv.

    If index_url is provided, we do a two-phase install:
    1. Install torch packages from the custom index (e.g., ROCm)
    2. Install remaining packages from PyPI
    """
    logger.debug(f"Installing {len(requirements)} package(s)...")

    # Packages that should come from the custom index (torch ecosystem)
    torch_packages = {"torch", "torchvision", "torchaudio", "pytorch-triton-rocm"}

    if index_url:
        # Split requirements into torch packages and others
        torch_reqs = [r for r in requirements if any(tp in r for tp in torch_packages)]
        other_reqs = [r for r in requirements if not any(tp in r for tp in torch_packages)]

        # Install torch packages from custom index first
        if torch_reqs:
            torch_pkgs = " ".join(f'"{pkg}"' for pkg in torch_reqs)
            cmd = f"""
            export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
            uv pip install --python {venv_full_path}/bin/python --index-url {index_url} {torch_pkgs}
            """
            logger.info(f"Installing torch packages from {index_url}...")
            for line in client.exec_stream(cmd):
                print(line, flush=True)

        # Install other packages from PyPI
        if other_reqs:
            other_pkgs = " ".join(f'"{pkg}"' for pkg in other_reqs)
            cmd = f"""
            export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
            uv pip install --python {venv_full_path}/bin/python {other_pkgs}
            """
            logger.info("Installing remaining packages from PyPI...")
            for line in client.exec_stream(cmd):
                print(line, flush=True)
    else:
        # No custom index - install everything from PyPI
        packages = " ".join(f'"{pkg}"' for pkg in requirements)
        cmd = f"""
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        uv pip install --python {venv_full_path}/bin/python {packages}
        """
        for line in client.exec_stream(cmd):
            print(line, flush=True)

    logger.debug("Packages installed")


def _verify_venv(client: "SSHClient", venv_full_path: str) -> None:
    """Verify venv works."""
    venv_python = f"{venv_full_path}/bin/python"
    result = client.exec(f"{venv_python} --version")

    assert result.exit_code == 0, f"Python venv verification failed: {result.stderr}"

    version = result.stdout.strip() if result.stdout else "unknown"
    logger.debug(f"Python venv verified: {version}")


# =============================================================================
# Async versions (for use with AsyncSSHClient)
# =============================================================================


async def async_setup_python_env(
    client: "AsyncSSHClient",
    workspace: str,
    requirements: list[str],
    python_version: str = ">=3.10",
    venv_path: str = ".venv",
    index_url: str | None = None,
) -> PythonEnvState:
    """Async version of setup_python_env for use with AsyncSSHClient.

    Args:
        client: AsyncSSHClient instance
        workspace: Absolute path to workspace on remote
        requirements: pip packages like ["torch>=2.0", "triton"]
        python_version: Python version requirement
        venv_path: Venv location relative to workspace
        index_url: Custom package index URL (e.g., for ROCm torch)

    Returns:
        PythonEnvState with paths and env vars
    """
    assert client is not None, "client cannot be None"
    assert workspace, "workspace must be non-empty"
    assert requirements, "requirements must be non-empty"

    logger.debug(f"Setting up python environment in {workspace}")

    # Expand workspace path
    workspace = await client.expand_path(workspace)

    # Verify workspace exists (create if not)
    result = await client.exec(f"mkdir -p {workspace}")
    assert result.exit_code == 0, f"Failed to create workspace: {result.stderr}"

    venv_full_path = f"{workspace}/{venv_path}"

    # Step 1: Ensure uv is installed
    await _async_ensure_uv(client)

    # Step 2: Create venv
    await _async_create_venv(client, workspace, venv_full_path, python_version)

    # Step 3: Install requirements
    await _async_install_packages(client, venv_full_path, requirements, index_url)

    # Step 4: Verify venv works
    await _async_verify_venv(client, venv_full_path)

    logger.info("Python environment ready")

    # Build state
    venv_python = f"{venv_full_path}/bin/python"
    venv_bin = f"{venv_full_path}/bin"

    env_vars = {
        "PATH": f"{venv_bin}:$PATH",
        "PYTHONUNBUFFERED": "1",
    }

    return PythonEnvState(
        venv_python=venv_python,
        venv_bin=venv_bin,
        workspace=workspace,
        env_vars=env_vars,
    )


async def _async_ensure_uv(client: "AsyncSSHClient") -> None:
    """Ensure uv is installed (async version)."""
    result = await client.exec("command -v uv || echo 'NOT_FOUND'")
    if "NOT_FOUND" not in result.stdout:
        logger.debug("uv already installed")
        return

    logger.info("Installing uv...")
    install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    result = await client.exec(install_cmd)
    assert result.exit_code == 0, f"uv installation failed: {result.stderr}"
    logger.debug("uv installed")


async def _async_create_venv(
    client: "AsyncSSHClient",
    workspace: str,
    venv_full_path: str,
    python_version: str,
) -> None:
    """Create venv using uv (async version)."""
    logger.debug("Creating virtual environment...")

    # Generate minimal pyproject.toml for uv
    pyproject_toml = f"""[project]
name = "remote-env"
version = "0.1.0"
requires-python = "{python_version}"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
"""

    # Write pyproject.toml using heredoc
    write_cmd = f"cat > {workspace}/pyproject.toml << 'EOF'\n{pyproject_toml}\nEOF"
    result = await client.exec(write_cmd)
    assert result.exit_code == 0, f"Failed to write pyproject.toml: {result.stderr}"

    # Create venv with uv, specifying Python version
    py_version_num = python_version.lstrip(">=<~")
    cmd = f"""
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    cd {workspace}
    uv venv {venv_full_path} --python {py_version_num}
    """
    result = await client.exec(cmd)
    assert result.exit_code == 0, f"venv creation failed: {result.stderr}"

    logger.debug(f"Virtual environment created at {venv_full_path}")


async def _async_install_packages(
    client: "AsyncSSHClient",
    venv_full_path: str,
    requirements: list[str],
    index_url: str | None = None,
) -> None:
    """Install pip packages into venv (async version).

    If index_url is provided, we do a two-phase install:
    1. Install torch packages from the custom index (e.g., ROCm)
    2. Install remaining packages from PyPI

    This is necessary because uv prefers newer versions from PyPI,
    which would install CUDA torch instead of ROCm torch.
    """
    logger.info(f"Installing {len(requirements)} package(s)...")

    # Packages that should come from the custom index (torch ecosystem)
    torch_packages = {"torch", "torchvision", "torchaudio", "pytorch-triton-rocm"}

    if index_url:
        # Split requirements into torch packages and others
        torch_reqs = [r for r in requirements if any(tp in r for tp in torch_packages)]
        other_reqs = [r for r in requirements if not any(tp in r for tp in torch_packages)]

        # Install torch packages from custom index first (no extra index to avoid PyPI confusion)
        if torch_reqs:
            torch_pkgs = " ".join(f'"{pkg}"' for pkg in torch_reqs)
            cmd = f"""
            export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
            uv pip install --python {venv_full_path}/bin/python --index-url {index_url} {torch_pkgs}
            """
            logger.info(f"Installing torch packages from {index_url}...")
            result = await client.exec(cmd)
            assert result.exit_code == 0, f"torch install failed: {result.stderr}\n{result.stdout}"

        # Install other packages from PyPI
        if other_reqs:
            other_pkgs = " ".join(f'"{pkg}"' for pkg in other_reqs)
            cmd = f"""
            export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
            uv pip install --python {venv_full_path}/bin/python {other_pkgs}
            """
            logger.info("Installing remaining packages from PyPI...")
            result = await client.exec(cmd)
            assert result.exit_code == 0, f"pip install failed: {result.stderr}\n{result.stdout}"
    else:
        # No custom index - install everything from PyPI
        packages = " ".join(f'"{pkg}"' for pkg in requirements)
        cmd = f"""
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        uv pip install --python {venv_full_path}/bin/python {packages}
        """
        result = await client.exec(cmd)
        assert result.exit_code == 0, f"pip install failed: {result.stderr}\n{result.stdout}"

    logger.debug("Packages installed")


async def _async_verify_venv(client: "AsyncSSHClient", venv_full_path: str) -> None:
    """Verify venv works (async version)."""
    venv_python = f"{venv_full_path}/bin/python"
    result = await client.exec(f"{venv_python} --version")

    assert result.exit_code == 0, f"Python venv verification failed: {result.stderr}"

    version = result.stdout.strip() if result.stdout else "unknown"
    logger.debug(f"Python venv verified: {version}")
