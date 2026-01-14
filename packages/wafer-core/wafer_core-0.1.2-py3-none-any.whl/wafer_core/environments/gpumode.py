"""GPUMode simplified tool environment - single write_kernel tool.

Minimal tool interface for kernel optimization:
- One tool: write_kernel(filepath, code) - writes AND auto-submits
- Reference files injected into initial context
- Future-proof for beam search and agentic workflows

Tiger Style:
- Simplest thing that works
- Single responsibility (one tool)
- Composition over inheritance
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from wafer_core.rollouts.dtypes import (
    AgentState,
    Message,
    Tool,
    ToolCall,
    ToolFunction,
    ToolFunctionParameter,
    ToolResult,
)
from wafer_core.utils.code_validation import (
    create_validation_error_result,
    validate_language_requirements,
)
from wafer_core.utils.exceptions import RemoteDeploymentError
from wafer_core.utils.kernel_utils.deployment import DeploymentState

# Import pure utility functions
from wafer_core.utils.remote_execution import (
    KernelExecutionContext,
    ProfilingArtifactConfig,
    execute_kernel_remote,
    setup_remote_deployment,
)
from wafer_core.utils.workspace_tools import write_file

logger = logging.getLogger(__name__)


# ── Configuration ─────────────────────────────────────────────────────────────

BENCHMARK_NAME = "gpumode"
DEFAULT_GPU_ID = 0


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclass
class KernelSubmission:
    """Record of a single kernel submission attempt."""

    filepath: str
    attempt_number: int

    # Compilation
    compiled: bool = False
    compile_error: str | None = None
    error_details: str | None = None

    # Test results (populated after execution)
    correctness_score: float = 0.0
    geomean_speedup: float = 0.0
    all_correct: bool = False

    # Raw results for detailed analysis
    raw_results: dict | None = None

    # Artifact path (from submission library)
    artifact_path: str | None = None


# ── Tool Definition ───────────────────────────────────────────────────────────

write_kernel_tool = Tool(
    type="function",
    function=ToolFunction(
        name="write_kernel",
        description="Write a kernel file to workspace and automatically test it on remote GPU. Returns correctness and performance feedback.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "filepath": {
                    "type": "string",
                    "description": "Filename for the kernel (e.g., 'kernel.py', 'optimized.py')",
                },
                "code": {"type": "string", "description": "Complete kernel implementation code"},
            },
        ),
        required=["filepath", "code"],
    ),
)


# ── Environment ───────────────────────────────────────────────────────────────


@dataclass
class GPUModeSimpleEnvironment:
    """Simplified GPUMode environment with single write_kernel tool.

    NO INHERITANCE - uses composition with pure utility functions.

    Design:
    - Single tool: write_kernel(filepath, code) - auto-submits for testing
    - Reference files injected into initial prompt (no need to read)
    - Submission history stored in environment state
    - Future-proof for beam search (workspace persists across calls)

    Modes:
    - Legacy mode: Provide ssh_target, ssh_key, gpu_ids (single target deployment)
    - Targets mode: Provide available_targets (pluggable target routing)
      When using targets mode, ssh_target/ssh_key/gpu_ids are optional (not used)
    """

    # Sample data and configuration
    sample_data: dict

    # Legacy SSH fields (optional when using targets mode)
    ssh_target: str | None = None
    ssh_key: str = "~/.ssh/id_ed25519"
    gpu_ids: list[int] = field(default_factory=lambda: [DEFAULT_GPU_ID])

    # Profiling config
    profile_on_success: bool = False
    ncu_on_success: bool = False

    # Artifacts directory
    artifacts_dir: Path | None = None

    # Pluggable targets (Phase 5) - when provided, use target-based routing
    # When available_targets is set, ssh_target/ssh_key/gpu_ids are ignored
    available_targets: list | None = None  # list[TargetConfig] but avoiding import

    # Workspace directory (set during deployment)
    workspace_dir: Path | None = field(default=None, repr=False, compare=False)

    # Deployment state (lazy initialization)
    _deployment_state: DeploymentState | None = field(default=None, repr=False, compare=False)
    _initialized: bool = False

    # Pluggable targets deployment cache (Phase 4)
    # Maps target.name → DeploymentState for reuse across operations
    _deployment_state_cache: dict = field(default_factory=dict, repr=False, compare=False)

    # Submission tracking
    submissions: list[KernelSubmission] = field(default_factory=list, repr=False)
    best_submission: KernelSubmission | None = field(default=None, repr=False)

    @property
    def gpu_id(self) -> int:
        """Get the first GPU ID for single-GPU operations."""
        return self.gpu_ids[0] if self.gpu_ids else DEFAULT_GPU_ID

    @property
    def problem_id(self) -> str:
        """Extract problem ID from sample_data."""
        return self.sample_data["problem_id"]

    @property
    def problem_description(self) -> str:
        """Extract problem description from sample_data."""
        return self.sample_data.get("problem_description", "")

    @property
    def test_suite(self) -> str:
        """Get test suite name from sample_data or use default."""
        return self.sample_data.get("test_suite", f"{BENCHMARK_NAME}_correctness")

    @property
    def benchmark_suite(self) -> str:
        """Get benchmark suite name."""
        return f"{BENCHMARK_NAME}_benchmark"

    @property
    def reference_backend(self) -> str:
        """Get reference backend name from sample_data or use default."""
        return self.sample_data.get("reference_backend", "reference")

    @property
    def language(self) -> str:
        """Extract language from sample_data, defaulting to 'pytorch'."""
        return self.sample_data.get("language", "pytorch")

    def __post_init__(self) -> None:
        """Validate configuration.

        In targets mode (available_targets provided), ssh_target is optional.
        In legacy mode (no available_targets), ssh_target is required.
        """
        assert self.sample_data, "sample_data cannot be empty"
        assert "problem_id" in self.sample_data, "sample_data must contain problem_id"

        # Validate mode: either use targets OR legacy SSH (not neither)
        if self.available_targets is None:
            # Legacy mode: require SSH configuration
            assert self.ssh_target, (
                "ssh_target required in legacy mode (or provide available_targets for targets mode)"
            )
            assert "@" in self.ssh_target, (
                f"ssh_target missing '@' (must be user@host:port): {self.ssh_target}"
            )
            assert ":" in self.ssh_target, (
                f"ssh_target missing ':' (must be user@host:port): {self.ssh_target}"
            )
        else:
            # Targets mode: ssh_target optional (targets contain their own SSH config)
            assert len(self.available_targets) > 0, (
                "available_targets cannot be empty (or provide ssh_target for legacy mode)"
            )

    def get_tools(self) -> list[Tool]:
        """Return tools available to agent.

        Simplified environment provides only write_kernel.
        """
        return [write_kernel_tool]

    async def on_assistant_message(self, message: Message, state: AgentState) -> AgentState:
        """Hook called when assistant sends a message (no-op for this environment)."""
        return state

    async def serialize(self) -> dict:
        """Serialize environment state for checkpointing."""
        from dataclasses import asdict

        from wafer_core.utils.environment_serialization import serialize_environment_checkpoint

        # Serialize available_targets to JSON-safe dicts
        serialized_targets = None
        if self.available_targets is not None:
            serialized_targets = [asdict(target) for target in self.available_targets]

        return serialize_environment_checkpoint(
            sample_data=self.sample_data,
            ssh_target=self.ssh_target,  # Can be None for Modal-only
            ssh_key=self.ssh_key,
            gpu_ids=self.gpu_ids,
            deployment_state=self._deployment_state,
            workspace_dir=str(self.workspace_dir) if self.workspace_dir else None,
            additional_data={
                "_initialized": self._initialized,
                "artifacts_dir": str(self.artifacts_dir) if self.artifacts_dir else None,
                "profile_on_success": self.profile_on_success,
                "ncu_on_success": self.ncu_on_success,
                # Serialize available_targets as JSON-safe dicts
                "available_targets": serialized_targets,
                # Serialize submission tracking (required for serialize/deserialize cycle in agent loop)
                "submissions": [asdict(s) for s in self.submissions],
                "best_submission": asdict(self.best_submission) if self.best_submission else None,
            },
        )

    async def exec_tool(
        self,
        tool_call: ToolCall,
        current_state: AgentState,
        run_config: Any,
        checkpoint_store: Any = None,
        cancel_scope: Any = None,
    ) -> ToolResult:
        """Execute a tool call."""
        # Setup workspace on first tool use
        if not self._initialized:
            await self.setup_remote_environment()

        # Route to write_kernel handler
        if tool_call.name == "write_kernel":
            return await self._write_kernel(
                tool_call.args["filepath"], tool_call.args["code"], current_state
            )
        else:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Unknown tool: {tool_call.name}",
            )

    def requires_confirmation(self, tool_call: ToolCall) -> bool:
        """Whether this tool requires user confirmation."""
        return False

    async def setup_remote_environment(self) -> None:
        """Setup remote environment (one-time deployment).

        Uses pure function from wafer_core.utils.remote_execution.
        """
        if self._initialized:
            logger.debug("   Remote environment already initialized, skipping setup")
            return

        # Log processing info (only once, on first setup)
        logger.info(f"processing sample: {BENCHMARK_NAME} problem {self.problem_id}")

        # Create local workspace directory (per-sample isolation)
        import tempfile

        workspace_root = Path(tempfile.mkdtemp(prefix="kernel_workspace_"))
        self.workspace_dir = workspace_root

        assert self.workspace_dir is not None
        assert self.workspace_dir.exists()

        logger.debug(f"created local workspace: {self.workspace_dir}")

        # Write reference files to workspace (for workspace persistence)
        reference_code = self.sample_data.get("reference_code")
        if reference_code:
            (self.workspace_dir / "reference_kernel.py").write_text(reference_code)
            logger.debug("wrote reference_kernel.py to workspace")

        task_py = self.sample_data.get("task_py")
        if task_py:
            (self.workspace_dir / "task.py").write_text(task_py)
            logger.debug("wrote task.py to workspace")

        # ONLY setup SSH deployment if using legacy mode (no available_targets)
        if self.available_targets is None:
            # Type assertion: In legacy mode, ssh_target must be set (validated in __post_init__)
            assert self.ssh_target is not None, "ssh_target required in legacy mode"
            logger.debug(f"ssh: {self.ssh_target}, gpu: {self.gpu_id}")

            # Use pure function for remote deployment
            state, err = await setup_remote_deployment(
                ssh_target=self.ssh_target,
                ssh_key=self.ssh_key,
                gpu_id=self.gpu_id,
                benchmark_name=BENCHMARK_NAME,
            )

            if err:
                raise RemoteDeploymentError(err)

            self._deployment_state = state
        else:
            # Targets mode: deployment happens lazily per-target in run_operation_on_target()
            logger.debug(f"using pluggable targets: {[t.name for t in self.available_targets]}")

        self._initialized = True

    def _format_error_feedback(self, submission: KernelSubmission) -> str:
        """Format feedback for compilation/execution errors."""
        error_section = submission.compile_error or "Unknown error"

        return f"""Kernel compilation/execution failed (Attempt {submission.attempt_number}):

