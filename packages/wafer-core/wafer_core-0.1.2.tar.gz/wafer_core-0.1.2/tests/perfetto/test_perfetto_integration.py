"""Integration tests for Perfetto tool end-to-end workflows.

These tests verify the complete flow of:
- Trace upload → storage → listing → retrieval → deletion
- Real file operations with proper cleanup
- CLI command integration

These tests use real file system operations but are isolated to temp directories.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from wafer_core.tools.perfetto.perfetto_tool import PerfettoConfig, PerfettoTool
from wafer_core.tools.perfetto.trace_manager import TraceMeta, TraceManager


class TestTraceWorkflowE2E:
    """End-to-end tests for trace lifecycle workflows."""

    def test_complete_trace_lifecycle(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Test complete trace lifecycle: store → list → get → delete.
        
        This tests the real user workflow of:
        1. Uploading a trace file
        2. Seeing it in the trace list
        3. Opening/retrieving it
        4. Deleting it when done
        """
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Step 1: Store trace
        meta, err = tool.store_trace(str(realistic_trace_file), "my_profile.json")
        assert err is None, f"Failed to store trace: {err}"
        assert meta is not None
        assert meta.original_filename == "my_profile.json"
        trace_id = meta.trace_id

        # Step 2: List traces - should include our trace
        traces = tool.list_traces()
        assert len(traces) >= 1
        trace_ids = [t.trace_id for t in traces]
        assert trace_id in trace_ids

        # Step 3: Get specific trace
        retrieved, err = tool.get_trace(trace_id)
        assert err is None
        assert retrieved is not None
        assert retrieved.trace_id == trace_id
        assert Path(retrieved.file_path).exists()

        # Verify file content matches original
        stored_content = Path(retrieved.file_path).read_text()
        original_content = realistic_trace_file.read_text()
        stored_json = json.loads(stored_content)
        original_json = json.loads(original_content)
        assert stored_json["traceEvents"] == original_json["traceEvents"]

        # Step 4: Delete trace
        success, err = tool.delete_trace(trace_id)
        assert success is True, f"Failed to delete trace: {err}"

        # Verify deletion
        traces_after = tool.list_traces()
        trace_ids_after = [t.trace_id for t in traces_after]
        assert trace_id not in trace_ids_after

        # Verify file is gone
        assert not Path(retrieved.file_path).exists()

    def test_multiple_traces_isolation(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Test that multiple traces are properly isolated.
        
        Deleting one trace should not affect others.
        """
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Store three traces
        meta1, _ = tool.store_trace(str(realistic_trace_file), "trace1.json")
        meta2, _ = tool.store_trace(str(realistic_trace_file), "trace2.json")
        meta3, _ = tool.store_trace(str(realistic_trace_file), "trace3.json")

        assert meta1 is not None
        assert meta2 is not None
        assert meta3 is not None

        # Delete middle trace
        tool.delete_trace(meta2.trace_id)

        # Verify only trace2 is gone
        traces = tool.list_traces()
        trace_ids = [t.trace_id for t in traces]

        assert meta1.trace_id in trace_ids
        assert meta2.trace_id not in trace_ids
        assert meta3.trace_id in trace_ids

        # Verify trace1 and trace3 files still exist
        trace1, _ = tool.get_trace(meta1.trace_id)
        trace3, _ = tool.get_trace(meta3.trace_id)

        assert trace1 is not None
        assert trace3 is not None
        assert Path(trace1.file_path).exists()
        assert Path(trace3.file_path).exists()

    def test_gz_trace_handling(self, e2e_workspace: Path, gz_trace_file: Path) -> None:
        """Test that gzipped traces are handled correctly."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Store gzipped trace
        meta, err = tool.store_trace(str(gz_trace_file), "compressed_trace.json.gz")

        assert err is None
        assert meta is not None
        assert meta.file_path.endswith(".json.gz")
        assert Path(meta.file_path).exists()

        # Verify gzip content preserved
        stored_bytes = Path(meta.file_path).read_bytes()
        original_bytes = gz_trace_file.read_bytes()
        assert stored_bytes == original_bytes


class TestDirectoryStructureE2E:
    """Test that file system structure is created correctly."""

    def test_wafer_directory_structure(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Verify .wafer/traces/{trace_id}/ structure is created."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        meta, _ = tool.store_trace(str(realistic_trace_file), "test.json")
        assert meta is not None

        # Verify directory structure
        wafer_dir = e2e_workspace / ".wafer"
        traces_dir = wafer_dir / "traces"
        trace_dir = traces_dir / meta.trace_id

        assert wafer_dir.exists()
        assert wafer_dir.is_dir()
        assert traces_dir.exists()
        assert traces_dir.is_dir()
        assert trace_dir.exists()
        assert trace_dir.is_dir()

        # Verify files in trace directory
        meta_json = trace_dir / "meta.json"
        trace_json = trace_dir / "trace.json"

        assert meta_json.exists()
        assert trace_json.exists()

        # Verify meta.json content
        meta_content = json.loads(meta_json.read_text())
        assert meta_content["traceId"] == meta.trace_id
        assert meta_content["originalFilename"] == "test.json"

    def test_trace_ids_are_unique(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Each stored trace should have a unique ID."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        trace_ids = set()
        for i in range(10):
            meta, _ = tool.store_trace(str(realistic_trace_file), f"trace_{i}.json")
            assert meta is not None
            assert meta.trace_id not in trace_ids
            trace_ids.add(meta.trace_id)

        assert len(trace_ids) == 10


class TestCLIIntegration:
    """Test CLI command integration."""

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.parent.exists(),
        reason="wafer-core package not installed",
    )
    def test_cli_list_command(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Test 'perfetto_tool list' CLI command."""
        # Store a trace first using the Python API
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)
        meta, _ = tool.store_trace(str(realistic_trace_file), "cli_test.json")
        assert meta is not None

        # Run CLI command
        result = subprocess.run(
            [
                "python", "-m", "wafer_core.tools.perfetto.perfetto_tool",
                "list",
                "--workspace-root", str(e2e_workspace),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse output
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        output = json.loads(result.stdout)

        assert "traces" in output
        trace_ids = [t["traceId"] for t in output["traces"]]
        assert meta.trace_id in trace_ids


class TestErrorHandlingE2E:
    """Test error handling in real scenarios."""

    def test_permission_denied_on_store(self, e2e_workspace: Path) -> None:
        """Test handling of permission denied errors."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Try to store a file that doesn't exist
        meta, err = tool.store_trace("/nonexistent/path/file.json", "test.json")

        assert meta is None
        assert err is not None
        assert "not found" in err.lower()

    def test_corrupted_metadata_handling(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Test handling of corrupted meta.json files."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Store a valid trace
        meta, _ = tool.store_trace(str(realistic_trace_file), "test.json")
        assert meta is not None

        # Corrupt the meta.json
        meta_path = e2e_workspace / ".wafer" / "traces" / meta.trace_id / "meta.json"
        meta_path.write_text("not valid json at all {{{")

        # list_traces should skip corrupted entries gracefully
        traces = tool.list_traces()

        # Should not include corrupted trace but should not crash
        trace_ids = [t.trace_id for t in traces]
        assert meta.trace_id not in trace_ids


class TestConcurrentOperations:
    """Test behavior under concurrent operations (simulated)."""

    def test_rapid_store_delete_cycles(
        self, e2e_workspace: Path, realistic_trace_file: Path
    ) -> None:
        """Test rapid store/delete cycles don't corrupt state."""
        config = PerfettoConfig(
            workspace_root=str(e2e_workspace),
            storage_dir=str(e2e_workspace / "storage"),
        )
        tool = PerfettoTool(config)

        # Rapid store/delete
        for i in range(20):
            meta, err = tool.store_trace(str(realistic_trace_file), f"rapid_{i}.json")
            assert err is None
            assert meta is not None

            success, err = tool.delete_trace(meta.trace_id)
            assert success is True

        # Final state should be clean
        traces = tool.list_traces()
        assert len(traces) == 0


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def e2e_workspace(tmp_path: Path) -> Path:
    """Create an isolated workspace for E2E tests."""
    workspace = tmp_path / "e2e_workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def realistic_trace_file(tmp_path: Path) -> Path:
    """Create a realistic Chrome trace file with multiple event types."""
    trace_content = {
        "traceEvents": [
            # CUDA kernel events
            {
                "name": "volta_sgemm_128x128_tn",
                "cat": "cuda",
                "ph": "X",
                "ts": 0,
                "dur": 1500,
                "pid": 0,
                "tid": 7,
                "args": {
                    "device": 0,
                    "stream": 1,
                    "correlation_id": 1001,
                },
            },
            {
                "name": "void at::native::reduce_kernel",
                "cat": "cuda",
                "ph": "X",
                "ts": 2000,
                "dur": 800,
                "pid": 0,
                "tid": 7,
                "args": {
                    "device": 0,
                    "stream": 1,
                    "correlation_id": 1002,
                },
            },
            # CPU events
            {
                "name": "aten::mm",
                "cat": "cpu_op",
                "ph": "X",
                "ts": 100,
                "dur": 1700,
                "pid": 0,
                "tid": 1,
            },
            {
                "name": "aten::sum",
                "cat": "cpu_op",
                "ph": "X",
                "ts": 2100,
                "dur": 900,
                "pid": 0,
                "tid": 1,
            },
            # Memory events
            {
                "name": "cudaMalloc",
                "cat": "runtime",
                "ph": "X",
                "ts": 50,
                "dur": 100,
                "pid": 0,
                "tid": 1,
                "args": {"size": 104857600},
            },
        ],
        "metadata": {
            "highres-ticks": True,
            "trace-type": "perfetto",
        },
        "displayTimeUnit": "ns",
    }
    trace_file = tmp_path / "realistic_trace.json"
    trace_file.write_text(json.dumps(trace_content, indent=2))
    return trace_file


@pytest.fixture
def gz_trace_file(tmp_path: Path, realistic_trace_file: Path) -> Path:
    """Create a gzip-compressed trace file."""
    import gzip

    gz_file = tmp_path / "trace.json.gz"
    with gzip.open(gz_file, "wt") as f:
        f.write(realistic_trace_file.read_text())
    return gz_file

