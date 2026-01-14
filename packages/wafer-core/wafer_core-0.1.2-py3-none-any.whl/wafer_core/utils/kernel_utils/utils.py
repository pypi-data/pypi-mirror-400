"""Verification and benchmarking utilities for GPU kernels.

Provides tolerance-based matching and performance measurement,
following backend-bench patterns but with explicit error handling.
"""

import sys
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from wafer_core.utils.exceptions import ReferenceBenchmarkError
from wafer_core.utils.ncu_profile_tools import NCU_COMPREHENSIVE_METRICS

# Numerical stability constants
EPSILON_SAFE_DIVISION = 1e-8  # Prevent division by zero in relative error calculations

# Profiling timeouts
NCU_TIMEOUT_SECONDS = 300  # 5 minutes - NVIDIA Nsight Compute profiling timeout


@dataclass
class ErrorInfo:
    """Structured error information from kernel execution.

    Attributes:
        exc_type: Exception type name (e.g., "ValueError")
        exc_message: Exception message
        formatted_tb: Full formatted traceback string
        source_file: Filename where error occurred (if available)
        source_line: Line number where error occurred (if available)
    """

    exc_type: str
    exc_message: str
    formatted_tb: str
    source_file: str | None = None
    source_line: int | None = None

    def to_string(self) -> str:
        """Convert to string format for display.

        Handles different error types:
        - Implementation errors: "Implementation failed: ValueError: ..."
        - Reference errors: "Reference failed: ValueError: ..."
        - Output mismatches: "Output mismatch: ..."
        """
        if self.exc_type.startswith("Reference "):
            # Reference error
            actual_type = self.exc_type.replace("Reference ", "")
            prefix = f"Reference failed: {actual_type}"
        elif self.exc_type == "OutputMismatch":
            # Output mismatch (no exception)
            return f"Output mismatch: {self.exc_message}"
        else:
            # Implementation error
            prefix = f"Implementation failed: {self.exc_type}"

        if self.formatted_tb:
            return f"{prefix}: {self.exc_message}\n{self.formatted_tb}"
        else:
            return f"{prefix}: {self.exc_message}"

    def get_signature(self) -> str:
        """Get a signature for deduplication.

        Returns same error signature if errors are from same line in user code.
        """
        if self.source_file and self.source_line:
            return f"{self.exc_type}: {self.exc_message} | {self.source_file}:{self.source_line}"
        else:
            return f"{self.exc_type}: {self.exc_message}"


def allclose_with_error(
    actual: torch.Tensor,
    expected: torch.Tensor,
    rtol: float,
    atol: float,
) -> tuple[bool, float, float]:
    """Check if tensors match within tolerance and return error metrics.

    Args:
        actual: Computed result
        expected: Reference result
        rtol: Relative tolerance
        atol: Absolute tolerance

    Returns:
        (is_match, max_abs_error, max_rel_error)
    """
    # Tiger Style: Assert preconditions
    assert actual.shape == expected.shape, f"Shape mismatch: {actual.shape} vs {expected.shape}"
    assert rtol > 0, f"rtol must be positive, got {rtol}"
    assert atol > 0, f"atol must be positive, got {atol}"

    # Compute errors
    abs_diff = torch.abs(actual - expected)
    max_abs_error = float(abs_diff.max().item())

    # Avoid division by zero in relative error
    expected_abs = torch.abs(expected)
    rel_diff = abs_diff / torch.where(expected_abs > EPSILON_SAFE_DIVISION, expected_abs, torch.ones_like(expected_abs))
    max_rel_error = float(rel_diff.max().item())

    # Check tolerance
    is_match = bool(torch.allclose(actual, expected, rtol=rtol, atol=atol))

    return is_match, max_abs_error, max_rel_error


def _compute_tensor_errors(
    actual: torch.Tensor,
    expected: torch.Tensor,
    rtol: float,
    atol: float,
) -> tuple[float, float, torch.Tensor]:
    """Compute absolute and relative errors between tensors.

    Tiger Style: Pure computation, no branching.

    Args:
        actual: Computed result
        expected: Reference result
        rtol: Relative tolerance
        atol: Absolute tolerance

    Returns:
        (max_abs_error, max_rel_error, mismatched_mask)
    """
    # Compute absolute errors
    abs_diff = torch.abs(actual - expected)
    max_abs_error = float(abs_diff.max().item())

    # Compute relative errors (avoid division by zero)
    expected_abs = torch.abs(expected)
    rel_diff = abs_diff / torch.where(expected_abs > EPSILON_SAFE_DIVISION, expected_abs, torch.ones_like(expected_abs))
    max_rel_error = float(rel_diff.max().item())

    # Find tolerance mismatches
    tolerance = atol + rtol * expected_abs
    tol_mismatched = abs_diff > tolerance

    # Find NaN mismatches
    nan_mismatched = torch.logical_xor(torch.isnan(actual), torch.isnan(expected))

    # Find inf mismatches
    actual_inf = torch.isposinf(actual) | torch.isneginf(actual)
    expected_inf = torch.isposinf(expected) | torch.isneginf(expected)
    inf_mismatched = torch.logical_xor(actual_inf, expected_inf)

    # Combine all mismatches
    mismatched = tol_mismatched | nan_mismatched | inf_mismatched

    return max_abs_error, max_rel_error, mismatched