{error_section}

Please fix the error and submit a corrected version."""

    def _format_failed_tests(self, failed_tests: list[dict], max_tests: int = 3) -> str:
        """Format details of failed tests for feedback.

        Args:
            failed_tests: List of failed test dicts from correctness_tests
            max_tests: Maximum number of tests to show details for

        Returns:
            Formatted string with test failure details
        """
        if not failed_tests:
            return ""

        lines = []
        shown = 0

        for test in failed_tests[:max_tests]:
            test_name = test.get("test_name", "unknown")
            error_msg = test.get("error_msg", "")
            error_type = test.get("error_type", "")
            test_params = test.get("test_params", "")

            # Format test header
            lines.append(f"  ❌ {test_name}")
            if test_params:
                lines.append(f"     Parameters: {test_params}")

            # Format error details
            if error_type:
                lines.append(f"     Error type: {error_type}")

            if error_msg:
                # Truncate very long error messages but show enough context
                error_lines = error_msg.split("\n")
                if len(error_lines) > 10:
                    # Show first 5 and last 3 lines
                    truncated = error_lines[:5] + ["     ..."] + error_lines[-3:]
                    error_text = "\n".join(f"     {line}" for line in truncated)
                else:
                    error_text = "\n".join(f"     {line}" for line in error_lines)
                lines.append(f"     Details:\n{error_text}")

            lines.append("")  # Blank line between tests
            shown += 1

        # Note if more tests failed
        remaining = len(failed_tests) - shown
        if remaining > 0:
            lines.append(f"  ... and {remaining} more test(s) failed")

        return "\n".join(lines)

    def _format_success_feedback(self, submission: KernelSubmission) -> str:
        """Format feedback for successful execution."""
        # Build correctness summary
        if submission.all_correct:
            correctness_summary = "✅ All correctness tests passed!"
        else:
            passed = submission.raw_results.get("passed_tests", 0) if submission.raw_results else 0
            total = submission.raw_results.get("total_tests", 0) if submission.raw_results else 0
            correctness_summary = f"⚠️  Correctness: {passed}/{total} tests passed ({submission.correctness_score:.1%})"

        # Build performance summary
        perf_summary = f"Performance: {submission.geomean_speedup:.2f}x speedup vs reference"

        # Best submission marker
        is_best = self.best_submission == submission
        best_marker = " (NEW BEST!)" if is_best else ""

        # Build failed test details if not all correct
        failed_tests_section = ""
        if not submission.all_correct and submission.raw_results:
            correctness_tests = submission.raw_results.get("correctness_tests", [])
            failed_tests = [t for t in correctness_tests if not t.get("is_correct", True)]
            if failed_tests:
                failed_tests_section = (
                    f"\nFailed tests:\n{self._format_failed_tests(failed_tests)}\n"
                )

        # Build final message
        if submission.all_correct:
            closing = "Great! All tests passed."
        else:
            closing = "Please fix the failing tests before optimizing performance."

        return f"""Kernel test results (Attempt {submission.attempt_number}){best_marker}:

