"""Trace Processor Manager - Binary management for Perfetto trace_processor.

This module handles:
- Downloading trace_processor binary
- Building trace_processor from source (via build_trace_processor.py)
- Version detection and compatibility checking
- Starting/stopping trace_processor HTTP server

Tiger Style:
- Explicit status reporting
- Graceful fallbacks (WASM mode if binary unavailable)
- Clear error messages with actionable suggestions
"""

import logging
import os
import platform
import signal
import stat
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from wafer_core.tools.perfetto.build_trace_processor import (
    BuildConfig,
    TraceProcessorBuilder,
)

logger = logging.getLogger(__name__)

# Constants
TRACE_PROCESSOR_PORT = 9001
TRACE_PROCESSOR_DOWNLOAD_URL = "https://get.perfetto.dev/trace_processor"


@dataclass(frozen=True)
class TraceProcessorStatus:
    """Status of trace_processor binary.
    
    WHY frozen=True: Status is a snapshot, immutable.
    """
    available: bool
    binary_path: str | None
    version: str | None
    version_matches_ui: bool
    ui_version: str | None
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "available": self.available,
            "binaryPath": self.binary_path,
            "version": self.version,
            "versionMatchesUi": self.version_matches_ui,
            "uiVersion": self.ui_version,
            "error": self.error,
        }


@dataclass
class TraceProcessorServer:
    """Handle to a running trace_processor server.
    
    Note: NOT frozen because we track mutable state (process, pid).
    """
    process: subprocess.Popen
    port: int
    trace_path: str
    pid: int

    def is_running(self) -> bool:
        """Check if the server is still running."""
        return self.process.poll() is None

    def stop(self) -> None:
        """Stop the server."""
        if self.is_running():
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


