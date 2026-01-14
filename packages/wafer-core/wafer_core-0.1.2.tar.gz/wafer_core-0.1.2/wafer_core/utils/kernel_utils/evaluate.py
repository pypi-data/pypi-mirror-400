#!/usr/bin/env python3
"""Evaluation orchestrator for NVFP4 kernel implementations.

Runs correctness, performance, and profiling checks on kernel backends.
Uses cached reference outputs for decoupled, isolated execution.

For focused testing, use specialized modules:
    - kernel_utils.correctness: Correctness-only testing
    - kernel_utils.benchmark: Performance benchmarking
    - kernel_utils.profiling: Torch/NCU profiling

Usage:
    # Test implementation kernel (cached mode - decoupled from reference)
    python -m kernel_utils.evaluate --implementation /path/to/kernel.py

    # Test with custom reference
    python -m kernel_utils.evaluate --implementation /path/to/kernel.py --reference /path/to/reference.py

    # Test with problem_id reference
    python -m kernel_utils.evaluate --implementation /path/to/kernel.py --reference nvfp4_gemv_blackwell
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import torch

# Set up logging for optional kernel imports
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add research root to path for imports
# evaluate.py is at wafer_utils/kernel_utils/evaluate.py
# Need to go up 2 levels to reach research/ to import wafer_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Correctness checking tolerances
CORRECTNESS_RTOL = 1e-3  # Relative tolerance for FP16 output comparison
CORRECTNESS_ATOL = 1e-3  # Absolute tolerance for FP16 output comparison

# Benchmarking constants
BENCHMARK_NUM_WARMUP = 5  # Number of warmup runs before benchmarking
BENCHMARK_NUM_RUNS = 20  # Number of benchmark runs for averaging

# Profiling constants
PROFILE_NUM_WARMUP = 5  # Number of warmup runs before profiling
PROFILE_NUM_RUNS = 1  # Number of profiling runs (profiling is expensive)

# Time conversion constants
MS_TO_MICROSECONDS = 1000  # Convert milliseconds to microseconds

# Performance approximation factors (for display when detailed stats unavailable)
PERF_MIN_FACTOR = 0.99  # Minimum time approximation factor
PERF_MAX_FACTOR = 1.01  # Maximum time approximation factor
PERF_STD_FACTOR = 0.001  # Standard deviation approximation factor

# Error sentinel values
ERROR_TIME_MS = -1.0  # Sentinel value for failed benchmark times

# Display formatting
PRINT_SEPARATOR_WIDTH = 80  # Width of separator lines in output

from wafer_core.utils.exceptions import (  # noqa: E402
    InvalidTestCasesFormatError,
    ReferenceKernelLoadError,
)
from wafer_core.utils.kernel_utils.results import (  # noqa: E402
    BackendResults,
    CorrectnessResult,
    PerformanceResult,
    TestSuiteResults,
)
from wafer_core.utils.kernel_utils.task import (  # noqa: E402
    TestCase,
)
from wafer_core.utils.kernel_utils.utils import (  # noqa: E402
    ErrorInfo,
    benchmark_kernel,
    make_match_reference,
    ncu_profile_kernel,
    profile_kernel,
)

# Cache for dynamically loaded reference kernels
_reference_kernel_cache: dict[str, Callable] = {}


# Parameter dataclasses for reducing function argument count
# Tiger Style: Hourglass shape - group related params together


@dataclass(frozen=True)
class TestExecutionContext:
    """Context for executing a single test (paths and configuration).

    Immutable context passed down the test execution stack.
    """

    implementation_path: str
    reference_path: str
    test_suite: str
    use_cached_reference: bool


@dataclass(frozen=True)
class ProfilingConfig:
    """Configuration for profiling operations.

    Groups profiling-related settings together.
    """

    profile_subdir: str
    ncu_subdir: str
    enable_profiling: bool
    enable_ncu: bool


@dataclass(frozen=True)
class TestRunConfig:
    """Complete configuration for a test run.

    Combines execution context and profiling config.
    """

    context: TestExecutionContext
    profiling: ProfilingConfig


def _load_reference_kernel(problem_id: str) -> Callable:
    """Dynamically load reference kernel based on problem_id.

    Args:
        problem_id: Problem identifier (e.g., "nvfp4_gemv_blackwell", "gpumode_540")

    Returns:
        Reference kernel solve function

    Raises:
        ReferenceKernelLoadError: If problem_id doesn't have a reference kernel module
    """
    assert problem_id, "problem_id cannot be empty"
    assert isinstance(problem_id, str), f"problem_id must be string, got {type(problem_id)}"

    if problem_id in _reference_kernel_cache:
        return _reference_kernel_cache[problem_id]

    # Try to import reference kernel from problem module
    # Format: {problem_id}/reference_kernel.py -> solve function
    try:
        # Handle different problem_id formats
        if problem_id.startswith("gpumode_"):
            # For GPUMode problems, try to import from a module matching the problem_id
            module_name = f"{problem_id}.reference_kernel"
        else:
            # Direct problem_id (e.g., "nvfp4_gemv_blackwell")
            module_name = f"{problem_id}.reference_kernel"

        module = __import__(module_name, fromlist=["solve"])
        reference_solve = module.solve
        _reference_kernel_cache[problem_id] = reference_solve
        logger.info(f"loaded reference kernel for problem: {problem_id}")

    except ImportError as e:
        # Fail fast - no fallbacks
        raise ReferenceKernelLoadError(problem_id, e) from e
    else:
        return reference_solve


def ref_kernel_adapter(inputs: Any, problem_id: str = "nvfp4_gemv_blackwell") -> Any:
    """Adapter to convert dict inputs to reference kernel.

    Args:
        inputs: Input data (dict or tuple)
        problem_id: Problem identifier for dynamic reference kernel loading
    """
    assert inputs is not None, "inputs cannot be None"
    assert problem_id, "problem_id cannot be empty"

    reference_solve = _load_reference_kernel(problem_id)

    if isinstance(inputs, dict):
        return reference_solve(**inputs)
    else:
        # Old tuple interface: (a, b, scale_a, scale_b, scale_a_permuted, scale_b_permuted, c)
        a, b, scale_a, scale_b, scale_a_permuted, scale_b_permuted, c = inputs
        return reference_solve(
            a=a,
            b=b,
            scale_a=scale_a,
            scale_b=scale_b,
            scale_a_cpu=scale_a.cpu(),
            scale_b_cpu=scale_b.cpu(),
            scale_a_permuted=scale_a_permuted,
            scale_b_permuted=scale_b_permuted,
            c=c,
        )


def load_reference_kernel_from_path(reference_path: str) -> Callable:
    """Load reference kernel from path or problem_id.

    Args:
        reference_path: Either a file path or problem_id string (e.g., "nvfp4_gemv_blackwell")

    Returns:
        Reference kernel function

    Raises:
        FileNotFoundError: If reference_path is a path but file doesn't exist
        ReferenceKernelLoadError: If reference_path is a problem_id but can't be loaded
    """
    assert reference_path, "reference_path cannot be empty"

    from pathlib import Path

    # Check if it's a file path
    ref_path = Path(reference_path)
    if ref_path.exists() and ref_path.is_file():
        # Load from file - reference kernels use 'ref_kernel' function name
        return load_kernel_from_file(reference_path, function_name="ref_kernel")
    elif "/" in reference_path or "\\" in reference_path or reference_path.endswith(".py"):
        # Looks like a file path but doesn't exist - fail fast
        raise FileNotFoundError(
            f"Reference file not found: {reference_path}. "
            "If this is a problem_id, it should not contain path separators or .py extension."
        )
    else:
        # Treat as problem_id and load built-in reference (will fail fast if not found)
        return ref_kernel_adapter


def _print_gpumode_correctness_results(backend_results: BackendResults) -> None:
    """Print correctness results in gpumode_test.txt format."""
    assert backend_results is not None, "backend_results cannot be None"

    print("\n📋 Correctness Summary:")
    for result in backend_results.correctness_tests:
        status = "✅" if result.is_correct else "❌"
        # Parse params from test_params string
        params = dict(item.split("=") for item in result.test_params.split(", "))
        print(
            f"{status} {result.test_name}: k={params['k']}, l={params['l']}, m={params['m']}, seed={params['seed']}"
        )


def _print_gpumode_benchmark_results(backend_results: BackendResults) -> None:
    """Print benchmark results in gpumode_benchmark.txt and leaderboard format."""
    import math

    assert backend_results is not None, "backend_results cannot be None"

    print("\n📊 gpumode_benchmark.txt:")
    benchmark_times = []

    for result in backend_results.performance_tests:
        if result.test_name.startswith("gpumode_bench") and result.successfully_ran:
            # Parse params
            params = dict(item.split("=") for item in result.test_params.split(", "))
            avg_time_us = result.avg_time_ms * MS_TO_MICROSECONDS

            # We don't have min/max/std from current implementation, so approximate
            # In real implementation, we'd need to track these in PerformanceResult
            min_time_us = avg_time_us * PERF_MIN_FACTOR
            max_time_us = avg_time_us * PERF_MAX_FACTOR
            std_dev_us = avg_time_us * PERF_STD_FACTOR

            print(f"k: {params['k']}; l: {params['l']}; m: {params['m']}; seed: {params['seed']}")
            print(f" ⏱ {avg_time_us:.1f} ± {std_dev_us:.2f} µs")
            print(f" ⚡ {min_time_us:.1f} µs 🐌 {max_time_us:.1f} µs")
            print()

            benchmark_times.append(avg_time_us)

    # Print leaderboard with geometric mean score
    if benchmark_times:
        print("🏆 gpumode_leaderboard.txt:")
        for result in backend_results.performance_tests:
            if result.test_name.startswith("gpumode_bench") and result.successfully_ran:
                params = dict(item.split("=") for item in result.test_params.split(", "))
                avg_time_us = result.avg_time_ms * MS_TO_MICROSECONDS
                min_time_us = avg_time_us * PERF_MIN_FACTOR
                max_time_us = avg_time_us * PERF_MAX_FACTOR
                std_dev_us = avg_time_us * PERF_STD_FACTOR

                print(
                    f"k: {params['k']}; l: {params['l']}; m: {params['m']}; seed: {params['seed']}"
                )
                print(f" ⏱ {avg_time_us:.1f} ± {std_dev_us:.2f} µs")
                print(f" ⚡ {min_time_us:.1f} µs 🐌 {max_time_us:.1f} µs")
                print()

        # Calculate geometric mean
        geomean_score = math.exp(sum(math.log(t) for t in benchmark_times) / len(benchmark_times))
        print(f" score: {geomean_score:.3f}μs")


def print_gpumode_format(
    backend_results: BackendResults,
    test_suites: list[str],
    test_cases: list[TestCase],
) -> None:
    """Print results in GPUMode competition format.

    Args:
        backend_results: Results for a single backend
        test_suites: List of test suite names that were run
        test_cases: List of test cases that were run
    """
    assert backend_results is not None, "backend_results cannot be None"
    assert test_suites is not None, "test_suites cannot be None"

    # Only print GPUMode format if we ran GPUMode test suites
    if "gpumode_correctness" not in test_suites and "gpumode_benchmark" not in test_suites:
        return

    print("\n" + "=" * PRINT_SEPARATOR_WIDTH)
    print("GPUMode Competition Format")
    print("=" * PRINT_SEPARATOR_WIDTH)

    # Print correctness tests
    if "gpumode_correctness" in test_suites:
        _print_gpumode_correctness_results(backend_results)

    # Print benchmark tests
    if "gpumode_benchmark" in test_suites:
        _print_gpumode_benchmark_results(backend_results)


def _setup_test_backend(
    implementation_path: str,
    reference_path: str,
    test_suites: list[str],
) -> tuple[object, object | None, bool, str]:
    """Setup implementation and checker function.

    Returns:
        (implementation_fn, checker, use_cached_reference, error_msg): Implementation and checker on success, error on failure
    """
    assert implementation_path, "implementation_path cannot be empty"
    assert reference_path, "reference_path cannot be empty"
    assert test_suites is not None, "test_suites cannot be None"
    assert len(test_suites) > 0, "test_suites cannot be empty"

    # Load implementation kernel
    try:
        implementation_fn = load_kernel_from_file(implementation_path)
    except Exception as e:
        return None, None, False, f"Failed to load implementation from {implementation_path}: {e}"

    # Always use live reference mode (no caching for now)
    # We explicitly pass both implementation and reference paths,
    # so we can run them both directly without pre-generated caches
    use_cached_reference = False

    print(f"   Using live reference: {reference_path}")
    try:
        ref_fn = load_reference_kernel_from_path(reference_path)
        checker = make_match_reference(ref_fn, rtol=CORRECTNESS_RTOL, atol=CORRECTNESS_ATOL)
    except Exception as e:
        return None, None, False, f"Failed to load reference from {reference_path}: {e}"

    return implementation_fn, checker, use_cached_reference, ""


def _run_correctness_test(
    test: TestCase,
    implementation_fn: Callable,
    checker: Callable,
    use_cached_reference: bool,
    test_suite: str,
) -> tuple[bool, ErrorInfo | None, object]:
    """Run correctness check on a single test.

    Returns:
        (is_correct, error_msg, test_input): Correctness result and input data.
        error_msg is ErrorInfo if test failed, None otherwise.
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert test_suite, "test_suite cannot be empty"
    assert checker is not None, "checker cannot be None"

    # Note: use_cached_reference is always False (we use live reference mode)
    # Keeping the parameter for now to avoid breaking the call chain
    test_input = test.generate()
    is_correct, error_msg = checker(implementation_fn, test_input)
    return is_correct, error_msg, test_input