def _format_mismatch_details(
    actual: torch.Tensor,
    expected: torch.Tensor,
    mismatched: torch.Tensor,
    rtol: float,
    atol: float,
    max_print: int,
) -> list[str]:
    """Format detailed mismatch information for debugging.

    Tiger Style: Pure formatting function.

    Args:
        actual: Computed result
        expected: Reference result
        mismatched: Boolean mask of mismatched elements
        rtol: Relative tolerance
        atol: Absolute tolerance
        max_print: Maximum mismatch locations to print

    Returns:
        List of formatted mismatch detail strings
    """
    mismatch_details = []
    num_mismatched = mismatched.count_nonzero().item()
    mismatch_details.append(f"Number of mismatched elements: {num_mismatched}")

    # Get mismatch locations
    mismatch_indices = torch.nonzero(mismatched)
    num_to_print = min(max_print, len(mismatch_indices))

    # Compute errors for details
    abs_diff = torch.abs(actual - expected)
    expected_abs = torch.abs(expected)
    tolerance = atol + rtol * expected_abs

    # Check special cases
    nan_mismatched = torch.logical_xor(torch.isnan(actual), torch.isnan(expected))
    actual_inf = torch.isposinf(actual) | torch.isneginf(actual)
    expected_inf = torch.isposinf(expected) | torch.isneginf(expected)
    inf_mismatched = torch.logical_xor(actual_inf, expected_inf)

    # Format each mismatch
    for i in range(num_to_print):
        idx = mismatch_indices[i]
        pos = tuple(idx.tolist())
        actual_val = actual[pos].item()
        expected_val = expected[pos].item()
        diff_val = abs_diff[pos].item()
        tol_val = tolerance[pos].item()

        # Determine mismatch type
        if nan_mismatched[pos]:
            mismatch_type = "NaN mismatch"
        elif inf_mismatched[pos]:
            mismatch_type = "Inf mismatch"
        else:
            mismatch_type = "Tolerance mismatch"

        mismatch_details.append(
            f"ERROR AT {pos}: {mismatch_type} - "
            f"got={actual_val:.6f}, expected={expected_val:.6f}, "
            f"diff={diff_val:.6f}, tol={tol_val:.6f}"
        )

    if num_mismatched > max_print:
        mismatch_details.append(f"... and {num_mismatched - max_print} more mismatched elements")

    return mismatch_details


def allclose_with_error_verbose(
    actual: torch.Tensor,
    expected: torch.Tensor,
    rtol: float,
    atol: float,
    max_print: int = 5,
) -> tuple[bool, float, float, list[str]]:
    """Check if tensors match within tolerance with detailed mismatch locations.

    Enhanced version that provides exact locations of mismatches for better debugging.

    Tiger Style: Orchestrator - delegates computation and formatting to helpers.

    Based on Steve's verbose_allclose pattern.

    Args:
        actual: Computed result
        expected: Reference result
        rtol: Relative tolerance
        atol: Absolute tolerance
        max_print: Maximum number of mismatch locations to include in details

    Returns:
        (is_match, max_abs_error, max_rel_error, mismatch_details)
        mismatch_details: List of strings describing mismatches (empty if match)
    """
    # Validate inputs
    assert actual.shape == expected.shape, f"Shape mismatch: {actual.shape} vs {expected.shape}"
    assert rtol > 0, f"rtol must be positive, got {rtol}"
    assert atol > 0, f"atol must be positive, got {atol}"
    assert max_print > 0, f"max_print must be positive, got {max_print}"

    # Check shape mismatch first
    if actual.shape != expected.shape:
        return (
            False,
            float("inf"),
            float("inf"),
            [f"SIZE MISMATCH: got {actual.shape}, expected {expected.shape}"],
        )

    # Compute errors and find mismatches
    max_abs_error, max_rel_error, mismatched = _compute_tensor_errors(actual, expected, rtol, atol)

    # Check if tensors match
    is_match = bool(torch.allclose(actual, expected, rtol=rtol, atol=atol))

    # If match, return early
    if is_match:
        return is_match, max_abs_error, max_rel_error, []

    # Format mismatch details for debugging
    mismatch_details = _format_mismatch_details(actual, expected, mismatched, rtol, atol, max_print)

    return is_match, max_abs_error, max_rel_error, mismatch_details


