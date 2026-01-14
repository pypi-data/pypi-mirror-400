"""Shared types for kernel execution across different backends.

These dataclasses are used by both SSH (remote_execution) and Modal backends
to pass execution context and configuration.

Tiger Style:
- Pure data structures (no logic)
- Immutable (frozen=True)
- No external dependencies (only stdlib + Path)
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KernelExecutionContext:
    """Context for kernel execution (problem, test suite, benchmark info).

    Groups the problem identification and test configuration together.
    Used by both SSH and Modal execution backends.
    """

    problem_id: str
    sample_data: dict
    test_suite: str
    reference_backend: str
    benchmark_name: str
    benchmark_suite: str
    language: str | None = None


@dataclass(frozen=True)
class ProfilingArtifactConfig:
    """Configuration for profiling and artifact collection.

    Controls whether to run profiling and where to save artifacts.
    Used by both SSH and Modal execution backends.
    """

    profile_on_success: bool = False
    ncu_on_success: bool = False
    artifacts_dir: Path | None = None
