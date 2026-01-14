"""Unit tests for Perfetto TraceManager.

Tests trace file storage, listing, retrieval, and deletion operations.
"""

import json
import tempfile
from pathlib import Path

import pytest

from wafer_core.tools.perfetto.trace_manager import TraceMeta, TraceManager


class TestTraceMetaSerialization:
    """Test TraceMeta serialization and deserialization."""

    def test_to_dict_contains_all_fields(self) -> None:
        """TraceMeta.to_dict() should include all fields."""
        meta = TraceMeta(
            trace_id="trace_123",
            original_filename="test.json",
            workspace_path="/workspace",
            timestamp=1704067200000,
            size_bytes=1024,
            file_path="/workspace/.wafer/traces/trace_123/trace.json",
            workspace_id="ws_456",
            git_commit_hash="abc123def",
        )

        result = meta.to_dict()

        assert result["traceId"] == "trace_123"
        assert result["originalFilename"] == "test.json"
        assert result["workspacePath"] == "/workspace"
        assert result["timestamp"] == 1704067200000
        assert result["sizeBytes"] == 1024
        assert result["filePath"] == "/workspace/.wafer/traces/trace_123/trace.json"
        assert result["workspaceId"] == "ws_456"
        assert result["gitCommitHash"] == "abc123def"

    def test_from_dict_reconstructs_meta(self) -> None:
        """TraceMeta.from_dict() should reconstruct original object."""
        original = TraceMeta(
            trace_id="trace_123",
            original_filename="test.json",
            workspace_path="/workspace",
            timestamp=1704067200000,
            size_bytes=1024,
            file_path="/workspace/.wafer/traces/trace_123/trace.json",
            workspace_id="ws_456",
            git_commit_hash="abc123def",
        )

        reconstructed = TraceMeta.from_dict(original.to_dict())

        assert reconstructed.trace_id == original.trace_id
        assert reconstructed.original_filename == original.original_filename
        assert reconstructed.workspace_path == original.workspace_path
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.size_bytes == original.size_bytes
        assert reconstructed.file_path == original.file_path
        assert reconstructed.workspace_id == original.workspace_id
        assert reconstructed.git_commit_hash == original.git_commit_hash

    def test_from_dict_handles_optional_fields(self) -> None:
        """TraceMeta.from_dict() should handle missing optional fields."""
        data = {
            "traceId": "trace_123",
            "originalFilename": "test.json",
            "workspacePath": "/workspace",
            "timestamp": 1704067200000,
            "sizeBytes": 1024,
            "filePath": "/workspace/.wafer/traces/trace_123/trace.json",
        }

        meta = TraceMeta.from_dict(data)

        assert meta.workspace_id is None
        assert meta.git_commit_hash is None