def make_match_reference(
    reference_fn: Callable,
    rtol: float = 1e-3,
    atol: float = 1e-3,
) -> Callable[[Callable, Any], tuple[bool, ErrorInfo | None]]:
    """Create a checker function that compares implementation to reference.

    Args:
        reference_fn: Ground truth implementation
        rtol: Relative tolerance
        atol: Absolute tolerance

    Returns:
        Checker function: impl_fn -> (is_correct, error_msg | None)
    """
    # Tiger Style: Assert function arguments
    assert callable(reference_fn), "reference_fn must be callable"
    assert rtol > 0, f"rtol must be positive, got {rtol}"
    assert atol > 0, f"atol must be positive, got {atol}"

    def checker(impl_fn: Callable, test_input: Any) -> tuple[bool, ErrorInfo | None]:
        """Check if implementation matches reference.

        Returns:
            (is_correct, error_info | None)
            error_info is ErrorInfo object on implementation error, string on reference/mismatch error, None on success
        """
        assert callable(impl_fn), "impl_fn must be callable"

        try:
            # Run reference
            ref_output = reference_fn(test_input)
        except Exception as e:
            # Capture structured error info for reference failures too
            _, _, exc_tb = sys.exc_info()
            formatted_tb = traceback.format_exc()

            # Extract source file and line from traceback
            source_file = None
            source_line = None
            if exc_tb:
                # Walk traceback to find user code
                tb_obj = exc_tb
                while tb_obj:
                    frame = tb_obj.tb_frame
                    filename = frame.f_code.co_filename
                    # Look for reference kernel file
                    if "reference_kernel.py" in filename or "reference" in filename:
                        source_file = Path(filename).name
                        source_line = tb_obj.tb_lineno
                        break
                    tb_obj = tb_obj.tb_next

            error_info = ErrorInfo(
                exc_type=f"Reference {type(e).__name__}",  # Prefix to distinguish from impl errors
                exc_message=str(e),
                formatted_tb=formatted_tb,
                source_file=source_file,
                source_line=source_line,
            )
            return False, error_info

        try:
            # Run implementation (must not mutate test_input!)
            impl_output = impl_fn(test_input)
        except Exception as e:
            # Capture structured error info
            _, _, exc_tb = sys.exc_info()
            formatted_tb = traceback.format_exc()

            # Extract source file and line from traceback
            source_file = None
            source_line = None
            if exc_tb:
                # Walk traceback to find user code (not library code)
                tb_obj = exc_tb
                while tb_obj:
                    frame = tb_obj.tb_frame
                    filename = frame.f_code.co_filename
                    # Look for user's kernel file
                    if "agent_kernel.py" in filename or "optimized/" in filename:
                        source_file = Path(filename).name
                        source_line = tb_obj.tb_lineno
                        break
                    tb_obj = tb_obj.tb_next

            error_info = ErrorInfo(
                exc_type=type(e).__name__,
                exc_message=str(e),
                formatted_tb=formatted_tb,
                source_file=source_file,
                source_line=source_line,
            )
            return False, error_info

        # Compare outputs
        is_match, max_abs_err, max_rel_err = allclose_with_error(impl_output, ref_output, rtol=rtol, atol=atol)

        if is_match:
            return True, None
        else:
            # Use ErrorInfo for output mismatches too (no traceback since it's not an exception)
            error_msg = (
                f"max_abs_error={max_abs_err:.6f} (tol={atol}), " f"max_rel_error={max_rel_err:.6f} (tol={rtol})"
            )
            error_info = ErrorInfo(
                exc_type="OutputMismatch",
                exc_message=error_msg,
                formatted_tb="",  # No traceback for numerical mismatches
                source_file=None,
                source_line=None,
            )
            return False, error_info

    return checker


def benchmark_kernel(
    kernel_fn: Callable,
    test_input: Any,
    num_warmup: int = 10,
    num_runs: int = 100,
    use_triton: bool = True,
) -> tuple[float, str | None]:
    """Benchmark kernel execution time.

    Args:
        kernel_fn: Kernel to benchmark
        test_input: Input data (will be called multiple times)
        num_warmup: Warmup iterations
        num_runs: Measurement iterations
        use_triton: Use Triton's do_bench for GPU (more accurate)

    Returns:
        (avg_time_ms, error_msg | None)
        error_msg is None on success
    """
    # Tiger Style: Assert arguments
    assert callable(kernel_fn), "kernel_fn must be callable"
    assert num_warmup > 0, f"num_warmup must be positive, got {num_warmup}"
    assert num_runs > 0, f"num_runs must be positive, got {num_runs}"

    try:
        # Try Triton benchmarking for GPU (more accurate)
        if use_triton and torch.cuda.is_available():
            try:
                import triton.testing  # type: ignore[import-untyped]

                # Triton's do_bench handles warmup and synchronization
                time_ms = triton.testing.do_bench(
                    lambda: kernel_fn(test_input),
                    warmup=num_warmup,
                    rep=num_runs,
                )
            except ImportError:
                # Fall through to manual timing if Triton not available
                pass
            else:
                return time_ms, None

        # Fallback: Manual timing (original implementation)
        # Warmup
        for _ in range(num_warmup):
            _ = kernel_fn(test_input)

        # Ensure CUDA synchronization if on GPU
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        # Measure
        start_time = time.perf_counter()
        for _ in range(num_runs):
            _ = kernel_fn(test_input)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        end_time = time.perf_counter()

        avg_time_ms = ((end_time - start_time) / num_runs) * 1000.0

    except Exception as e:
        tb = traceback.format_exc()
        return -1.0, f"Benchmark failed: {type(e).__name__}: {e}\n{tb}"
    else:
        return avg_time_ms, None


