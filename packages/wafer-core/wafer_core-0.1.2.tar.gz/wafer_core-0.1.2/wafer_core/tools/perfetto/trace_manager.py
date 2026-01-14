"""Trace Manager - Storage and management of Perfetto trace files.

This module handles:
- Storing uploaded trace files in workspace
- Listing available traces
- Deleting traces
- Reading trace metadata

Tiger Style:
- Immutable dataclasses for data
- Explicit error handling with tuple returns
- Single responsibility functions
"""

import json
import logging
import secrets
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TraceMeta:
    """Metadata for a stored trace file.
    
    WHY frozen=True: Trace metadata is immutable once created.
    To "update" metadata, create a new TraceMeta.
    """
    trace_id: str
    original_filename: str
    workspace_path: str
    timestamp: int  # Unix timestamp in milliseconds
    size_bytes: int
    file_path: str
    workspace_id: str | None = None
    git_commit_hash: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "traceId": self.trace_id,
            "originalFilename": self.original_filename,
            "workspacePath": self.workspace_path,
            "workspaceId": self.workspace_id,
            "gitCommitHash": self.git_commit_hash,
            "timestamp": self.timestamp,
            "sizeBytes": self.size_bytes,
            "filePath": self.file_path,
        }

    @staticmethod
    def from_dict(data: dict) -> "TraceMeta":
        """Create TraceMeta from dictionary."""
        return TraceMeta(
            trace_id=data["traceId"],
            original_filename=data["originalFilename"],
            workspace_path=data["workspacePath"],
            workspace_id=data.get("workspaceId"),
            git_commit_hash=data.get("gitCommitHash"),
            timestamp=data["timestamp"],
            size_bytes=data["sizeBytes"],
            file_path=data["filePath"],
        )