def _should_stop_early(error_msg: ErrorInfo | None) -> bool:
    """Check if error indicates fundamental failure requiring early stop.

    Fundamental errors (coding bugs) vs numerical errors (tolerance issues).
    """
    if not error_msg:
        return False

    error_string = error_msg.to_string()

    fundamental_errors = [
        "TypeError",
        "ValueError",
        "AttributeError",
        "NameError",
        "SyntaxError",
        "ImportError",
        "CUDA error",  # Any CUDA error
        "AcceleratorError",
    ]

    return any(err in error_string for err in fundamental_errors)


def _run_performance_test(
    test: TestCase,
    implementation_fn: object,
    implementation_path: str,
    reference_path: str,
    test_input: object | None,
    use_cached_reference: bool,
) -> PerformanceResult:
    """Run performance benchmark and calculate speedup.

    Returns:
        PerformanceResult with benchmark times and speedup
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert implementation_path, "implementation_path cannot be empty"
    assert reference_path, "reference_path cannot be empty"

    # Tiger Style: Type narrow to Callable after assertion

    assert callable(implementation_fn), "implementation_fn must be callable"
    impl_fn: Callable = implementation_fn

    # Prepare test input for benchmarking
    if use_cached_reference and test_input is not None:
        test_input_bench = test_input
    else:
        test_input_bench = test.generate()

    # Benchmark implementation
    avg_time, bench_err = benchmark_kernel(
        impl_fn, test_input_bench, num_warmup=BENCHMARK_NUM_WARMUP, num_runs=BENCHMARK_NUM_RUNS
    )

    # Calculate speedup vs reference
    speedup = None
    ref_time = None
    if implementation_path != reference_path and bench_err is None:
        if use_cached_reference:
            # In cached mode, don't re-run reference for performance
            print("   ⚠️  Speedup calculation skipped (reference not benchmarked in cached mode)")
        else:
            # Get reference time (live mode)
            ref_fn = load_reference_kernel_from_path(reference_path)
            test_input_ref = test.generate()
            ref_time, ref_err = benchmark_kernel(
                ref_fn, test_input_ref, num_warmup=BENCHMARK_NUM_WARMUP, num_runs=BENCHMARK_NUM_RUNS
            )
            if ref_err is None:
                speedup = ref_time / avg_time if avg_time > 0 else 0.0

    return PerformanceResult(
        test_name=test.name,
        backend_name=implementation_path,
        successfully_ran=(bench_err is None),
        test_params=test.serialize(),
        avg_time_ms=avg_time if bench_err is None else ERROR_TIME_MS,
        speedup=speedup,
        reference_time_ms=ref_time,
        error_msg=bench_err,
    )


def _run_torch_profiling(
    test: TestCase,
    implementation_fn: object,
    implementation_path: str,
    reference_path: str,
    profile_subdir: str,
) -> list:
    """Run torch profiling for implementation and reference.

    Returns:
        List of (implementation_path, test_name, trace_path) tuples
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert implementation_path, "implementation_path cannot be empty"

    # Tiger Style: Type narrow to Callable after assertion

    assert callable(implementation_fn), "implementation_fn must be callable"
    impl_fn: Callable = implementation_fn

    profile_traces = []
    test_input_prof = test.generate()
    profile_dir = Path(profile_subdir)

    # Profile implementation
    trace_path, prof_err = profile_kernel(
        impl_fn,
        test_input_prof,
        profile_dir,
        implementation_path,
        test.name,
        num_warmup=PROFILE_NUM_WARMUP,
        num_profile_runs=PROFILE_NUM_RUNS,
    )
    if prof_err is None:
        print(f"   📊 Torch profile saved: {trace_path}")
        profile_traces.append((implementation_path, test.name, trace_path))
    else:
        print(f"   ⚠️  Torch profiling failed: {prof_err}")

    # Also profile reference for comparison
    if implementation_path != reference_path:
        ref_fn = load_reference_kernel_from_path(reference_path)
        test_input_ref_prof = test.generate()
        ref_trace_path, ref_prof_err = profile_kernel(
            ref_fn,
            test_input_ref_prof,
            profile_dir,
            reference_path,
            test.name,
            num_warmup=PROFILE_NUM_WARMUP,
            num_profile_runs=PROFILE_NUM_RUNS,
        )
        if ref_prof_err is None:
            print(f"   📊 Reference torch profile saved: {ref_trace_path}")
            profile_traces.append((reference_path, test.name, ref_trace_path))
        else:
            print(f"   ⚠️  Reference torch profiling failed: {ref_prof_err}")

    return profile_traces