class TestTraceManagerBasicOperations:
    """Test basic TraceManager operations."""

    def test_list_traces_empty_workspace(self, tmp_workspace: Path) -> None:
        """Listing traces in empty workspace should return empty list."""
        manager = TraceManager(str(tmp_workspace))

        traces = manager.list_traces()

        assert traces == []

    def test_store_trace_creates_directory_structure(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Storing a trace should create .wafer/traces/{trace_id} directory."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.store_trace(str(sample_trace_file), "my_trace.json")

        assert err is None
        assert meta is not None
        assert (tmp_workspace / ".wafer" / "traces").exists()
        assert (tmp_workspace / ".wafer" / "traces" / meta.trace_id).is_dir()

    def test_store_trace_copies_file(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Stored trace should be accessible at filePath."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.store_trace(str(sample_trace_file), "my_trace.json")

        assert err is None
        assert meta is not None
        assert Path(meta.file_path).exists()
        assert Path(meta.file_path).read_text() == sample_trace_file.read_text()

    def test_store_trace_creates_metadata_file(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Storing trace should create meta.json file."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.store_trace(str(sample_trace_file), "my_trace.json")

        assert err is None
        assert meta is not None
        meta_path = tmp_workspace / ".wafer" / "traces" / meta.trace_id / "meta.json"
        assert meta_path.exists()

        meta_data = json.loads(meta_path.read_text())
        assert meta_data["traceId"] == meta.trace_id
        assert meta_data["originalFilename"] == "my_trace.json"

    def test_store_trace_preserves_gz_extension(
        self, tmp_workspace: Path
    ) -> None:
        """Storing .gz trace should preserve compression."""
        manager = TraceManager(str(tmp_workspace))

        # Create a .gz file
        gz_file = tmp_workspace / "trace.json.gz"
        gz_file.write_bytes(b"\x1f\x8b\x08\x00test_gzip_data")

        meta, err = manager.store_trace(str(gz_file), "trace.json.gz")

        assert err is None
        assert meta is not None
        assert meta.file_path.endswith("trace.json.gz")

    def test_store_trace_fails_on_empty_file(self, tmp_workspace: Path) -> None:
        """Storing empty file should return error."""
        manager = TraceManager(str(tmp_workspace))
        empty_file = tmp_workspace / "empty.json"
        empty_file.touch()

        meta, err = manager.store_trace(str(empty_file), "empty.json")

        assert meta is None
        assert err is not None
        assert "empty" in err.lower()

    def test_store_trace_fails_on_nonexistent_file(
        self, tmp_workspace: Path
    ) -> None:
        """Storing nonexistent file should return error."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.store_trace("/nonexistent/path/file.json", "file.json")

        assert meta is None
        assert err is not None
        assert "not found" in err.lower()


class TestTraceManagerListTraces:
    """Test TraceManager.list_traces()."""

    def test_list_traces_returns_all_stored_traces(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """list_traces should return all stored traces."""
        manager = TraceManager(str(tmp_workspace))

        # Store multiple traces
        manager.store_trace(str(sample_trace_file), "trace1.json")
        manager.store_trace(str(sample_trace_file), "trace2.json")
        manager.store_trace(str(sample_trace_file), "trace3.json")

        traces = manager.list_traces()

        assert len(traces) == 3
        filenames = [t.original_filename for t in traces]
        assert "trace1.json" in filenames
        assert "trace2.json" in filenames
        assert "trace3.json" in filenames

    def test_list_traces_sorted_by_timestamp_newest_first(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Traces should be sorted newest first."""
        manager = TraceManager(str(tmp_workspace))

        manager.store_trace(str(sample_trace_file), "trace1.json")
        manager.store_trace(str(sample_trace_file), "trace2.json")
        manager.store_trace(str(sample_trace_file), "trace3.json")

        traces = manager.list_traces()

        # Verify descending timestamp order
        timestamps = [t.timestamp for t in traces]
        assert timestamps == sorted(timestamps, reverse=True)


class TestTraceManagerGetTrace:
    """Test TraceManager.get_trace()."""

    def test_get_trace_returns_stored_trace(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """get_trace should return previously stored trace."""
        manager = TraceManager(str(tmp_workspace))
        stored_meta, _ = manager.store_trace(str(sample_trace_file), "test.json")

        meta, err = manager.get_trace(stored_meta.trace_id)

        assert err is None
        assert meta is not None
        assert meta.trace_id == stored_meta.trace_id
        assert meta.original_filename == "test.json"

    def test_get_trace_nonexistent_returns_error(
        self, tmp_workspace: Path
    ) -> None:
        """get_trace for nonexistent ID should return error."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.get_trace("nonexistent_id")

        assert meta is None
        assert err is not None
        assert "not found" in err.lower()

    def test_get_trace_empty_id_returns_error(self, tmp_workspace: Path) -> None:
        """get_trace with empty ID should return error."""
        manager = TraceManager(str(tmp_workspace))

        meta, err = manager.get_trace("")

        assert meta is None
        assert err is not None
        assert "required" in err.lower()

    def test_get_trace_path_traversal_blocked(
        self, tmp_workspace: Path
    ) -> None:
        """get_trace should block path traversal attempts."""
        manager = TraceManager(str(tmp_workspace))

        # Try various path traversal patterns
        for malicious_id in ["../../../etc/passwd", "foo/../bar", "foo/bar", "foo\\bar"]:
            meta, err = manager.get_trace(malicious_id)
            assert meta is None
            assert err is not None
            assert "invalid" in err.lower()


class TestTraceManagerDeleteTrace:
    """Test TraceManager.delete_trace()."""

    def test_delete_trace_removes_directory(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """delete_trace should remove the trace directory."""
        manager = TraceManager(str(tmp_workspace))
        meta, _ = manager.store_trace(str(sample_trace_file), "test.json")
        trace_dir = tmp_workspace / ".wafer" / "traces" / meta.trace_id

        assert trace_dir.exists()

        success, err = manager.delete_trace(meta.trace_id)

        assert success is True
        assert err is None
        assert not trace_dir.exists()

    def test_delete_trace_removes_from_list(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Deleted trace should not appear in list_traces."""
        manager = TraceManager(str(tmp_workspace))
        meta, _ = manager.store_trace(str(sample_trace_file), "test.json")

        manager.delete_trace(meta.trace_id)

        traces = manager.list_traces()
        trace_ids = [t.trace_id for t in traces]
        assert meta.trace_id not in trace_ids

    def test_delete_nonexistent_trace_succeeds(
        self, tmp_workspace: Path
    ) -> None:
        """Deleting nonexistent trace should succeed (idempotent)."""
        manager = TraceManager(str(tmp_workspace))

        success, err = manager.delete_trace("nonexistent_id")

        assert success is True
        assert err is None

    def test_delete_trace_path_traversal_blocked(
        self, tmp_workspace: Path
    ) -> None:
        """delete_trace should block path traversal attempts."""
        manager = TraceManager(str(tmp_workspace))

        for malicious_id in ["../../../etc/passwd", "foo/../bar", "foo/bar"]:
            success, err = manager.delete_trace(malicious_id)
            assert success is False
            assert err is not None
            assert "invalid" in err.lower()


class TestTraceManagerValidation:
    """Test TraceManager.validate_trace_file()."""

    def test_validate_valid_json_trace(self, sample_trace_file: Path) -> None:
        """Valid JSON trace should pass validation."""
        manager = TraceManager("/tmp")

        valid, err = manager.validate_trace_file(str(sample_trace_file))

        assert valid is True
        assert err is None

    def test_validate_nonexistent_file(self) -> None:
        """Nonexistent file should fail validation."""
        manager = TraceManager("/tmp")

        valid, err = manager.validate_trace_file("/nonexistent/path/file.json")

        assert valid is False
        assert err is not None
        assert "not found" in err.lower()

    def test_validate_empty_file(self, tmp_workspace: Path) -> None:
        """Empty file should fail validation."""
        manager = TraceManager(str(tmp_workspace))
        empty_file = tmp_workspace / "empty.json"
        empty_file.touch()

        valid, err = manager.validate_trace_file(str(empty_file))

        assert valid is False
        assert err is not None
        assert "empty" in err.lower()

    def test_validate_invalid_json_structure(self, tmp_workspace: Path) -> None:
        """Invalid JSON structure should fail validation."""
        manager = TraceManager(str(tmp_workspace))
        invalid_file = tmp_workspace / "invalid.json"
        invalid_file.write_text("this is not json at all!")

        valid, err = manager.validate_trace_file(str(invalid_file))

        assert valid is False
        assert err is not None
        assert "invalid json" in err.lower()


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace directory."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def sample_trace_file(tmp_path: Path) -> Path:
    """Create a sample Chrome trace JSON file."""
    trace_content = {
        "traceEvents": [
            {"name": "kernel1", "ph": "X", "ts": 0, "dur": 1000},
            {"name": "kernel2", "ph": "X", "ts": 1000, "dur": 2000},
        ],
        "metadata": {"test": True},
    }
    trace_file = tmp_path / "sample_trace.json"
    trace_file.write_text(json.dumps(trace_content))
    return trace_file