class TraceManager:
    """Manages storage and retrieval of Perfetto trace files.
    
    Traces are stored in: {workspace_root}/.wafer/traces/{trace_id}/
    Each trace directory contains:
    - trace.json (or trace.json.gz) - The actual trace file
    - meta.json - Metadata about the trace
    """

    def __init__(self, workspace_root: str):
        """Initialize TraceManager.
        
        Args:
            workspace_root: Path to workspace root directory
        """
        assert workspace_root, "workspace_root is required"
        self.workspace_root = Path(workspace_root)
        self.traces_dir = self.workspace_root / ".wafer" / "traces"

    def ensure_traces_dir(self) -> Path:
        """Ensure the traces directory exists.
        
        Returns:
            Path to traces directory
        """
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        return self.traces_dir

    def list_traces(self) -> list[TraceMeta]:
        """List all traces in the workspace.
        
        Returns:
            List of TraceMeta sorted by timestamp (newest first)
        """
        if not self.traces_dir.exists():
            return []

        traces: list[TraceMeta] = []
        
        for trace_dir in self.traces_dir.iterdir():
            if not trace_dir.is_dir():
                continue
            
            # Skip temporary directories (traces being written)
            if trace_dir.name.startswith(".tmp-"):
                continue
            
            meta_path = trace_dir / "meta.json"
            if not meta_path.exists():
                # Skip incomplete traces (should not happen with atomic writes)
                continue
            
            try:
                meta_data = json.loads(meta_path.read_text())
                traces.append(TraceMeta.from_dict(meta_data))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse metadata for trace {trace_dir.name}: {e}")
                continue

        # Sort by timestamp (newest first)
        traces.sort(key=lambda t: t.timestamp, reverse=True)
        return traces

    def get_trace(self, trace_id: str) -> tuple[TraceMeta | None, str | None]:
        """Get a specific trace by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            (TraceMeta, None) on success, (None, error_message) on failure
        """
        if not trace_id:
            return None, "trace_id is required"
        
        # Security: prevent path traversal
        if ".." in trace_id or "/" in trace_id or "\\" in trace_id:
            return None, "Invalid trace_id"
        
        trace_dir = self.traces_dir / trace_id
        if not trace_dir.exists():
            return None, f"Trace {trace_id} not found"
        
        meta_path = trace_dir / "meta.json"
        if not meta_path.exists():
            return None, f"Metadata not found for trace {trace_id}"
        
        try:
            meta_data = json.loads(meta_path.read_text())
            return TraceMeta.from_dict(meta_data), None
        except (json.JSONDecodeError, KeyError) as e:
            return None, f"Failed to parse metadata: {e}"

    def store_trace(
        self,
        source_path: str,
        original_filename: str,
        workspace_id: str | None = None,
    ) -> tuple[TraceMeta | None, str | None]:
        """Store a trace file in the workspace using atomic directory creation.
        
        WHY atomic: Creates trace directory with all contents in a temporary location,
        then atomically renames it to final location. This prevents list_traces() from
        seeing incomplete trace directories (race condition).
        
        Args:
            source_path: Path to the source trace file
            original_filename: Original name of the file
            workspace_id: Optional workspace identifier
            
        Returns:
            (TraceMeta, None) on success, (None, error_message) on failure
        """
        source = Path(source_path)
        
        # Validate source file
        if not source.exists():
            return None, f"Source file not found: {source_path}"
        if not source.is_file():
            return None, f"Source is not a file: {source_path}"
        
        # Validate file size (basic check - not empty)
        stats = source.stat()
        if stats.st_size == 0:
            return None, "Trace file is empty"
        
        # Generate trace ID
        trace_id = f"{int(datetime.now().timestamp() * 1000)}-{secrets.token_hex(4)}"
        
        # Ensure traces directory exists
        self.ensure_traces_dir()
        
        # Create temporary directory for atomic write
        # WHY .tmp- prefix: list_traces() skips directories starting with .tmp-
        temp_dir = self.traces_dir / f".tmp-{trace_id}"
        trace_dir = self.traces_dir / trace_id
        
        try:
            temp_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            return None, f"Temporary directory already exists: {temp_dir}"
        
        # Determine target filename (preserve .gz extension)
        ext = Path(original_filename).suffix
        target_filename = "trace.json.gz" if ext == ".gz" else "trace.json"
        temp_trace_path = temp_dir / target_filename
        final_trace_path = trace_dir / target_filename
        
        # Copy file to temporary directory
        try:
            shutil.copy2(source, temp_trace_path)
        except Exception as e:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, f"Failed to copy trace file: {e}"
        
        # Get git commit hash (best effort)
        git_commit = self._get_git_commit_hash()
        
        # Create metadata with final path (not temp path)
        meta = TraceMeta(
            trace_id=trace_id,
            original_filename=original_filename,
            workspace_path=str(self.workspace_root),
            workspace_id=workspace_id,
            git_commit_hash=git_commit,
            timestamp=int(datetime.now().timestamp() * 1000),
            size_bytes=stats.st_size,
            file_path=str(final_trace_path),
        )
        
        # Write metadata to temporary directory
        temp_meta_path = temp_dir / "meta.json"
        try:
            temp_meta_path.write_text(json.dumps(meta.to_dict(), indent=2))
        except Exception as e:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, f"Failed to save metadata: {e}"
        
        # Atomically rename temporary directory to final location
        # WHY atomic: rename() is atomic on most filesystems, so list_traces()
        # will never see a partially-written trace directory
        try:
            temp_dir.rename(trace_dir)
        except Exception as e:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, f"Failed to finalize trace directory: {e}"
        
        logger.info(f"Stored trace: {original_filename} ({stats.st_size} bytes) -> {trace_id}")
        return meta, None

    def delete_trace(self, trace_id: str) -> tuple[bool, str | None]:
        """Delete a trace by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            (True, None) on success, (False, error_message) on failure
        """
        if not trace_id:
            return False, "trace_id is required"
        
        # Security: prevent path traversal
        if ".." in trace_id or "/" in trace_id or "\\" in trace_id:
            return False, "Invalid trace_id"
        
        trace_dir = self.traces_dir / trace_id
        
        if not trace_dir.exists():
            # Already deleted - success
            logger.warning(f"Trace {trace_id} does not exist (may already be deleted)")
            return True, None
        
        if not trace_dir.is_dir():
            return False, f"Trace path is not a directory: {trace_dir}"
        
        # Verify it's within traces directory (security check)
        resolved_trace_dir = trace_dir.resolve()
        resolved_traces_dir = self.traces_dir.resolve()
        if not str(resolved_trace_dir).startswith(str(resolved_traces_dir)):
            return False, "Invalid trace path - security check failed"
        
        try:
            shutil.rmtree(trace_dir)
            logger.info(f"Deleted trace: {trace_id}")
            return True, None
        except Exception as e:
            return False, f"Failed to delete trace: {e}"

    def validate_trace_file(self, trace_path: str) -> tuple[bool, str | None]:
        """Validate a trace file.
        
        Checks:
        - File exists
        - File is not empty
        - File is readable
        - Basic JSON structure (for .json files)
        
        Args:
            trace_path: Path to trace file
            
        Returns:
            (True, None) on valid, (False, error_message) on invalid
        """
        path = Path(trace_path)
        
        if not path.exists():
            return False, f"File not found: {trace_path}"
        
        if not path.is_file():
            return False, f"Not a file: {trace_path}"
        
        stats = path.stat()
        if stats.st_size == 0:
            return False, "Trace file is empty"
        
        # For JSON files, validate basic structure
        if path.suffix == ".json":
            try:
                with open(path) as f:
                    # Just read first few bytes to check it's valid JSON start
                    start = f.read(100)
                    if not (start.strip().startswith("{") or start.strip().startswith("[")):
                        return False, "Invalid JSON structure"
            except Exception as e:
                return False, f"Failed to read file: {e}"
        
        return True, None

    def _get_git_commit_hash(self) -> str | None:
        """Get git commit hash for the workspace (best effort).
        
        Returns:
            Git commit hash or None if not available
        """
        git_dir = self.workspace_root / ".git"
        if not git_dir.exists():
            return None
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip() or None
        except Exception:
            pass
        
        return None


