"""Remote kernel deployment utilities.

Reusable deployment logic extracted from kernel_environment.py.
Used by both the agent environment and manual testing scripts.

Tiger Style:
- Frozen dataclasses for config/state
- Pure functions for computation
- No classes (functional style)
- Explicit error returns (tuples, not exceptions)
- Push ifs up, fors down
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from wafer_core.remote_env import PythonEnvState
from wafer_core.utils.exceptions import (
    MissingFunctionDefinitionError,
    MissingReferenceCodeError,
    SpecLoaderMissingError,
    SpecLoadError,
    UnknownSuiteTypeError,
)

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from wafer_core.ssh import SSHClient

logger = logging.getLogger(__name__)

# Project subdirectory within monorepo
PROJECT_SUBDIR = "research/async-wevin/benchmarks/gpumode"

# Exit codes (POSIX standard)
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Timeouts (in seconds)
TMUX_TIMEOUT_SECONDS = 600  # 10 minutes - max smoke test execution time
TMUX_POLL_INTERVAL_SECONDS = 2.0

# GPUMode dataset path
GPUMODE_DATASET_PATH = "datasets/gpumode_problems.jsonl"


# Helper functions for GPUMode JSONL dataset


def _load_problem_from_dataset(problem_id: str, dataset_path: str = GPUMODE_DATASET_PATH) -> dict | None:
    """Load problem data from JSONL dataset.

    Args:
        problem_id: Problem identifier (e.g., "histogram_v2")
        dataset_path: Path to JSONL dataset file

    Returns:
        Problem data dict if found, None otherwise
    """
    try:
        with open(dataset_path) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("problem_id") == problem_id:
                    return entry
    except FileNotFoundError:
        logger.warning(f"Dataset file not found: {dataset_path}")
        return None
    except Exception as e:
        logger.warning(f"Error loading problem from dataset: {e}")
        return None
    else:
        return None


def _generate_reference_kernel_from_jsonl(problem_data: dict) -> str:
    """Generate reference_kernel.py content from JSONL problem data.

    Args:
        problem_data: Problem data from JSONL dataset

    Returns:
        Python code for reference_kernel.py
    """
    reference_code = problem_data.get("reference_code", "")
    if not reference_code:
        raise MissingReferenceCodeError(problem_data.get("problem_id", "unknown"))

    # The reference_code should already be complete Python code
    # Just add a header comment
    problem_id = problem_data.get("problem_id", "unknown")
    gpumode_id = problem_data.get("gpumode_problem_id", "unknown")
    leetgpu_id = problem_data.get("leetgpu_challenge_id", None)

    if leetgpu_id:
        header = f'''"""Reference kernel for {problem_id} (LeetGPU Challenge #{leetgpu_id}).

Auto-generated from JSONL dataset.
"""
'''
    else:
        header = f'''"""Reference kernel for {problem_id} (GPUMode #{gpumode_id}).

Auto-generated from JSONL dataset.
"""
'''

    # Add function alias for compatibility
    # LeetGPU uses solve(), GPUMode uses ref_kernel()
    # Check which one is defined and add an alias for the other
    footer = ""
    if "def solve(" in reference_code and "def ref_kernel(" not in reference_code:
        # LeetGPU format - add ref_kernel alias
        footer = "\n\n# Alias for evaluate.py compatibility\nref_kernel = solve\n"
    elif "def ref_kernel(" in reference_code and "def solve(" not in reference_code:
        # GPUMode format - add solve alias (for consistency)
        footer = "\n\n# Alias for LeetGPU compatibility\nsolve = ref_kernel\n"

    return header + reference_code + footer


def _generate_task_py_stub() -> str:
    """Generate a minimal task.py stub as fallback for GPUMode problems.

    Returns:
        Python code for task.py that provides generic type aliases
    """
    return '''"""Type definitions for GPUMode problem.

Auto-generated stub for GPUMode problems.
"""
from typing import TypeVar
import torch

# Generic type variables - actual types determined by generate_input()
input_t = TypeVar("input_t")
output_t = TypeVar("output_t")
'''


def _generate_test_suite_from_jsonl(
    problem_data: dict, suite_type: str = "gpumode_correctness", language_filter: str | None = None
) -> list[dict]:
    """Generate test suite JSON from JSONL problem data.

    Args:
        problem_data: Problem data from JSONL dataset
        suite_type: Type of test suite (e.g., "gpumode_correctness", "leetgpu_correctness")
        language_filter: Optional language to filter tests by (e.g., "cute", "pytorch").
                        Used for LeetGPU to only run tests for specific language.

    Returns:
        List of test case dicts
    """
    # Map suite type to data array
    # Both GPUMode and LeetGPU use the same structure: tests for correctness, benchmarks for performance
    if suite_type.endswith("_correctness"):
        tests = problem_data.get("tests", [])
    elif suite_type.endswith("_benchmark"):
        tests = problem_data.get("benchmarks", [])
    else:
        raise UnknownSuiteTypeError(suite_type)

    # Filter by language if specified (for LeetGPU multi-language problems)
    if language_filter:
        tests = [t for t in tests if t.get("language") == language_filter]
        logger.debug(f"   Filtered to {len(tests)} test(s) for language={language_filter}")

    if not tests:
        # No tests found for this suite type - raise UnknownSuiteTypeError
        raise UnknownSuiteTypeError(
            f"{suite_type} for problem {problem_data.get('problem_id')}"
            + (f" (language={language_filter})" if language_filter else "")
        )

    return tests


@dataclass(frozen=True)
class TestKernelParams:
    """Parameters for test_kernel function.

    Immutable configuration for kernel testing.
    Tiger Style: Explicit data structure instead of kwargs dict.
    """

    state: "DeploymentState"
    kernel_code: str
    backend_name: str
    test_suite: str
    reference_backend: str
    problem_id: str
    sample_data: dict | None
    profile: bool
    ncu: bool
    language_filter: str | None
    artifact_dir: str | None


@dataclass(frozen=True)
class DeploymentConfig:
    """Configuration for remote deployment.

    Immutable, serializable deployment configuration.
    """

    ssh_target: str
    ssh_key: str = "~/.ssh/id_ed25519"
    gpu_id: int = 0
    workspace_path: str = "~/.wafer/workspaces/wafer"
    cuda_launch_blocking: bool = False  # Enable for detailed CUDA error traces (verbose)
    project_subdir: str = "research/async-wevin/benchmarks/gpumode"  # Project path within monorepo
    dataset_path: str = "datasets/gpumode_problems.jsonl"  # Relative to project_subdir

    def __post_init__(self) -> None:
        """Validate configuration."""
        assert self.ssh_target, "ssh_target cannot be empty"
        assert "@" in self.ssh_target, f"ssh_target missing '@' (must be user@host:port): {self.ssh_target}"
        assert ":" in self.ssh_target, f"ssh_target missing ':' (must be user@host:port): {self.ssh_target}"
        assert self.gpu_id >= 0, f"gpu_id must be >= 0, got: {self.gpu_id}"


@dataclass(frozen=True)
class DeploymentState:
    """State after successful deployment setup.

    Immutable deployment state - setup once, use many times.
    Now serializable! The SSH client is created lazily on first access.
    """

    workspace_path: str
    env_state: PythonEnvState
    config: DeploymentConfig

    # Private cache for lazy SSH client (excluded from serialization)
    _ssh_client_cache: Optional["SSHClient"] = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
        metadata={"serialize": False},  # Mark for exclusion
    )

    @property
    def ssh_client(self) -> "SSHClient":
        """Lazy-create SSH client on first access.

        This allows DeploymentState to be serialized without the active SSH connection.
        The client is recreated from config when needed after deserialization.
        """
        if self._ssh_client_cache is None:
            from wafer_core.ssh import SSHClient

            # Use object.__setattr__ because the dataclass is frozen
            object.__setattr__(
                self,
                "_ssh_client_cache",
                SSHClient(self.config.ssh_target, self.config.ssh_key),
            )
        # Type checker knows this is not None after the if block
        assert self._ssh_client_cache is not None
        return self._ssh_client_cache

    def to_dict(self) -> dict:
        """Serialize to dict, excluding non-serializable cache fields.

        Returns a dict suitable for JSON serialization and checkpointing.
        """
        from dataclasses import asdict as dataclass_asdict
        from dataclasses import fields

        # Get all fields that should be serialized
        result = {}
        for f in fields(self):
            if f.metadata.get("serialize", True):  # Include unless explicitly excluded
                value = getattr(self, f.name)
                # Recursively convert nested dataclasses
                if hasattr(value, "__dataclass_fields__"):
                    result[f.name] = dataclass_asdict(value)
                else:
                    result[f.name] = value
        return result


@dataclass(frozen=True)
class EvaluationParams:
    """Parameters for kernel evaluation.

    Groups evaluation-specific options to reduce function argument count.
    """

    backend_name: str
    test_suite: str
    reference_backend: str
    problem_id: str = "nvfp4_gemv_blackwell"
    kernel_path: str | None = None
    run_dir: str | None = None
    profile: bool = False
    ncu: bool = False
    language_filter: str | None = None
    sample_data: dict | None = None
    artifact_dir: str | None = None


@dataclass(frozen=True)
class TestResults:
    """Results from kernel testing.

    Immutable test results.
    """

    correctness_score: float
    geomean_speedup: float
    all_correct: bool
    correctness_tests: list = field(default_factory=list)
    performance_tests: list = field(default_factory=list)


# Setup functions - Helper functions (pure computation, minimal branching)


async def _connect_and_deploy(
    config: DeploymentConfig,
) -> tuple[Optional["SSHClient"], str | None, str | None]:
    """Connect to remote and deploy codebase via upload_files().

    Uses upload_files() with .gitignore support for fast, incremental-feeling uploads.
    Syncs uncommitted changes (unlike git-based push which only syncs committed files).

    Returns:
        (ssh_client, project_path, error): Client and paths on success, error on failure
    """
    from wafer_core.ssh import SSHClient
    from wafer_core.utils.path_utils import get_research_root

    # Validate SSH key exists before attempting connection
    ssh_key_path = Path(config.ssh_key).expanduser()  # noqa: ASYNC240
    if not ssh_key_path.exists():  # noqa: ASYNC240
        error_msg = (
            f"SSH private key not found: {config.ssh_key}\n"
            f"  Expanded path: {ssh_key_path}\n"
            f"\n"
            f"To fix this:\n"
            f"  1. Ensure your SSH key exists at the path above\n"
            f"  2. Or update SSH_KEY in your config file to point to your key\n"
            f"  3. Default location is ~/.ssh/id_ed25519\n"
            f"\n"
            f"Test your SSH connection:\n"
            f"  ssh -i {config.ssh_key} {config.ssh_target.split(':')[0]}\n"
        )
        logger.error(error_msg)
        return None, None, error_msg

    logger.debug(f"📡 Connecting to {config.ssh_target}")
    ssh_client = SSHClient(config.ssh_target, config.ssh_key)

    # Find local research root to upload
    try:
        local_research_root = get_research_root(Path(__file__))
    except Exception as e:
        return None, None, f"Failed to find local research root: {e}"

    # Expand remote workspace path
    workspace_path_expanded = ssh_client.expand_path(config.workspace_path)
    logger.debug(f"   Remote workspace: {workspace_path_expanded}")

    # Create remote workspace directory
    mkdir_result = ssh_client.exec(f"mkdir -p {workspace_path_expanded}")
    if mkdir_result.exit_code != EXIT_SUCCESS:
        return None, None, f"Failed to create remote workspace: {mkdir_result.stderr}"

    # Upload local research root to remote workspace
    logger.info("uploading codebase")
    logger.debug(f"   Local: {local_research_root}")
    logger.debug(f"   Remote: {workspace_path_expanded}")

    upload_result = ssh_client.upload_files(
        local_path=str(local_research_root),
        remote_path=workspace_path_expanded,
        recursive=True,
        respect_gitignore=True,
    )

    if not upload_result.success:
        return None, None, f"Failed to upload codebase: {upload_result.error_message}"

    logger.debug(f"   Uploaded {upload_result.files_copied} files ({upload_result.total_bytes} bytes)")
    logger.debug(f"   Upload time: {upload_result.duration_seconds:.1f}s")

    # The workspace now contains the research root contents directly
    # project_subdir is relative to research root, so project_path = workspace + project_subdir
    project_path = f"{workspace_path_expanded}/{config.project_subdir}"
    logger.debug(f"   Project path: {project_path}")

    # Verify project subdirectory exists
    check_result = ssh_client.exec(f"test -d {project_path}")
    if check_result.exit_code != EXIT_SUCCESS:
        return (
            None,
            None,
            f"Project subdirectory does not exist: {project_path}. Check that project_subdir is correct.",
        )

    return ssh_client, project_path, None


def _load_target_config(gpu_id: int) -> Any:  # Returns TargetConfig
    """Load target configuration for GPU setup.

    Tiger Style: Pure computation, loads config based on GPU ID.

    Args:
        gpu_id: GPU ID to configure for

    Returns:
        Target configuration for the GPU
    """
    import importlib.util
    import sys

    # Load path_utils to get research root
    path_utils_path = Path(__file__).parent.parent / "path_utils.py"
    spec = importlib.util.spec_from_file_location("path_utils", path_utils_path)
    if spec is None:
        raise SpecLoadError(str(path_utils_path))
    if spec.loader is None:
        raise SpecLoaderMissingError(str(path_utils_path))

    path_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(path_utils)

    # Add research root to path to import configs
    research_root = path_utils.get_research_root(Path(__file__))
    research_root_str = str(research_root)
    if research_root_str not in sys.path:
        sys.path.insert(0, research_root_str)

    from configs.base_config import TargetConfig

    # Create target config
    target = TargetConfig(
        gpu_type="B200",
        gpu_ids=[gpu_id],
        compute_capability="10.0",
        python_version="3.10",
        cuda_version="12.8",
    )

    return target


# NOTE: _create_venv_if_needed() has been removed.
# Venv creation is now handled by kerbal.setup_python_env() which:
# - Auto-installs uv if missing
# - Creates venv idempotently
# - Handles all the PATH setup automatically


def _install_pytorch_if_needed(
    ssh_client: "SSHClient",
    project_path: str,
    target: Any,
) -> str | None:
    """Install PyTorch with custom index if needed.

    Tiger Style: Side-effect function, returns error or None.

    Args:
        ssh_client: SSH SSH client
        project_path: Path to project directory
        target: Target configuration

    Returns:
        Error message if installation failed, None on success
    """
    index_flags = target.get_uv_index_flags()
    if not index_flags:
        return None  # Will be installed with other dependencies

    torch_req = target.get_torch_requirement()
    logger.debug("   Installing PyTorch...")

    install_torch_cmd = f"""
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    cd {project_path}
    uv pip install --python .venv/bin/python {index_flags} "{torch_req}"
    """
    result = ssh_client.exec(install_torch_cmd)

    if result.exit_code != EXIT_SUCCESS:
        return f"Failed to install PyTorch: {result.stderr}"

    logger.debug("   ✅ PyTorch installed")
    return None


async def _setup_python_env(
    ssh_client: "SSHClient", project_path: str, gpu_id: int
) -> tuple[PythonEnvState | None, str | None]:
    """Setup Python virtual environment with dependencies.

    Tiger Style: Orchestrator with control flow, calls helpers sequentially.

    NOTE: This function now delegates to kerbal.setup_python_env() which:
    - Auto-installs uv if missing (fixes "uv: command not found")
    - Creates venv if needed
    - Handles all package installation

    Returns:
        (env_state, error): Python environment state on success, error on failure
    """
    from wafer_core.remote_env import setup_python_env

    logger.debug("📦 Setting up Python dependencies...")

    # Load target configuration
    target = _load_target_config(gpu_id)
    logger.debug(f"   Target: {target.gpu_type} (CUDA {target.cuda_version})")

    # Build requirements list
    torch_req = target.get_torch_requirement()
    index_flags = target.get_uv_index_flags()

    # If custom PyTorch index needed, install it separately first
    # Then let kerbal handle the rest
    if index_flags:
        # Install PyTorch with custom index AFTER kerbal creates venv
        # We'll do this in two passes:
        # 1. Let kerbal create venv and install non-PyTorch deps
        # 2. Then install PyTorch separately

        other_requirements = ["triton", "nvidia-cutlass-dsl==4.3.0.dev0", "ninja"]

        # First pass: create venv and install non-PyTorch deps
        env_state = setup_python_env(
            ssh_client,
            project_path,
            requirements=other_requirements,
            python_version=f">={target.python_version}",
        )

        # Second pass: install PyTorch with custom index
        pytorch_err = _install_pytorch_if_needed(ssh_client, project_path, target)
        if pytorch_err:
            return None, pytorch_err
    else:
        # No custom index needed - let kerbal handle everything
        all_requirements = [torch_req, "triton", "nvidia-cutlass-dsl==4.3.0.dev0", "ninja"]

        env_state = setup_python_env(
            ssh_client,
            project_path,
            requirements=all_requirements,
            python_version=f">={target.python_version}",
        )

    logger.debug(f"   Python: {env_state.venv_python}")
    logger.debug(f"   Workspace: {env_state.workspace}")

    return env_state, None


async def setup_deployment(config: DeploymentConfig) -> tuple[DeploymentState | None, str | None]:
    """Setup remote environment (Phase 1).

    Deploys codebase and sets up Python environment.
    This is expensive - only do once per session.

    Args:
        config: Deployment configuration

    Returns:
        (state, error): Deployment state on success, error message on failure
    """
    logger.info("setting up remote environment")

    # Connect and deploy
    ssh_client, project_path, err = await _connect_and_deploy(config)
    if err:
        return None, err
    assert ssh_client is not None, "_connect_and_deploy returned no error but ssh_client is None"
    assert project_path is not None, "_connect_and_deploy returned no error but project_path is None"

    # Setup Python environment
    env_state, err = await _setup_python_env(ssh_client, project_path, config.gpu_id)
    if err:
        return None, err
    assert env_state is not None, "_setup_python_env returned no error but env_state is None"

    logger.info("remote environment ready")

    # Return immutable state
    # Note: ssh_client is not stored directly - it's created lazily via property
    # This makes DeploymentState serializable (no active SSH connections/threads)
    state = DeploymentState(
        workspace_path=project_path,
        env_state=env_state,
        config=config,
    )

    # Pre-populate the client cache to reuse the connection we just made
    # (avoids reconnecting immediately after setup)
    object.__setattr__(state, "_ssh_client_cache", ssh_client)

    return state, None


# Testing functions


async def test_kernel(
    params: TestKernelParams,
) -> tuple[TestResults | None, str | None]:
    """Deploy and test a kernel (Phase 2).

    Fast path - assumes setup_deployment() already called.

    Tiger Style: Single dataclass parameter instead of many individual params.
    Makes control flow explicit and prevents parameter drift.

    Args:
        params: TestKernelParams configuration

    Returns:
        (results, error): Results on success, error message on failure
    """
    logger.debug(f"🚀 Testing kernel: {params.backend_name}")

    # Step 1: Determine function name and file path from problem_id
    kernel_function_name = _get_kernel_function_name(params.problem_id)

    # Step 2: Write kernel file
    kernel_filename = f"{params.backend_name}_kernel.py"
    # params.state.workspace_path is already the project path (includes PROJECT_SUBDIR)
    # Make path problem-specific
    kernel_path = f"{params.state.workspace_path}/{params.problem_id}/optimized/{kernel_filename}"

    write_err = write_kernel_file(
        params.state.ssh_client,
        kernel_path,
        params.kernel_code,
        function_name=kernel_function_name,
    )
    if write_err:
        return None, write_err

    logger.debug("   ✅ Kernel file written")

    # Step 2: Run tests
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"test_{params.backend_name}_{timestamp}"

    # Create evaluation params
    eval_params = EvaluationParams(
        backend_name=params.backend_name,
        test_suite=params.test_suite,
        reference_backend=params.reference_backend,
        problem_id=params.problem_id,
        kernel_path=kernel_path,
        run_dir=run_dir,
        profile=params.profile,
        ncu=params.ncu,
        language_filter=params.language_filter,
        sample_data=params.sample_data,
        artifact_dir=params.artifact_dir,
    )

    results, err = run_evaluate(
        ssh_client=params.state.ssh_client,
        workspace_path=params.state.workspace_path,
        env_state=params.state.env_state,
        eval_params=eval_params,
        config=params.state.config,
    )

    if err:
        return None, err

    # If no error, results must be valid (run_evaluate contract)
    assert results is not None, "run_evaluate returned no error but results is None"

    logger.debug("   ✅ Tests complete")
    logger.debug(f"      Correctness: {results.correctness_score:.2f}")
    logger.debug(f"      Speedup: {results.geomean_speedup:.2f}x")

    return results, None


async def test_existing_kernel(
    state: DeploymentState,
    backend_name: str,
    test_suite: str,
    reference_backend: str = "reference",
    profile: bool = False,
    ncu: bool = False,
) -> tuple[TestResults | None, str | None]:
    """Test an existing kernel (already in codebase).

    Args:
        state: Deployment state from setup_deployment()
        backend_name: Existing backend name (e.g., "cute", "triton")
        test_suite: Test suite to run
        reference_backend: Reference backend for comparison
        profile: Enable torch.profiler
        ncu: Enable NCU profiling

    Returns:
        (results, error): Results on success, error message on failure
    """
    logger.debug(f"🚀 Testing existing kernel: {backend_name}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"test_{backend_name}_{timestamp}"

    # Create evaluation params
    eval_params = EvaluationParams(
        backend_name=backend_name,
        test_suite=test_suite,
        reference_backend=reference_backend,
        run_dir=run_dir,
        profile=profile,
        ncu=ncu,
    )

    # Run tests without --kernel-file (backend already registered)
    results, err = run_evaluate_existing(
        ssh_client=state.ssh_client,
        workspace_path=state.workspace_path,
        env_state=state.env_state,
        eval_params=eval_params,
        config=state.config,
    )

    if err:
        return None, err

    # If no error, results must be valid (run_evaluate_existing contract)
    assert results is not None, "run_evaluate_existing returned no error but results is None"

    logger.debug("   ✅ Tests complete")
    logger.debug(f"      Correctness: {results.correctness_score:.2f}")
    logger.debug(f"      Speedup: {results.geomean_speedup:.2f}x")

    return results, None


# Pure helper functions (no state, explicit inputs/outputs)


def _get_kernel_function_name(problem_id: str) -> str:
    """Get standard kernel function name.

    Uses GPU Mode's standard naming convention: all submission kernels use 'custom_kernel'.

    Args:
        problem_id: Problem identifier (unused, kept for backward compatibility)

    Returns:
        Always returns 'custom_kernel'
    """
    # Use GPU Mode's standard function name for all submissions
    return "custom_kernel"


def _wrap_kernel_code(kernel_code: str, function_name: str = "custom_kernel") -> str:
    """Validate that agent kernel code defines the required function name.

    No aliasing, no wrapping, no magic. The LLM is told exactly what to do in the prompt.
    If it doesn't follow the convention, fail immediately with a clear error.

    Args:
        kernel_code: Raw kernel code from agent
        function_name: Name of function that must be defined (default: "custom_kernel")

    Returns:
        Kernel code as-is (if valid)

    Raises:
        ValueError: If the required function is not found
    """
    assert kernel_code, "kernel_code cannot be empty"
    assert function_name, "function_name cannot be empty"

    # Check if function is defined
    has_function_def = f"def {function_name}(" in kernel_code

    if not has_function_def:
        raise MissingFunctionDefinitionError(function_name)

    return kernel_code


def write_kernel_file(
    ssh_client: Any, kernel_path: str, kernel_code: str, function_name: str = "nvfp4_kernel"
) -> str | None:
    """Write kernel code to remote file.

    Pure function - takes explicit inputs, returns error or None.

    Args:
        ssh_client: SSH client instance
        kernel_path: Remote file path
        kernel_code: Python kernel code
        function_name: Name of function that must be defined (e.g., "nvfp4_kernel")

    Returns:
        Error message on failure, None on success
    """
    # Assert preconditions
    assert ssh_client is not None, "ssh_client cannot be None"
    assert kernel_path, "kernel_path cannot be empty"
    assert len(kernel_path) > 0, "kernel_path must be non-empty string"
    assert kernel_code, "kernel_code cannot be empty"
    assert len(kernel_code) > 0, "kernel_code must be non-empty string"
    assert function_name, "function_name cannot be empty"

    # Wrap kernel code to ensure function_name is defined
    wrapped_code = _wrap_kernel_code(kernel_code, function_name)

    # Create parent directory if it doesn't exist
    kernel_dir = Path(kernel_path).parent
    mkdir_cmd = f"mkdir -p '{kernel_dir}'"
    mkdir_result = ssh_client.exec(mkdir_cmd)

    if mkdir_result.exit_code != 0:
        return f"Failed to create kernel directory: {mkdir_result.stderr}"

    write_cmd = f"cat > '{kernel_path}' << 'EOF'\n{wrapped_code}\nEOF"
    result = ssh_client.exec(write_cmd)

    if result.exit_code != 0:
        return f"Failed to write kernel file: {result.stderr}"

    return None


def _validate_evaluate_command_args(cmd_args: list[str]) -> tuple[bool, str | None]:
    """Validate that command arguments match evaluate.py's argument parser.

    This catches argument mismatches early (e.g., missing --implementation).

    Args:
        cmd_args: List of command arguments (without the python -m kernel_utils.evaluate part)

    Returns:
        (is_valid, error_message): True if valid, False with error message if invalid
    """
    import argparse
    import io
    import sys

    # Create parser matching evaluate.py's _parse_arguments (NEW API)
    parser = argparse.ArgumentParser(description="Run GPU kernel evaluation with correctness and performance testing")
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

    # Try to parse the arguments
    # argparse calls sys.exit() on error, so we redirect stderr and catch the error
    old_stderr = sys.stderr
    old_exit = sys.exit
    error_output = io.StringIO()

    def mock_exit(code: int = 0) -> None:
        raise SystemExit(code)

    # Tiger Style: Intentional shadowing for test isolation
    sys.exit = mock_exit  # type: ignore[assignment]
    sys.stderr = error_output

    try:
        parser.parse_args(cmd_args)
    except SystemExit as e:
        # argparse called sys.exit() - this means validation failed
        error_msg = error_output.getvalue()
        if error_msg:
            return False, error_msg.strip()
        return (
            False,
            f"Argument parsing failed (exit code {e.code if hasattr(e, 'code') else 'unknown'})",
        )
    except Exception as e:
        return False, f"Argument validation error: {e}"
    else:
        return True, None
    finally:
        sys.stderr = old_stderr
        sys.exit = old_exit


def _build_evaluate_command(
    workspace_path: str,
    env_state: PythonEnvState,
    eval_params: EvaluationParams,
) -> str:
    """Build evaluate command string with isolated run directory.

    Args:
        workspace_path: Remote workspace path (benchmarks/gpumode)
        env_state: Python environment state (includes venv_python, PATH, etc)
        eval_params: Evaluation parameters (backend, paths, profiling options, etc.)

    Returns:
        Complete command string

    Note:
        All files are now in the isolated run_dir:
        - {run_dir}/reference_kernel.py
        - {run_dir}/task.py
        - {run_dir}/test_cases.json
        - {run_dir}/agent_kernel.py (the implementation)
    """
    # Unpack eval_params
    backend_name = eval_params.backend_name
    kernel_path = eval_params.kernel_path
    test_suite = eval_params.test_suite
    run_dir = eval_params.run_dir
    profile = eval_params.profile
    ncu = eval_params.ncu
    # Build command using new API with isolated run directory
    research_root = "/".join(workspace_path.rstrip("/").split("/")[:-2])
    abs_run_dir = f"{workspace_path}/{run_dir}"

    # All paths are now relative to run_dir (isolated)
    impl_path = kernel_path if kernel_path else f"{abs_run_dir}/agent_kernel.py"
    reference_path = f"{abs_run_dir}/reference_kernel.py"
    test_cases_path = f"{abs_run_dir}/test_cases.json"

    # Build command: cd to run_dir (so reference_kernel.py imports work)
    # Run evaluate.py directly using absolute path, set PATH from env_state
    # evaluate.py bootstraps its own sys.path, so no PYTHONPATH needed
    evaluate_script = f"{research_root}/wafer_utils/kernel_utils/evaluate.py"
    cmd_parts = [
        f"cd {abs_run_dir} &&",
        f"PATH={env_state.venv_bin}:$PATH {env_state.venv_python} {evaluate_script}",
        f"--implementation {impl_path}",
        f"--reference {reference_path}",
        f"--test-cases {test_cases_path}",
        f"--run-dir {abs_run_dir}",
        f"--artifact-name {backend_name}",
    ]

    # Add profile flag if enabled
    if profile or ncu:
        cmd_parts.append("--profile")

    # Benchmark mode - for now, assume all tests should include benchmarking
    # TODO: Make this configurable based on test_suite
    if "benchmark" in test_suite.lower():
        cmd_parts.append("--benchmark")

    # Extract just the arguments (after "kernel_utils.evaluate") for validation
    full_cmd = " ".join(cmd_parts)
    if "kernel_utils.evaluate" in full_cmd:
        # Extract args after "kernel_utils.evaluate"
        eval_idx = full_cmd.index("kernel_utils.evaluate") + len("kernel_utils.evaluate")
        args_str = full_cmd[eval_idx:].strip()
        # Split into argument list (handles quoted paths)
        import shlex

        try:
            cmd_args = shlex.split(args_str)
            # Validate arguments match evaluate.py's parser
            is_valid, error_msg = _validate_evaluate_command_args(cmd_args)
            assert is_valid, (
                f"Command arguments don't match evaluate.py parser: {error_msg}\n"
                f"Command: {full_cmd}\n"
                f"Args: {cmd_args}"
            )
        except Exception as e:
            # If parsing fails, log but don't fail (might be edge case)
            logger.warning(f"Could not validate command arguments: {e}")

    return " ".join(cmd_parts)


# Test function to verify validation works (can be called manually or in tests)
def test_command_validation() -> None:
    """Test that command validation catches argument mismatches.

    This is a simple smoke test to verify the validation function works.
    Can be called manually: python -c "from wafer_core.utils.kernel_utils.deployment import test_command_validation; test_command_validation()"
    """
    # Test 1: Valid arguments should pass (new API)
    valid_args = [
        "--implementation",
        "test.py",
        "--reference",
        "nvfp4_gemv_blackwell/reference_kernel.py",
        "--test-cases",
        "nvfp4_gemv_blackwell/test_suites/smoke.json",
    ]
    is_valid, error = _validate_evaluate_command_args(valid_args)
    assert is_valid, f"Valid args should pass validation, got error: {error}"

    # Test 2: Missing --implementation should fail
    invalid_args = [
        "--reference",
        "nvfp4_gemv_blackwell/reference_kernel.py",
        "--test-cases",
        "nvfp4_gemv_blackwell/test_suites/smoke.json",
    ]
    is_valid, error = _validate_evaluate_command_args(invalid_args)
    assert not is_valid, "Missing --implementation should fail validation"
    assert error is not None
    assert (
        "implementation" in error.lower() or "required" in error.lower()
    ), f"Error message should mention implementation, got: {error}"

    print("✅ Command validation tests passed")


def _run_tmux_test(
    ssh_client: "SSHClient",
    workspace_path: str,
    backend_name: str,
    test_command: str,
    run_dir: str,
    gpu_id: int,
    cuda_launch_blocking: bool,
) -> tuple[str | None, str | None]:
    """Run test in tmux session and stream logs.

    Returns:
        (log_content, error): Log content on success, error on failure
    """
    from wafer_core.remote_jobs import (
        LogStreamConfig,
        start_tmux_session,
        stream_log_until_complete,
    )

    session_name = f"test_{backend_name}_{datetime.now().strftime('%H%M%S')}"
    log_file = f"{workspace_path}/{run_dir}/evaluate.log"

    logger.debug(f"   Running tests in tmux: {session_name}")

    # Start tmux session
    _, err = start_tmux_session(
        client=ssh_client,
        session_name=session_name,
        command=test_command,
        workspace=workspace_path,
        log_file=log_file,
        env_vars={
            "CUDA_VISIBLE_DEVICES": str(gpu_id),
            "CUDA_LAUNCH_BLOCKING": "1" if cuda_launch_blocking else "0",
            "PYTHONUNBUFFERED": "1",
            "TORCH_SHOW_CPP_STACKTRACES": "0",  # Suppress verbose C++ stack traces
        },
    )

    if err:
        return None, f"Failed to start tmux session: {err}"

    # Stream logs and wait for completion
    stream_config = LogStreamConfig(
        session_name=session_name,
        log_file=log_file,
        timeout_sec=TMUX_TIMEOUT_SECONDS,
        poll_interval_sec=TMUX_POLL_INTERVAL_SECONDS,
    )

    success, _, err = stream_log_until_complete(client=ssh_client, config=stream_config)

    # Download log file
    log_cat_result = ssh_client.exec(f"cat {log_file}")
    log_content = None
    if log_cat_result.exit_code == EXIT_SUCCESS:
        log_content = log_cat_result.stdout

    # Check for errors
    if not success:
        error_details = extract_error_from_log(log_content) if log_content else None
        return None, f"Test execution failed: {err}\n\n{error_details or ''}"

    return log_content, None


def _parse_test_results(
    ssh_client: "SSHClient",
    workspace_path: str,
    run_dir: str,
    backend_name: str,
    log_content: str | None,
) -> tuple[TestResults | None, str | None]:
    """Parse and extract test results from results.json.

    Returns:
        (results, error): Parsed results on success, error on failure
    """
    results_remote = f"{workspace_path}/{run_dir}/results.json"

    # First check if results file exists
    ls_result = ssh_client.exec(f"ls -lh {results_remote}")
    file_exists = ls_result.exit_code == EXIT_SUCCESS

    cat_result = ssh_client.exec(f"cat {results_remote}")

    if cat_result.exit_code != EXIT_SUCCESS:
        error_details = extract_error_from_log(log_content) if log_content else None
        error_msg = f"Failed to read results file: {results_remote}\n"
        error_msg += f"File exists: {file_exists}\n"
        if cat_result.stderr:
            error_msg += f"Cat error: {cat_result.stderr}\n"
        if error_details:
            error_msg += f"\nError from log:\n{error_details}"
        elif log_content:
            # Show last 50 lines of log if no specific error found
            log_lines = log_content.split("\n")
            error_msg += "\nLast 50 lines of log:\n" + "\n".join(log_lines[-50:])
        return None, error_msg

    # Parse JSON
    results_dict = json.loads(cat_result.stdout)

    # Extract backend results (handles both old and new format)
    backend_results = extract_backend_results(results_dict, backend_name)
    if backend_results is None:
        return None, f"Backend {backend_name} not in results"

    results = TestResults(
        correctness_score=backend_results["correctness_score"],
        geomean_speedup=backend_results["geomean_speedup"],
        all_correct=backend_results["all_correct"],
        correctness_tests=backend_results.get("correctness_tests", []),
        performance_tests=backend_results.get("performance_tests", []),
    )

    return results, None


def _sync_artifact_from_remote(
    ssh_client: "SSHClient",
    workspace_path: str,
    backend_name: str,
    local_artifact_dir: str = "results/artifacts",
    run_dir: str | None = None,
) -> tuple[Path | None, str | None]:
    """Sync artifact directory from remote to local.

    Args:
        ssh_client: SSH client
        workspace_path: Remote workspace path
        backend_name: Backend name (for backwards compatibility, not used)
        local_artifact_dir: Local directory to sync to
        run_dir: Run directory to sync artifacts from (e.g., "test_agent_20231122_143022")

    Returns:
        (local_path, error): Path to local artifact on success, error on failure
    """
    if not run_dir:
        logger.error("⚠️  run_dir is required for artifact syncing")
        return None, "run_dir is required"

    remote_artifact_path = f"{workspace_path}/{run_dir}/artifact"

    # Check if artifact exists in run directory
    logger.info(f"📦 Checking for artifact: {remote_artifact_path}")
    check_result = ssh_client.exec(f"test -d {remote_artifact_path} && echo exists")
    logger.debug(f"   Check result: exit_code={check_result.exit_code}, stdout='{check_result.stdout}'")

    if check_result.exit_code != EXIT_SUCCESS or "exists" not in check_result.stdout:
        logger.warning(f"⚠️  No artifact found in {run_dir}/artifact/")
        logger.debug(f"   Checked path: {remote_artifact_path}")
        return None, None

    # Create local path using run_dir as the artifact name
    local_base = Path(local_artifact_dir)
    local_base.mkdir(parents=True, exist_ok=True)
    local_artifact_path = local_base / run_dir

    logger.info("📦 Syncing artifact from remote...")
    logger.info(f"   Remote: {remote_artifact_path}")
    logger.info(f"   Local:  {local_artifact_path}")

    # Download directory recursively
    try:
        ssh_client.download_files(
            remote_path=remote_artifact_path, local_path=str(local_artifact_path), recursive=True
        )
    except Exception as e:
        logger.warning(f"⚠️  Failed to sync artifact: {e}")
        return None, str(e)
    else:
        logger.debug("   ✅ Artifact synced")
        return local_artifact_path, None


def _setup_run_dir_files(
    ssh_client: "SSHClient",
    workspace_path: str,
    eval_params: EvaluationParams,
    dataset_path: str,
) -> tuple[bool, str | None]:
    """Setup isolated run directory with all required files.

    Creates a fresh isolated directory for each run with:
    - reference_kernel.py (from dataset)
    - task.py (from dataset)
    - test_cases.json (filtered by language if specified)

    Args:
        ssh_client: SSH client
        workspace_path: Remote workspace path
        eval_params: Evaluation parameters (problem_id, test_suite, run_dir, etc.)
        dataset_path: Path to JSONL dataset (fallback if sample_data not provided)

    Returns:
        (success, error_msg): True if setup succeeded, error message on failure
    """
    # Unpack eval_params
    run_dir = eval_params.run_dir
    problem_id = eval_params.problem_id
    test_suite = eval_params.test_suite
    sample_data = eval_params.sample_data
    language_filter = eval_params.language_filter
    run_dir_path = f"{workspace_path}/{run_dir}"

    # Use sample_data if provided, otherwise load from JSONL
    if sample_data:
        logger.debug("📝 Setting up run directory from sample_data...")
        problem_data = sample_data
    else:
        logger.debug("📝 Setting up run directory from JSONL dataset...")

        # Load problem data from local JSONL dataset
        research_root = Path(__file__).parent.parent.parent

        # Extract project subdirectory from workspace_path
        if "research/" in workspace_path:
            project_rel_path = workspace_path.split("research/")[1]
            project_local_path = research_root / project_rel_path
        else:
            project_local_path = research_root / "benchmarks" / workspace_path.split("/")[-1]

        dataset_local_path = project_local_path / dataset_path
        problem_data = _load_problem_from_dataset(problem_id, str(dataset_local_path))

        if not problem_data:
            return False, f"Problem {problem_id} not found in dataset: {dataset_local_path}"

    try:
        # Generate reference kernel
        reference_code = _generate_reference_kernel_from_jsonl(problem_data)

        # Generate test suite (with language filtering for LeetGPU)
        test_cases = _generate_test_suite_from_jsonl(problem_data, test_suite, language_filter)
        test_suite_json = json.dumps(test_cases, indent=2)

        # Generate task.py
        task_py = problem_data.get("task_py", _generate_task_py_stub())

        # Write files to run directory
        write_cmd = f"""
cat > {run_dir_path}/reference_kernel.py << 'REFERENCE_EOF'
{reference_code}
REFERENCE_EOF

cat > {run_dir_path}/test_cases.json << 'TESTCASES_EOF'
{test_suite_json}
TESTCASES_EOF

cat > {run_dir_path}/task.py << 'TASK_EOF'
{task_py}
TASK_EOF
"""
        result = ssh_client.exec(write_cmd)
        if result.exit_code != EXIT_SUCCESS:
            return False, f"Failed to write run directory files: {result.stderr}"

    except Exception as e:
        return False, f"Failed to generate run directory files: {e}"
    else:
        logger.debug(f"   ✅ Run directory setup complete: {run_dir_path}")
        if language_filter:
            logger.debug(f"   Language: {language_filter} ({len(test_cases)} test(s))")

        return True, None


def _run_evaluate_impl(
    ssh_client: "SSHClient",
    workspace_path: str,
    env_state: PythonEnvState,
    eval_params: EvaluationParams,
    config: DeploymentConfig,
) -> tuple[TestResults | None, str | None]:
    """Shared implementation for running kernel evaluation.

    Args:
        ssh_client: SSH client
        workspace_path: Remote workspace path
        env_state: Python environment state (includes venv_python, PATH, etc)
        eval_params: Evaluation parameters (backend, test suite, profiling options, etc.)
        config: Deployment configuration (GPU ID, dataset path, etc.)

    Returns:
        (results, error): Results on success, error on failure
    """
    # Unpack eval_params for easier access
    backend_name = eval_params.backend_name
    kernel_path = eval_params.kernel_path
    test_suite = eval_params.test_suite
    _reference_backend = eval_params.reference_backend
    _problem_id = eval_params.problem_id
    run_dir = eval_params.run_dir
    profile = eval_params.profile
    ncu = eval_params.ncu
    _language_filter = eval_params.language_filter
    _sample_data = eval_params.sample_data
    artifact_dir = eval_params.artifact_dir

    # Unpack config for easier access
    gpu_id = config.gpu_id
    cuda_launch_blocking = config.cuda_launch_blocking

    # Tiger Style: Assert run_dir is not None
    assert run_dir is not None, "run_dir must be provided for kernel evaluation"

    # Create run directory
    mkdir_cmd = f"mkdir -p {workspace_path}/{run_dir}"
    mkdir_result = ssh_client.exec(mkdir_cmd)
    if mkdir_result.exit_code != EXIT_SUCCESS:
        return None, f"Failed to create run directory: {mkdir_result.stderr}"

    # Setup isolated run directory with fresh files (reference_kernel.py, task.py, test_cases.json)
    files_ok, files_err = _setup_run_dir_files(
        ssh_client,
        workspace_path,
        eval_params,
        config.dataset_path,
    )
    if not files_ok:
        return None, f"Run directory setup failed: {files_err}"

    # Build command
    test_cmd = _build_evaluate_command(
        workspace_path,
        env_state,
        eval_params,
    )

    # Log the command with flags highlighted
    flags = f"--implementation {kernel_path} --reference {run_dir}/reference_kernel.py --test-cases {run_dir}/test_cases.json --run-dir {run_dir} --artifact-name {backend_name}"
    if profile or ncu:
        flags += " --profile"
    if "benchmark" in test_suite.lower():
        flags += " --benchmark"
    logger.info(f"evaluate.py {flags}")

    # Run test in tmux
    log_content, err = _run_tmux_test(
        ssh_client,
        workspace_path,
        backend_name,
        test_cmd,
        run_dir,
        gpu_id,
        cuda_launch_blocking,
    )
    logger.info(f"🔍 DEBUG: Tmux test completed - err={err}")
    if err:
        logger.warning(f"⚠️  Tmux test failed, but will still try to sync artifacts: {err}")
        # DON'T return early - continue to sync artifacts even on tmux failure
        # return None, err

    # Sync artifact from remote to local BEFORE parsing results
    # This ensures we get artifacts even if parsing fails
    # Use custom artifact_dir if provided, otherwise default to "results/artifacts"
    local_artifact_dir = artifact_dir if artifact_dir else "results/artifacts"
    logger.info(
        f"🔍 DEBUG: About to sync artifact - run_dir={run_dir}, local_artifact_dir={local_artifact_dir}, artifact_dir_param={artifact_dir}"
    )
    artifact_path, sync_err = _sync_artifact_from_remote(
        ssh_client,
        workspace_path,
        backend_name,
        local_artifact_dir=local_artifact_dir,
        run_dir=run_dir,
    )
    logger.info(f"🔍 DEBUG: Sync returned - artifact_path={artifact_path}, sync_err={sync_err}")
    if sync_err:
        logger.warning(f"⚠️  Artifact sync failed (non-fatal): {sync_err}")
    elif artifact_path:
        logger.info(f"   ✅ Artifact available at: {artifact_path}")
    else:
        logger.warning(f"⚠️  No artifact path returned (artifact_path={artifact_path}, sync_err={sync_err})")

    # Parse results
    results, err = _parse_test_results(ssh_client, workspace_path, run_dir, backend_name, log_content)
    if err:
        return None, err

    return results, None


def run_evaluate(
    ssh_client: Any,
    workspace_path: str,
    env_state: PythonEnvState,
    eval_params: EvaluationParams,
    config: DeploymentConfig,
) -> tuple[TestResults | None, str | None]:
    """Run kernel evaluation with custom kernel.

    Pure function - all inputs explicit, returns tuple.
    Thin wrapper around _run_evaluate_impl.
    """
    return _run_evaluate_impl(
        ssh_client=ssh_client,
        workspace_path=workspace_path,
        env_state=env_state,
        eval_params=eval_params,
        config=config,
    )


def run_evaluate_existing(
    ssh_client: Any,
    workspace_path: str,
    env_state: PythonEnvState,
    eval_params: EvaluationParams,
    config: DeploymentConfig,
) -> tuple[TestResults | None, str | None]:
    """Run kernel evaluation with existing backend (no --kernel-file).

    Similar to run_evaluate but for backends already in the codebase.
    Thin wrapper around _run_evaluate_impl.
    """
    return _run_evaluate_impl(
        ssh_client=ssh_client,
        workspace_path=workspace_path,
        env_state=env_state,
        eval_params=eval_params,
        config=config,
    )


def extract_backend_results(results_dict: dict, backend_name: str) -> dict | None:
    """Extract backend results from results JSON.

    Handles two formats:
    1. Old format: {backend_name: {...}}
    2. New format: {backends: [{backend_name: ..., ...}]}

    Args:
        results_dict: Parsed results JSON
        backend_name: Backend to extract (e.g., "agent_v2")

    Returns:
        Backend results dict, or None if not found
    """
    # Assert preconditions
    assert results_dict is not None, "results_dict cannot be None"
    assert isinstance(results_dict, dict), f"results_dict must be dict, got {type(results_dict)}"
    assert backend_name, "backend_name cannot be empty"

    # Try old format first (flat dict)
    if backend_name in results_dict:
        backend_data = results_dict[backend_name]
        assert isinstance(backend_data, dict), "Backend data must be dict"
        return backend_data

    # Try new format (nested under "backends")
    if "backends" in results_dict:
        backends_list = results_dict["backends"]
        assert isinstance(backends_list, list), "backends must be list"

        for backend in backends_list:
            stored_name = backend.get("backend_name", "")
            # Try exact match first
            if stored_name == backend_name:
                return backend
            # Try matching against path patterns:
            # backend_name might be "agent_v2" but stored as "optimized/agent_v2_kernel.py"
            if backend_name in stored_name:
                # Check if it's a path-based match (e.g., "optimized/agent_v2_kernel.py" contains "agent_v2")
                # Make sure we're not doing a substring match of something else
                if f"/{backend_name}_" in stored_name or f"{backend_name}_kernel" in stored_name:
                    return backend

    return None


def extract_error_from_log(log_content: str) -> str | None:
    """Extract useful error information from test log.

    Pure function - finds first error (root cause), not last.

    Args:
        log_content: Full log file content

    Returns:
        Extracted error message, or None if can't parse
    """
    if not log_content:
        return None

    lines = log_content.split("\n")

    error_markers = [
        "Traceback (most recent call last)",
        "Error:",
        "AssertionError",
        "ImportError",
        "ModuleNotFoundError",
        "SyntaxError",
        "NameError",
        "AttributeError",
        "RuntimeError",
        "FAILED",
        "CUDA error",
        "triton.CompilationError",
    ]

    # Find FIRST error (root cause)
    first_error_idx = -1
    for i in range(len(lines)):
        if any(marker in lines[i] for marker in error_markers):
            first_error_idx = i
            break

    if first_error_idx == -1:
        return "\n".join(lines[-30:])

    # Extract context (limited to avoid massive CUDA assertion spam)
    start_idx = max(0, first_error_idx - 5)
    end_idx = min(len(lines), first_error_idx + 30)  # Reduced from 50 to 30
    error_lines = lines[start_idx:end_idx]

    # Check if we truncated repetitive CUDA assertions
    has_more_lines = (first_error_idx + 30) < len(lines)
    if has_more_lines:
        # Check if remaining lines are repetitive CUDA thread errors
        next_few_lines = lines[end_idx : min(len(lines), end_idx + 5)]
        if any("thread:" in line and "Assertion" in line for line in next_few_lines):
            error_lines.append("... (additional repetitive CUDA thread assertions truncated)")

    return "\n".join(error_lines)


# Convenience functions for one-shot usage


async def quick_test_kernel(
    ssh_target: str,
    gpu_id: int,
    kernel_code: str,
    backend_name: str,
    test_suite: str,
    reference_backend: str = "reference",
) -> tuple[TestResults | None, str | None]:
    """Quick one-shot kernel test (convenience function).

    Sets up deployment and tests kernel in one call.
    Less efficient than reusing state for multiple tests.

    Args:
        ssh_target: SSH target
        gpu_id: GPU device ID
        kernel_code: Kernel code
        backend_name: Backend name
        test_suite: Test suite
        reference_backend: Reference backend

    Returns:
        (results, error): Results on success, error on failure
    """
    config = DeploymentConfig(ssh_target=ssh_target, gpu_id=gpu_id)
    state, err = await setup_deployment(config)
    if err:
        return None, err

    # If no error, state must be valid (setup_deployment contract)
    assert state is not None, "setup_deployment returned no error but state is None"

    # Build params for test_kernel
    params = TestKernelParams(
        state=state,
        kernel_code=kernel_code,
        backend_name=backend_name,
        test_suite=test_suite,
        reference_backend=reference_backend,
        problem_id="nvfp4_gemv_blackwell",  # Default from original signature
        sample_data=None,
        profile=False,
        ncu=False,
        language_filter=None,
        artifact_dir=None,
    )

    return await test_kernel(params)
