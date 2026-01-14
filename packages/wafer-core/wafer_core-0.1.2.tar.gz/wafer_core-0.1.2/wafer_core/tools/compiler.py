"""CUDA compiler utilities.

Provides CUDA compilation to PTX/SASS and architecture detection.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from wafer_core.telemetry.decorators import with_telemetry
from wafer_core.tools.tool_finder import (
    find_nvcc,
    find_nvdisasm,
    get_install_command,
    get_nvcc_version,
)

# Minimum CUDA version required for each architecture
ARCH_MIN_CUDA_VERSION: dict[str, str] = {
    "sm_100": "12.8",  # B200/GB200 (Blackwell) requires CUDA 12.8+
    "sm_90": "11.8",  # H100/H200/GH200 (Hopper)
    "sm_89": "11.8",  # L4/L40/L40S (Ada Lovelace)
    "sm_86": "11.1",  # A10/A16/A40/RTX 30xx (Ampere consumer)
    "sm_80": "11.0",  # A100/A30 (Ampere datacenter)
    "sm_75": "10.0",  # T4/RTX 20xx (Turing)
    "sm_70": "9.0",  # V100 (Volta)
}

# Fallback architectures when target is not supported
ARCH_FALLBACK: dict[str, str] = {
    "sm_100": "sm_90",  # B200 can fall back to Hopper
    "sm_90": "sm_80",  # Hopper can fall back to Ampere
    "sm_89": "sm_86",  # Ada can fall back to Ampere consumer
}


@dataclass(frozen=True)
class CompileResult:
    """Result of CUDA compilation."""

    success: bool
    ptx: str | None = None
    sass: str | None = None
    error: str | None = None
    arch_used: str = ""
    nvcc_path: str | None = None
    nvcc_version: str | None = None
    ptx_mapping: dict[str, Any] | None = None
    sass_mapping: dict[str, Any] | None = None
    stage: str | None = None  # 'ptx' or 'cubin' if error occurred at specific stage


@dataclass(frozen=True)
class ArchDetectResult:
    """Result of GPU architecture detection."""

    detected: bool
    arch: str
    compute_capability: str | None = None
    gpu_name: str | None = None
    gpu_type: str | None = None
    fallback_archs: list[str] = field(default_factory=list)


def _check_arch_support(nvcc_path: str, arch: str) -> tuple[bool, str | None]:
    """Check if nvcc supports a specific architecture.

    Args:
        nvcc_path: Path to nvcc executable
        arch: Target architecture (e.g., sm_100)

    Returns:
        Tuple of (is_supported, error_message)
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cu", delete=False) as f:
            f.write("__global__ void test_kernel() {}\n")
            test_file = f.name

        try:
            result = subprocess.run(
                [nvcc_path, f"--arch={arch}", "--dryrun", "-c", test_file],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True, None

            error_output = result.stderr or result.stdout or ""
            if "not defined" in error_output.lower() or "invalid" in error_output.lower():
                return False, f"Architecture {arch} is not supported by this CUDA toolkit"
            return False, error_output.strip()[:500]
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass
    except subprocess.TimeoutExpired:
        return False, f"Timeout checking architecture support for {arch}"
    except (FileNotFoundError, PermissionError, OSError) as e:
        return False, f"Failed to check architecture support: {e!s}"


def _format_arch_compatibility_error(
    arch: str,
    nvcc_path: str,
    nvcc_version: str | None,
    arch_error: str | None,
    gpu_info: str | None = None,
) -> str:
    """Format a helpful architecture compatibility error message."""
    required_version = ARCH_MIN_CUDA_VERSION.get(arch, "unknown")
    fallback_arch = ARCH_FALLBACK.get(arch)

    lines = [
        "❌ Architecture Compatibility Error",
        "",
        f"Target Architecture: {arch}",
        f"CUDA Toolkit Path: {nvcc_path}",
        f"CUDA Version: {nvcc_version or 'unknown'}",
        f"Required Version: CUDA {required_version}+",
    ]

    if gpu_info:
        lines.append(f"Detected GPU: {gpu_info}")

    lines.extend(
        [
            "",
            f"Your CUDA toolkit (version {nvcc_version or 'unknown'}) does not support {arch}.",
            "",
        ]
    )

    if fallback_arch:
        lines.extend(
            [
                f"💡 Quick Fix: Use {fallback_arch} instead of {arch}",
                f"   Select '{fallback_arch}' in the Architecture dropdown.",
                "   This will work with your current CUDA version.",
                "",
            ]
        )

    lines.extend(
        [
            "🔧 To Fix Permanently:",
            f"1. Upgrade CUDA toolkit to version {required_version} or later",
            "   Download from: https://developer.nvidia.com/cuda-downloads",
            "",
            f"2. Or select a compatible architecture ({fallback_arch or 'sm_90'}) in the UI",
            "",
            "📋 Technical Details:",
            f"   {arch_error[:300] if arch_error else 'No additional details'}",
        ]
    )

    return "\n".join(lines)


def _parse_ptx_line_mapping(ptx_content: str) -> dict[str, Any]:
    """Parse .loc directives from PTX to build source->PTX line mapping."""
    mapping: dict[str, Any] = {
        "source_to_asm": {},
        "asm_to_source": {},
    }

    lines = ptx_content.split("\n")
    current_source_line = None

    for ptx_line_num, line in enumerate(lines, 1):
        loc_match = re.match(r"\s*\.loc\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if loc_match:
            current_source_line = int(loc_match.group(2))
            continue

        stripped = line.strip()
        if current_source_line and stripped and not stripped.startswith("//"):
            if stripped and (not stripped.startswith(".") or stripped.startswith(".pragma")):
                mapping["asm_to_source"][ptx_line_num] = current_source_line

                if current_source_line not in mapping["source_to_asm"]:
                    mapping["source_to_asm"][current_source_line] = []
                if ptx_line_num not in mapping["source_to_asm"][current_source_line]:
                    mapping["source_to_asm"][current_source_line].append(ptx_line_num)

    return mapping


def _parse_sass_line_mapping(sass_content: str) -> dict[str, Any]:
    """Parse nvdisasm output for source file correlation."""
    mapping: dict[str, Any] = {
        "source_to_asm": {},
        "asm_to_source": {},
    }

    lines = sass_content.split("\n")
    current_source_line = None

    for sass_line_num, line in enumerate(lines, 1):
        source_match = re.search(r"//##.*line\s+(\d+)", line, re.IGNORECASE)
        if source_match:
            current_source_line = int(source_match.group(1))
            continue

        stripped = line.strip()
        if current_source_line and stripped and not stripped.startswith("//"):
            if re.match(r"/\*[0-9a-fA-Fx]+\*/", stripped):
                mapping["asm_to_source"][sass_line_num] = current_source_line

                if current_source_line not in mapping["source_to_asm"]:
                    mapping["source_to_asm"][current_source_line] = []
                if sass_line_num not in mapping["source_to_asm"][current_source_line]:
                    mapping["source_to_asm"][current_source_line].append(sass_line_num)

    return mapping


def _find_include_paths(source_path: Path) -> list[str]:
    """Auto-detect common library include paths relative to the source file."""
    include_paths = []
    source_dir = source_path.parent.resolve()

    # Always include source file's directory
    include_paths.append(str(source_dir))

    # Search for CUTLASS in source dir and up to 5 parent directories
    search_dir = source_dir
    for _ in range(6):
        cutlass_include = search_dir / "cutlass" / "include"
        if cutlass_include.is_dir():
            include_paths.append(str(cutlass_include))
            cute_include = cutlass_include / "cute"
            if cute_include.is_dir():
                include_paths.append(str(cute_include))
            break
        if search_dir.parent == search_dir:
            break
        search_dir = search_dir.parent

    # Track if we found PyTorch headers
    found_torch = False

    # Search for PyTorch/ATen headers in .venv
    search_dir = source_dir
    for _ in range(6):
        venv_dir = search_dir / ".venv"
        if venv_dir.is_dir():
            lib_dir = venv_dir / "lib"
            if lib_dir.is_dir():
                for python_dir in lib_dir.iterdir():
                    if python_dir.name.startswith("python"):
                        torch_include = python_dir / "site-packages" / "torch" / "include"
                        if torch_include.is_dir():
                            found_torch = True
                            include_paths.append(str(torch_include))
                            torch_api = torch_include / "torch" / "csrc" / "api" / "include"
                            if torch_api.is_dir():
                                include_paths.append(str(torch_api))
                            break
            break
        if search_dir.parent == search_dir:
            break
        search_dir = search_dir.parent

    # If PyTorch headers found, search for Python development headers
    if found_torch:
        python_include = None

        try:
            result = subprocess.run(
                ["python3-config", "--includes"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for flag in result.stdout.strip().split():
                    if flag.startswith("-I"):
                        candidate = Path(flag[2:])
                        if candidate.is_dir() and (candidate / "Python.h").exists():
                            python_include = candidate
                            break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        if python_include is None:
            try:
                import sysconfig

                candidate = Path(sysconfig.get_path("include"))
                if candidate.is_dir() and (candidate / "Python.h").exists():
                    python_include = candidate
            except (ImportError, TypeError):
                pass

        if python_include is None:
            for common_path in [
                Path("/usr/include/python3.12"),
                Path("/usr/include/python3.11"),
                Path("/usr/include/python3.10"),
                Path("/usr/include/python3"),
            ]:
                if common_path.is_dir() and (common_path / "Python.h").exists():
                    python_include = common_path
                    break

        if python_include:
            include_paths.append(str(python_include))

    # Add system CUDA include if exists
    cuda_include = Path("/usr/local/cuda/include")
    if cuda_include.is_dir():
        include_paths.append(str(cuda_include))

    return include_paths


@with_telemetry("detect_arch")
def detect_arch(nvcc_path: str | None = None) -> ArchDetectResult:
    """Detect GPU architecture using nvidia-smi.

    Args:
        nvcc_path: Optional path to nvcc (not used, for API consistency)

    Returns:
        ArchDetectResult with detection results
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap,name", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            line = result.stdout.strip().split("\n")[0].strip()
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                cap = parts[0]
                gpu_name = ",".join(parts[1:])

                if "." in cap:
                    major, minor = cap.split(".")
                    arch = f"sm_{major}{minor}"

                    # Map GPU name to GPU type
                    gpu_type = None
                    gpu_name_upper = gpu_name.upper()
                    if "L4" in gpu_name_upper:
                        gpu_type = "L4"
                    elif "L40S" in gpu_name_upper or "L40" in gpu_name_upper:
                        gpu_type = "L40S"
                    elif "T4" in gpu_name_upper:
                        gpu_type = "T4"
                    elif "A10" in gpu_name_upper and "A100" not in gpu_name_upper:
                        gpu_type = "A10"
                    elif "A100" in gpu_name_upper:
                        if "80" in gpu_name_upper or "80GB" in gpu_name_upper:
                            gpu_type = "A100-80GB"
                        else:
                            gpu_type = "A100-40GB"
                    elif "H100" in gpu_name_upper:
                        gpu_type = "H100"
                    elif "H200" in gpu_name_upper:
                        gpu_type = "H200"
                    elif "B200" in gpu_name_upper:
                        gpu_type = "B200"

                    return ArchDetectResult(
                        detected=True,
                        arch=arch,
                        compute_capability=cap,
                        gpu_name=gpu_name,
                        gpu_type=gpu_type,
                    )
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError, OSError):
        pass

    # Fallback
    return ArchDetectResult(
        detected=False,
        arch="sm_80",
        fallback_archs=["sm_90", "sm_89", "sm_86", "sm_80", "sm_75", "sm_70"],
    )


@with_telemetry("compile_cuda")
def compile_cuda(
    file_path: str,
    arch: str,
    nvcc_path: str | None = None,
    compiler_options: str | None = None,
    *,
    verbose: bool = False,
) -> CompileResult:
    """Compile CUDA file to PTX and SASS.

    Args:
        file_path: Path to CUDA source file
        arch: Target architecture (e.g., sm_100)
        nvcc_path: Optional explicit path to nvcc (overrides auto-detection)
        compiler_options: Optional additional compiler options
        verbose: If True, print debug information to stderr

    Returns:
        CompileResult with compilation results or error
    """

    def log(msg: str) -> None:
        if verbose:
            print(f"[NVCC] {msg}", file=sys.stderr, flush=True)

    # Find nvcc
    if nvcc_path and os.path.isfile(nvcc_path) and os.access(nvcc_path, os.X_OK):
        nvcc = nvcc_path
        log(f"Using provided nvcc path: {nvcc}")
    else:
        nvcc = find_nvcc(verbose=verbose)
        if nvcc_path:
            log(f"Provided nvcc path '{nvcc_path}' not valid, using auto-detected: {nvcc}")
        else:
            log(f"Using auto-detected nvcc: {nvcc}")

    nvdisasm = find_nvdisasm(verbose=verbose)

    if not nvcc:
        return CompileResult(
            success=False,
            error=(
                "❌ NVCC Not Found\n\n"
                "The CUDA compiler (nvcc) was not found on your system.\n\n"
                "🔧 To Fix:\n"
                f"1. Install CUDA Toolkit: {get_install_command()}\n"
                "2. Or download from: https://developer.nvidia.com/cuda-downloads\n"
                "3. Restart VS Code after installation"
            ),
        )

    # Get nvcc version for error messages
    version = get_nvcc_version(nvcc)
    log(f"Version: {version}")

    # Check architecture compatibility BEFORE attempting compilation
    arch_supported, arch_error = _check_arch_support(nvcc, arch)
    if not arch_supported:
        error_msg = _format_arch_compatibility_error(arch, nvcc, version, arch_error)
        return CompileResult(
            success=False,
            error=error_msg,
            nvcc_path=nvcc,
            nvcc_version=version,
        )

    path = Path(file_path)
    if not path.exists():
        return CompileResult(
            success=False,
            error=f"❌ File Not Found\n\nThe file does not exist: {file_path}",
        )

    # Create temp directory for intermediate files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Handle .cuh header files by creating a wrapper .cu file
        compile_path = path
        if path.suffix == ".cuh":
            wrapper_file = Path(tmpdir) / f"{path.stem}_wrapper.cu"
            include_line = f'#include "{path}"\n'
            wrapper_file.write_text(include_line)
            compile_path = wrapper_file

        ptx_path = Path(tmpdir) / f"{path.stem}.ptx"
        cubin_path = Path(tmpdir) / f"{path.stem}.cubin"

        # Auto-detect include paths
        include_paths = _find_include_paths(path)

        # Build include flags
        include_flags = []
        for inc_path in include_paths:
            include_flags.extend(["-I", inc_path])

        include_flags.extend(["-I", str(path.parent)])

        # Generate PTX with line info
        ptx_cmd = [
            nvcc,
            "-ptx",
            f"-arch={arch}",
            "--generate-line-info",
            *include_flags,
            str(compile_path),
            "-o",
            str(ptx_path),
        ]

        if compiler_options:
            ptx_cmd.extend(compiler_options.split())

        try:
            ptx_result = subprocess.run(
                ptx_cmd, capture_output=True, text=True, timeout=120
            )

            if ptx_result.returncode != 0:
                error_msg = ptx_result.stderr or "PTX compilation failed"

                # Check if error is related to missing Python headers
                if "Python.h" in error_msg and (
                    "No such file" in error_msg or "fatal error" in error_msg
                ):
                    source_content = path.read_text()
                    if (
                        "torch/extension.h" in source_content
                        or "torch/extension" in source_content
                    ):
                        error_msg = (
                            f"{error_msg}\n\n"
                            "⚠️  Missing Python development headers.\n"
                            "This file includes PyTorch headers which require Python.h.\n\n"
                            "To fix this, install Python development headers:\n"
                            "  • Ubuntu/Debian: sudo apt-get install python3-dev\n"
                            "  • Fedora/RHEL: sudo dnf install python3-devel\n"
                            "  • Arch: sudo pacman -S python\n"
                            "  • macOS: Usually included with Xcode Command Line Tools\n"
                        )

                return CompileResult(
                    success=False,
                    error=error_msg,
                    stage="ptx",
                    nvcc_path=nvcc,
                    nvcc_version=version,
                )

            ptx_content = ptx_path.read_text()
            ptx_mapping = _parse_ptx_line_mapping(ptx_content)

        except subprocess.TimeoutExpired:
            return CompileResult(
                success=False,
                error="PTX compilation timed out",
                stage="ptx",
                nvcc_path=nvcc,
                nvcc_version=version,
            )
        except (FileNotFoundError, PermissionError, OSError) as e:
            return CompileResult(
                success=False,
                error=str(e),
                stage="ptx",
                nvcc_path=nvcc,
                nvcc_version=version,
            )

        # Generate SASS (cubin + nvdisasm)
        sass_content = None
        sass_mapping = None

        if nvdisasm:
            cubin_cmd = [
                nvcc,
                "-cubin",
                f"-arch={arch}",
                "--generate-line-info",
                *include_flags,
                str(compile_path),
                "-o",
                str(cubin_path),
            ]

            if compiler_options:
                cubin_cmd.extend(compiler_options.split())

            try:
                cubin_result = subprocess.run(
                    cubin_cmd, capture_output=True, text=True, timeout=120
                )

                if cubin_result.returncode == 0:
                    sass_cmd = [nvdisasm, "-c", "-g", str(cubin_path)]
                    sass_result = subprocess.run(
                        sass_cmd, capture_output=True, text=True, timeout=60
                    )

                    if sass_result.returncode == 0:
                        sass_content = sass_result.stdout
                        sass_mapping = _parse_sass_line_mapping(sass_result.stdout)
            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError, OSError):
                # SASS is optional, don't fail if it doesn't work
                pass

        return CompileResult(
            success=True,
            ptx=ptx_content,
            sass=sass_content,
            arch_used=arch,
            nvcc_path=nvcc,
            nvcc_version=version,
            ptx_mapping=ptx_mapping,
            sass_mapping=sass_mapping,
        )