# ── Public API Functions (for TypeScript callWaferCore) ──────────────────────

def list_traces_for_workspace(workspace_root: str) -> list[dict]:
    """List all traces in the workspace.
    
    Args:
        workspace_root: Path to workspace root directory
        
    Returns:
        List of trace metadata dictionaries
    """
    manager = TraceManager(workspace_root)
    traces = manager.list_traces()
    return [t.to_dict() for t in traces]


def store_trace_for_workspace(
    source_path: str,
    workspace_root: str,
    original_filename: str,
    workspace_id: str | None = None,
) -> dict:
    """Store a trace file in the workspace.
    
    Args:
        source_path: Path to the source trace file
        workspace_root: Path to workspace root directory
        original_filename: Original name of the file
        workspace_id: Optional workspace identifier
        
    Returns:
        Dictionary with success status and trace metadata or error
    """
    manager = TraceManager(workspace_root)
    meta, err = manager.store_trace(source_path, original_filename, workspace_id)
    
    if err:
        return {"success": False, "error": err}
    
    assert meta is not None
    return {"success": True, "trace": meta.to_dict()}


def delete_trace_for_workspace(trace_id: str, workspace_root: str) -> dict:
    """Delete a trace by ID.
    
    Args:
        trace_id: Trace identifier
        workspace_root: Path to workspace root directory
        
    Returns:
        Dictionary with success status and optional error
    """
    manager = TraceManager(workspace_root)
    success, err = manager.delete_trace(trace_id)
    
    if err:
        return {"success": False, "error": err}
    
    return {"success": True}