def benchmark_vs_reference(
    impl_fn: Callable,
    reference_fn: Callable,
    test_input: Any,
    num_warmup: int = 10,
    num_runs: int = 100,
    use_triton: bool = True,
) -> tuple[float, float, float, str | None]:
    """Benchmark implementation against reference and compute speedup.

    Args:
        impl_fn: Implementation kernel to benchmark
        reference_fn: Reference kernel for comparison
        test_input: Test data
        num_warmup: Warmup iterations
        num_runs: Measurement iterations
        use_triton: Use Triton's do_bench if available

    Returns:
        (speedup, impl_time_ms, ref_time_ms, error_msg | None)
        speedup = ref_time / impl_time
        error_msg is None on success
    """
    try:
        # Benchmark reference
        ref_time, ref_err = benchmark_kernel(reference_fn, test_input, num_warmup, num_runs, use_triton)
        if ref_err:
            return 0.0, -1.0, -1.0, f"Reference benchmark failed: {ref_err}"

        # Benchmark implementation
        impl_time, impl_err = benchmark_kernel(impl_fn, test_input, num_warmup, num_runs, use_triton)
        if impl_err:
            return 0.0, impl_time, ref_time, f"Implementation benchmark failed: {impl_err}"

        # Calculate speedup
        speedup = ref_time / impl_time if impl_time > 0 else 0.0

    except Exception as e:
        tb = traceback.format_exc()
        return 0.0, -1.0, -1.0, f"Speedup comparison failed: {type(e).__name__}: {e}\n{tb}"
    else:
        return speedup, impl_time, ref_time, None


def compare_backends(
    implementation_paths: list[str],
    test_input: Any,
    reference_path: str = "nvfp4_gemv_blackwell",
    num_warmup: int = 10,
    num_runs: int = 100,
    use_triton: bool = True,
) -> dict[str, tuple[float, float]]:
    """Compare performance of multiple implementations against reference.

    Args:
        implementation_paths: List of implementation file paths to compare
        test_input: Test data
        reference_path: Path to reference kernel file or problem_id for speedup calculation
        num_warmup: Warmup iterations
        num_runs: Measurement iterations
        use_triton: Use Triton's do_bench if available

    Returns:
        Dict mapping implementation_path -> (speedup, time_ms)
        speedup is relative to reference_path
    """
    from wafer_core.utils.kernel_utils.evaluate import (
        load_kernel_from_file,
        load_reference_kernel_from_path,
    )

    # Benchmark reference first
    ref_fn = load_reference_kernel_from_path(reference_path)
    ref_time, ref_err = benchmark_kernel(ref_fn, test_input, num_warmup, num_runs, use_triton)
    if ref_err:
        raise ReferenceBenchmarkError(reference_path, ref_err)

    results = {}

    for impl_path in implementation_paths:
        if impl_path == reference_path:
            # Reference has speedup of 1.0
            results[impl_path] = (1.0, ref_time)
            continue

        impl_fn = load_kernel_from_file(impl_path)
        time_ms, err = benchmark_kernel(impl_fn, test_input, num_warmup, num_runs, use_triton)

        if err:
            results[impl_path] = (0.0, -1.0)
        else:
            speedup = ref_time / time_ms if time_ms > 0 else 0.0
            results[impl_path] = (speedup, time_ms)

    return results


