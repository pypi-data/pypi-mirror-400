"""Remote execution utilities for GPU benchmark environments.

Pure functions for setting up and running code on remote GPU servers.

Tiger Style:
- Pure functions (no hidden state)
- Explicit error handling
- Clear separation of concerns
"""

import logging
from dataclasses import replace
from pathlib import Path

from wafer_core.utils.execution_types import KernelExecutionContext, ProfilingArtifactConfig
from wafer_core.utils.kernel_utils.deployment import (
    DeploymentConfig,
    DeploymentState,
    TestKernelParams,
    setup_deployment,
    test_kernel,
)

logger = logging.getLogger(__name__)


async def setup_remote_deployment(
    ssh_target: str,
    ssh_key: str,
    gpu_id: int,
    benchmark_name: str,
    project_subdir: str | None = None,
    dataset_path: str | None = None,
    workspace_path: str = "~/.wafer/workspaces/wafer",
) -> tuple[DeploymentState | None, str | None]:
    """Setup remote GPU environment for code execution.

    Deploys codebase via bifrost and sets up venv.

    Args:
        ssh_target: SSH connection string (user@host:port)
        ssh_key: Path to SSH key file
        gpu_id: GPU ID to use
        benchmark_name: Benchmark name ("gpumode", "leetgpu", etc.)
        project_subdir: Optional project subdirectory (e.g., "benchmarks/leetgpu")
        dataset_path: Optional dataset path (e.g., "datasets/leetgpu_problems.jsonl")
        workspace_path: Remote workspace path

    Returns:
        Tuple of (deployment_state, error_message)
        - deployment_state: DeploymentState if successful, None on error
        - error_message: Error string if failed, None on success

    Example:
        >>> state, err = await setup_remote_deployment(
        ...     ssh_target="user@host:22",
        ...     ssh_key="~/.ssh/id_rsa",
        ...     gpu_id=0,
        ...     benchmark_name="gpumode",
        ... )
        >>> if err:
        ...     print(f"Setup failed: {err}")
        >>> else:
        ...     print("Deployment ready!")
    """
    # Build config
    # Tiger Style: Explicit parameters instead of kwargs dict
    # Add optional paths for benchmarks that need them (e.g., LeetGPU)
    # GPUMode doesn't use these - it relies on full wafer monorepo deployment
    if benchmark_name == "leetgpu" and project_subdir and dataset_path:
        config = DeploymentConfig(
            ssh_target=ssh_target,
            ssh_key=ssh_key,
            gpu_id=gpu_id,
            workspace_path=workspace_path,
            project_subdir=project_subdir,
            dataset_path=dataset_path,
        )
    else:
        # Use defaults for project_subdir and dataset_path
        config = DeploymentConfig(
            ssh_target=ssh_target,
            ssh_key=ssh_key,
            gpu_id=gpu_id,
            workspace_path=workspace_path,
        )

    # Setup deployment (logging happens in setup_deployment)
    state, err = await setup_deployment(config)

    if err:
        logger.error(f"deployment setup failed: {err}")
        return None, err

    return state, None


async def execute_kernel_remote(
    deployment_state: DeploymentState,
    kernel_code: str,
    context: KernelExecutionContext,
    profiling_config: ProfilingArtifactConfig | None = None,
) -> dict:
    """Execute kernel code on remote GPU with correctness and benchmark testing.

    Two-phase execution:
    1. Correctness tests (required)
    2. Benchmark tests (only if correctness passes)
    3. Optional profiling (if requested and benchmarks pass)

    Args:
        deployment_state: Remote deployment state
        kernel_code: Code to execute
        context: Execution context (problem, test suite, benchmark info)
        profiling_config: Configuration for profiling and artifact collection

    Returns:
        Dict with keys:
            - compiled: bool
            - error_message: str | None
            - correctness_score: float (0.0 to 1.0)
            - all_correct: bool
            - passed_tests: int
            - total_tests: int
            - geomean_speedup: float

    Example:
        >>> ctx = KernelExecutionContext(
        ...     problem_id="p1",
        ...     sample_data={...},
        ...     test_suite="correctness",
        ...     reference_backend="reference",
        ...     benchmark_name="gpumode",
        ...     benchmark_suite="benchmark",
        ... )
        >>> results = await execute_kernel_remote(
        ...     deployment_state=state,
        ...     kernel_code="def solve(A, B): return A + B",
        ...     context=ctx,
        ... )
        >>> if results["all_correct"]:
        ...     print(f"Speedup: {results['geomean_speedup']:.2f}x")
    """
    # Use default profiling config if not provided
    if profiling_config is None:
        profiling_config = ProfilingArtifactConfig()

    # Prepare problem_id (LeetGPU needs special formatting)
    formatted_problem_id = (
        f"challenge_{context.problem_id}" if context.benchmark_name == "leetgpu" else context.problem_id
    )

    # Build test_kernel params
    # Tiger Style: Explicit dataclass instead of kwargs dict
    test_params = TestKernelParams(
        state=deployment_state,
        kernel_code=kernel_code,
        backend_name="agent",
        test_suite=context.test_suite,
        reference_backend=context.reference_backend,
        problem_id=formatted_problem_id,
        sample_data=context.sample_data,
        profile=False,
        ncu=False,
        language_filter=context.language,  # None if not provided
        artifact_dir=str(profiling_config.artifacts_dir) if profiling_config.artifacts_dir else None,
    )

    # PHASE 1: Correctness tests
    logger.debug("   Running correctness tests...")
    results, err = await test_kernel(test_params)

    if err:
        return {
            "compiled": False,
            "error_message": err,
            "correctness_score": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
            "geomean_speedup": 0.0,
        }

    # If no error, results must be valid (test_kernel contract)
    assert results is not None, "test_kernel returned no error but results is None"

    # PHASE 2: Benchmark tests (only if correctness passes)
    if results.all_correct:
        logger.debug("   ✅ Correctness passed - running benchmarks...")

        # Switch to benchmark suite
        # Tiger Style: Create new immutable params instead of mutating dict
        benchmark_params = replace(test_params, test_suite=context.benchmark_suite)

        # Run benchmarks WITHOUT profiling first
        results_benchmark, err_benchmark = await test_kernel(benchmark_params)

        if not err_benchmark:
            assert results_benchmark is not None, "test_kernel returned no error but results is None"
            results = results_benchmark
            logger.debug(f"   📊 Benchmark speedup: {results.geomean_speedup:.2f}x")

            # PHASE 3: Optional profiling
            if profiling_config.profile_on_success or profiling_config.ncu_on_success:
                logger.debug(
                    f"   🔍 Running profiling: profile={profiling_config.profile_on_success}, ncu={profiling_config.ncu_on_success}"
                )

                # Create profiled version with new backend name and profiling flags
                profiled_params = replace(
                    benchmark_params,
                    backend_name="agent_profiled",
                    profile=profiling_config.profile_on_success,
                    ncu=profiling_config.ncu_on_success,
                )

                _, err_profile = await test_kernel(profiled_params)

                if not err_profile:
                    logger.debug("   ✅ Profiling data collected")
                else:
                    logger.warning(f"   ⚠️  Profiling failed: {err_profile}")

    # Convert TestResults to dict
    return {
        "compiled": True,
        "error_message": None,
        "correctness_score": results.correctness_score,
        "all_correct": results.all_correct,
        "passed_tests": (
            len([t for t in results.correctness_tests if t.get("is_correct", False)])
            if results.correctness_tests
            else 0
        ),
        "total_tests": len(results.correctness_tests) if results.correctness_tests else 0,
        "geomean_speedup": results.geomean_speedup,
    }


