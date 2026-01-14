"""Data types for the capture module."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ExecutionResult:
    """Result of executing a command."""

    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    start_time: datetime
    end_time: datetime


@dataclass(frozen=True)
class FileInfo:
    """Information about a single file."""

    path: Path  # Relative path from working directory
    size: int  # Size in bytes
    mtime: float  # Modification time (Unix timestamp)
    checksum: str | None = None  # SHA256 checksum (optional, computed on demand)


@dataclass(frozen=True)
class DirectorySnapshot:
    """Snapshot of directory state at a point in time."""

    files: dict[Path, FileInfo]  # Path -> FileInfo mapping
    timestamp: datetime
    root: Path  # Root directory of snapshot


@dataclass(frozen=True)
class ArtifactDiff:
    """Difference between two directory snapshots."""

    new_files: list[Path]  # Files created
    modified_files: list[Path]  # Files modified
    deleted_files: list[Path]  # Files deleted


@dataclass(frozen=True)
class GitContext:
    """Git repository context."""

    repo_url: str | None = None  # Remote URL (e.g., "https://github.com/user/repo")
    commit_hash: str | None = None  # Full commit SHA
    branch: str | None = None  # Current branch name
    is_dirty: bool = False  # Whether working directory has uncommitted changes


@dataclass(frozen=True)
class GPUContext:
    """GPU hardware context."""

    model: str | None = None  # GPU model (e.g., "H100", "A100")
    driver_version: str | None = None  # Driver version
    cuda_version: str | None = None  # CUDA version


@dataclass(frozen=True)
class SystemContext:
    """System information context."""

    hostname: str | None = None
    platform: str | None = None  # e.g., "Linux", "Darwin"
    python_version: str | None = None


@dataclass(frozen=True)
class CaptureContext:
    """Complete execution context."""

    git: GitContext
    gpu: GPUContext
    system: SystemContext
    working_dir: Path
    environment_variables: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MetricsResult:
    """Extracted metrics from execution."""

    stdout_metrics: dict[str, float] = field(default_factory=dict)
    ncu_metrics: dict[str, float] | None = None
    ncu_file_path: Path | None = None


@dataclass
class CaptureConfig:
    label: str
    command: str
    working_dir: Path
    variant: str | None = None
    code_denylist: list[str] = field(
        default_factory=lambda: [
            "*.o", "*.so", "*.a", "*.exe", "*.dll", "*.dylib",
            "**/venv/**", "**/node_modules/**", "**/build/**", "**/__pycache__/**", "**/.git/**",
            "*.npy", "*.pt", "*.pth", "*.safetensors", "*.ckpt",
            "*.pyc", "*.pyo",
        ]
    )
    artifact_denylist: list[str] = field(
        default_factory=lambda: [
            "*.o", "*.so", "*.a", "*.exe", "*.dll", "*.dylib",
            "**/venv/**", "**/node_modules/**", "**/build/**", "**/__pycache__/**",
            "*.pyc", "*.pyo",
        ]
    )
    env_vars: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class CaptureResult:
    id: str
    label: str
    variant: str | None
    command: str
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    context: CaptureContext
    metrics: MetricsResult
    artifacts: list[Path]
    code_files: dict[Path, str]
    created_at: datetime
    tags: list[str] = field(default_factory=list)