def profile_kernel(
    kernel_fn: Callable,
    test_input: Any,
    output_dir: Path,
    backend_name: str,
    test_name: str,
    num_warmup: int = 5,
    num_profile_runs: int = 1,
) -> tuple[str, str | None]:
    """Profile kernel execution using torch.profiler.

    Args:
        kernel_fn: Kernel to profile
        test_input: Input data
        output_dir: Directory to save profile traces
        backend_name: Name of backend being profiled
        test_name: Name of test case
        num_warmup: Warmup iterations before profiling
        num_profile_runs: Number of profiling runs to capture

    Returns:
        (trace_path, error_msg | None)
        trace_path is the path to the saved trace JSON file
        error_msg is None on success
    """
    assert callable(kernel_fn), "kernel_fn must be callable"
    assert num_warmup >= 0, f"num_warmup must be non-negative, got {num_warmup}"
    assert num_profile_runs > 0, f"num_profile_runs must be positive, got {num_profile_runs}"

    try:
        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Warmup
        for _ in range(num_warmup):
            _ = kernel_fn(test_input)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        # Profile with torch.profiler
        trace_filename = f"{backend_name}_{test_name}_profile"
        chrome_trace_path = str(output_dir / f"{trace_filename}.json")

        with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ],
            record_shapes=True,
            profile_memory=True,
            with_stack=True,
        ) as prof:
            for _ in range(num_profile_runs):
                kernel_fn(test_input)
                if num_profile_runs > 1:
                    prof.step()

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        # Export chrome trace (don't use tensorboard handler to avoid double-save)
        prof.export_chrome_trace(chrome_trace_path)

    except Exception as e:
        tb = traceback.format_exc()
        return "", f"Profiling failed: {type(e).__name__}: {e}\n{tb}"
    else:
        return chrome_trace_path, None


def _generate_ncu_script(
    implementation_path: str,
    params_path: Path,
    project_dir: Path,
) -> str:
    """Generate NCU profiling script content.

    Returns:
        Python script content as string
    """
    import os

    # Determine function name from PROBLEM_ID if needed
    problem_id = os.environ.get("PROBLEM_ID", "nvfp4_gemv_blackwell")
    if problem_id == "nvfp4_gemv_blackwell":
        function_name = "nvfp4_kernel"
    elif problem_id.startswith("gpumode_"):
        function_name = f"{problem_id}_kernel"
    else:
        function_name = f"{problem_id}_kernel"

    return f"""
import sys
import os
import json
import torch
import importlib.util
from pathlib import Path

# Add project directory to path so imports work (for wafer_utils)
project_dir = Path('{project_dir}')
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Also add CWD (run_dir) for reference_kernel imports
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

# Add wafer_utils to path so reference_kernel can import make_match_reference
wafer_utils_parent = project_dir / 'wafer_utils' / 'kernel_utils'
if str(wafer_utils_parent) not in sys.path:
    sys.path.insert(0, str(wafer_utils_parent))

# Create a minimal 'utils' module alias for reference_kernel's "from utils import make_match_reference"
# This is needed because reference_kernel.py imports "from utils import make_match_reference"
# but the actual function is in wafer_utils.kernel_utils.utils
from wafer_core.utils.kernel_utils.utils import make_match_reference
class _utils_module:
    make_match_reference = make_match_reference
sys.modules['utils'] = _utils_module

# Load test parameters
with open('{params_path}', 'r') as f:
    params = json.load(f)

# Import reference_kernel from CWD (evaluate.py sets CWD to run_dir)
from reference_kernel import generate_input

# Generate test input
test_input = generate_input(**params)

# Load kernel function from file
kernel_path = Path('{implementation_path}')
if not kernel_path.is_absolute():
    kernel_path = project_dir / kernel_path

spec = importlib.util.spec_from_file_location("kernel_module", kernel_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Find kernel function: try custom_kernel first (gpumode), then problem-specific names
kernel_fn = None
for fn_name in ['custom_kernel', '{function_name}']:
    if hasattr(module, fn_name):
        kernel_fn = getattr(module, fn_name)
        break
if kernel_fn is None:
    raise RuntimeError(f"No kernel function found in {{kernel_path}}. Tried: custom_kernel, {function_name}")

# Run the kernel once (NCU will profile this execution)
result = kernel_fn(test_input)

# Synchronize to ensure kernel completes
if torch.cuda.is_available():
    torch.cuda.synchronize()

print("Kernel execution completed")
"""


def _find_ncu_executable() -> str | None:
    """Find NCU executable in common locations.

    Returns:
        Path to ncu or None if not found
    """
    import glob
    import shutil

    # Try PATH first
    ncu_path = shutil.which("ncu")
    if ncu_path:
        return ncu_path

    # Check common CUDA installation paths
    common_paths = [
        "/usr/local/cuda/bin/ncu",
        "/usr/local/cuda-12/bin/ncu",
        "/usr/local/cuda-12.8/bin/ncu",
        "/usr/local/cuda-12.6/bin/ncu",
        "/usr/local/cuda-12.4/bin/ncu",
        "/opt/nvidia/nsight-compute/ncu",
    ]

    for cuda_path in common_paths:
        if Path(cuda_path).exists():
            return cuda_path

    # Check versioned Nsight Compute directories (e.g., /opt/nvidia/nsight-compute-2024.1.0/ncu)
    versioned_patterns = [
        "/opt/nvidia/nsight-compute-*/ncu",
        "/usr/local/nsight-compute-*/ncu",
        "/opt/nsight-compute-*/ncu",
        "/opt/nvidia/nsight-compute/ncu",
    ]

    for pattern in versioned_patterns:
        matches = glob.glob(pattern)
        if matches:
            # Return most recent version (sorted alphabetically, highest version last)
            return sorted(matches)[-1]

    return None


