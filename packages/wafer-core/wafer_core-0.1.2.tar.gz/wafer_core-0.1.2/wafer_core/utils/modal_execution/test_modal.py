#!/usr/bin/env python3
"""Standalone test for Modal execution backend.

Tests Modal execution independently of the main codebase.

Usage:
    # Set Modal credentials (or pass explicitly)
    export MODAL_TOKEN_ID="ak-xxx"
    export MODAL_TOKEN_SECRET="as-yyy"

    # Run test
    python wafer_utils/modal_execution/test_modal.py

    # Or with explicit credentials
    python wafer_utils/modal_execution/test_modal.py --token-id ak-xxx --token-secret as-yyy
"""

import argparse
import asyncio
import logging

from wafer_core.utils.execution_types import KernelExecutionContext, ProfilingArtifactConfig
from wafer_core.utils.modal_execution import (
    execute_kernel_modal,
    setup_modal_deployment,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Test Kernels
# ══════════════════════════════════════════════════════════════════════════════


SIMPLE_KERNEL = """
import torch

def custom_kernel(x: torch.Tensor) -> torch.Tensor:
    '''Simple test kernel: multiply by 2.'''
    return x * 2
"""

REFERENCE_KERNEL = """
import torch

def ref_kernel(x: torch.Tensor) -> torch.Tensor:
    '''Reference: multiply by 2.'''
    return x * 2

def generate_input(input_shape, seed):
    '''Generate test input tensors.'''
    torch.manual_seed(seed)
    return torch.randn(input_shape, device='cuda')
"""

# Test cases for simple kernel
TEST_CASES = [
    {"input_shape": [10], "seed": 42},
    {"input_shape": [100], "seed": 123},
]

BENCHMARK_CASES = [
    {"input_shape": [1000], "seed": 42},
]


# ══════════════════════════════════════════════════════════════════════════════
# Test Functions
# ══════════════════════════════════════════════════════════════════════════════


async def test_modal_setup(
    token_id: str | None = None,
    token_secret: str | None = None,
    workspace: str | None = None,
) -> None:
    """Test Modal deployment setup."""
    logger.info("=" * 80)
    logger.info("TEST: Modal Setup")
    logger.info("=" * 80)

    state, err = await setup_modal_deployment(
        modal_token_id=token_id,
        modal_token_secret=token_secret,
        modal_workspace=workspace,
        app_name="test-kernel-eval",
        gpu_type="B200",
    )

    if err:
        logger.error(f"❌ Setup failed: {err}")
        return

    # Type narrowing: if no error, state must be non-None
    assert state is not None, "state should not be None when err is None"

    logger.info("✅ Setup successful")
    logger.info(f"   App: {state.app_name}")
    logger.info(f"   GPU: {state.gpu_type}")
    logger.info(f"   Timeout: {state.timeout_seconds}s")


async def test_modal_execution(
    token_id: str | None = None,
    token_secret: str | None = None,
    workspace: str | None = None,
) -> None:
    """Test Modal kernel execution."""
    logger.info("=" * 80)
    logger.info("TEST: Modal Execution")
    logger.info("=" * 80)

    # Setup
    state, err = await setup_modal_deployment(
        modal_token_id=token_id,
        modal_token_secret=token_secret,
        modal_workspace=workspace,
        app_name="test-kernel-eval",
        gpu_type="B200",
    )

    if err:
        logger.error(f"❌ Setup failed: {err}")
        return

    # Type narrowing: if no error, state must be non-None
    assert state is not None, "state should not be None when err is None"

    # Create execution context
    context = KernelExecutionContext(
        problem_id="test_simple_kernel",
        sample_data={
            "reference_code": REFERENCE_KERNEL,
            "tests": TEST_CASES,
            "benchmarks": BENCHMARK_CASES,
        },
        test_suite="test_correctness",
        reference_backend="reference",
        benchmark_name="test",
        benchmark_suite="test_benchmark",
        language="pytorch",
    )

    profiling_config = ProfilingArtifactConfig(
        profile_on_success=False,  # Skip profiling for simple test
        ncu_on_success=False,
    )

    # Execute
    logger.info("Executing kernel on Modal...")
    results = await execute_kernel_modal(
        modal_state=state,
        kernel_code=SIMPLE_KERNEL,
        context=context,
        profiling_config=profiling_config,
    )

    # Check results
    logger.info("-" * 80)
    logger.info("Results:")
    logger.info(f"  Compiled: {results['compiled']}")
    logger.info(f"  Error: {results.get('error_message')}")
    logger.info(f"  Correctness: {results['correctness_score']}")
    logger.info(f"  All Correct: {results['all_correct']}")
    logger.info(f"  Speedup: {results['geomean_speedup']:.2f}x")
    logger.info(f"  Tests: {results['passed_tests']}/{results['total_tests']}")

    if results["compiled"] and results["all_correct"]:
        logger.info("✅ Execution successful - kernel passed all tests!")
    elif results["compiled"]:
        logger.warning("⚠️  Kernel compiled but some tests failed")
    else:
        logger.error("❌ Kernel compilation failed")


async def test_full_flow(
    token_id: str | None = None,
    token_secret: str | None = None,
    workspace: str | None = None,
) -> None:
    """Test complete Modal execution flow."""
    logger.info("=" * 80)
    logger.info("FULL TEST: Modal Backend")
    logger.info("=" * 80)

    await test_modal_setup(token_id, token_secret, workspace)
    print()
    await test_modal_execution(token_id, token_secret, workspace)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test Modal execution backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use environment variables (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
  python test_modal.py

  # Explicit credentials
  python test_modal.py --token-id ak-xxx --token-secret as-yyy

  # With workspace
  python test_modal.py --workspace my-team

  # Run specific test
  python test_modal.py --test setup
  python test_modal.py --test execution
""",
    )

    parser.add_argument(
        "--token-id",
        help="Modal token ID (or use MODAL_TOKEN_ID env var)",
    )
    parser.add_argument(
        "--token-secret",
        help="Modal token secret (or use MODAL_TOKEN_SECRET env var)",
    )
    parser.add_argument(
        "--workspace",
        help="Modal workspace name (optional)",
    )
    parser.add_argument(
        "--test",
        choices=["setup", "execution", "full"],
        default="full",
        help="Which test to run (default: full)",
    )

    args = parser.parse_args()

    # Run selected test
    if args.test == "setup":
        await test_modal_setup(args.token_id, args.token_secret, args.workspace)
    elif args.test == "execution":
        await test_modal_execution(args.token_id, args.token_secret, args.workspace)
    else:
        await test_full_flow(args.token_id, args.token_secret, args.workspace)


if __name__ == "__main__":
    asyncio.run(main())
