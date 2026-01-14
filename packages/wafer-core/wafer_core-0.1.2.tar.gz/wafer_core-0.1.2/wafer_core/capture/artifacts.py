"""Directory snapshot and artifact detection."""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import trio

from wafer_core.capture.dtypes import ArtifactDiff, DirectorySnapshot, FileInfo

logger = logging.getLogger(__name__)


def _matches_denylist(path: Path, denylist: list[str]) -> bool:
    """Check if path matches any denylist pattern.

    Args:
        path: Path to check
        denylist: List of glob patterns

    Returns:
        True if path matches any pattern
    """
    from fnmatch import fnmatch

    path_str = str(path)
    for pattern in denylist:
        # Try both the path itself and with **/ prefix for directory patterns
        if fnmatch(path_str, pattern):
            return True
        if "**/" in pattern:
            # Remove **/ and try matching just the pattern
            simple_pattern = pattern.replace("**/", "")
            if fnmatch(path_str, simple_pattern) or fnmatch(
                path.name, simple_pattern
            ):
                return True
            # Check if any parent directory matches
            for parent in path.parents:
                if fnmatch(str(parent), pattern) or fnmatch(parent.name, simple_pattern):
                    return True
    return False


async def compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex string of SHA256 checksum

    Raises:
        OSError: If file cannot be read
    """
    hasher = hashlib.sha256()

    def _compute() -> str:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # Run in thread to avoid blocking
    return await trio.to_thread.run_sync(_compute)


async def snapshot_directory(
    root: Path | str, denylist: list[str] | None = None
) -> DirectorySnapshot:
    logger.debug(f"Creating directory snapshot: {root}")
    root = Path(root)
    denylist = denylist or []

    files: dict[Path, FileInfo] = {}

    def _scan() -> dict[Path, FileInfo]:
        """Scan directory tree (runs in thread)."""
        result: dict[Path, FileInfo] = {}
        for item in root.rglob("*"):
            if not item.is_file():
                continue

            # Get relative path from root
            try:
                rel_path = item.relative_to(root)
            except ValueError:
                continue

            # Check denylist
            if _matches_denylist(rel_path, denylist):
                logger.debug(f"Skipping denylisted file: {rel_path}")
                continue

            # Get file info
            try:
                stat = item.stat()
                file_info = FileInfo(
                    path=rel_path,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    checksum=None,  # Computed on demand
                )
                result[rel_path] = file_info
            except OSError as e:
                logger.warning(f"Failed to stat file {rel_path}: {e}")
                continue

        return result

    # Run directory scan in thread
    files = await trio.to_thread.run_sync(_scan)

    logger.info(f"Snapshot complete: {len(files)} files")

    return DirectorySnapshot(
        files=files, timestamp=datetime.now(timezone.utc), root=root
    )


def diff_snapshots(before: DirectorySnapshot, after: DirectorySnapshot) -> ArtifactDiff:
    """Compute difference between two directory snapshots.

    Args:
        before: Snapshot taken before execution
        after: Snapshot taken after execution

    Returns:
        ArtifactDiff with new, modified, and deleted files
    """
    logger.debug("Computing snapshot diff")

    before_paths = set(before.files.keys())
    after_paths = set(after.files.keys())

    # New files
    new_files = sorted(after_paths - before_paths)

    # Deleted files
    deleted_files = sorted(before_paths - after_paths)

    # Modified files (exist in both but different mtime or size)
    modified_files: list[Path] = []
    for path in sorted(before_paths & after_paths):
        before_info = before.files[path]
        after_info = after.files[path]

        # Check if modified (different size or mtime)
        if (
            before_info.size != after_info.size
            or before_info.mtime != after_info.mtime
        ):
            modified_files.append(path)

    logger.info(
        f"Diff: {len(new_files)} new, {len(modified_files)} modified, {len(deleted_files)} deleted"
    )

    return ArtifactDiff(
        new_files=new_files, modified_files=modified_files, deleted_files=deleted_files
    )


async def collect_file_contents(
    root: Path, paths: list[Path], compute_checksums: bool = True
) -> dict[Path, str]:
    """Collect contents of multiple files.

    Args:
        root: Root directory
        paths: List of relative paths to collect
        compute_checksums: Whether to compute checksums (not used, kept for API)

    Returns:
        Dictionary mapping path to file contents

    Raises:
        OSError: If any file cannot be read
    """
    logger.debug(f"Collecting {len(paths)} files")

    async def read_file(path: Path) -> tuple[Path, str]:
        """Read a single file."""
        full_path = root / path

        def _read() -> str:
            with open(full_path, encoding="utf-8", errors="replace") as f:
                return f.read()

        content = await trio.to_thread.run_sync(_read)
        return path, content

    # Read all files concurrently
    results: dict[Path, str] = {}
    async with trio.open_nursery() as nursery:
        result_list: list[tuple[Path, str]] = []

        async def _collect() -> None:
            for path in paths:
                try:
                    result = await read_file(path)
                    result_list.append(result)
                except Exception as e:
                    logger.warning(f"Failed to read {path}: {e}")

        nursery.start_soon(_collect)

    results = dict(result_list)
    logger.info(f"Collected {len(results)} files")
    return results