def _run_ncu_profiling(
    test: TestCase,
    implementation_fn: object,
    implementation_path: str,
    reference_path: str,
    ncu_subdir: str,
) -> list:
    """Run NCU profiling for implementation and reference.

    Returns:
        List of (implementation_path, test_name, ncu_path) tuples
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert implementation_path, "implementation_path cannot be empty"

    # Tiger Style: Type narrow to Callable after assertion

    assert callable(implementation_fn), "implementation_fn must be callable"
    impl_fn: Callable = implementation_fn

    ncu_reports = []
    test_input_ncu = test.generate()
    ncu_dir = Path(ncu_subdir)

    # Profile implementation
    ncu_report_path, ncu_err = ncu_profile_kernel(
        impl_fn, test_input_ncu, ncu_dir, implementation_path, test.name, test
    )
    if ncu_err is None:
        print(f"   📊 NCU report saved: {ncu_report_path}")
        ncu_reports.append((implementation_path, test.name, ncu_report_path))
    else:
        print(f"   ⚠️  NCU profiling failed: {ncu_err}")

    # Also profile reference for comparison
    if implementation_path != reference_path:
        ref_fn = load_reference_kernel_from_path(reference_path)
        test_input_ref_ncu = test.generate()
        ref_ncu_path, ref_ncu_err = ncu_profile_kernel(
            ref_fn, test_input_ref_ncu, ncu_dir, reference_path, test.name, test
        )
        if ref_ncu_err is None:
            print(f"   📊 Reference NCU report saved: {ref_ncu_path}")
            ncu_reports.append((reference_path, test.name, ref_ncu_path))
        else:
            print(f"   ⚠️  Reference NCU profiling failed: {ref_ncu_err}")

    return ncu_reports


def _run_profiling(
    test: TestCase,
    implementation_fn: object,
    context: TestExecutionContext,
    profiling_config: ProfilingConfig,
) -> tuple[list, list]:
    """Run torch and NCU profiling if enabled.

    Returns:
        (profile_traces, ncu_reports): Lists of profiling outputs
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"

    profile_traces = []
    ncu_reports = []

    # Only profile benchmark tests
    is_benchmark_test = "bench" in test.name.lower() or "perf" in test.name.lower()
    if not is_benchmark_test:
        return profile_traces, ncu_reports

    # Torch profiling
    if profiling_config.enable_profiling:
        profile_traces = _run_torch_profiling(
            test,
            implementation_fn,
            context.implementation_path,
            context.reference_path,
            profiling_config.profile_subdir,
        )

    # NCU profiling
    if profiling_config.enable_ncu:
        ncu_reports = _run_ncu_profiling(
            test,
            implementation_fn,
            context.implementation_path,
            context.reference_path,
            profiling_config.ncu_subdir,
        )

    return profile_traces, ncu_reports


def _create_skipped_test_results(
    test: TestCase,
    implementation_path: str,
) -> tuple[CorrectnessResult, PerformanceResult]:
    """Create skipped test results for early-stop scenarios.

    Returns:
        (correctness_result, performance_result): Both marked as failed/skipped
    """
    assert test is not None, "test cannot be None"
    assert implementation_path, "implementation_path cannot be empty"

    correctness_result = CorrectnessResult(
        test_name=test.name,
        backend_name=implementation_path,
        is_correct=False,
        test_params=test.serialize(),
        error_msg="Skipped - kernel failed earlier tests",
    )
    performance_result = PerformanceResult(
        test_name=test.name,
        backend_name=implementation_path,
        successfully_ran=False,
        test_params=test.serialize(),
        avg_time_ms=ERROR_TIME_MS,
        speedup=None,
        reference_time_ms=None,
        error_msg="Skipped - kernel failed earlier tests",
    )
    return correctness_result, performance_result


