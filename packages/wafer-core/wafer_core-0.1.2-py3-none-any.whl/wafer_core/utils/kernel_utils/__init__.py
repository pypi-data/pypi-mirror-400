"""Kernel utilities for NVFP4 testing.

Provides type definitions, verification utilities, and benchmarking
tools for GPU kernel testing.

NOTE: Most imports are lazy to avoid requiring torch in environments
that only use deployment utilities.
"""

from typing import Any

# Only import deployment utilities by default (no torch dependency)
# Other utilities are imported lazily when needed


def __getattr__(name: str) -> Any:
    """Lazy imports to avoid requiring torch in deployment-only environments."""
    if name in ("input_t", "output_t", "TestCase"):
        from wafer_core.utils.kernel_utils.task import (  # noqa: F401
            TestCase,
            input_t,
            output_t,
        )

        return locals()[name]

    if name in (
        "allclose_with_error",
        "make_match_reference",
        "benchmark_kernel",
        "benchmark_vs_reference",
        "compare_backends",
    ):
        from wafer_core.utils.kernel_utils.utils import (  # noqa: F401
            allclose_with_error,
            benchmark_kernel,
            benchmark_vs_reference,
            compare_backends,
            make_match_reference,
        )

        return locals()[name]

    if name in ("CorrectnessResult", "PerformanceResult", "BackendResults", "TestSuiteResults"):
        from wafer_core.utils.kernel_utils.results import (  # noqa: F401
            BackendResults,
            CorrectnessResult,
            PerformanceResult,
            TestSuiteResults,
        )

        return locals()[name]

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = [  # noqa: F822
    # Type aliases
    "input_t",
    "output_t",
    # Test structures
    "TestCase",
    # Verification utilities
    "allclose_with_error",
    "make_match_reference",
    "benchmark_kernel",
    "benchmark_vs_reference",
    "compare_backends",
    # Result structures
    "CorrectnessResult",
    "PerformanceResult",
    "BackendResults",
    "TestSuiteResults",
]
