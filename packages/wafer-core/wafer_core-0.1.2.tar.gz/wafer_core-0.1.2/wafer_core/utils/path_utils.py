"""Path utilities for research codebase.

Centralized path resolution and sys.path management to eliminate
repetitive and fragile path manipulation code.

Tiger Style:
- Pure functions (no hidden state)
- Explicit error handling
- Use pathlib exclusively
"""

import sys
from pathlib import Path

from wafer_core.utils.exceptions import BenchmarkNameInferenceError, ResearchRootNotFoundError


def get_research_root(file_path: Path) -> Path:
    """Resolve research root directory from any file location.

    Walks up the directory tree from file_path to find the research root.
    Research root is identified by the presence of 'wafer_utils' directory.
    Note: 'rollouts' is installed as a package dependency, not a local directory.

    Supports two layouts:
    1. Old layout: research/wafer_utils/... (research root has wafer_utils/)
    2. New layout: wafer/research/async-wevin/wafer_utils/... (look for research/async-wevin)

    Args:
        file_path: Path to any file in the research tree

    Returns:
        Path to research root directory

    Raises:
        RuntimeError: If research root cannot be found
    """
    current = file_path.resolve() if file_path.is_file() else file_path

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Check if this looks like research root (has wafer_utils/ directory)
        # Note: rollouts is installed as a package, not a local directory
        if (parent / "wafer_utils").is_dir():
            return parent

    # Fallback: look for wafer monorepo structure
    # In wafer/ monorepo, research root is at wafer/research/async-wevin
    for parent in [current] + list(current.parents):
        research_root = parent / "research" / "async-wevin"
        if research_root.is_dir() and (research_root / "wafer_utils").is_dir():
            return research_root

    raise ResearchRootNotFoundError(str(file_path))


def setup_research_paths(research_root: Path, additional_paths: list[Path] | None = None) -> None:
    """Setup sys.path with research directories.

    Adds research root, wafer_utils/, and rollouts/ to sys.path in the correct order.
    Optionally adds additional paths.

    Args:
        research_root: Path to research root directory
        additional_paths: Optional list of additional paths to add
    """
    paths_to_add = [
        research_root / "wafer_utils",
        research_root / "rollouts",
        research_root,
    ]

    if additional_paths:
        paths_to_add.extend(additional_paths)

    # Add paths in reverse order so they're searched in forward order
    for path in reversed(paths_to_add):
        path_str = str(path.resolve())
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def infer_benchmark_name(config_path: Path) -> str:
    """Infer benchmark name from config file path.

    Safely extracts benchmark name from config path structure.
    Looks for patterns like:
    - configs/benchmarks/{benchmark_name}/...
    - benchmarks/{benchmark_name}/...

    Args:
        config_path: Path to config file

    Returns:
        Benchmark name (e.g., 'leetgpu', 'gpumode')

    Raises:
        ValueError: If benchmark name cannot be inferred
    """
    parts = config_path.parts

    # Look for 'benchmarks' directory in path
    try:
        benchmarks_idx = parts.index("benchmarks")
        if benchmarks_idx + 1 < len(parts):
            return parts[benchmarks_idx + 1]
    except ValueError:
        pass

    # Fallback: try to infer from parent directory name
    # This handles cases like benchmarks/gpumode/entrypoint.py
    parent = config_path.parent
    if parent.name and parent.name != "benchmarks":
        return parent.name

    raise BenchmarkNameInferenceError(str(config_path))


def resolve_dataset_path(dataset_path: str | Path, base_dir: Path) -> Path:
    """Resolve dataset path consistently.

    Handles both relative and absolute paths. Relative paths are resolved
    relative to base_dir (typically research_root).

    Args:
        dataset_path: Dataset path (string or Path)
        base_dir: Base directory for resolving relative paths

    Returns:
        Resolved absolute Path
    """
    path = Path(dataset_path)

    if path.is_absolute():
        return path.resolve()

    return (base_dir / path).resolve()
