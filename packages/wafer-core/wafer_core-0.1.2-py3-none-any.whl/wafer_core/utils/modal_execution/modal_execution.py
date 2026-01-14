"""Modal execution API - parallel to remote_execution.py.

Provides the same API as remote_execution.py but using Modal serverless GPUs
instead of SSH connections.

Tiger Style:
- Pure functions (no hidden state)
- Explicit error handling (tuple returns)
- Match remote_execution.py API for easy swapping

Note: Modal execution runs in a subprocess to avoid trio_asyncio conflicts.
Modal SDK uses asyncio internally, which is incompatible with trio_asyncio
Running in a subprocess provides complete isolation.
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass

from wafer_core.utils.execution_types import KernelExecutionContext, ProfilingArtifactConfig
from wafer_core.utils.modal_execution.modal_config import ModalConfig

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Modal Deployment State
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ModalDeploymentState:
    """State for Modal deployment (parallel to DeploymentState for SSH).

    Holds Modal app configuration and credentials.
    """

    app_name: str
    modal_config: ModalConfig
    gpu_type: str
    compute_capability: str
    timeout_seconds: int
    cpu_count: int
    memory_gb: int


# ══════════════════════════════════════════════════════════════════════════════
# Setup Functions
# ══════════════════════════════════════════════════════════════════════════════


async def setup_modal_deployment(
    modal_token_id: str | None = None,
    modal_token_secret: str | None = None,
    modal_workspace: str | None = None,
    app_name: str = "kernel-eval",
    gpu_type: str = "B200",
    compute_capability: str = "10.0",
    timeout_seconds: int = 600,
    cpu_count: int = 4,
    memory_gb: int = 16,
) -> tuple[ModalDeploymentState | None, str | None]:
    """Setup Modal deployment (parallel to setup_remote_deployment).

    This is a lightweight operation - Modal apps are deployed lazily on first invocation.
    This function just validates configuration and creates the deployment state.

    Args:
        modal_token_id: Modal API token ID (or None to use env var)
        modal_token_secret: Modal API token secret (or None to use env var)
        modal_workspace: Optional Modal workspace name
        app_name: Modal app name
        gpu_type: GPU type (e.g., "B200", "H100")
        compute_capability: CUDA compute capability
        timeout_seconds: Max execution time
        cpu_count: CPUs for kernel compilation
        memory_gb: Memory allocation

    Returns:
        Tuple of (deployment_state, error_message)
        - deployment_state: ModalDeploymentState if successful, None on error
        - error_message: Error string if failed, None on success

    Example:
        >>> state, err = await setup_modal_deployment(
        ...     modal_token_id="ak-xxx",
        ...     modal_token_secret="as-yyy",
        ...     gpu_type="B200",
        ... )
        >>> if err:
        ...     print(f"Setup failed: {err}")
        >>> else:
        ...     print(f"Modal ready: {state.app_name}")
    """
    try:
        # Create Modal config (validates credentials)
        modal_config = ModalConfig(
            token_id=modal_token_id,
            token_secret=modal_token_secret,
            workspace=modal_workspace,
        )

        # Create deployment state
        state = ModalDeploymentState(
            app_name=app_name,
            modal_config=modal_config,
            gpu_type=gpu_type,
            compute_capability=compute_capability,
            timeout_seconds=timeout_seconds,
            cpu_count=cpu_count,
            memory_gb=memory_gb,
        )

        logger.info(f"modal deployment ready: app={app_name}, gpu={gpu_type}")
        return state, None

    except Exception as e:
        logger.error(f"modal deployment setup failed: {e}")
        return None, str(e)


# ══════════════════════════════════════════════════════════════════════════════
# Execution Functions
# ══════════════════════════════════════════════════════════════════════════════


async def _execute_kernel_modal_subprocess(
    modal_state: ModalDeploymentState,
    kernel_code: str,
    context: KernelExecutionContext,
    profiling_config: ProfilingArtifactConfig | None = None,
) -> dict:
    """Execute kernel via subprocess to avoid trio_asyncio conflicts.

    Modal SDK uses asyncio internally, which conflicts with trio_asyncio
    Running Modal in a subprocess provides complete
    isolation from the parent process's event loop.

    Args:
        modal_state: Modal deployment state
        kernel_code: Kernel code to execute
        context: Execution context (problem, test suite, etc.)
        profiling_config: Profiling configuration

    Returns:
        Dict with execution results (same format as execute_kernel_modal)
    """
    import asyncio
    import os

    # Get wafer_core package path for subprocess
    import wafer_core as _wafer_core

    wafer_core_path = os.path.dirname(_wafer_core.__file__)

    # Prepare subprocess input as JSON
    subprocess_input = {
        "wafer_core_path": wafer_core_path,
        "modal_state": {
            "app_name": modal_state.app_name,
            "modal_config": {
                "token_id": modal_state.modal_config.token_id,
                "token_secret": modal_state.modal_config.token_secret,
                "workspace": modal_state.modal_config.workspace,
            },
            "gpu_type": modal_state.gpu_type,
            "compute_capability": modal_state.compute_capability,
            "timeout_seconds": modal_state.timeout_seconds,
            "cpu_count": modal_state.cpu_count,
            "memory_gb": modal_state.memory_gb,
        },
        "kernel_code": kernel_code,
        "context": {
            "problem_id": context.problem_id,
            "sample_data": context.sample_data,
            "test_suite": context.test_suite,
            "benchmark_suite": context.benchmark_suite,
            "reference_backend": context.reference_backend,
            "benchmark_name": context.benchmark_name,
            "language": context.language,
        },
        "profiling_config": {
            "profile_on_success": profiling_config.profile_on_success
            if profiling_config
            else False,
            "ncu_on_success": profiling_config.ncu_on_success if profiling_config else False,
        }
        if profiling_config
        else None,
    }

    # Create subprocess script (inline implementation to avoid import issues)
    subprocess_script = """