class TraceProcessorManager:
    """Manages trace_processor binary and server.
    
    Responsibilities:
    - Find/download/build trace_processor binary
    - Start/stop trace_processor HTTP server
    - Version management and compatibility checking
    """

    def __init__(
        self,
        storage_dir: str,
        perfetto_source_dir: str | None = None,
        build_script_path: str | None = None,  # Deprecated: kept for API compatibility
        ui_version: str | None = None,
    ):
        """Initialize TraceProcessorManager.
        
        Args:
            storage_dir: Directory to store trace_processor binary
            perfetto_source_dir: Path to Perfetto source (for building)
            build_script_path: Deprecated - Python build is used instead
            ui_version: Expected UI version for compatibility checking
        """
        self.storage_dir = Path(storage_dir)
        self.perfetto_source_dir = Path(perfetto_source_dir) if perfetto_source_dir else None
        # build_script_path is deprecated - we now use Python build_trace_processor module
        self.ui_version = ui_version
        
        # Track running server
        self._server: TraceProcessorServer | None = None

    def get_binary_path(self) -> Path:
        """Get the expected path to trace_processor binary."""
        return self.storage_dir / "trace_processor"

    def get_platform_binary_name(self) -> tuple[str | None, str | None]:
        """Get platform-specific binary name.
        
        Returns:
            (binary_name, None) on success, (None, error_message) on failure
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "darwin":
            if machine in ("arm64", "aarch64"):
                return "trace_processor_mac_arm64", None
            else:
                return "trace_processor_mac_x64", None
        elif system == "linux":
            if machine in ("arm64", "aarch64"):
                return "trace_processor_linux_arm64", None
            else:
                return "trace_processor_linux_x64", None
        else:
            return None, f"Unsupported platform: {system}/{machine}"

    def get_binary_version(self, binary_path: Path) -> str | None:
        """Get version from trace_processor binary.
        
        Returns:
            Version string (e.g., "v49.0-33a4fd078") or None
        """
        if not binary_path.exists():
            return None
        
        try:
            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout
            
            # Try to match version with commit hash (e.g., v49.0-33a4fd078)
            import re
            match = re.search(r"v\d+\.\d+-[a-f0-9]+", output, re.IGNORECASE)
            if match:
                return match.group(0)
            
            # Fallback to base version (e.g., v49.0)
            match = re.search(r"v\d+\.\d+", output, re.IGNORECASE)
            if match:
                return match.group(0)
            
            return None
        except Exception as e:
            logger.warning(f"Failed to get trace_processor version: {e}")
            return None

    def is_version_compatible(self, tp_version: str | None) -> bool:
        """Check if trace_processor version is compatible with UI.
        
        Returns:
            True if compatible or if we can't determine compatibility
        """
        if not self.ui_version or not tp_version:
            return True
        
        # Extract base versions (v49.0 from v49.0-33a4fd078)
        import re
        
        def get_base_version(v: str) -> str | None:
            match = re.match(r"v\d+\.\d+", v)
            return match.group(0) if match else None
        
        ui_base = get_base_version(self.ui_version)
        tp_base = get_base_version(tp_version)
        
        if not ui_base or not tp_base:
            return True
        
        return ui_base == tp_base

    def ensure_binary(self) -> tuple[str | None, str | None]:
        """Ensure trace_processor binary is available.
        
        Tries in order:
        1. Use existing binary if version matches
        2. Build from source (if available)
        3. Download prebuilt binary
        
        Returns:
            (binary_path, None) on success, (None, error_message) on failure
        """
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        binary_path = self.get_binary_path()
        
        # Check existing binary
        if binary_path.exists():
            try:
                os.access(binary_path, os.X_OK)
                version = self.get_binary_version(binary_path)
                if self.is_version_compatible(version):
                    logger.info(f"Using existing trace_processor at {binary_path} (version: {version})")
                    return str(binary_path), None
                else:
                    logger.warning(f"Existing trace_processor version mismatch (TP: {version}, UI: {self.ui_version})")
            except Exception:
                # Binary exists but not executable, try to fix
                try:
                    binary_path.chmod(binary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    version = self.get_binary_version(binary_path)
                    if self.is_version_compatible(version):
                        logger.info(f"Fixed permissions for trace_processor at {binary_path}")
                        return str(binary_path), None
                except Exception:
                    pass
        
        # Try building from source
        build_result = self._try_build_from_source()
        if build_result:
            return build_result, None
        
        # Try downloading
        download_result, download_err = self._try_download()
        if download_result:
            return download_result, None
        
        # All methods failed
        return None, download_err or "Failed to obtain trace_processor binary"

    def _try_build_from_source(self) -> str | None:
        """Try to build trace_processor from source using Python builder.
        
        Uses the pure-Python build_trace_processor module instead of shell scripts.
        
        Returns:
            Path to binary on success, None on failure
        """
        if not self.perfetto_source_dir:
            logger.info("Perfetto source not configured - skipping source build")
            return None
        
        if not self.perfetto_source_dir.exists():
            logger.info(f"Perfetto source not found at {self.perfetto_source_dir} - skipping source build")
            return None
        
        logger.info("Building trace_processor from source (using Python builder)...")
        logger.info("This may take 5-10 minutes on first build")
        
        try:
            config = BuildConfig(
                perfetto_source_dir=self.perfetto_source_dir,
                storage_dir=self.storage_dir,
                ui_version=self.ui_version,
            )
            
            builder = TraceProcessorBuilder(config)
            result = builder.build()
            
            if not result.success:
                logger.warning(f"Build from source failed: {result.error}")
                return None
            
            if result.binary_path and Path(result.binary_path).exists():
                logger.info(f"Successfully built trace_processor from source (version: {result.version})")
                return result.binary_path
            else:
                logger.warning("Build completed but binary not found")
                return None
                
        except Exception as e:
            logger.warning(f"Build from source failed: {e}")
            return None

    def _try_download(self) -> tuple[str | None, str | None]:
        """Try to download prebuilt trace_processor binary.
        
        Returns:
            (path, None) on success, (None, error_message) on failure
        """
        binary_name, err = self.get_platform_binary_name()
        if err:
            return None, err
        
        assert binary_name is not None
        url = f"{TRACE_PROCESSOR_DOWNLOAD_URL}/{binary_name}"
        target_path = self.storage_dir / binary_name
        
        logger.info(f"Downloading trace_processor from {url}")
        
        try:
            # Download with urllib (no external dependencies)
            urllib.request.urlretrieve(url, target_path)
            
            # Make executable
            target_path.chmod(target_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            # Create symlink to standard name
            binary_path = self.get_binary_path()
            if binary_path.exists() or binary_path.is_symlink():
                binary_path.unlink()
            binary_path.symlink_to(binary_name)
            
            # Check version
            version = self.get_binary_version(binary_path)
            if not self.is_version_compatible(version):
                logger.warning(f"Downloaded binary version mismatch (TP: {version}, UI: {self.ui_version})")
                logger.warning("Some queries may fail - consider building from source")
            
            logger.info(f"Downloaded trace_processor to {binary_path} (version: {version})")
            return str(binary_path), None
            
        except Exception as e:
            return None, f"Failed to download trace_processor: {e}"

    def get_status(self) -> TraceProcessorStatus:
        """Get current status of trace_processor.
        
        Returns:
            TraceProcessorStatus with availability info
        """
        binary_path = self.get_binary_path()
        
        if not binary_path.exists():
            return TraceProcessorStatus(
                available=False,
                binary_path=None,
                version=None,
                version_matches_ui=False,
                ui_version=self.ui_version,
                error="Binary not found",
            )
        
        try:
            os.access(binary_path, os.X_OK)
        except Exception:
            return TraceProcessorStatus(
                available=False,
                binary_path=str(binary_path),
                version=None,
                version_matches_ui=False,
                ui_version=self.ui_version,
                error="Binary not executable",
            )
        
        version = self.get_binary_version(binary_path)
        version_matches = self.is_version_compatible(version)
        
        return TraceProcessorStatus(
            available=True,
            binary_path=str(binary_path),
            version=version,
            version_matches_ui=version_matches,
            ui_version=self.ui_version,
        )

    def start_server(self, trace_path: str, port: int = TRACE_PROCESSOR_PORT) -> tuple[TraceProcessorServer | None, str | None]:
        """Start trace_processor HTTP server with a trace file.
        
        Args:
            trace_path: Path to trace file to load
            port: HTTP port to listen on (default: 9001)
            
        Returns:
            (TraceProcessorServer, None) on success, (None, error_message) on failure
        """
        # Stop existing server first
        self.stop_server()
        
        # Ensure binary available
        binary_path, err = self.ensure_binary()
        if err or not binary_path:
            return None, err or "trace_processor binary not available"
        
        # Validate trace file
        if not Path(trace_path).exists():
            return None, f"Trace file not found: {trace_path}"
        
        # Kill any process using the port
        self._kill_port_users(port)
        
        # Start server
        logger.info(f"Starting trace_processor --httpd on port {port}")
        try:
            process = subprocess.Popen(
                [binary_path, "--httpd", f"--http-port={port}", trace_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Wait for server to be ready
            if not self._wait_for_server(port, timeout=30):
                # Check if process died
                if process.poll() is not None:
                    stderr = process.stderr.read().decode() if process.stderr else ""
                    return None, f"trace_processor exited: {stderr[:500]}"
                return None, f"trace_processor server not responding on port {port}"
            
            server = TraceProcessorServer(
                process=process,
                port=port,
                trace_path=trace_path,
                pid=process.pid,
            )
            self._server = server
            
            logger.info(f"trace_processor server ready on port {port}")
            return server, None
            
        except Exception as e:
            return None, f"Failed to start trace_processor: {e}"

    def stop_server(self) -> None:
        """Stop the running trace_processor server."""
        if self._server:
            logger.info("Stopping trace_processor server")
            self._server.stop()
            self._server = None

    def get_running_server(self) -> TraceProcessorServer | None:
        """Get the currently running server (if any).
        
        Returns:
            TraceProcessorServer if running, None otherwise
        """
        if self._server and self._server.is_running():
            return self._server
        return None

    def _kill_port_users(self, port: int) -> None:
        """Kill trace_processor processes using the specified port.
        
        WHY: trace_processor won't start if port is in use.
        Only kills processes that are actually trace_processor instances.
        """
        system = platform.system().lower()
        
        if system in ("darwin", "linux"):
            try:
                result = subprocess.run(
                    ["lsof", f"-ti:{port}"],
                    capture_output=True,
                    text=True,
                )
                pids = result.stdout.strip().split()
                
                for pid in pids:
                    if not pid:
                        continue
                    
                    try:
                        pid_int = int(pid)
                        
                        # Check if this is actually trace_processor
                        is_trace_processor = False
                        if system == "linux":
                            try:
                                # Read process name from /proc/PID/comm
                                comm_path = Path(f"/proc/{pid_int}/comm")
                                if comm_path.exists():
                                    proc_name = comm_path.read_text().strip()
                                    is_trace_processor = "trace_processor" in proc_name.lower()
                                
                                # Also check exe symlink
                                if not is_trace_processor:
                                    exe_path = Path(f"/proc/{pid_int}/exe")
                                    if exe_path.exists():
                                        exe_target = exe_path.readlink()
                                        is_trace_processor = "trace_processor" in str(exe_target).lower()
                            except (FileNotFoundError, PermissionError, OSError):
                                # Process might have died, skip
                                continue
                        elif system == "darwin":
                            # On macOS, use ps to get process name
                            try:
                                ps_result = subprocess.run(
                                    ["ps", "-p", str(pid_int), "-o", "comm="],
                                    capture_output=True,
                                    text=True,
                                    timeout=1,
                                )
                                proc_name = ps_result.stdout.strip()
                                is_trace_processor = "trace_processor" in proc_name.lower()
                            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                                continue
                        
                        # Only kill if it's trace_processor
                        if is_trace_processor:
                            # Try graceful termination first
                            os.kill(pid_int, signal.SIGTERM)
                            time.sleep(0.5)
                            try:
                                # Check if still running, force kill if needed
                                os.kill(pid_int, 0)  # Check if process exists
                                os.kill(pid_int, signal.SIGKILL)
                                logger.info(f"Killed trace_processor process {pid_int} using port {port}")
                            except ProcessLookupError:
                                # Already dead
                                logger.info(f"trace_processor process {pid_int} terminated gracefully")
                        else:
                            logger.warning(
                                f"Port {port} is in use by non-trace_processor process (PID {pid_int}) - not killing"
                            )
                            return  # Don't proceed if port is used by something else
                            
                    except (ValueError, ProcessLookupError, OSError):
                        # Process doesn't exist or invalid PID
                        pass
                        
            except Exception as e:
                logger.warning(f"Failed to check port users: {e}")
                # Don't proceed if we can't verify what's using the port
                return
        
        # Wait for port to be released
        time.sleep(1)

    def _wait_for_server(self, port: int, timeout: int = 30) -> bool:
        """Wait for server to be ready on port.
        
        Args:
            port: Port to check
            timeout: Maximum seconds to wait
            
        Returns:
            True if server is ready, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try HTTP connection to /status endpoint
                import http.client
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                conn.request("GET", "/status")
                response = conn.getresponse()
                if response.status == 200:
                    return True
            except Exception:
                pass
            
            time.sleep(1)
        
        return False

