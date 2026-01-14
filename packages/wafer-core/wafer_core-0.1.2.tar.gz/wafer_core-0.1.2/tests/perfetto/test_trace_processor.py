"""Unit tests for Perfetto TraceProcessorManager.

Tests binary management, version detection, and server operations.
"""

import os
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wafer_core.tools.perfetto.trace_processor import (
    TRACE_PROCESSOR_PORT,
    TraceProcessorManager,
    TraceProcessorServer,
    TraceProcessorStatus,
)


class TestTraceProcessorStatusSerialization:
    """Test TraceProcessorStatus serialization."""

    def test_to_dict_contains_all_fields(self) -> None:
        """TraceProcessorStatus.to_dict() should include all fields."""
        status = TraceProcessorStatus(
            available=True,
            binary_path="/path/to/binary",
            version="v49.0-abc123",
            version_matches_ui=True,
            ui_version="v49.0",
        )

        result = status.to_dict()

        assert result["available"] is True
        assert result["binaryPath"] == "/path/to/binary"
        assert result["version"] == "v49.0-abc123"
        assert result["versionMatchesUi"] is True
        assert result["uiVersion"] == "v49.0"
        assert result["error"] is None

    def test_to_dict_with_error(self) -> None:
        """TraceProcessorStatus.to_dict() should include error field."""
        status = TraceProcessorStatus(
            available=False,
            binary_path=None,
            version=None,
            version_matches_ui=False,
            ui_version="v49.0",
            error="Binary not found",
        )

        result = status.to_dict()

        assert result["available"] is False
        assert result["error"] == "Binary not found"


class TestTraceProcessorServerState:
    """Test TraceProcessorServer state management."""

    def test_is_running_returns_true_when_process_active(self) -> None:
        """is_running should return True when process poll returns None."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running

        server = TraceProcessorServer(
            process=mock_process,
            port=9001,
            trace_path="/path/to/trace.json",
            pid=12345,
        )

        assert server.is_running() is True

    def test_is_running_returns_false_when_process_terminated(self) -> None:
        """is_running should return False when process has exited."""
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Exited

        server = TraceProcessorServer(
            process=mock_process,
            port=9001,
            trace_path="/path/to/trace.json",
            pid=12345,
        )

        assert server.is_running() is False

    def test_stop_terminates_running_process(self) -> None:
        """stop() should terminate and wait for process."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running

        server = TraceProcessorServer(
            process=mock_process,
            port=9001,
            trace_path="/path/to/trace.json",
            pid=12345,
        )

        server.stop()

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()


class TestTraceProcessorManagerPlatformDetection:
    """Test platform-specific binary name detection."""

    @pytest.mark.parametrize(
        "system,machine,expected",
        [
            ("darwin", "arm64", "trace_processor_mac_arm64"),
            ("darwin", "aarch64", "trace_processor_mac_arm64"),
            ("darwin", "x86_64", "trace_processor_mac_x64"),
            ("linux", "arm64", "trace_processor_linux_arm64"),
            ("linux", "aarch64", "trace_processor_linux_arm64"),
            ("linux", "x86_64", "trace_processor_linux_x64"),
        ],
    )
    def test_get_platform_binary_name(
        self, system: str, machine: str, expected: str
    ) -> None:
        """Platform detection should return correct binary name."""
        manager = TraceProcessorManager(storage_dir="/tmp/test")

        with patch("platform.system", return_value=system):
            with patch("platform.machine", return_value=machine):
                name, err = manager.get_platform_binary_name()

        assert err is None
        assert name == expected

    def test_get_platform_binary_name_unsupported_platform(self) -> None:
        """Unsupported platform should return error."""
        manager = TraceProcessorManager(storage_dir="/tmp/test")

        with patch("platform.system", return_value="windows"):
            with patch("platform.machine", return_value="x86_64"):
                name, err = manager.get_platform_binary_name()

        assert name is None
        assert err is not None
        assert "unsupported" in err.lower()


