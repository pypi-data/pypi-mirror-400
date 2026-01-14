"""Tool finder for CUDA development tools (nvcc, nvdisasm).

Provides cross-platform detection of CUDA toolkit executables using
multiple search strategies.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Known nvcc installation paths by platform
NVCC_PATHS: dict[str, list[str]] = {
    "linux": [
        "/usr/local/cuda/bin/nvcc",
        "/usr/local/cuda-13.0/bin/nvcc",
        "/usr/local/cuda-12.0/bin/nvcc",
        "/usr/local/cuda-11.8/bin/nvcc",
        "/opt/nvidia/cuda/bin/nvcc",
        "/usr/bin/nvcc",
        "/usr/local/bin/nvcc",
    ],
    "darwin": [
        "/usr/local/cuda/bin/nvcc",
        "/Developer/NVIDIA/CUDA/bin/nvcc",
    ],
    "windows": [
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin\nvcc.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin\nvcc.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin\nvcc.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2\bin\nvcc.exe",
    ],
}

# Known nvdisasm paths (usually same dir as nvcc)
NVDISASM_PATHS: dict[str, list[str]] = {
    "linux": [
        "/usr/local/cuda/bin/nvdisasm",
        "/usr/local/cuda-13.0/bin/nvdisasm",
        "/usr/local/cuda-12.0/bin/nvdisasm",
        "/usr/local/cuda-11.8/bin/nvdisasm",
        "/opt/nvidia/cuda/bin/nvdisasm",
        "/usr/bin/nvdisasm",
    ],
    "darwin": [
        "/usr/local/cuda/bin/nvdisasm",
    ],
    "windows": [
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin\nvdisasm.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin\nvdisasm.exe",
    ],
}


def get_platform() -> str:
    """Get normalized platform name.

    Returns:
        One of: 'linux', 'darwin', 'windows'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    return "linux"


def _enhance_path() -> str:
    """Enhance PATH with common CUDA installation directories.

    Returns:
        The enhanced PATH string
    """
    current_path = os.environ.get("PATH", "")
    path_parts = current_path.split(os.pathsep) if current_path else []

    common_paths = [
        "/usr/local/cuda/bin",
        "/usr/local/cuda-13.0/bin",
        "/usr/local/cuda-12.0/bin",
        "/usr/local/cuda-11.8/bin",
        "/opt/nvidia/cuda/bin",
    ]

    # Dynamically scan for version-specific CUDA directories
    if os.path.isdir("/usr/local"):
        try:
            items = os.listdir("/usr/local")
            for item in items:
                if item.startswith("cuda-") and os.path.isdir(
                    os.path.join("/usr/local", item)
                ):
                    bin_path = os.path.join("/usr/local", item, "bin")
                    if os.path.isdir(bin_path):
                        common_paths.append(bin_path)
        except (OSError, PermissionError):
            pass

    # Add paths that aren't already in PATH
    for path in common_paths:
        if path not in path_parts:
            path_parts.append(path)

    enhanced_path = os.pathsep.join(path_parts)
    os.environ["PATH"] = enhanced_path
    return enhanced_path


def _verify_nvcc_executable(nvcc_path: str) -> bool:
    """Verify that a found executable is actually nvcc.

    Args:
        nvcc_path: Path to potential nvcc executable

    Returns:
        True if the executable appears to be nvcc
    """
    try:
        test_result = subprocess.run(
            [nvcc_path, "--version"], capture_output=True, text=True, timeout=2
        )
        output = (test_result.stdout or "") + (test_result.stderr or "")
        if (
            "nvcc" in output.lower()
            or "cuda compiler" in output.lower()
            or "nvidia" in output.lower()
        ):
            return True
        if test_result.returncode == 0 and output.strip():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        pass
    # If we can't verify, still return True if file exists and is executable
    return True