{correctness_summary}

{perf_summary}
{failed_tests_section}
{closing}"""

    def _is_better_than_best(self, submission: KernelSubmission) -> bool:
        """Check if submission is better than current best.

        Criteria:
        1. Correctness first (must pass all tests)
        2. Then performance (higher speedup)
        """
        if not self.best_submission:
            return True

        # Prioritize correctness
        if submission.all_correct and not self.best_submission.all_correct:
            return True
        if not submission.all_correct and self.best_submission.all_correct:
            return False

        # Both correct or both incorrect - compare performance
        return submission.geomean_speedup > self.best_submission.geomean_speedup

    async def _write_kernel(
        self, filepath: str, code: str, current_state: AgentState
    ) -> ToolResult:
        """Write kernel file to workspace and automatically submit for testing.

        This is the single tool that combines write + submit.
        """
        # workspace_dir must be set during _ensure_deployed (programmer error if None)
        assert self.workspace_dir is not None, (
            "workspace_dir not initialized - call _ensure_deployed first"
        )

        # Write to workspace using pure function
        write_result = await write_file(filepath, code, self.workspace_dir)
        if write_result.is_error:
            return ToolResult(
                is_error=True,
                content="",
                error=write_result.error,
            )

        logger.debug(f"wrote kernel to workspace: {filepath} ({len(code)} chars)")
        logger.debug(f"attempt: {len(self.submissions) + 1}")

        # Create submission record
        submission = KernelSubmission(filepath=filepath, attempt_number=len(self.submissions) + 1)

        # Validate language requirements (CuteDSL)
        is_valid, validation_error = validate_language_requirements(code, self.language)
        if not is_valid:
            logger.warning(f"⚠️  Language validation failed: {validation_error}")
            eval_results = create_validation_error_result(validation_error, self.language)

            # Treat as compilation failure
            submission.compiled = False
            submission.compile_error = eval_results.get("error_message", "Validation failed")
            self.submissions.append(submission)

            error_msg = self._format_error_feedback(submission)
            logger.info("tests failed: validation error")

            return ToolResult(is_error=True, content="", error=error_msg)

        # Execute on remote GPU using pure function
        logger.info(f"testing kernel on remote gpu (problem: {self.problem_id})")

        # Create execution context (used by both legacy and pluggable target paths)
        context = KernelExecutionContext(
            problem_id=self.problem_id,
            sample_data=self.sample_data,
            test_suite=self.test_suite,
            reference_backend=self.reference_backend,
            benchmark_name=BENCHMARK_NAME,
            benchmark_suite=self.benchmark_suite,
            language=None,  # GPUMode doesn't use language filter
        )

        # Create profiling config (used by both legacy and pluggable target paths)
        profiling_config = ProfilingArtifactConfig(
            profile_on_success=self.profile_on_success,
            ncu_on_success=self.ncu_on_success,
            artifacts_dir=self.artifacts_dir,
        )

        # Phase 4: Check if pluggable targets are enabled
        if self.available_targets is not None:
            # NEW: Use pluggable target system
            from wafer_core.utils.kernel_utils.targets import (
                run_operation_on_target,
                select_target_for_operation,
            )

            # Select target for correctness operation
            target = select_target_for_operation("correctness", self.available_targets)
            if target is None:
                return ToolResult(
                    is_error=True,
                    content="",
                    error="No capable target available for correctness testing",
                )

            logger.debug(f"   Selected target for correctness: {target.name}")

            # Run on selected target (with deployment state caching)
            eval_results, err = await run_operation_on_target(
                operation="correctness",
                target=target,
                kernel_code=code,
                context=context,
                profiling_config=profiling_config,
                check_availability=True,
                deployment_state_cache=self._deployment_state_cache,
            )

            if err:
                # Treat as compilation/execution failure
                submission.compiled = False
                submission.compile_error = err
                self.submissions.append(submission)

                error_msg = self._format_error_feedback(submission)
                logger.info(f"tests failed: {err}")

                return ToolResult(is_error=True, content="", error=error_msg)

        else:
            # LEGACY: Use direct deployment (backward compatibility)
            # _deployment_state must be set during _ensure_deployed (programmer error if None)
            assert self._deployment_state is not None, (
                "_deployment_state not initialized - call _ensure_deployed first"
            )

            eval_results = await execute_kernel_remote(
                deployment_state=self._deployment_state,
                kernel_code=code,
                context=context,
                profiling_config=profiling_config,
            )

        # Type narrowing: execute_kernel_remote always returns dict, never None
        assert eval_results is not None, "eval_results should not be None"

        if not eval_results["compiled"]:
            # Compilation failure
            submission.compiled = False
            submission.compile_error = eval_results.get("error_message", "Unknown error")
            self.submissions.append(submission)

            error_msg = self._format_error_feedback(submission)
            logger.info("tests failed: compilation error")

            return ToolResult(is_error=True, content="", error=error_msg)
        else:
            # Success - parse results
            submission.compiled = True
            submission.correctness_score = eval_results["correctness_score"]
            submission.geomean_speedup = eval_results["geomean_speedup"]
            submission.all_correct = eval_results["all_correct"]
            submission.raw_results = eval_results

            self.submissions.append(submission)

            # Update best submission
            if self._is_better_than_best(submission):
                self.best_submission = submission
                logger.debug("new best submission")

            success_msg = self._format_success_feedback(submission)

            if submission.all_correct:
                logger.info(
                    f"tests complete: all correct, speedup={submission.geomean_speedup:.2f}x"
                )
            else:
                passed = eval_results.get("passed_tests", 0)
                total = eval_results.get("total_tests", 0)
                logger.info(
                    f"tests complete: {passed}/{total} passed, speedup={submission.geomean_speedup:.2f}x"
                )

            return ToolResult(is_error=False, content=success_msg, error=None)

    async def on_tool_call(self, tool_name: str, tool_args: dict, state: AgentState) -> ToolResult:
        """Handle tool calls from agent (deprecated - use exec_tool instead)."""
        # For backwards compatibility with older rollouts versions
        from wafer_core.rollouts.dtypes import ToolCall

        tool_call = ToolCall(id="", name=tool_name, args=tool_args)

        return await self.exec_tool(tool_call, state, None, None)

    @staticmethod
    async def deserialize(data: dict) -> "GPUModeSimpleEnvironment":
        """Deserialize environment from checkpoint.

        Uses pure function from wafer_core.utils.environment_serialization.
        """
        from wafer_core.utils.environment_serialization import deserialize_environment_checkpoint
        from wafer_core.utils.kernel_utils.targets import BaremetalTarget, ModalTarget, VMTarget

        checkpoint = deserialize_environment_checkpoint(data)

        # Reconstruct available_targets from serialized dicts
        available_targets = None
        if checkpoint.get("available_targets") is not None:
            available_targets = []
            for target_dict in checkpoint["available_targets"]:
                # Determine target type by checking for unique fields
                if "modal_app_name" in target_dict:
                    available_targets.append(ModalTarget(**target_dict))
                elif "ncu_available" in target_dict and target_dict["ncu_available"]:
                    # Baremetal typically has NCU support
                    available_targets.append(BaremetalTarget(**target_dict))
                else:
                    # VM or baremetal without NCU
                    available_targets.append(VMTarget(**target_dict))

        env = GPUModeSimpleEnvironment(
            sample_data=checkpoint["sample_data"],
            ssh_target=checkpoint["ssh_target"],
            ssh_key=checkpoint.get("ssh_key", "~/.ssh/id_ed25519"),
            gpu_ids=checkpoint.get("gpu_ids", [checkpoint.get("gpu_id", DEFAULT_GPU_ID)]),
            profile_on_success=checkpoint.get("profile_on_success", False),
            ncu_on_success=checkpoint.get("ncu_on_success", False),
            artifacts_dir=Path(checkpoint["artifacts_dir"])
            if checkpoint.get("artifacts_dir")
            else None,
            # Restore available_targets with reconstructed objects
            available_targets=available_targets,
        )

        # Restore workspace_dir and initialization state
        if checkpoint.get("workspace_dir"):
            env.workspace_dir = Path(checkpoint["workspace_dir"])
        env._initialized = checkpoint.get("_initialized", False)

        # Restore deployment state if it exists (deserialization helper reconstructs it)
        if checkpoint.get("deployment_state"):
            env._deployment_state = checkpoint["deployment_state"]

        # Restore submission tracking
        if checkpoint.get("submissions"):
            env.submissions = [KernelSubmission(**s) for s in checkpoint["submissions"]]
        if checkpoint.get("best_submission"):
            env.best_submission = KernelSubmission(**checkpoint["best_submission"])

        return env


async def create_environment(sample_data: dict, config: Any) -> GPUModeSimpleEnvironment:
    """Factory function to create environment for a sample.

    This is called by the evaluation framework for each sample in the dataset.

    Args:
        sample_data: Dataset sample with problem description, test suite, etc.
        config: Evaluation config with SSH target and other settings

    Returns:
        Fresh GPUModeSimpleEnvironment instance
    """
    # Extract gpu_ids from config
    if hasattr(config, "environment_config"):
        gpu_ids = config.environment_config.get("gpu_ids", [config.gpu_id])
    else:
        gpu_ids = [config.gpu_id]

    # Extract available_targets from config (Phase 4)
    available_targets = None
    if hasattr(config, "environment") and hasattr(config.environment, "available_targets"):
        available_targets = config.environment.available_targets

    return GPUModeSimpleEnvironment(
        sample_data=sample_data,
        ssh_target=config.ssh_target,
        gpu_ids=gpu_ids,
        artifacts_dir=getattr(config, "artifacts_dir", None),
        available_targets=available_targets,
    )
