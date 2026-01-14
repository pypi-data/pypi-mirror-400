"""Modal app for serverless kernel evaluation.

This module defines the Modal app that runs kernel evaluation on serverless GPUs.
It reuses the same evaluate.py logic as the SSH backend.

Tiger Style:
- Reuse existing evaluation logic (DRY)
- Explicit dependencies in Modal image
- Clear function signatures
"""

from pathlib import Path

import modal

# ══════════════════════════════════════════════════════════════════════════════
# Modal Image Configuration
# ══════════════════════════════════════════════════════════════════════════════


# Build Modal image with all dependencies
# This image is cached and reused across function invocations
def build_modal_image(
    gpu_type: str = "B200",
    compute_capability: str = "10.0",
) -> modal.Image:
    """Build Modal image with PyTorch, CUTLASS, and evaluation dependencies.

    Uses explicit local code inclusion to avoid pulling in SSH deployment code.

    Phase 2 solution from MODAL_HANDOFF.md:
    - Use add_local_dir with ignore parameter to exclude deployment files
    - Only include files needed for kernel evaluation

    Args:
        gpu_type: GPU type (determines PyTorch index URL)
        compute_capability: CUDA compute capability

    Returns:
        Modal Image ready for kernel evaluation
    """
    # Determine PyTorch index based on GPU type
    # Match logic from configs/base_config.py
    if gpu_type in ["B200", "GB200"] or compute_capability.startswith("10."):
        # Blackwell requires PyTorch 2.8+ with CUDA 12.8
        torch_index = "https://download.pytorch.org/whl/nightly/cu128"
        torch_version = "torch>=2.8.0"
    else:
        # Older GPUs (H100, A100) use stable PyTorch
        torch_index = "https://download.pytorch.org/whl/cu124"
        torch_version = "torch>=2.4.0"

    # Build image with dependencies
    image = (
        modal.Image.debian_slim(python_version="3.10")
        # System dependencies
        .apt_install("git", "build-essential")
        # PyTorch (GPU-specific index)
        .pip_install(
            torch_version,
            index_url=torch_index,
            extra_index_url="https://pypi.org/simple",
        )
        # CUDA toolkit dependencies
        .pip_install(
            "triton",
            "ninja",
            index_url="https://pypi.nvidia.com",
            extra_index_url="https://pypi.org/simple",
        )
        # Evaluation dependencies
        .pip_install(
            "numpy",
            "scipy",
            "pytest",
        )
        # Create empty __init__.py files for proper Python package structure
        # MUST run before add_local_* commands (Modal restriction)
        .run_commands(
            "mkdir -p /root/wafer_core/utils",
            "touch /root/wafer_core/__init__.py",
            "touch /root/wafer_core/utils/__init__.py",
        )
        # Add only kernel evaluation utilities (avoid rollouts dependency)
        # wafer_core/utils/ contains files that import rollouts (workspace_tools.py, etc.)
        # We only need the kernel_utils/ subdirectory + exceptions.py + ncu_profile_tools.py
        .add_local_dir(
            local_path=Path(__file__).parent.parent
            / "kernel_utils",  # wafer_core/utils/kernel_utils/
            remote_path="/root/wafer_core/utils/kernel_utils",
        )
        .add_local_file(
            local_path=Path(__file__).parent.parent
            / "exceptions.py",  # wafer_core/utils/exceptions.py
            remote_path="/root/wafer_core/utils/exceptions.py",
        )
        .add_local_file(
            local_path=Path(__file__).parent.parent
            / "ncu_profile_tools.py",  # wafer_core/utils/ncu_profile_tools.py
            remote_path="/root/wafer_core/utils/ncu_profile_tools.py",
        )
    )

    return image


# ══════════════════════════════════════════════════════════════════════════════
# Modal App Definition
# ══════════════════════════════════════════════════════════════════════════════


# Create app (can be customized per target)
def create_modal_app(
    app_name: str = "test-kernel-eval",  # Match test script default
    gpu_type: str = "B200",
    compute_capability: str = "10.0",
) -> modal.App:
    """Create Modal app for kernel evaluation.

    Args:
        app_name: Modal app name
        gpu_type: GPU type for image building
        compute_capability: CUDA compute capability

    Returns:
        Modal App instance
    """
    image = build_modal_image(gpu_type=gpu_type, compute_capability=compute_capability)
    return modal.App(name=app_name, image=image)


# Default app (can be overridden)
app = create_modal_app()


