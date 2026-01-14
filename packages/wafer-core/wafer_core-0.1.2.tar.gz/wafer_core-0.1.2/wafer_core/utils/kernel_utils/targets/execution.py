"""Execution wrapper for running operations on pluggable targets.

Tiger Style:
- Pure functions where possible
- Explicit error handling (tuple returns)
- Thin wrapper around existing deployment.py

Key functions:
- find_free_gpu(): Try GPUs in order until finding free one
- check_target_available(): Check if target has any free GPUs
- run_operation_on_target(): Execute operation on selected target (TODO: Phase 4)
"""

from typing import TYPE_CHECKING, Literal

from wafer_core.utils.kernel_utils.gpu_validation import check_gpus_available
from wafer_core.utils.kernel_utils.targets.config import ModalTarget, TargetConfig

if TYPE_CHECKING:
    from wafer_core.ssh import SSHClient
    from wafer_core.utils.execution_types import KernelExecutionContext, ProfilingArtifactConfig
    from wafer_core.utils.kernel_utils.deployment import DeploymentState


def find_free_gpu(
    ssh_client: "SSHClient",
    target: TargetConfig,
    memory_threshold_mb: int = 1000,
    util_threshold_pct: int = 5,
) -> tuple[int | None, str | None]:
    """Find first free GPU from target's gpu_ids list.

    Tries each GPU in order until finding one that's free.
    This allows multiple GPUs per target with automatic failover.

    Tiger Style: Explicit error handling via tuple returns.

    Args:
        ssh_client: Connected SSH client
        target: Target with list of GPU IDs to check
        memory_threshold_mb: Consider GPU busy if > this much memory used
        util_threshold_pct: Consider GPU busy if > this % utilized

    Returns:
        (gpu_id, None) if found free GPU
        (None, error) if all GPUs busy or check failed

    Example:
        target.gpu_ids = [6, 7]
        gpu_id, err = find_free_gpu(client, target)
        # GPU 6 is busy → skip
        # GPU 7 is free → returns (7, None)
    """
    # Type narrowing: Only SSH-based targets supported (not Modal)
    assert not isinstance(target, ModalTarget), f"find_free_gpu only supports SSH targets, got {type(target).__name__}"

    for gpu_id in target.gpu_ids:
        available, _err_msg = check_gpus_available(
            ssh_client,
            gpu_ids=[gpu_id],  # Check one GPU at a time
            memory_threshold_mb=memory_threshold_mb,
            util_threshold_pct=util_threshold_pct,
        )
        if available:
            return gpu_id, None

    # All GPUs busy
    return None, f"All GPUs busy on {target.name}: {target.gpu_ids}"


async def check_target_available(
    target: TargetConfig,
    memory_threshold_mb: int = 1000,
    util_threshold_pct: int = 5,
) -> tuple[int | None, str | None]:
    """Check if target has any available GPUs (SSH reachable, at least one GPU free).

    Tiger Style: Async function with explicit error handling.

    Args:
        target: Target to check
        memory_threshold_mb: Consider GPU busy if > this much memory used
        util_threshold_pct: Consider GPU busy if > this % utilized

    Returns:
        (gpu_id, None) if found free GPU (returns the specific GPU ID)
        (None, error) if no GPUs available or SSH failed

    Example:
        gpu_id, err = await check_target_available(vultr_baremetal)
        if err:
            print(f"Target unavailable: {err}")
        else:
            print(f"Using GPU {gpu_id}")
    """
    # Modal targets don't have GPU availability checks (serverless)
    if isinstance(target, ModalTarget):
        from wafer_core.utils.modal_execution.modal_execution import (
            check_modal_available,
            setup_modal_deployment,
        )

        # Setup Modal deployment to validate credentials
        modal_state, err = await setup_modal_deployment(
            modal_token_id=target.modal_token_id,
            modal_token_secret=target.modal_token_secret,
            modal_workspace=target.modal_workspace,
            app_name=target.modal_app_name,
            gpu_type=target.gpu_type,
        )
        if err:
            return None, f"Modal setup failed: {err}"

        assert modal_state is not None

        # Check if Modal is accessible
        available, err = await check_modal_available(modal_state)
        if not available:
            return None, f"Modal unavailable: {err}"

        # Modal is serverless - return sentinel value (0) for "GPU available"
        return 0, None

    # SSH-based targets (VM/Baremetal)
    # Type narrowing: Modal already returned above, so target must be SSH-based
    assert not isinstance(target, ModalTarget), "Modal target should have returned above"

    from wafer_core.utils.kernel_utils.deployment import (
        DeploymentConfig,
        setup_deployment,
    )

    # Convert target to DeploymentConfig
    deployment_config = DeploymentConfig(
        ssh_target=target.ssh_target,
        ssh_key=target.ssh_key,
        gpu_id=target.gpu_ids[0],  # Use first for connection check
        workspace_path="~/.wafer/workspaces/wafer",  # Default
    )

    # Setup deployment (validates SSH, connection, etc)
    deployment, err = await setup_deployment(deployment_config)
    if err:
        return None, f"SSH connection failed: {err}"
    assert deployment is not None

    # Find first free GPU using existing check_gpus_available()
    ssh_client = deployment.ssh_client
    return find_free_gpu(
        ssh_client,
        target,
        memory_threshold_mb,
        util_threshold_pct,
    )


async def run_operation_on_target(
    operation: Literal["correctness", "benchmark", "torch_profile", "ncu_profile"],
    target: TargetConfig,
    kernel_code: str,
    context: "KernelExecutionContext",
    profiling_config: "ProfilingArtifactConfig | None" = None,
    check_availability: bool = True,
    deployment_state_cache: dict[str, "DeploymentState"] | None = None,
) -> tuple[dict | None, str | None]:
    """Execute operation on selected target using existing deployment.py machinery.

    Tiger Style:
    - Explicit error handling (tuple returns)
    - Thin wrapper around existing test_kernel()
    - Optional deployment state caching
    - Pure function (cache passed in, not managed here)

    This function:
    1. Finds a free GPU on the target (if check_availability=True)
    2. Converts target to DeploymentConfig with the specific GPU
    3. Sets up deployment (or reuses cached state)
    4. Builds TestKernelParams based on operation type
    5. Calls test_kernel() from deployment.py
    6. Returns results

    Args:
        operation: What to run (correctness, benchmark, torch_profile, ncu_profile)
        target: Where to run it (may have multiple GPUs)
        kernel_code: Kernel code to test
        context: Execution context (problem_id, test_suite, sample_data, etc.)
        profiling_config: Optional profiling configuration
        check_availability: Whether to check GPU availability first (default: True)
        deployment_state_cache: Optional cache dict for deployment states (key = target.name)

    Returns:
        (result_dict, None): Operation results on success
        (None, error): Error message on failure

    Example:
        >>> cache = {}  # Reuse across multiple operations
        >>> result, err = await run_operation_on_target(
        ...     operation="correctness",
        ...     target=vultr_baremetal,
        ...     kernel_code=code,
        ...     context=ctx,
        ...     deployment_state_cache=cache,
        ... )
        >>> if not err:
        ...     print(f"Correctness: {result['correctness_score']}")
    """
    from wafer_core.utils.execution_types import ProfilingArtifactConfig

    # Use default profiling config if not provided
    if profiling_config is None:
        profiling_config = ProfilingArtifactConfig()

    # ══════════════════════════════════════════════════════════════════════════════
    # Modal Execution Path (Phase 5)
    # ══════════════════════════════════════════════════════════════════════════════

    if isinstance(target, ModalTarget):
        # Route to Modal serverless execution
        from wafer_core.utils.modal_execution.modal_execution import (
            execute_kernel_modal,
            setup_modal_deployment,
        )

        # Check if Modal operation is supported
        if operation == "ncu_profile":
            return None, "NCU profiling not supported on Modal (no privileged access)"

        # Setup Modal deployment (lightweight - just validates config)
        modal_state, err = await setup_modal_deployment(
            modal_token_id=target.modal_token_id,
            modal_token_secret=target.modal_token_secret,
            modal_workspace=target.modal_workspace,
            app_name=target.modal_app_name,
            gpu_type=target.gpu_type,
            compute_capability=target.compute_capability,
            timeout_seconds=target.timeout_seconds,
            cpu_count=target.cpu_count,
            memory_gb=target.memory_gb,
        )
        if err:
            return None, f"Modal deployment setup failed: {err}"

        assert modal_state is not None

        # Execute kernel on Modal
        results = await execute_kernel_modal(
            modal_state=modal_state,
            kernel_code=kernel_code,
            context=context,
            profiling_config=profiling_config,
        )

        # Modal returns same format as SSH execution
        return results, None

    # ══════════════════════════════════════════════════════════════════════════════
    # SSH Execution Path (VM/Baremetal)
    # ══════════════════════════════════════════════════════════════════════════════

    # Type narrowing: Modal already returned above, so target must be SSH-based
    assert not isinstance(target, ModalTarget), "Modal target should have returned above"

    from wafer_core.utils.kernel_utils.deployment import (
        TestKernelParams,
        setup_deployment,
        test_kernel,
    )
    from wafer_core.utils.kernel_utils.targets.config import target_to_deployment_config

    # Step 1: Find a free GPU on this target (or use first GPU if skipping check)
    gpu_id: int
    if check_availability:
        # Check if we have cached deployment state for this target
        if deployment_state_cache is not None and target.name in deployment_state_cache:
            # Reuse cached deployment's SSH client for GPU check
            cached_state = deployment_state_cache[target.name]
            ssh_client = cached_state.ssh_client
            gpu_id_opt, err = find_free_gpu(ssh_client, target)
            if err:
                return None, f"No available GPU on {target.name}: {err}"
            assert gpu_id_opt is not None
            gpu_id = gpu_id_opt
        else:
            # No cache - need to setup deployment to check availability
            gpu_id_opt, err = await check_target_available(target)
            if err:
                return None, f"No available GPU on {target.name}: {err}"
            assert gpu_id_opt is not None
            gpu_id = gpu_id_opt
    else:
        # Skip availability check - use first GPU
        gpu_id = target.gpu_ids[0]

    # Step 2: Get or create deployment state
    deployment_state: DeploymentState
    if deployment_state_cache is not None and target.name in deployment_state_cache:
        # Reuse cached deployment state
        deployment_state = deployment_state_cache[target.name]
    else:
        # Setup new deployment
        deployment_config = target_to_deployment_config(target, gpu_id)
        state, err = await setup_deployment(deployment_config)
        if err:
            return None, f"Deployment setup failed for {target.name}: {err}"
        assert state is not None
        deployment_state = state

        # Cache it if cache provided
        if deployment_state_cache is not None:
            deployment_state_cache[target.name] = deployment_state

    # Step 3: Map operation to test_suite and profiling flags
    # Based on existing code patterns from remote_execution.py
    test_suite: str
    backend_name: str
    profile_flag: bool
    ncu_flag: bool

    if operation == "correctness":
        test_suite = context.test_suite  # e.g., "gpumode_correctness"
        backend_name = "agent"
        profile_flag = False
        ncu_flag = False
    elif operation == "benchmark":
        test_suite = context.benchmark_suite  # e.g., "gpumode_benchmark"
        backend_name = "agent"
        profile_flag = False
        ncu_flag = False
    elif operation == "torch_profile":
        test_suite = context.benchmark_suite  # Run on benchmark suite
        backend_name = "agent_profiled"
        profile_flag = True
        ncu_flag = False
    elif operation == "ncu_profile":
        test_suite = context.benchmark_suite  # Run on benchmark suite
        backend_name = "agent_ncu"
        profile_flag = False
        ncu_flag = True
    else:
        return None, f"Unknown operation: {operation}"

    # Step 4: Format problem_id (LeetGPU needs special formatting)
    formatted_problem_id = (
        f"challenge_{context.problem_id}" if context.benchmark_name == "leetgpu" else context.problem_id
    )

    # Step 5: Build TestKernelParams
    test_params = TestKernelParams(
        state=deployment_state,
        kernel_code=kernel_code,
        backend_name=backend_name,
        test_suite=test_suite,
        reference_backend=context.reference_backend,
        problem_id=formatted_problem_id,
        sample_data=context.sample_data,
        profile=profile_flag,
        ncu=ncu_flag,
        language_filter=context.language,
        artifact_dir=str(profiling_config.artifacts_dir) if profiling_config.artifacts_dir else None,
    )

    # Step 6: Call test_kernel() from deployment.py
    results, err = await test_kernel(test_params)
    if err:
        return None, f"test_kernel failed: {err}"

    assert results is not None

    # Step 7: Convert TestResults to dict format (matching execute_kernel_remote pattern)
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
    }, None