def _build_ncu_command(
    ncu_path: str,
    report_path: Path,
    ncu_args: str,
    script_path: Path,
    output_format: str = "ncu-rep",
) -> list[str]:
    """Build NCU command with sudo if available.

    Args:
        ncu_path: Path to ncu executable
        report_path: Output file path (without extension for ncu-rep format)
        ncu_args: Additional NCU arguments
        script_path: Python script to profile
        output_format: Output format - "ncu-rep" for binary or "csv" for CSV

    Returns:
        Command as list of strings
    """
    import subprocess
    import sys

    # Check if we can use sudo (NCU needs it for GPU performance counters)
    use_sudo = False
    try:
        sudo_check = subprocess.run(["sudo", "-n", "true"], capture_output=True)
        if sudo_check.returncode == 0:
            use_sudo = True
    except FileNotFoundError:
        # sudo not installed (e.g., in Docker container) - run without sudo
        pass

    ncu_cmd = []
    if use_sudo:
        ncu_cmd.extend(["sudo", "-E"])  # -E preserves environment

    ncu_cmd.append(ncu_path)

    if output_format == "csv":
        # CSV format for quick analysis
        ncu_cmd.extend(
            [
                "--csv",
                "--log-file",
                str(report_path),
                "--force-overwrite",
            ]
        )
    else:
        # Binary .ncu-rep format for detailed analysis with wafer ncu-analyze
        # --export writes binary format, --page=details captures full metrics
        ncu_cmd.extend(
            [
                "--export",
                str(report_path),  # NCU adds .ncu-rep extension automatically
                "--force-overwrite",
                "--page=details",  # Capture detailed metrics
            ]
        )

    # Add custom metrics if provided
    if ncu_args:
        ncu_cmd.extend(ncu_args.split())

    # Add the Python command
    ncu_cmd.extend([sys.executable, str(script_path)])

    return ncu_cmd


def ncu_profile_kernel(
    kernel_fn: Callable,
    test_input: Any,
    output_dir: Path,
    backend_name: str,
    test_name: str,
    test_case: Any = None,
    ncu_args: str | None = None,
    output_format: str = "ncu-rep",
) -> tuple[str, str | None]:
    """Profile kernel execution using NVIDIA Nsight Compute (ncu).

    Orchestrates NCU profiling by creating temp script and running ncu.

    Args:
        kernel_fn: Kernel to profile
        test_input: Input data (tuple from TestCase.generate())
        output_dir: Directory to save NCU reports
        backend_name: Name of backend being profiled
        test_name: Name of test case
        test_case: TestCase object (optional, for backward compatibility)
        ncu_args: Arguments to pass to ncu (default: comprehensive metrics for csv, none for ncu-rep)
        output_format: Output format - "ncu-rep" for binary (default) or "csv" for CSV

    Returns:
        (report_path, error_msg): Path to report on success, error on failure
    """
    import json
    import subprocess

    assert callable(kernel_fn), "kernel_fn must be callable"

    # Use comprehensive metrics by default for CSV format (ncu-rep uses --page=details instead)
    if ncu_args is None and output_format == "csv":
        ncu_args = f"--metrics {NCU_COMPREHENSIVE_METRICS}"
    elif ncu_args is None:
        ncu_args = ""

    try:
        # Setup paths
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize backend_name for use in filenames (it may be a full path)
        safe_backend_name = Path(backend_name).stem  # e.g., "/path/to/kernel.py" -> "kernel"

        script_path = output_dir / f"_ncu_temp_{safe_backend_name}_{test_name}.py"
        params_path = output_dir / f"_ncu_temp_{safe_backend_name}_{test_name}.json"

        # Set report path based on format
        if output_format == "csv":
            report_path = output_dir / f"{safe_backend_name}_{test_name}_ncu.csv"
        else:
            # For ncu-rep, NCU adds .ncu-rep extension automatically
            report_path = output_dir / f"{safe_backend_name}_{test_name}_ncu"

        # test_case is required (caller must provide it)
        assert test_case is not None, "test_case must be provided"

        # Save test parameters (TestCase uses params dict, not direct attributes)
        test_params = test_case.params
        with open(params_path, "w") as f:
            json.dump(test_params, f)

        # Generate and write profiling script
        # project_dir needs to be the parent of wafer_utils so "from wafer_core.utils..." imports work
        # __file__ is .../wafer_utils/kernel_utils/utils.py
        # parent.parent.parent gets us to .../async-wevin (the research root)
        project_dir = Path(__file__).parent.parent.parent.absolute()
        script_content = _generate_ncu_script(backend_name, params_path, project_dir)

        with open(script_path, "w") as f:
            f.write(script_content)

        # Find NCU executable
        ncu_path = _find_ncu_executable()
        if ncu_path is None:
            return "", "NCU not found - ensure NVIDIA Nsight Compute is installed and in PATH"

        # Build and run NCU command
        ncu_cmd = _build_ncu_command(ncu_path, report_path, ncu_args, script_path, output_format)

        result = subprocess.run(
            ncu_cmd,
            capture_output=True,
            text=True,
            timeout=NCU_TIMEOUT_SECONDS,
        )

        # Clean up temporary files
        script_path.unlink(missing_ok=True)
        params_path.unlink(missing_ok=True)

        # Check result
        if result.returncode != 0:
            error_msg = f"NCU exit code {result.returncode}\n"
            if result.stdout:
                error_msg += f"stdout: {result.stdout}\n"
            if result.stderr:
                error_msg += f"stderr: {result.stderr}"
            return "", error_msg

        # For ncu-rep format, NCU adds the extension automatically
        final_report_path = str(report_path) + ".ncu-rep" if output_format != "csv" else str(report_path)
        return final_report_path, None

    except subprocess.TimeoutExpired:
        return "", "NCU profiling timed out (>5 minutes)"
    except FileNotFoundError:
        return "", "NCU not found - ensure NVIDIA Nsight Compute is installed and in PATH"
    except Exception as e:
        tb = traceback.format_exc()
        return "", f"NCU profiling failed: {type(e).__name__}: {e}\n{tb}"