import asyncio
import json
import logging
import os
import sys
import types
import importlib.util

# CRITICAL: Block trio_asyncio from being imported BEFORE any other imports
# trio_asyncio hooks into asyncio and causes Modal to fail with AssertionError
# We create a fake module that does nothing
fake_trio_asyncio = types.ModuleType('trio_asyncio')
fake_trio_asyncio.__file__ = '<blocked>'
sys.modules['trio_asyncio'] = fake_trio_asyncio

# Setup basic logging for subprocess
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_file_directly(module_name, file_path):
    \"\"\"Import a Python file directly without going through package __init__.py.\"\"\"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

async def execute_modal_kernel(wafer_core_path, modal_state_dict, kernel_code, context_dict, profiling_config_dict):
    \"\"\"Execute Modal kernel in clean subprocess (no trio_asyncio).\"\"\"
    try:
        # Import modal modules directly (avoiding heavy imports)
        modal_config_path = os.path.join(wafer_core_path, 'utils', 'modal_execution', 'modal_config.py')
        modal_app_path = os.path.join(wafer_core_path, 'utils', 'modal_execution', 'modal_app.py')

        modal_config_module = import_file_directly('modal_config_direct', modal_config_path)
        modal_app_module = import_file_directly('modal_app_direct', modal_app_path)

        ModalConfig = modal_config_module.ModalConfig

        modal_config = ModalConfig(
            token_id=modal_state_dict["modal_config"]["token_id"],
            token_secret=modal_state_dict["modal_config"]["token_secret"],
            workspace=modal_state_dict["modal_config"]["workspace"],
        )

        # Set Modal credentials
        env = modal_config.to_env_dict()
        os.environ.update(env)

        run_evaluation_fn = modal_app_module.run_kernel_evaluation

        # Extract data from context
        reference_code = context_dict["sample_data"].get("reference_code", "")
        if not reference_code:
            return {
                "compiled": False,
                "error_message": "No reference_code in sample_data",
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "all_correct": False,
                "passed_tests": 0,
                "total_tests": 0,
            }

        test_cases = context_dict["sample_data"].get("tests", [])
        benchmark_cases = context_dict["sample_data"].get("benchmarks", [])

        # Determine profiling
        profile = False
        if profiling_config_dict:
            profile = profiling_config_dict.get("profile_on_success", False)
            if profiling_config_dict.get("ncu_on_success"):
                logger.warning("NCU profiling not supported on Modal, skipping")

        # Invoke Modal function with app.run() context manager
        # This auto-deploys the app if needed
        logger.info(f"invoking modal function: {modal_state_dict['app_name']}")

        with modal_app_module.app.run():
            results = run_evaluation_fn.remote(
                kernel_code=kernel_code,
                reference_code=reference_code,
                problem_id=context_dict["problem_id"],
                test_suite=context_dict["test_suite"],
                benchmark_suite=context_dict["benchmark_suite"],
                reference_backend=context_dict["reference_backend"],
                test_cases=test_cases,
                benchmark_cases=benchmark_cases,
                language=context_dict["language"] or "pytorch",
                profile=profile,
            )

        logger.info(f"modal execution complete: compiled={results.get('compiled')}")
        return results

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"{type(e).__name__}: {str(e) or repr(e)}\\n\\nTraceback:\\n{error_trace}"
        logger.error(f"modal execution failed: {error_msg}")
        return {
            "compiled": False,
            "error_message": f"Modal execution error: {error_msg}",
            "correctness_score": 0.0,
            "geomean_speedup": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
        }

