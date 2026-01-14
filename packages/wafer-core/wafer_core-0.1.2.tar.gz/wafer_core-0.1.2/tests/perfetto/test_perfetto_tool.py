"""Unit tests for PerfettoTool - the main orchestration layer.

Tests the integration between TraceManager and TraceProcessorManager.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wafer_core.tools.perfetto.perfetto_tool import PerfettoConfig, PerfettoTool
from wafer_core.tools.perfetto.trace_manager import TraceMeta
from wafer_core.tools.perfetto.trace_processor import TraceProcessorStatus


class TestPerfettoConfig:
    """Test PerfettoConfig frozen dataclass."""

    def test_config_is_immutable(self) -> None:
        """PerfettoConfig should be immutable (frozen)."""
        config = PerfettoConfig(
            workspace_root="/workspace",
            storage_dir="/storage",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            config.workspace_root = "/other"

    def test_config_with_all_options(self) -> None:
        """PerfettoConfig should accept all optional parameters."""
        config = PerfettoConfig(
            workspace_root="/workspace",
            storage_dir="/storage",
            perfetto_source_dir="/perfetto",
            build_script_path="/build.sh",
            ui_version="v49.0",
        )

        assert config.workspace_root == "/workspace"
        assert config.storage_dir == "/storage"
        assert config.perfetto_source_dir == "/perfetto"
        assert config.build_script_path == "/build.sh"
        assert config.ui_version == "v49.0"

    def test_config_default_optional_fields(self) -> None:
        """Optional fields should default to None."""
        config = PerfettoConfig(
            workspace_root="/workspace",
            storage_dir="/storage",
        )

        assert config.perfetto_source_dir is None
        assert config.build_script_path is None
        assert config.ui_version is None


class TestPerfettoToolTraceManagement:
    """Test PerfettoTool trace management methods."""

    def test_list_traces_delegates_to_manager(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """list_traces should return traces from TraceManager."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / ".wafer" / "perfetto"),
        )
        tool = PerfettoTool(config)

        # Store a trace via the tool
        tool.store_trace(str(sample_trace_file), "test.json")

        traces = tool.list_traces()

        assert len(traces) == 1
        assert traces[0].original_filename == "test.json"

    def test_store_trace_returns_metadata(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """store_trace should return TraceMeta on success."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / ".wafer" / "perfetto"),
        )
        tool = PerfettoTool(config)

        meta, err = tool.store_trace(str(sample_trace_file), "test.json")

        assert err is None
        assert meta is not None
        assert isinstance(meta, TraceMeta)
        assert meta.original_filename == "test.json"
        assert meta.size_bytes > 0

    def test_store_trace_with_workspace_id(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """store_trace should accept workspace_id."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / ".wafer" / "perfetto"),
        )
        tool = PerfettoTool(config)

        meta, err = tool.store_trace(
            str(sample_trace_file),
            "test.json",
            workspace_id="ws_123",
        )

        assert err is None
        assert meta is not None
        assert meta.workspace_id == "ws_123"

    def test_get_trace_retrieves_stored_trace(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """get_trace should retrieve previously stored trace."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / ".wafer" / "perfetto"),
        )
        tool = PerfettoTool(config)

        stored, _ = tool.store_trace(str(sample_trace_file), "test.json")
        assert stored is not None

        retrieved, err = tool.get_trace(stored.trace_id)

        assert err is None
        assert retrieved is not None
        assert retrieved.trace_id == stored.trace_id

    def test_delete_trace_removes_trace(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """delete_trace should remove trace from workspace."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / ".wafer" / "perfetto"),
        )
        tool = PerfettoTool(config)

        meta, _ = tool.store_trace(str(sample_trace_file), "test.json")
        assert meta is not None

        success, err = tool.delete_trace(meta.trace_id)

        assert success is True
        assert err is None

        # Verify it's gone
        traces = tool.list_traces()
        assert len(traces) == 0