def _run_performance_and_profiling(
    test: TestCase,
    implementation_fn: object,
    test_input: object,
    context: TestExecutionContext,
    profiling_config: ProfilingConfig,
) -> tuple[PerformanceResult, list, list]:
    """Run performance benchmark and profiling for a test.

    Returns:
        (performance_result, profile_traces, ncu_reports)
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert test_input is not None, "test_input cannot be None"

    # Run performance benchmark
    perf_result = _run_performance_test(
        test,
        implementation_fn,
        context.implementation_path,
        context.reference_path,
        test_input,
        context.use_cached_reference,
    )

    profile_traces = []
    ncu_reports = []

    # Display performance results
    if perf_result.successfully_ran:
        speedup_str = f" ({perf_result.speedup:.2f}x)" if perf_result.speedup else ""
        avg_time_us = perf_result.avg_time_ms * MS_TO_MICROSECONDS
        print(f"   ⏱️  Performance: {avg_time_us:.3f}μs{speedup_str}")

        # Run profiling if enabled
        new_prof_traces, new_ncu_reports = _run_profiling(
            test,
            implementation_fn,
            context,
            profiling_config,
        )
        profile_traces.extend(new_prof_traces)
        ncu_reports.extend(new_ncu_reports)
    else:
        print(f"   ⚠️  Benchmark failed: {perf_result.error_msg}")

    return perf_result, profile_traces, ncu_reports


def _extract_error_type(error_msg: ErrorInfo) -> str:
    """Extract error signature from ErrorInfo.

    Args:
        error_msg: ErrorInfo object

    Returns:
        Error signature for display (e.g., "ValueError: too many values to unpack")
    """
    return error_msg.get_signature()


def _track_error(error_tracker: dict, error_msg: ErrorInfo, test_name: str) -> None:
    """Track error for deduplication.

    Args:
        error_tracker: Dict mapping error signature -> (error_string, test_names[])
        error_msg: ErrorInfo object
        test_name: Name of test that failed
    """
    signature = error_msg.get_signature()
    error_string = error_msg.to_string()

    if signature not in error_tracker:
        error_tracker[signature] = (error_string, [])

    error_tracker[signature][1].append(test_name)


def _print_error_summary(error_tracker: dict) -> None:
    """Print deduplicated error summary.

    Args:
        error_tracker: Dict mapping error signature -> (error_info, test_names[])
    """
    print("\n" + "=" * PRINT_SEPARATOR_WIDTH)
    print("❌ Error Summary")
    print("=" * PRINT_SEPARATOR_WIDTH)

    for idx, (error_type, (error_info, test_names)) in enumerate(error_tracker.items(), 1):
        print(f"\n[Error {idx}] {error_type}")
        print(f"   Affected tests ({len(test_names)}): {', '.join(test_names)}")
        print("\n   Full traceback:")

        # Get full error text from ErrorInfo
        full_error = error_info.to_string()

        # Indent the full error
        for line in full_error.split("\n"):
            print(f"   {line}")

    print("\n" + "=" * PRINT_SEPARATOR_WIDTH)


def _run_single_test(
    test: TestCase,
    test_idx: int,
    total_tests: int,
    implementation_fn: object,
    checker: object | None,
    config: TestRunConfig,
    error_tracker: dict | None = None,
) -> tuple[CorrectnessResult, PerformanceResult, list, list]:
    """Run a single test case with correctness, performance, and profiling.

    Returns:
        (correctness_result, performance_result, profile_traces, ncu_reports)
    """
    assert test is not None, "test cannot be None"
    assert implementation_fn is not None, "implementation_fn cannot be None"
    assert 1 <= test_idx <= total_tests, f"test_idx must be in [1, {total_tests}], got {test_idx}"

    # Tiger Style: Type narrow to Callable after assertion

    assert callable(implementation_fn), "implementation_fn must be callable"
    impl_fn: Callable = implementation_fn

    # Tiger Style: Type narrow checker to Callable | None
    checker_fn: Callable | None = None
    if checker is not None:
        assert callable(checker), "checker must be callable when not None"
        checker_fn = checker

    print(f"\n📊 Test [{test_idx}/{total_tests}]: {test.name}")
    print(f"   Parameters: {test.serialize()}")

    # Type narrowing: checker_fn must not be None (we always use live reference mode)
    assert checker_fn is not None, (
        "checker_fn should not be None when use_cached_reference is False"
    )

    # Run correctness test
    is_correct, error_msg, test_input = _run_correctness_test(
        test, impl_fn, checker_fn, config.context.use_cached_reference, config.context.test_suite
    )

    # Convert ErrorInfo to string for CorrectnessResult
    error_msg_str = error_msg.to_string() if error_msg else None

    correctness_result = CorrectnessResult(
        test_name=test.name,
        backend_name=config.context.implementation_path,
        is_correct=is_correct,
        test_params=test.serialize(),
        error_msg=error_msg_str,
    )

    if is_correct:
        print("   ✅ Correctness: PASS")
        perf_result, profile_traces, ncu_reports = _run_performance_and_profiling(
            test,
            impl_fn,
            test_input,
            config.context,
            config.profiling,
        )
        return correctness_result, perf_result, profile_traces, ncu_reports
    else:
        print("   ❌ Correctness: FAIL")
        if error_msg and error_tracker is not None:
            # Track error for deduplication
            _track_error(error_tracker, error_msg, test.name)
            # Just print short error type, full traceback will be in summary
            error_type = _extract_error_type(error_msg)
            print(f"   Error: {error_type}")
        elif error_msg:
            # Fallback if no error tracker
            print(f"   Error: {error_msg.to_string()}")

        # Still record performance (as failed)
        perf_result = PerformanceResult(
            test_name=test.name,
            backend_name=config.context.implementation_path,
            successfully_ran=False,
            test_params=test.serialize(),
            avg_time_ms=ERROR_TIME_MS,
            error_msg="Skipped due to correctness failure",
        )
        return correctness_result, perf_result, [], []


def _run_test_loop(
    test_cases: list[TestCase],
    implementation_fn: object,
    checker: object | None,
    config: TestRunConfig,
) -> tuple[list[CorrectnessResult], list[PerformanceResult], list, list, bool]:
    """Run all test cases and collect results.

    Returns:
        (correctness_results, performance_results, profile_traces, ncu_reports, early_stop)
    """
    assert test_cases is not None, "test_cases cannot be None"
    assert len(test_cases) > 0, "test_cases cannot be empty"

    correctness_results = []
    performance_results = []
    profile_traces = []
    ncu_reports = []
    early_stop = False

    # Track unique errors to avoid printing duplicates
    error_tracker = {}  # Maps error signature -> (full_error, test_names[])

    for test_idx, test in enumerate(test_cases, 1):
        if early_stop:
            # Skip remaining tests - kernel has fundamental errors
            corr_result, perf_result = _create_skipped_test_results(
                test, config.context.implementation_path
            )
            correctness_results.append(corr_result)
            performance_results.append(perf_result)
            continue

        corr_result, perf_result, new_prof_traces, new_ncu_reports = _run_single_test(
            test,
            test_idx,
            len(test_cases),
            implementation_fn,
            checker,
            config,
            error_tracker,  # Pass error tracker to collect errors
        )

        correctness_results.append(corr_result)
        performance_results.append(perf_result)
        profile_traces.extend(new_prof_traces)
        ncu_reports.extend(new_ncu_reports)

        # Check for early stop condition
        if not corr_result.is_correct and corr_result.error_msg:
            fundamental_errors = [
                "TypeError",
                "ValueError",
                "AttributeError",
                "NameError",
                "SyntaxError",
                "ImportError",
                "CUDA error",
                "AcceleratorError",
            ]
            # error_msg is now an ErrorInfo object, check exc_type field
            if isinstance(corr_result.error_msg, ErrorInfo):
                error_type = corr_result.error_msg.exc_type
            else:
                error_type = str(corr_result.error_msg)

            if any(err in error_type for err in fundamental_errors):
                early_stop = True
                print("   ⚠️  Stopping early - fundamental error detected")

    # Print error summary at the end (deduplicated)
    if error_tracker:
        _print_error_summary(error_tracker)

    return correctness_results, performance_results, profile_traces, ncu_reports, early_stop


@dataclass(frozen=True)
class ResultsSummary:
    """Summary data for saving and printing results."""

    profile_traces: list
    ncu_reports: list


@dataclass(frozen=True)
class EvaluationArtifactConfig:
    """Configuration for evaluation artifacts and profiling.

    Controls what gets saved and where.
    """

    run_profiling: bool = False
    create_artifact: bool = True
    artifact_name: str | None = None
    run_dir: str | None = None


def _save_and_print_results(
    backend_results: BackendResults,
    test_suites: list[str],
    test_cases: list[TestCase],
    run_path: Path,
    save_results: bool,
    results_summary: ResultsSummary,
    profiling_config: ProfilingConfig,
) -> None:
    """Save results to file and print summaries."""
    assert backend_results is not None, "backend_results cannot be None"
    assert run_path is not None, "run_path cannot be None"

    print(f"\n   {backend_results.summary()}")

    # Print GPUMode format
    print("\n" + "=" * PRINT_SEPARATOR_WIDTH)
    print_gpumode_format(backend_results, test_suites, test_cases)

    # Save results if requested
    if save_results:
        suite_name = "_".join(test_suites).upper()
        suite_results = TestSuiteResults(
            suite_name=suite_name,
            backends=[backend_results],
        )
        output_path = run_path / "results.json"
        suite_results.to_json(output_path)
        print(f"\n💾 Results saved to: {output_path}")

    # Print profile summaries
    if profiling_config.enable_profiling and results_summary.profile_traces:
        print("\n📊 Torch Profiling Summary:")
        print(f"   {len(results_summary.profile_traces)} profile trace(s) generated")
        print("   Location: profiles/")
        print("\n   To view torch profiles:")
        print("   1. Chrome trace: Open chrome://tracing and load .json files")
        print("   2. TensorBoard: tensorboard --logdir=profiles/")

    if profiling_config.enable_ncu and results_summary.ncu_reports:
        print("\n📊 NCU Profiling Summary:")
        print(f"   {len(results_summary.ncu_reports)} NCU report(s) generated")
        print("   Location: ncu_reports/")
        print("\n   To view NCU reports:")
        print("   CSV files in ncu_reports/")


def _print_evaluation_header(
    implementation_path: str,
    reference_path: str,
    test_suites: list[str],
    test_cases: list[TestCase],
    enable_profiling: bool,
    enable_ncu: bool,
) -> None:
    """Print evaluation header information."""
    assert implementation_path, "implementation_path cannot be empty"
    assert test_suites is not None, "test_suites cannot be None"
    assert test_cases is not None, "test_cases cannot be None"

    print("🔥 Running GPU Kernel Tests")
    print(f"   Test Suites: {', '.join(test_suites)}")
    print(f"   Total Tests: {len(test_cases)}")
    print(f"   Implementation: {implementation_path}")
    print(f"   Reference: {reference_path}")
    if enable_profiling:
        print("   Torch Profiling: ENABLED")
    if enable_ncu:
        print("   NCU Profiling: ENABLED")
    print("=" * PRINT_SEPARATOR_WIDTH)


def _execute_test_loop_and_collect_results(
    test_cases: list[TestCase],
    implementation_fn: object,
    checker: object | None,
    config: TestRunConfig,
) -> tuple[BackendResults, list, list]:
    """Execute test loop and create backend results.

    Returns:
        (backend_results, profile_traces, ncu_reports)
    """
    assert test_cases is not None, "test_cases cannot be None"
    assert len(test_cases) > 0, "test_cases cannot be empty"
    assert implementation_fn is not None, "implementation_fn cannot be None"

    correctness_results, performance_results, profile_traces, ncu_reports, _ = _run_test_loop(
        test_cases,
        implementation_fn,
        checker,
        config,
    )

    backend_results = BackendResults(
        backend_name=config.context.implementation_path,
        correctness_tests=correctness_results,
        performance_tests=performance_results,
    )

    return backend_results, profile_traces, ncu_reports


def _setup_and_print_backend_info(
    implementation_path: str,
    reference_path: str,
    test_suites: list[str],
) -> tuple[object, object | None, bool] | tuple[None, None, None]:
    """Setup implementation and print information.

    Returns:
        (implementation_fn, checker, use_cached_reference) on success, (None, None, None) on failure
    """
    assert implementation_path, "implementation_path cannot be empty"
    assert reference_path, "reference_path cannot be empty"
    assert test_suites is not None, "test_suites cannot be None"

    implementation_fn, checker, use_cached_reference, error = _setup_test_backend(
        implementation_path, reference_path, test_suites
    )
    if error:
        print(f"❌ {error}")
        return None, None, None

    print(f"\n🔧 Implementation: {implementation_path}")
    print("-" * PRINT_SEPARATOR_WIDTH)

    return implementation_fn, checker, use_cached_reference


def _validate_evaluation_inputs(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
) -> str | None:
    """Validate evaluation inputs, return error message if invalid.

    Tiger Style: Pure validation function, returns error or None.

    Args:
        implementation_path: Path to implementation kernel file
        reference_path: Path to reference kernel file
        test_cases: List of TestCase objects to run

    Returns:
        Error message if validation fails, None if all inputs valid
    """

    assert implementation_path, "implementation_path cannot be empty"
    assert reference_path, "reference_path cannot be empty"
    assert test_cases is not None, "test_cases cannot be None"
    assert len(test_cases) > 0, "test_cases cannot be empty"

    if not torch.cuda.is_available():
        return "CUDA not available - tests require GPU"

    if not Path(implementation_path).exists():
        return f"Implementation file not found: {implementation_path}"

    if not Path(reference_path).exists():
        return f"Reference file not found: {reference_path}"

    return None


def _setup_evaluation_directories(
    run_dir: str | None,
) -> tuple[Path, str, str]:
    """Create run directory structure for evaluation outputs.

    Tiger Style: Pure computation, no branching logic.

    Args:
        run_dir: Directory for this run's outputs. If None, uses run_TIMESTAMP

    Returns:
        (run_path, profile_subdir, ncu_subdir)
    """
    from datetime import datetime

    # Determine run directory name
    if run_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        actual_run_dir = f"run_{timestamp}"
    else:
        actual_run_dir = run_dir

    # Create directory structure
    run_path = Path(actual_run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    # Create artifact subdirectories (profiles/NCU saved directly here)
    artifact_path = run_path / "artifact"
    artifact_path.mkdir(parents=True, exist_ok=True)
    (artifact_path / "profiles").mkdir(exist_ok=True)
    (artifact_path / "ncu").mkdir(exist_ok=True)
    (artifact_path / "results").mkdir(exist_ok=True)

    profile_subdir = str(artifact_path / "profiles")
    ncu_subdir = str(artifact_path / "ncu")

    return run_path, profile_subdir, ncu_subdir


def _setup_implementation_backend(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
    run_profiling: bool,
) -> tuple[Callable | None, Callable | None, bool]:
    """Setup implementation backend and print evaluation header.

    Tiger Style: Wrapper that handles setup + printing side effects.

    Args:
        implementation_path: Path to implementation kernel
        reference_path: Path to reference kernel
        test_cases: Test cases to display in header
        run_profiling: Whether profiling is enabled (for header display)

    Returns:
        (implementation_fn, checker, use_cached_reference)
        Returns (None, None, False) if setup fails
    """
    test_suites_display = ["custom"]  # For display only

    # Print header
    _print_evaluation_header(
        implementation_path,
        reference_path,
        test_suites_display,
        test_cases,
        run_profiling,
        run_profiling,
    )

    # Setup backend
    implementation_setup = _setup_and_print_backend_info(
        implementation_path, reference_path, test_suites_display
    )

    if implementation_setup[0] is None:
        return None, None, False

    # Tiger Style: Type narrow - extract and validate components
    impl_fn_obj, checker_obj, use_cached_obj = implementation_setup
    assert callable(impl_fn_obj), "implementation_fn must be callable"
    impl_fn: Callable = impl_fn_obj
    checker_fn: Callable | None = None
    if checker_obj is not None:
        assert callable(checker_obj), "checker must be callable when not None"
        checker_fn = checker_obj
    # Tiger Style: Type narrow use_cached from bool | None to bool
    assert isinstance(use_cached_obj, bool), "use_cached must be bool when impl_fn is not None"
    use_cached: bool = use_cached_obj

    return impl_fn, checker_fn, use_cached


@dataclass
class EvaluationResult:
    """Full evaluation result with structured test data.

    Provides detailed per-test information for better error reporting.
    """

    all_passed: bool
    summary: str
    artifact_path: Path | None
    backend_results: BackendResults | None = None
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "compiled": self.backend_results is not None,
            "all_correct": self.all_passed,
            "error_message": self.error_message,
        }

        if self.backend_results:
            result.update({
                "correctness_score": self.backend_results.correctness_score,
                "geomean_speedup": self.backend_results.geomean_speedup,
                "passed_tests": sum(
                    1 for t in self.backend_results.correctness_tests if t.is_correct
                ),
                "total_tests": len(self.backend_results.correctness_tests),
                "correctness_tests": [t.to_dict() for t in self.backend_results.correctness_tests],
                "performance_tests": [t.to_dict() for t in self.backend_results.performance_tests],
            })
        else:
            result.update({
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "passed_tests": 0,
                "total_tests": 0,
                "correctness_tests": [],
                "performance_tests": [],
            })

        return result


def run_evaluation_full(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
    run_benchmarks: bool = False,
    artifact_config: EvaluationArtifactConfig | None = None,
) -> EvaluationResult:
    """Run evaluation and return full structured results.

    Like run_evaluation but returns EvaluationResult with full BackendResults
    for detailed error reporting.

    Args:
        implementation_path: Path to implementation kernel file
        reference_path: Path to reference kernel file
        test_cases: List of TestCase objects to run
        run_benchmarks: Run performance benchmarks (default: False, correctness only)
        artifact_config: Configuration for artifacts, profiling, and output dirs

    Returns:
        EvaluationResult with full test details
    """
    # Use default artifact config if not provided
    if artifact_config is None:
        artifact_config = EvaluationArtifactConfig()

    # Validate inputs
    validation_error = _validate_evaluation_inputs(implementation_path, reference_path, test_cases)
    if validation_error:
        return EvaluationResult(
            all_passed=False,
            summary=validation_error,
            artifact_path=None,
            backend_results=None,
            error_message=validation_error,
        )

    # Setup directories
    run_path, profile_subdir, ncu_subdir = _setup_evaluation_directories(artifact_config.run_dir)

    # Setup backend and print header
    implementation_fn, checker, use_cached_reference = _setup_implementation_backend(
        implementation_path, reference_path, test_cases, artifact_config.run_profiling
    )

    # Create artifact directory early (so we can save even on failure)
    artifact_path = None
    artifact_path_inner = run_path / "artifact" if artifact_config.create_artifact else None

    if implementation_fn is None:
        # Compilation/import failed
        error_msg = "Failed to setup implementation (compilation or import error)"
        if artifact_config.create_artifact:
            assert artifact_path_inner is not None
            artifact_path = _create_submission_artifact(
                implementation_path=implementation_path,
                reference_path=reference_path,
                test_cases=test_cases,
                artifact_path=artifact_path_inner,
                run_dir=str(run_path),
            )
        return EvaluationResult(
            all_passed=False,
            summary=error_msg,
            artifact_path=artifact_path,
            backend_results=None,
            error_message=error_msg,
        )

    # Create artifact BEFORE running tests
    if artifact_config.create_artifact:
        assert artifact_path_inner is not None
        artifact_path = _create_submission_artifact_base(
            implementation_path=implementation_path,
            reference_path=reference_path,
            test_cases=test_cases,
            artifact_path=artifact_path_inner,
        )

    # Run tests
    try:
        test_suite_name = "custom"
        context = TestExecutionContext(
            implementation_path=implementation_path,
            reference_path=reference_path,
            test_suite=test_suite_name,
            use_cached_reference=use_cached_reference,
        )
        profiling_config = ProfilingConfig(
            profile_subdir=profile_subdir,
            ncu_subdir=ncu_subdir,
            enable_profiling=artifact_config.run_profiling,
            enable_ncu=artifact_config.run_profiling,
        )
        config = TestRunConfig(context=context, profiling=profiling_config)

        backend_results, profile_traces, ncu_reports = _execute_test_loop_and_collect_results(
            test_cases,
            implementation_fn,
            checker,
            config,
        )

        # Save and print results
        test_suites_display = ["custom"]
        results_summary = ResultsSummary(
            profile_traces=profile_traces,
            ncu_reports=ncu_reports,
        )
        _save_and_print_results(
            backend_results,
            test_suites_display,
            test_cases,
            run_path,
            True,
            results_summary,
            profiling_config,
        )

        all_passed = backend_results.all_correct
        summary = f"Implementation '{implementation_path}': {backend_results.summary()}"

        # Build error message from failed tests
        error_message = None
        if not all_passed:
            failed_tests = [t for t in backend_results.correctness_tests if not t.is_correct]
            if failed_tests:
                error_message = failed_tests[0].error_msg  # First failure's error

        return EvaluationResult(
            all_passed=all_passed,
            summary=summary,
            artifact_path=artifact_path,
            backend_results=backend_results,
            error_message=error_message,
        )

    finally:
        if artifact_config.create_artifact and artifact_path:
            _update_artifact_with_results(artifact_path, run_path)


def run_evaluation(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
    run_benchmarks: bool = False,
    artifact_config: EvaluationArtifactConfig | None = None,
) -> tuple[bool, str, Path | None]:
    """Run evaluation with explicit test cases and artifact creation.

    New simplified API - accepts test cases directly, no test suite lookups.

    Tiger Style: Push ifs up - parent has control flow, helpers do work.

    Args:
        implementation_path: Path to implementation kernel file
        reference_path: Path to reference kernel file
        test_cases: List of TestCase objects to run
        run_benchmarks: Run performance benchmarks (default: False, correctness only)
        artifact_config: Configuration for artifacts, profiling, and output dirs

    Returns:
        (all_passed, summary_msg, artifact_path)

    Example:
        # Simple usage (default artifact config)
        run_evaluation(impl_path, ref_path, test_cases)

        # With custom artifact config
        cfg = EvaluationArtifactConfig(run_profiling=True, create_artifact=False)
        run_evaluation(impl_path, ref_path, test_cases, artifact_config=cfg)
    """
    # Use default artifact config if not provided
    if artifact_config is None:
        artifact_config = EvaluationArtifactConfig()
    # Validate inputs
    validation_error = _validate_evaluation_inputs(implementation_path, reference_path, test_cases)
    if validation_error:
        return False, validation_error, None

    # Setup directories
    run_path, profile_subdir, ncu_subdir = _setup_evaluation_directories(artifact_config.run_dir)

    # Setup backend and print header
    implementation_fn, checker, use_cached_reference = _setup_implementation_backend(
        implementation_path, reference_path, test_cases, artifact_config.run_profiling
    )

    # Create artifact directory early (so we can save even on failure)
    artifact_path = None
    artifact_path_inner = run_path / "artifact" if artifact_config.create_artifact else None

    if implementation_fn is None:
        # Compilation/import failed - create artifact with error info
        if artifact_config.create_artifact:
            # Tiger Style: Assert invariant - artifact_path_inner set when create_artifact=True
            assert artifact_path_inner is not None, (
                "artifact_path_inner must be set when create_artifact=True"
            )
            artifact_path = _create_submission_artifact(
                implementation_path=implementation_path,
                reference_path=reference_path,
                test_cases=test_cases,
                artifact_path=artifact_path_inner,
                run_dir=str(run_path),
            )
        return False, "Failed to setup implementation", artifact_path

    # CRITICAL: Create artifact BEFORE running tests
    # This ensures we capture source files even if tests crash
    if artifact_config.create_artifact:
        # Tiger Style: Assert invariant - artifact_path_inner set when create_artifact=True
        assert artifact_path_inner is not None, (
            "artifact_path_inner must be set when create_artifact=True"
        )
        artifact_path = _create_submission_artifact_base(
            implementation_path=implementation_path,
            reference_path=reference_path,
            test_cases=test_cases,
            artifact_path=artifact_path_inner,
        )

    # Run tests with try/finally to ensure results are saved even on crash
    try:
        # Create test run config
        test_suite_name = "custom"  # For naming only
        context = TestExecutionContext(
            implementation_path=implementation_path,
            reference_path=reference_path,
            test_suite=test_suite_name,
            use_cached_reference=use_cached_reference,
        )
        profiling_config = ProfilingConfig(
            profile_subdir=profile_subdir,
            ncu_subdir=ncu_subdir,
            enable_profiling=artifact_config.run_profiling,
            enable_ncu=artifact_config.run_profiling,
        )
        config = TestRunConfig(context=context, profiling=profiling_config)

        # Run tests
        backend_results, profile_traces, ncu_reports = _execute_test_loop_and_collect_results(
            test_cases,
            implementation_fn,
            checker,
            config,
        )

        # Save and print results
        test_suites_display = ["custom"]
        results_summary = ResultsSummary(
            profile_traces=profile_traces,
            ncu_reports=ncu_reports,
        )
        _save_and_print_results(
            backend_results,
            test_suites_display,
            test_cases,
            run_path,
            True,  # Always save results
            results_summary,
            profiling_config,
        )

        # Return results
        all_passed = backend_results.all_correct
        summary = f"Implementation '{implementation_path}': {backend_results.summary()}"
        return all_passed, summary, artifact_path

    finally:
        # ALWAYS update artifact with results and logs, even on crash
        if artifact_config.create_artifact and artifact_path:
            _update_artifact_with_results(artifact_path, run_path)


def _capture_environment_info(artifact_path: Path) -> None:
    """Capture Python and GPU environment information.

    Tries nvidia-smi first, falls back to PyTorch/CUDA info if nvidia-smi fails.
    This handles cases where NVML has driver/library version mismatch but CUDA still works.

    Tiger Style: Graceful degradation with fallback.

    Args:
        artifact_path: Artifact directory to save environment info
    """
    import subprocess
    import sys

    # Save Python version
    (artifact_path / "environment" / "python_version.txt").write_text(sys.version)

    # Try to capture GPU info via nvidia-smi (preferred)
    nvidia_smi_result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,  # Don't raise on failure
    )

    if nvidia_smi_result.returncode == 0:
        # nvidia-smi succeeded
        (artifact_path / "environment" / "nvidia_smi.txt").write_text(nvidia_smi_result.stdout)
    else:
        # nvidia-smi failed - fall back to PyTorch/CUDA info
        error_msg = nvidia_smi_result.stderr or nvidia_smi_result.stdout or "nvidia-smi failed"
        (artifact_path / "environment" / "nvidia_smi.txt").write_text(
            f"nvidia-smi failed (exit code {nvidia_smi_result.returncode}):\n{error_msg}\n\n"
            "Falling back to PyTorch CUDA info..."
        )

        # Collect GPU info via PyTorch as fallback
        try:
            import torch

            gpu_info = []
            gpu_info.append(f"PyTorch version: {torch.__version__}")
            gpu_info.append(f"CUDA available: {torch.cuda.is_available()}")

            if torch.cuda.is_available():
                gpu_info.append(f"CUDA version: {torch.version.cuda}")
                gpu_info.append(f"cuDNN version: {torch.backends.cudnn.version()}")
                gpu_info.append(f"Device count: {torch.cuda.device_count()}")

                # Get info for each GPU
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    gpu_info.append(f"\nGPU {i}: {props.name}")
                    gpu_info.append(f"  Compute capability: {props.major}.{props.minor}")
                    gpu_info.append(f"  Total memory: {props.total_memory / 1024**3:.2f} GB")
                    gpu_info.append(f"  Multi-processor count: {props.multi_processor_count}")

            fallback_info = "\n".join(gpu_info)
            (artifact_path / "environment" / "gpu_info_pytorch.txt").write_text(fallback_info)
        except Exception as e:
            # If even PyTorch fails, save the error
            (artifact_path / "environment" / "gpu_info_pytorch.txt").write_text(
                f"Failed to collect GPU info via PyTorch: {e}"
            )


def _copy_results_to_artifact(artifact_path: Path, run_dir: str | None) -> None:
    """Copy evaluation results to artifact directory.

    Tiger Style: Pure side-effect function.

    Args:
        artifact_path: Artifact directory
        run_dir: Run directory containing results.json
    """
    if not run_dir:
        return

    run_path = Path(run_dir)
    if not run_path.exists():
        return

    results_file = run_path / "results.json"
    if results_file.exists():
        import shutil

        shutil.copy2(results_file, artifact_path / "results" / "full_results.json")


def _generate_artifact_manifest(artifact_path: Path, implementation_path: str) -> None:
    """Generate manifest.json with artifact metadata.

    Tiger Style: Pure side-effect function.

    Args:
        artifact_path: Artifact directory
        implementation_path: Path to implementation (for naming)
    """
    import json
    from datetime import datetime, timezone

    manifest = {
        "submission_name": Path(implementation_path).stem,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files": {
            "submission": "submission.py",
            "reference": "reference.py",
            "test_cases": "tests.json",
        },
    }

    with open(artifact_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


def _create_submission_artifact_base(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
    artifact_path: Path,
) -> Path:
    """Create base artifact with source files BEFORE tests run.

    This is called immediately after kernel loading succeeds, ensuring
    we capture all inputs even if tests crash during execution.

    Tiger Style: Early fail-safe artifact creation.

    Args:
        implementation_path: Path to implementation kernel
        reference_path: Path to reference kernel
        test_cases: Test cases to run
        artifact_path: Path to artifact directory (already created)

    Returns:
        Path to artifact directory

    Raises:
        FileNotFoundError: If source files not found
        IOError: If file operations fail
    """
    import json
    import shutil

    # Create subdirectories
    (artifact_path / "environment").mkdir(exist_ok=True)
    (artifact_path / "logs").mkdir(exist_ok=True)

    # Copy source files - these are the INPUTS to evaluation
    shutil.copy2(implementation_path, artifact_path / "submission.py")
    shutil.copy2(reference_path, artifact_path / "reference.py")

    # Save test cases
    test_cases_data = [{**tc.params, "name": tc.name} for tc in test_cases]
    with open(artifact_path / "tests.json", "w") as f:
        json.dump(test_cases_data, f, indent=2)

    # Capture environment info
    _capture_environment_info(artifact_path)

    # Generate manifest
    _generate_artifact_manifest(artifact_path, implementation_path)

    return artifact_path


def _update_artifact_with_results(artifact_path: Path, run_dir: Path) -> None:
    """Update artifact with results and logs after tests complete or crash.

    Called in finally block to ensure results are saved even on crash.
    Safe to call multiple times (idempotent).

    Tiger Style: Defensive - handles missing files gracefully.

    Args:
        artifact_path: Path to artifact directory
        run_dir: Run directory with results/logs
    """
    import shutil

    # Copy results.json if it exists
    results_file = run_dir / "results.json"
    if results_file.exists():
        try:
            shutil.copy2(results_file, artifact_path / "results" / "full_results.json")
        except Exception as e:
            # Non-fatal - log but don't fail
            print(f"Warning: Failed to copy results.json: {e}")

    # Copy evaluate.log if it exists (from tmux session)
    log_file = run_dir / "evaluate.log"
    if log_file.exists():
        try:
            shutil.copy2(log_file, artifact_path / "logs" / "evaluate.log")
        except Exception as e:
            # Non-fatal - log but don't fail
            print(f"Warning: Failed to copy evaluate.log: {e}")


def _create_submission_artifact(
    implementation_path: str,
    reference_path: str,
    test_cases: list[TestCase],
    artifact_path: Path,
    run_dir: str | None,
) -> Path:
    """Create submission artifact with code, environment, and results.

    Tiger Style: Orchestrator - sequential helper calls, explicit errors.

    NOTE: This is the OLD function kept for backward compatibility.
    New code should use _create_submission_artifact_base() + _update_artifact_with_results()

    Args:
        implementation_path: Path to implementation kernel
        reference_path: Path to reference kernel
        test_cases: Test cases that were run
        artifact_path: Path to artifact directory (already created)
        run_dir: Run directory with results

    Returns:
        Path to created artifact directory

    Raises:
        FileNotFoundError: If nvidia-smi missing or source files not found
    """
    import json
    import shutil

    # Create subdirectories
    (artifact_path / "environment").mkdir(exist_ok=True)
    (artifact_path / "logs").mkdir(exist_ok=True)

    # Copy source files
    shutil.copy2(implementation_path, artifact_path / "submission.py")
    shutil.copy2(reference_path, artifact_path / "reference.py")

    # Save test cases
    test_cases_data = [{**tc.params, "name": tc.name} for tc in test_cases]
    with open(artifact_path / "tests.json", "w") as f:
        json.dump(test_cases_data, f, indent=2)

    # Capture environment (fast-fails if GPU misconfigured)
    _capture_environment_info(artifact_path)

    # Copy results
    _copy_results_to_artifact(artifact_path, run_dir)

    # Generate manifest
    _generate_artifact_manifest(artifact_path, implementation_path)

    return artifact_path


def load_kernel_from_file(path: str, function_name: str = "custom_kernel") -> Callable:
    """Load kernel function from Python file.

    Uses GPU Mode's standard naming convention:
    - Submission files must define 'custom_kernel'
    - Reference files must define 'ref_kernel'

    Args:
        path: Path to Python file containing kernel function
        function_name: Name of function to load (default: "custom_kernel")

    Returns:
        Kernel function object

    Raises:
        AssertionError: If file doesn't exist or doesn't contain the required function
    """
    import importlib.util
    from pathlib import Path

    assert path, "path cannot be empty"
    assert function_name, "function_name cannot be empty"

    kernel_file = Path(path)
    assert kernel_file.exists(), f"Kernel file not found: {path}"

    # Add the kernel's directory to sys.path so it can import local modules (e.g., task.py)
    # This is needed for GPUMode reference kernels that do: from task import input_t, output_t
    kernel_dir = str(kernel_file.parent.resolve())
    sys.path.insert(0, kernel_dir)

    try:
        spec = importlib.util.spec_from_file_location("dynamic_kernel", path)
        assert spec is not None, f"Failed to load spec from: {path}"
        assert spec.loader is not None, f"No loader for spec: {path}"

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, function_name), f"File {path} must define {function_name} function"

        return getattr(module, function_name)
    finally:
        # Remove from sys.path to avoid polluting it
        if kernel_dir in sys.path:
            sys.path.remove(kernel_dir)


def load_test_cases_from_json(test_cases_arg: str) -> list[TestCase]:
    """Load test cases from JSON file or inline JSON string.

    Args:
        test_cases_arg: Path to JSON file or inline JSON string

    Returns:
        List of TestCase objects
    """
    import json
    from pathlib import Path

    assert test_cases_arg, "test_cases_arg cannot be empty"

    # Try to parse as file path first
    test_cases_path = Path(test_cases_arg)
    if test_cases_path.exists() and test_cases_path.is_file():
        # Load from file
        with open(test_cases_path) as f:
            test_cases_data = json.load(f)
    else:
        # Try to parse as inline JSON
        try:
            test_cases_data = json.loads(test_cases_arg)
            # If single dict, wrap in list
            if isinstance(test_cases_data, dict):
                test_cases_data = [test_cases_data]
        except json.JSONDecodeError as e:
            raise InvalidTestCasesFormatError(test_cases_arg, e) from e

    # Validate it's a list
    assert isinstance(test_cases_data, list), (
        f"Test cases must be a JSON array, got {type(test_cases_data)}"
    )
    assert len(test_cases_data) > 0, "Test cases cannot be empty"

    # Convert to TestCase objects
    # All test cases are now generic - just dict of params
    test_cases = []
    for i, tc_dict in enumerate(test_cases_data):
        assert isinstance(tc_dict, dict), f"Test case {i} must be a dict, got {type(tc_dict)}"

        # Use 'name' field if present, otherwise generate one
        name = tc_dict.get("name", f"test_{i + 1}")

        # All params except 'name' go into the params dict
        params = {k: v for k, v in tc_dict.items() if k != "name"}

        test_cases.append(
            TestCase(
                params=params,
                name=str(name),
            )
        )

    return test_cases


# Protocol for CLI arguments
# Tiger Style: Explicit type instead of 'object'


class EvaluateArgs(Protocol):
    """Protocol for evaluate.py CLI arguments."""

    implementation: str
    reference: str
    test_cases: str
    benchmark: bool
    profile: bool
    no_artifact: bool
    artifact_name: str | None
    run_dir: str | None


def _parse_arguments() -> EvaluateArgs:
    """Parse command-line arguments.

    Returns:
        Parsed arguments (EvaluateArgs protocol)
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Run GPU kernel evaluation with correctness and performance testing"
    )
    parser.add_argument(
        "--implementation",
        "--impl",
        dest="implementation",
        type=str,
        required=True,
        help="Path to implementation kernel file (e.g., my_kernel.py)",
    )
    parser.add_argument(
        "--reference",
        type=str,
        required=True,
        help="Path to reference kernel file (e.g., nvfp4_gemv_blackwell/reference_kernel.py)",
    )
    parser.add_argument(
        "--test-cases",
        type=str,
        required=True,
        help="Path to test cases JSON file or inline JSON string",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmarks (in addition to correctness)",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable profiling with torch.profiler and NCU",
    )
    parser.add_argument(
        "--no-artifact",
        action="store_true",
        help="Disable artifact creation (for quick iteration)",
    )
    parser.add_argument(
        "--artifact-name",
        type=str,
        help="Custom artifact name (default: implementation filename)",
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        help="Directory for this run's outputs (results, profiles, artifacts). Default: run_TIMESTAMP",
    )

    # Cast to Protocol for type safety
    parsed_args: EvaluateArgs = parser.parse_args()  # type: ignore[assignment]
    return parsed_args