# ══════════════════════════════════════════════════════════════════════════════
# Modal Function - Kernel Evaluation
# ══════════════════════════════════════════════════════════════════════════════


@app.function(
    gpu="B200",  # Can be overridden per invocation
    timeout=600,  # 10 minute timeout
    cpu=4,  # CPUs for kernel compilation
    memory=16384,  # 16GB RAM
)
def run_kernel_evaluation(
    kernel_code: str,
    reference_code: str,
    problem_id: str,
    test_suite: str,
    benchmark_suite: str,
    reference_backend: str,
    test_cases: list[dict],
    benchmark_cases: list[dict],
    language: str = "pytorch",
    profile: bool = False,
) -> dict:
    """Run kernel evaluation on Modal GPU.

    This function reuses the same evaluation logic as the SSH backend.
    It creates a temporary workspace, writes the kernel and reference files,
    and runs evaluate.py.

    Args:
        kernel_code: Kernel implementation code
        reference_code: Reference implementation code
        problem_id: Problem identifier
        test_suite: Test suite name (e.g., "gpumode_correctness")
        benchmark_suite: Benchmark suite name (e.g., "gpumode_benchmark")
        reference_backend: Reference backend name (e.g., "reference")
        test_cases: List of test case dicts
        benchmark_cases: List of benchmark case dicts
        language: Language/framework (e.g., "pytorch", "cute")
        profile: Whether to run torch profiler

    Returns:
        Dict with evaluation results including per-test details:
        {
            "compiled": bool,
            "error_message": str | None,
            "correctness_score": float,
            "geomean_speedup": float,
            "all_correct": bool,
            "passed_tests": int,
            "total_tests": int,
            "correctness_tests": list[dict],  # Per-test results with errors
            "performance_tests": list[dict],  # Per-test benchmark results
        }
    """
    import tempfile
    from pathlib import Path

    import torch

    from wafer_core.utils.kernel_utils.evaluate import (
        EvaluationArtifactConfig,
        run_evaluation_full,
    )
    from wafer_core.utils.kernel_utils.task import TestCase

    try:
        # Verify GPU is available
        if not torch.cuda.is_available():
            return {
                "compiled": False,
                "error_message": "CUDA not available in Modal container",
                "correctness_score": 0.0,
                "geomean_speedup": 0.0,
                "all_correct": False,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "correctness_tests": [],
                "performance_tests": [],
            }

        # Create temporary directory for kernel files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write kernel code to file
            kernel_file = tmp_path / "kernel.py"
            kernel_file.write_text(kernel_code)

            # Write reference code to file with the expected name
            # TestCase.generate() imports from 'reference_kernel', not 'reference'
            reference_file = tmp_path / "reference_kernel.py"
            reference_file.write_text(reference_code)

            # Convert test_cases dicts to TestCase objects
            test_case_objects = [
                TestCase(params=tc, name=f"test_{i + 1}") for i, tc in enumerate(test_cases)
            ]

            # Configure evaluation (no artifacts, no profiling for Modal)
            artifact_config = EvaluationArtifactConfig(
                run_profiling=profile,
                create_artifact=False,  # Don't create artifacts in Modal
                run_dir=None,
            )

            # Change working directory to temp path so TestCase.generate() can import reference_kernel
            # TestCase.generate() does: from reference_kernel import generate_input
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)

                # Run evaluation using the full results API
                eval_result = run_evaluation_full(
                    implementation_path=str(kernel_file),
                    reference_path=str(reference_file),
                    test_cases=test_case_objects,
                    run_benchmarks=True,  # Always run benchmarks
                    artifact_config=artifact_config,
                )
            finally:
                # Restore original working directory
                os.chdir(original_cwd)

            # Convert to dict with full details
            result = eval_result.to_dict()

            # Add GPU info
            result["gpu_info"] = {
                "available": True,
                "name": torch.cuda.get_device_name(0),
            }

            return result

    except Exception as e:
        # Return error with traceback
        import traceback

        error_trace = traceback.format_exc()
        return {
            "compiled": False,
            "error_message": f"{str(e)}\n\nTraceback:\n{error_trace}",
            "correctness_score": 0.0,
            "geomean_speedup": 0.0,
            "all_correct": False,
            "passed_tests": 0,
            "total_tests": len(test_cases),
            "correctness_tests": [],
            "performance_tests": [],
        }


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════


@app.function()
def health_check() -> dict:
    """Simple health check to verify Modal app is working.

    Returns:
        Dict with status and GPU info
    """
    import torch

    return {
        "status": "ok",
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }
