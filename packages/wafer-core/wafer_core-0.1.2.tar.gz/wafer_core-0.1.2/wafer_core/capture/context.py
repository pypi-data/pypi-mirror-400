"""Context capture: git, GPU, system information."""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

import trio

from wafer_core.capture.dtypes import CaptureContext, GitContext, GPUContext, SystemContext

logger = logging.getLogger(__name__)


async def collect_git_info(working_dir: Path) -> GitContext:
    """Collect git repository information.

    Args:
        working_dir: Working directory to check for git repo

    Returns:
        GitContext with git information (or empty if not a git repo)
    """
    logger.debug(f"Collecting git info from: {working_dir}")

    def _run_git(args: list[str]) -> str | None:
        """Run git command and return output."""
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"Git command failed: {e}")
        return None

    # Run git commands in thread
    def _collect() -> GitContext:
        # Check if it's a git repo
        if _run_git(["rev-parse", "--git-dir"]) is None:
            logger.debug("Not a git repository")
            return GitContext()

        # Get remote URL
        repo_url = _run_git(["config", "--get", "remote.origin.url"])

        # Get commit hash
        commit_hash = _run_git(["rev-parse", "HEAD"])

        # Get branch name
        branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])

        # Check if dirty (uncommitted changes)
        status_output = _run_git(["status", "--porcelain"])
        is_dirty = bool(status_output)

        logger.info(
            f"Git context: {branch}@{commit_hash[:8] if commit_hash else 'none'} (dirty={is_dirty})"
        )

        return GitContext(
            repo_url=repo_url,
            commit_hash=commit_hash,
            branch=branch,
            is_dirty=is_dirty,
        )

    return await trio.to_thread.run_sync(_collect)


async def collect_gpu_info() -> GPUContext:
    """Collect GPU hardware information.

    Returns:
        GPUContext with GPU information (or empty if no GPU/nvidia-smi)
    """
    logger.debug("Collecting GPU info")

    def _collect() -> GPUContext:
        try:
            # Try nvidia-smi to get GPU info
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,driver_version",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    parts = output.split(",")
                    if len(parts) >= 2:
                        gpu_name = parts[0].strip()
                        driver_version = parts[1].strip()

                        # Try to get CUDA version
                        cuda_result = subprocess.run(
                            ["nvidia-smi"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        cuda_version = None
                        if cuda_result.returncode == 0:
                            # Parse "CUDA Version: X.Y" from output
                            import re

                            match = re.search(
                                r"CUDA Version:\s+(\d+\.\d+)", cuda_result.stdout
                            )
                            if match:
                                cuda_version = match.group(1)

                        # Extract short GPU model (e.g., "H100" from "NVIDIA H100 80GB HBM3")
                        model = gpu_name
                        if "NVIDIA" in gpu_name:
                            # Try to extract model number
                            import re

                            match = re.search(r"([AHLTV]\d+)", gpu_name)
                            if match:
                                model = match.group(1)

                        logger.info(
                            f"GPU context: {model}, driver {driver_version}, CUDA {cuda_version}"
                        )

                        return GPUContext(
                            model=model,
                            driver_version=driver_version,
                            cuda_version=cuda_version,
                        )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"Failed to collect GPU info: {e}")

        logger.debug("No GPU info available")
        return GPUContext()

    return await trio.to_thread.run_sync(_collect)


def collect_system_info() -> SystemContext:
    """Collect system information.

    Returns:
        SystemContext with hostname, platform, Python version
    """
    logger.debug("Collecting system info")

    try:
        import socket

        hostname = socket.gethostname()
    except Exception:
        hostname = None

    platform_name = platform.system()  # 'Linux', 'Darwin', 'Windows'
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    logger.info(f"System context: {hostname} ({platform_name}), Python {python_version}")

    return SystemContext(
        hostname=hostname, platform=platform_name, python_version=python_version
    )


def collect_environment_variables(
    include_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Collect relevant environment variables.

    Args:
        include_patterns: Optional list of prefixes to include (e.g., ["CUDA_", "PATH"])
                         If None, includes common relevant variables

    Returns:
        Dictionary of environment variables
    """
    if include_patterns is None:
        # Default: capture CUDA-related, Python-related, and PATH
        include_patterns = [
            "CUDA_",
            "PYTHON",
            "PATH",
            "LD_LIBRARY_PATH",
            "LIBRARY_PATH",
            "CPATH",
            "PKG_CONFIG_PATH",
        ]

    env_vars: dict[str, str] = {}

    for key, value in os.environ.items():
        # Check if key matches any pattern
        for pattern in include_patterns:
            if key.startswith(pattern):
                env_vars[key] = value
                break

    logger.debug(f"Collected {len(env_vars)} environment variables")
    return env_vars


async def collect_capture_context(
    working_dir: Path,
    env_var_patterns: list[str] | None = None,
) -> CaptureContext:
    """Collect complete capture context.

    Args:
        working_dir: Working directory
        env_var_patterns: Optional patterns for environment variables to include

    Returns:
        Complete CaptureContext
    """
    logger.info("Collecting capture context")

    # Collect git and GPU info concurrently
    async with trio.open_nursery() as nursery:
        git_result = None
        gpu_result = None

        async def _git() -> None:
            nonlocal git_result
            git_result = await collect_git_info(working_dir)

        async def _gpu() -> None:
            nonlocal gpu_result
            gpu_result = await collect_gpu_info()

        nursery.start_soon(_git)
        nursery.start_soon(_gpu)

    # Collect system info (synchronous)
    system = collect_system_info()

    # Collect environment variables
    env_vars = collect_environment_variables(env_var_patterns)

    assert git_result is not None
    assert gpu_result is not None

    return CaptureContext(
        git=git_result,
        gpu=gpu_result,
        system=system,
        working_dir=working_dir,
        environment_variables=env_vars,
    )