def find_nvcc(*, verbose: bool = False) -> str | None:
    """Find nvcc executable on the system using multiple search strategies.

    Search strategies (in order):
    1. Enhanced PATH with common CUDA locations
    2. Known installation paths for the platform
    3. Dynamic scanning of /usr/local/cuda-* directories
    4. Filesystem search using find command

    Args:
        verbose: If True, print debug information to stderr

    Returns:
        Path to nvcc executable, or None if not found
    """

    def log(msg: str) -> None:
        if verbose:
            print(f"[NVCC] {msg}", file=sys.stderr, flush=True)

    log("Searching for NVCC executable...")

    # Strategy 1: Enhance PATH and check using shutil.which
    log("Strategy 1: Checking enhanced PATH...")
    _enhance_path()
    nvcc = shutil.which("nvcc")
    if nvcc:
        log(f"Found via enhanced PATH: {nvcc}")
        return nvcc

    # Strategy 2: Check known installation paths
    plat = get_platform()
    log(f"Strategy 2: Checking known paths for platform '{plat}'...")
    for p in NVCC_PATHS.get(plat, []):
        if os.path.isfile(p) and os.access(p, os.X_OK):
            log(f"Found at known path: {p}")
            return p

    # Strategy 3: Dynamically scan for version-specific CUDA paths
    if plat == "linux":
        log("Strategy 3: Scanning /usr/local/cuda-* directories...")
        cuda_base = "/usr/local"
        if os.path.isdir(cuda_base):
            try:
                items = os.listdir(cuda_base)
                cuda_dirs = [
                    item
                    for item in items
                    if item.startswith("cuda-")
                    and os.path.isdir(os.path.join(cuda_base, item))
                ]
                cuda_dirs.sort(reverse=True)  # Newer versions first
                for item in cuda_dirs:
                    nvcc_path = os.path.join(cuda_base, item, "bin", "nvcc")
                    if os.path.isfile(nvcc_path) and os.access(nvcc_path, os.X_OK):
                        log(f"Found at version-specific path: {nvcc_path}")
                        return nvcc_path
            except (OSError, PermissionError):
                pass

    # Strategy 4: Filesystem search
    if plat in ("linux", "darwin"):
        log("Strategy 4: Filesystem search...")
        search_dirs = [
            "/usr/local",
            "/opt",
            os.path.expanduser("~/.local"),
        ]

        for search_dir in search_dirs:
            if not os.path.isdir(search_dir):
                continue
            try:
                result = subprocess.run(
                    [
                        "find",
                        search_dir,
                        "-maxdepth",
                        "4",
                        "-type",
                        "f",
                        "-name",
                        "nvcc",
                        "-o",
                        "-name",
                        "nvcc.exe",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    found_paths = result.stdout.strip().split("\n")
                    for found_path in found_paths:
                        found_path = found_path.strip()
                        if (
                            found_path
                            and os.path.isfile(found_path)
                            and os.access(found_path, os.X_OK)
                        ):
                            if _verify_nvcc_executable(found_path):
                                log(f"Found via filesystem search: {found_path}")
                                return found_path
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                PermissionError,
                OSError,
            ):
                continue

    elif plat == "windows":
        program_files_dirs = [
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
        ]

        for base_dir in program_files_dirs:
            if not os.path.isdir(base_dir):
                continue
            try:
                for root, dirs, files in os.walk(base_dir):
                    depth = root[len(base_dir) :].count(os.sep)
                    if depth > 3:
                        dirs[:] = []
                        continue

                    for file in files:
                        if file.lower() in ("nvcc.exe", "nvcc"):
                            nvcc_path = os.path.join(root, file)
                            if os.path.isfile(nvcc_path) and os.access(
                                nvcc_path, os.X_OK
                            ):
                                if _verify_nvcc_executable(nvcc_path):
                                    return nvcc_path
            except (OSError, PermissionError):
                continue

    log("NVCC not found after all search strategies")
    return None


def find_nvdisasm(*, verbose: bool = False) -> str | None:
    """Find nvdisasm executable on the system.

    Prefers standard CUDA installation paths first.

    Args:
        verbose: If True, print debug information to stderr

    Returns:
        Path to nvdisasm executable, or None if not found
    """

    def log(msg: str) -> None:
        if verbose:
            print(f"[NVDISASM] {msg}", file=sys.stderr, flush=True)

    plat = get_platform()

    # Check known installation paths first
    for p in NVDISASM_PATHS.get(plat, []):
        if os.path.isfile(p) and os.access(p, os.X_OK):
            log(f"Found at known path: {p}")
            return p

    # Try to find nvdisasm relative to nvcc
    nvcc = find_nvcc(verbose=verbose)
    if nvcc:
        nvcc_dir = Path(nvcc).parent
        nvdisasm_name = "nvdisasm.exe" if plat == "windows" else "nvdisasm"
        nvdisasm_path = nvcc_dir / nvdisasm_name
        if nvdisasm_path.exists():
            log(f"Found relative to nvcc: {nvdisasm_path}")
            return str(nvdisasm_path)

    # Fall back to PATH
    nvdisasm = shutil.which("nvdisasm")
    if nvdisasm:
        log(f"Found in PATH: {nvdisasm}")
        return nvdisasm

    log("nvdisasm not found")
    return None


def get_nvcc_version(nvcc_path: str) -> str | None:
    """Get nvcc version string.

    Args:
        nvcc_path: Path to nvcc executable

    Returns:
        Version string (e.g., '12.0'), or None if unable to determine
    """
    try:
        result = subprocess.run(
            [nvcc_path, "--version"], capture_output=True, text=True, timeout=10
        )
        # Parse version from output like "Cuda compilation tools, release 12.0, V12.0.140"
        for line in result.stdout.split("\n"):
            if "release" in line.lower():
                match = re.search(r"release\s+(\d+\.\d+)", line, re.IGNORECASE)
                if match:
                    return match.group(1)
            if line.startswith("Cuda"):
                return line.strip()
        return result.stdout.strip().split("\n")[-1] if result.stdout else None
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError, OSError):
        return None


def get_install_command() -> str:
    """Get platform-appropriate install command for CUDA toolkit.

    Returns:
        Install command string
    """
    plat = get_platform()

    if plat == "linux":
        if shutil.which("apt-get") or shutil.which("apt"):
            return "sudo apt install nvidia-cuda-toolkit"
        elif shutil.which("dnf"):
            return "sudo dnf install cuda"
        elif shutil.which("yum"):
            return "sudo yum install cuda"
        else:
            return "Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads"
    elif plat == "darwin":
        return "Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads"
    else:  # Windows
        return "Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads"