async def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())

    # Execute kernel
    result = await execute_modal_kernel(
        wafer_core_path=input_data["wafer_core_path"],
        modal_state_dict=input_data["modal_state"],
        kernel_code=input_data["kernel_code"],
        context_dict=input_data["context"],
        profiling_config_dict=input_data["profiling_config"],
    )

    # Write result to stdout as JSON
    print(json.dumps(result))

asyncio.run(main())
"""

    # Spawn subprocess
    # Timeout = Modal timeout + 60s overhead
    timeout_seconds = modal_state.timeout_seconds + 60

    try:
        # Run subprocess with input
        # Check if we're in trio context and use appropriate method
        try:
            import trio

            # We're using trio - use to_thread
            # ruff: noqa: ASYNC221 - subprocess.run is intentionally blocking, wrapped in thread
            result = await trio.to_thread.run_sync(
                lambda: subprocess.run(  # noqa: ASYNC221
                    [sys.executable, "-c", subprocess_script],
                    input=json.dumps(subprocess_input),
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
            )
        except (ImportError, RuntimeError):
            # Not in trio context - use asyncio's executor
            loop = asyncio.get_event_loop()
            # ruff: noqa: ASYNC221 - subprocess.run is intentionally blocking, wrapped in executor
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(  # noqa: ASYNC221
                    [sys.executable, "-c", subprocess_script],
                    input=json.dumps(subprocess_input),
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                ),
            )

        # Check for errors
        if result.returncode != 0:
            error_msg = f"Subprocess failed with code {result.returncode}\n"
            # Increased limit to 10000 chars for better error visibility
            error_msg += f"STDERR: {result.stderr[:10000]}"
            logger.error(f"modal subprocess failed: {error_msg}")
            return {
                "compiled": False,
                "error_message": f"Modal subprocess error: {error_msg}",
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "all_correct": False,
                "passed_tests": 0,
                "total_tests": 0,
                "correctness_tests": [],
                "performance_tests": [],
            }

        # Parse result from stdout
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse subprocess output: {e}\n"
            # Increased limits for better debugging
            error_msg += f"STDOUT: {result.stdout[:10000]}\n"
            error_msg += f"STDERR: {result.stderr[:10000]}"
            logger.error(f"modal subprocess output parsing failed: {error_msg}")
            return {
                "compiled": False,
                "error_message": f"Modal subprocess output error: {error_msg}",
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "all_correct": False,
                "passed_tests": 0,
                "total_tests": 0,
                "correctness_tests": [],
                "performance_tests": [],
            }

    except subprocess.TimeoutExpired:
        error_msg = f"Subprocess timed out after {timeout_seconds}s"
        logger.error(f"modal subprocess timeout: {error_msg}")
        return {
            "compiled": False,
            "error_message": f"Modal subprocess timeout: {error_msg}",
            "correctness_score": 0.0,
            "geomean_speedup": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
            "correctness_tests": [],
            "performance_tests": [],
        }

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        error_msg = f"{type(e).__name__}: {str(e)}\n{error_trace}"
        logger.error(f"modal subprocess execution failed: {error_msg}")
        return {
            "compiled": False,
            "error_message": f"Modal subprocess error: {error_msg}",
            "correctness_score": 0.0,
            "geomean_speedup": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
            "correctness_tests": [],
            "performance_tests": [],
        }


async def _execute_kernel_modal_direct(
    modal_state: ModalDeploymentState,
    kernel_code: str,
    context: KernelExecutionContext,
    profiling_config: ProfilingArtifactConfig | None = None,
) -> dict:
    """Direct Modal execution (runs in clean subprocess, no trio_asyncio).

    This is the original implementation, now called from subprocess.
    """
    try:
        # Set Modal credentials for this invocation
        import os

        env = modal_state.modal_config.to_env_dict()
        os.environ.update(env)

        # Import the modal app module to get the function
        # This will auto-deploy on first .remote() call
        from wafer_core.utils.modal_execution import modal_app

        # Get the function directly from the module
        # The @app.function decorator makes it available as an attribute
        run_evaluation_fn = modal_app.run_kernel_evaluation

        logger.debug("using modal function from local module (will auto-deploy if needed)")

        # Extract reference code from sample_data
        reference_code = context.sample_data.get("reference_code", "")
        if not reference_code:
            return {
                "compiled": False,
                "error_message": "No reference_code in sample_data",
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "all_correct": False,
                "passed_tests": 0,
                "total_tests": 0,
            }

        # Extract test cases
        test_cases = context.sample_data.get("tests", [])
        benchmark_cases = context.sample_data.get("benchmarks", [])

        # Determine profiling (NCU not supported on Modal)
        profile = False
        if profiling_config:
            profile = profiling_config.profile_on_success
            if profiling_config.ncu_on_success:
                logger.warning("NCU profiling not supported on Modal, skipping")

        # Invoke Modal function (remote execution)
        # Need to run within app context for auto-deployment
        logger.info(f"invoking modal function: {modal_state.app_name}")

        with modal_app.app.run():
            results = run_evaluation_fn.remote(
                kernel_code=kernel_code,
                reference_code=reference_code,
                problem_id=context.problem_id,
                test_suite=context.test_suite,
                benchmark_suite=context.benchmark_suite,
                reference_backend=context.reference_backend,
                test_cases=test_cases,
                benchmark_cases=benchmark_cases,
                language=context.language or "pytorch",
                profile=profile,
            )

        logger.info(
            f"modal execution complete: compiled={results.get('compiled')}, "
            f"speedup={results.get('geomean_speedup', 0):.2f}x"
        )

        return results

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        error_msg = f"{type(e).__name__}: {str(e) or repr(e)}\n\nTraceback:\n{error_trace}"
        logger.error(f"modal execution failed: {error_msg}")
        return {
            "compiled": False,
            "error_message": f"Modal execution error: {error_msg}",
            "correctness_score": 0.0,
            "geomean_speedup": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
        }


async def execute_kernel_modal(
    modal_state: ModalDeploymentState,
    kernel_code: str,
    context: KernelExecutionContext,
    profiling_config: ProfilingArtifactConfig | None = None,
) -> dict:
    """Execute kernel code on Modal GPU (parallel to execute_kernel_remote).

    Invokes Modal serverless function to run kernel evaluation via subprocess
    to avoid trio_asyncio conflicts. Returns same result format as
    execute_kernel_remote for easy swapping.

    Args:
        modal_state: Modal deployment state
        kernel_code: Kernel code to execute
        context: Execution context (problem, test suite, etc.)
        profiling_config: Profiling configuration (NCU not supported on Modal)

    Returns:
        Dict with keys:
            - compiled: bool
            - error_message: str | None
            - correctness_score: float
            - geomean_speedup: float
            - all_correct: bool
            - passed_tests: int
            - total_tests: int

    Example:
        >>> results = await execute_kernel_modal(
        ...     modal_state=state,
        ...     kernel_code=code,
        ...     context=context,
        ... )
        >>> print(f"Speedup: {results['geomean_speedup']}")
    """
    # Use subprocess implementation to avoid trio_asyncio conflicts
    return await _execute_kernel_modal_subprocess(
        modal_state=modal_state,
        kernel_code=kernel_code,
        context=context,
        profiling_config=profiling_config,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Availability Checking
# ══════════════════════════════════════════════════════════════════════════════


async def check_modal_available(modal_state: ModalDeploymentState) -> tuple[bool, str | None]:
    """Check if Modal is available and accessible.

    Attempts to ping Modal API and verify credentials.
    Runs in subprocess to avoid trio/asyncio conflicts.

    Args:
        modal_state: Modal deployment state

    Returns:
        Tuple of (available, error_message)
        - available: True if Modal is accessible, False otherwise
        - error_message: Error string if unavailable, None if available

    Example:
        >>> available, err = await check_modal_available(state)
        >>> if not available:
        ...     print(f"Modal unavailable: {err}")
    """
    # Run in subprocess to avoid trio/asyncio conflicts
    # Modal SDK uses asyncio internally which conflicts with trio
    check_script = f"""
import os
import json

# Set credentials
os.environ["MODAL_TOKEN_ID"] = {repr(modal_state.modal_config.token_id)}
os.environ["MODAL_TOKEN_SECRET"] = {repr(modal_state.modal_config.token_secret)}
if {repr(modal_state.modal_config.workspace)}:
    os.environ["MODAL_WORKSPACE"] = {repr(modal_state.modal_config.workspace)}

try:
    import modal
    modal.App.lookup({repr(modal_state.app_name)}, create_if_missing=False)
    print(json.dumps({{"available": True, "error": None}}))
except Exception as e:
    print(json.dumps({{"available": False, "error": str(e)}}))
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", check_script],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Subprocess failed"
            logger.warning(f"modal availability check failed: {error_msg}")
            return False, error_msg

        response = json.loads(result.stdout.strip())
        if response["available"]:
            logger.debug(f"modal available: {modal_state.app_name}")
            return True, None
        else:
            logger.warning(f"modal unavailable: {response['error']}")
            return False, response["error"]

    except subprocess.TimeoutExpired:
        logger.warning("modal availability check timed out")
        return False, "Availability check timed out"
    except Exception as e:
        logger.warning(f"modal availability check error: {e}")
        return False, str(e)