class TestTraceProcessorVersionDetection:
    """Test version detection and compatibility."""

    def test_is_version_compatible_same_base_version(self) -> None:
        """Same base version should be compatible."""
        manager = TraceProcessorManager(
            storage_dir="/tmp/test",
            ui_version="v49.0-abc123",
        )

        assert manager.is_version_compatible("v49.0-def456") is True
        assert manager.is_version_compatible("v49.0") is True

    def test_is_version_compatible_different_base_version(self) -> None:
        """Different base versions should not be compatible."""
        manager = TraceProcessorManager(
            storage_dir="/tmp/test",
            ui_version="v49.0-abc123",
        )

        assert manager.is_version_compatible("v48.0-abc123") is False
        assert manager.is_version_compatible("v50.0") is False

    def test_is_version_compatible_no_ui_version(self) -> None:
        """Without UI version, any TP version should be compatible."""
        manager = TraceProcessorManager(storage_dir="/tmp/test")

        assert manager.is_version_compatible("v49.0") is True
        assert manager.is_version_compatible(None) is True

    def test_is_version_compatible_no_tp_version(self) -> None:
        """Without TP version, should assume compatible."""
        manager = TraceProcessorManager(
            storage_dir="/tmp/test",
            ui_version="v49.0",
        )

        assert manager.is_version_compatible(None) is True


class TestTraceProcessorManagerStatus:
    """Test TraceProcessorManager.get_status()."""

    def test_get_status_binary_not_found(self, tmp_path: Path) -> None:
        """Status should indicate binary not found."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        status = manager.get_status()

        assert status.available is False
        assert status.binary_path is None
        assert status.error is not None
        assert "not found" in status.error.lower()

    def test_get_status_binary_exists_and_executable(
        self, tmp_path: Path
    ) -> None:
        """Status should indicate available when binary exists."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        # Create a fake binary
        binary_path = tmp_path / "trace_processor"
        binary_path.write_text("#!/bin/bash\necho 'v49.0'")
        binary_path.chmod(0o755)

        with patch.object(manager, "get_binary_version", return_value="v49.0"):
            status = manager.get_status()

        assert status.available is True
        assert status.binary_path == str(binary_path)


class TestTraceProcessorManagerServerOperations:
    """Test server start/stop operations."""

    def test_get_running_server_returns_none_initially(
        self, tmp_path: Path
    ) -> None:
        """get_running_server should return None when no server started."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        assert manager.get_running_server() is None

    def test_stop_server_when_no_server_running(self, tmp_path: Path) -> None:
        """stop_server should be safe to call when no server running."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        # Should not raise
        manager.stop_server()

        assert manager.get_running_server() is None

    def test_start_server_fails_on_missing_trace_file(
        self, tmp_path: Path
    ) -> None:
        """start_server should fail if trace file doesn't exist."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        # Create a fake binary so we pass that check
        binary_path = tmp_path / "trace_processor"
        binary_path.write_text("fake binary")
        binary_path.chmod(0o755)

        with patch.object(manager, "ensure_binary", return_value=(str(binary_path), None)):
            server, err = manager.start_server("/nonexistent/trace.json")

        assert server is None
        assert err is not None
        assert "not found" in err.lower()

    def test_start_server_fails_on_missing_binary(self, tmp_path: Path) -> None:
        """start_server should fail if binary not available."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        with patch.object(
            manager, "ensure_binary", return_value=(None, "Binary not found")
        ):
            server, err = manager.start_server(str(tmp_path / "trace.json"))

        assert server is None
        assert err is not None
        assert "not available" in err.lower() or "not found" in err.lower()


class TestTraceProcessorManagerInvariants:
    """Property-based tests for TraceProcessorManager invariants."""

    def test_binary_path_within_storage_dir(self, tmp_path: Path) -> None:
        """Binary path should always be within storage directory."""
        manager = TraceProcessorManager(storage_dir=str(tmp_path))

        binary_path = manager.get_binary_path()

        assert str(binary_path).startswith(str(tmp_path))

    def test_default_port_constant(self) -> None:
        """TRACE_PROCESSOR_PORT should be 9001."""
        assert TRACE_PROCESSOR_PORT == 9001

    def test_server_tracks_correct_metadata(self) -> None:
        """TraceProcessorServer should track all provided metadata."""
        mock_process = MagicMock()
        
        server = TraceProcessorServer(
            process=mock_process,
            port=9001,
            trace_path="/path/to/trace.json",
            pid=12345,
        )

        assert server.port == 9001
        assert server.trace_path == "/path/to/trace.json"
        assert server.pid == 12345


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_subprocess_popen():
    """Mock subprocess.Popen for server tests."""
    with patch("subprocess.Popen") as mock:
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock.return_value = mock_process
        yield mock