async def profile_kernel_ncu_remote(
    deployment_state: DeploymentState,
    kernel_code: str,
    context: KernelExecutionContext,
    artifacts_dir: Path | None = None,
) -> tuple[str | None, str | None]:
    """Run NCU profiling on a kernel remotely.

    Runs benchmark suite with NCU enabled and returns raw CSV content.
    The caller is responsible for saving/parsing the profile.

    Args:
        deployment_state: Remote deployment state
        kernel_code: Code to profile
        context: Execution context (problem, test suite, benchmark info)
        artifacts_dir: Directory to save artifacts

    Returns:
        (csv_content, error): Raw NCU CSV on success, error message on failure
    """
    # Prepare problem_id
    formatted_problem_id = (
        f"challenge_{context.problem_id}" if context.benchmark_name == "leetgpu" else context.problem_id
    )

    # Build test_kernel params with NCU enabled
    test_params = TestKernelParams(
        state=deployment_state,
        kernel_code=kernel_code,
        backend_name="agent_ncu",
        test_suite=context.benchmark_suite,  # Use benchmark suite for profiling
        reference_backend=context.reference_backend,
        problem_id=formatted_problem_id,
        sample_data=context.sample_data,
        profile=False,
        ncu=True,  # Enable NCU
        language_filter=context.language,
        artifact_dir=str(artifacts_dir) if artifacts_dir else None,
    )

    logger.debug("   🔍 Running NCU profiling...")
    _, err = await test_kernel(test_params)

    if err:
        return None, f"NCU profiling failed: {err}"

    # Find and read the NCU CSV file
    if artifacts_dir is None:
        return None, "No artifacts directory configured - cannot retrieve NCU results"

    # Simple recursive search for any NCU CSV files
    csv_files = list(artifacts_dir.rglob("*_ncu.csv"))
    if not csv_files:
        return None, f"No NCU CSV files found in {artifacts_dir}"

    # Get the most recent CSV (sort by modification time)
    csv_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    csv_path = csv_files[0]

    try:
        csv_content = csv_path.read_text()
    except Exception as e:
        return None, f"Failed to read NCU CSV {csv_path}: {e}"
    else:
        logger.info(f"📊 Read NCU data from: {csv_path.name}")
        return csv_content, None


def wrap_code_with_function(code: str, wrapper_fn: str = "custom_kernel") -> str:
    """Wrap code block in a function wrapper.

    Used by LeetGPU to wrap solve() function into custom_kernel() interface.

    Args:
        code: Original code to wrap
        wrapper_fn: Name of wrapper function

    Returns:
        Code with wrapper appended

    Example:
        >>> code = "def solve(A, B, C, N): return A + B"
        >>> wrapped = wrap_code_with_function(code)
        >>> assert "def custom_kernel" in wrapped
    """
    return f"""{code}

# Wrapper to match GPUMode interface ({wrapper_fn})
def {wrapper_fn}(data):
    \"\"\"Wrapper that unpacks tuple and calls agent's solve() function.\"\"\"
    A, B, C, N, language = data
    return solve(A, B, C, N)
"""