def clone_data(data: Any) -> Any:
    """Recursively clone all tensors in nested data structures.

    This ensures each benchmark run gets fresh data, preventing:
    - Data corruption from previous runs
    - Cache effects from tensor reuse
    - Reference contamination

    Args:
        data: Nested structure containing tensors (tuple/list/dict/tensor)

    Returns:
        Deep copy with all tensors cloned
    """
    if isinstance(data, tuple):
        return tuple(clone_data(x) for x in data)
    elif isinstance(data, list):
        return [clone_data(x) for x in data]
    elif isinstance(data, dict):
        return {k: clone_data(v) for k, v in data.items()}
    elif isinstance(data, torch.Tensor):
        return data.clone()
    else:
        # Primitive types (int, float, str, None) - return as-is
        return data


def clear_l2_cache() -> None:
    """Flush GPU L2 cache for consistent benchmark measurements.

    Creates a large temporary tensor to evict L2 cache contents.
    This prevents cache effects from biasing consecutive benchmark runs.

    Critical for accurate adaptive benchmarking where we run the same
    kernel repeatedly and need consistent timing.
    """
    if torch.cuda.is_available():
        # Allocate large tensor to flush L2 cache
        # Size: 256MB should be larger than typical L2 cache
        dummy = torch.randn((1024, 1024, 64), device="cuda", dtype=torch.float32)
        del dummy
        torch.cuda.synchronize()


def _measure_single_kernel_run(kernel_fn: Callable, test_input: Any) -> float:
    """Measure single kernel execution time with CUDA events.

    Tiger Style: Pure measurement function, no side effects.

    Args:
        kernel_fn: Kernel to benchmark
        test_input: Input data (will be cloned)

    Returns:
        Duration in milliseconds
    """
    # Clear L2 cache for consistent measurements
    clear_l2_cache()

    # Measure with CUDA events (more accurate than CPU timing)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        start_event = torch.cuda.Event(enable_timing=True)
        end_event = torch.cuda.Event(enable_timing=True)

        start_event.record()
        _ = kernel_fn(clone_data(test_input))
        end_event.record()
        torch.cuda.synchronize()

        duration_ms = start_event.elapsed_time(end_event)
    else:
        # CPU fallback
        start = time.perf_counter()
        _ = kernel_fn(clone_data(test_input))
        duration_ms = (time.perf_counter() - start) * 1000.0

    return duration_ms