class TestPerfettoToolValidation:
    """Test PerfettoTool.validate_trace()."""

    def test_validate_valid_trace(self, sample_trace_file: Path) -> None:
        """validate_trace should pass for valid trace files."""
        config = PerfettoConfig(
            workspace_root="/tmp",
            storage_dir="/tmp/storage",
        )
        tool = PerfettoTool(config)

        valid, err = tool.validate_trace(str(sample_trace_file))

        assert valid is True
        assert err is None

    def test_validate_invalid_trace(self, tmp_workspace: Path) -> None:
        """validate_trace should fail for invalid files."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        invalid_file = tmp_workspace / "invalid.json"
        invalid_file.write_text("not json")

        valid, err = tool.validate_trace(str(invalid_file))

        assert valid is False
        assert err is not None


class TestPerfettoToolProcessorManagement:
    """Test PerfettoTool trace_processor management methods."""

    def test_check_processor_returns_status(self, tmp_workspace: Path) -> None:
        """check_processor should return TraceProcessorStatus."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        status = tool.check_processor()

        assert isinstance(status, TraceProcessorStatus)
        # Binary likely not found in test environment
        assert status.available is False

    def test_get_server_status_when_not_running(
        self, tmp_workspace: Path
    ) -> None:
        """get_server_status should indicate no server running."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        status = tool.get_server_status()

        assert status["running"] is False

    def test_stop_server_safe_when_not_running(
        self, tmp_workspace: Path
    ) -> None:
        """stop_server should be safe to call when no server running."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Should not raise
        tool.stop_server()

        assert tool.get_server_status()["running"] is False


class TestPerfettoToolCLI:
    """Test CLI command functions."""

    def test_cmd_list_returns_traces_dict(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """cmd_list should return dict with traces key."""
        from argparse import Namespace
        from wafer_core.tools.perfetto.perfetto_tool import cmd_list

        # Store a trace first
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)
        tool.store_trace(str(sample_trace_file), "test.json")

        args = Namespace(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )

        result = cmd_list(args)

        assert "traces" in result
        assert len(result["traces"]) == 1
        assert result["traces"][0]["originalFilename"] == "test.json"

    def test_cmd_store_success(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """cmd_store should return success with trace metadata."""
        from argparse import Namespace
        from wafer_core.tools.perfetto.perfetto_tool import cmd_store

        args = Namespace(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
            file=str(sample_trace_file),
            filename="test.json",
        )

        result = cmd_store(args)

        assert result["success"] is True
        assert "trace" in result
        assert result["trace"]["originalFilename"] == "test.json"

    def test_cmd_store_failure_nonexistent_file(
        self, tmp_workspace: Path
    ) -> None:
        """cmd_store should return error for nonexistent file."""
        from argparse import Namespace
        from wafer_core.tools.perfetto.perfetto_tool import cmd_store

        args = Namespace(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
            file="/nonexistent/file.json",
            filename="test.json",
        )

        result = cmd_store(args)

        assert result["success"] is False
        assert "error" in result

    def test_cmd_delete_success(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """cmd_delete should return success for existing trace."""
        from argparse import Namespace
        from wafer_core.tools.perfetto.perfetto_tool import cmd_delete, cmd_store

        # Store first
        store_args = Namespace(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
            file=str(sample_trace_file),
            filename="test.json",
        )
        store_result = cmd_store(store_args)
        trace_id = store_result["trace"]["traceId"]

        # Delete
        delete_args = Namespace(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
            trace_id=trace_id,
        )

        result = cmd_delete(delete_args)

        assert result["success"] is True


class TestPerfettoToolInvariants:
    """Property-based tests for PerfettoTool invariants."""

    def test_stored_trace_retrievable(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Every stored trace should be retrievable."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        meta, _ = tool.store_trace(str(sample_trace_file), "test.json")
        assert meta is not None

        retrieved, err = tool.get_trace(meta.trace_id)

        assert err is None
        assert retrieved is not None
        assert retrieved.trace_id == meta.trace_id

    def test_stored_trace_appears_in_list(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Every stored trace should appear in list_traces."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        meta, _ = tool.store_trace(str(sample_trace_file), "test.json")
        assert meta is not None

        traces = tool.list_traces()
        trace_ids = [t.trace_id for t in traces]

        assert meta.trace_id in trace_ids

    def test_deleted_trace_not_retrievable(
        self, tmp_workspace: Path, sample_trace_file: Path
    ) -> None:
        """Deleted trace should not be retrievable."""
        config = PerfettoConfig(
            workspace_root=str(tmp_workspace),
            storage_dir=str(tmp_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        meta, _ = tool.store_trace(str(sample_trace_file), "test.json")
        assert meta is not None

        tool.delete_trace(meta.trace_id)

        retrieved, err = tool.get_trace(meta.trace_id)

        assert retrieved is None
        assert err is not None


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