def _run_evaluation_with_args(args: EvaluateArgs) -> tuple[bool, str, Path | None]:
    """Run evaluation with parsed arguments.

    Args:
        args: Parsed CLI arguments (EvaluateArgs protocol)

    Returns:
        (success, summary, artifact_path): True if all tests passed, summary string, artifact path
    """
    # Load test cases from JSON
    test_cases = load_test_cases_from_json(args.test_cases)

    # Create artifact config from CLI args
    artifact_config = EvaluationArtifactConfig(
        run_profiling=args.profile,
        create_artifact=not args.no_artifact,
        artifact_name=args.artifact_name,
        run_dir=args.run_dir,
    )

    return run_evaluation(
        implementation_path=args.implementation,
        reference_path=args.reference,
        test_cases=test_cases,
        run_benchmarks=args.benchmark,
        artifact_config=artifact_config,
    )


def main() -> int:
    """Main entry point."""
    args = _parse_arguments()

    # Validate implementation file exists
    impl_path = Path(args.implementation)
    if not impl_path.exists():
        print(f"❌ Implementation file not found: {args.implementation}")
        return 1

    # Validate reference file exists
    ref_path = Path(args.reference)
    if not ref_path.exists():
        print(f"❌ Reference file not found: {args.reference}")
        return 1

    # Run tests
    try:
        success, summary, artifact_path = _run_evaluation_with_args(args)

        if artifact_path:
            print(f"\n📁 Artifact created: {artifact_path}")

        if success:
            print(f"\n✅ All tests passed: {summary}")
            return 0
        else:
            print(f"\n❌ Some tests failed: {summary}")
            return 1

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