def _check_benchmark_convergence(
    durations_ms: list[float],
    iteration: int,
    wallclock_elapsed: float,
    convergence_threshold: float,
    max_kernel_time_s: float,
    max_wallclock_s: float,
) -> tuple[bool, str]:
    """Check if benchmark has converged or hit time limits.

    Tiger Style: Pure computation, returns convergence decision.

    Args:
        durations_ms: List of measured durations
        iteration: Current iteration number
        wallclock_elapsed: Wallclock time elapsed
        convergence_threshold: Relative error threshold
        max_kernel_time_s: Max total kernel time
        max_wallclock_s: Max wallclock time

    Returns:
        (should_stop, reason): Whether to stop and why
    """
    import math

    # Need minimum runs before checking convergence
    if iteration < 2 or wallclock_elapsed <= 0.1:
        return False, ""

    # Calculate statistics
    n = len(durations_ms)
    mean = sum(durations_ms) / n
    variance = sum((x - mean) ** 2 for x in durations_ms) / (n - 1)
    std = math.sqrt(variance)
    err = std / math.sqrt(n)

    # Check convergence: relative error < threshold
    relative_error = err / mean if mean > 0 else float("inf")
    if relative_error < convergence_threshold:
        return True, "converged"

    # Check time limits
    total_kernel_time_s = (mean * n) / 1000.0
    if total_kernel_time_s > max_kernel_time_s:
        return True, "kernel_time_limit"

    if wallclock_elapsed > max_wallclock_s:
        return True, "wallclock_limit"

    return False, ""


def _compute_benchmark_statistics(
    durations_ms: list[float],
) -> tuple[float, float, float, float, float, int]:
    """Compute final benchmark statistics.

    Tiger Style: Pure computation, no side effects.

    Args:
        durations_ms: List of measured durations

    Returns:
        (mean_ms, std_ms, err_ms, best_ms, worst_ms, num_runs)
    """
    import math

    n = len(durations_ms)
    mean = sum(durations_ms) / n
    variance = sum((x - mean) ** 2 for x in durations_ms) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)
    err = std / math.sqrt(n)
    best = min(durations_ms)
    worst = max(durations_ms)

    return mean, std, err, best, worst, n


def benchmark_kernel_adaptive(
    kernel_fn: Callable,
    test_input: Any,
    convergence_threshold: float = 0.001,
    max_iterations: int = 200,
    max_kernel_time_s: float = 10.0,
    max_wallclock_s: float = 120.0,
) -> tuple[float, float, float, float, float, int, str | None]:
    """Adaptive benchmarking with convergence check.

    Runs kernel repeatedly until statistical convergence or time limits.
    Stops when relative error drops below threshold (default: 0.1%).

    Tiger Style: Orchestrator with control flow, delegates to helpers.

    Based on Steve's GPUMode competition benchmark strategy.

    Args:
        kernel_fn: Kernel to benchmark
        test_input: Input data (will be cloned for each run)
        convergence_threshold: Stop when (stderr/mean) < threshold (default: 0.001 = 0.1%)
        max_iterations: Maximum number of runs (default: 200)
        max_kernel_time_s: Stop when total kernel time exceeds this (default: 10s)
        max_wallclock_s: Stop when wallclock time exceeds this (default: 120s)

    Returns:
        (mean_ms, std_ms, err_ms, best_ms, worst_ms, num_runs, error_msg)
        - mean_ms: Average time in milliseconds
        - std_ms: Standard deviation in milliseconds
        - err_ms: Standard error (std / sqrt(n)) in milliseconds
        - best_ms: Fastest run in milliseconds
        - worst_ms: Slowest run in milliseconds
        - num_runs: Number of iterations performed
        - error_msg: None on success, error string on failure
    """
    # Validate inputs
    assert callable(kernel_fn), "kernel_fn must be callable"
    assert convergence_threshold > 0, f"convergence_threshold must be positive, got {convergence_threshold}"
    assert max_iterations > 0, f"max_iterations must be positive, got {max_iterations}"
    assert max_kernel_time_s > 0, f"max_kernel_time_s must be positive, got {max_kernel_time_s}"
    assert max_wallclock_s > 0, f"max_wallclock_s must be positive, got {max_wallclock_s}"

    durations_ms = []
    start_wallclock = time.perf_counter()

    try:
        # Run benchmark loop
        for i in range(max_iterations):
            # Measure single run
            duration_ms = _measure_single_kernel_run(kernel_fn, test_input)
            durations_ms.append(duration_ms)

            # Check convergence
            wallclock_elapsed = time.perf_counter() - start_wallclock
            should_stop, _ = _check_benchmark_convergence(
                durations_ms,
                i,
                wallclock_elapsed,
                convergence_threshold,
                max_kernel_time_s,
                max_wallclock_s,
            )
            if should_stop:
                break

        # Guard: ensure we have at least one successful run
        if not durations_ms:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0, "No successful benchmark runs"

        # Compute final statistics
        mean, std, err, best, worst, num_runs = _compute_benchmark_statistics(durations_ms)

    except Exception as e:
        # Catch kernel failures, CUDA errors, user code exceptions
        tb = traceback.format_exc()
        error_msg = f"Adaptive benchmark failed: {type(e).__name__}: {e}\n{tb}"
        return -1.0, 0.0, 0.0, 0.0, 0.0, 0, error_msg
    else:
        return mean, std, err, best, worst, num_runs, None
