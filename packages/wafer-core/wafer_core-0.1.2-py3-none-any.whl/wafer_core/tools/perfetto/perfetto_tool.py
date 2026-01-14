#!/usr/bin/env python3
"""Perfetto Tool - Main interface for Perfetto trace profiling.

This is the main entry point for the Perfetto tool, providing:
- Trace management (upload, list, delete)
- trace_processor server management
- CLI interface for standalone usage

Usage:
    python -m wafer_core.tools.perfetto.perfetto_tool check
    python -m wafer_core.tools.perfetto.perfetto_tool list --workspace-root /path/to/workspace
    python -m wafer_core.tools.perfetto.perfetto_tool store FILE --workspace-root /path/to/workspace
    python -m wafer_core.tools.perfetto.perfetto_tool delete TRACE_ID --workspace-root /path/to/workspace
    python -m wafer_core.tools.perfetto.perfetto_tool start-server TRACE_PATH --storage-dir /path/to/storage
    python -m wafer_core.tools.perfetto.perfetto_tool stop-server

Tiger Style:
- Single source of truth for Perfetto operations
- Explicit configuration via PerfettoConfig
- CLI for testing and standalone usage
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from wafer_core.tools.perfetto.trace_manager import TraceManager, TraceMeta
from wafer_core.tools.perfetto.trace_processor import (
    TRACE_PROCESSOR_PORT,
    TraceProcessorManager,
    TraceProcessorStatus,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PerfettoConfig:
    """Configuration for Perfetto tool.
    
    WHY frozen=True: Configuration is immutable once created.
    """
    workspace_root: str
    storage_dir: str
    perfetto_source_dir: str | None = None
    build_script_path: str | None = None
    ui_version: str | None = None


class PerfettoTool:
    """Main interface for Perfetto trace profiling tool.
    
    This class orchestrates:
    - TraceManager for trace file storage
    - TraceProcessorManager for binary and server management
    """

    def __init__(self, config: PerfettoConfig):
        """Initialize PerfettoTool.
        
        Args:
            config: PerfettoConfig with paths and settings
        """
        self.config = config
        self.trace_manager = TraceManager(config.workspace_root)
        self.processor_manager = TraceProcessorManager(
            storage_dir=config.storage_dir,
            perfetto_source_dir=config.perfetto_source_dir,
            build_script_path=config.build_script_path,
            ui_version=config.ui_version,
        )

    # ── Trace Management ─────────────────────────────────────────────────────

    def list_traces(self) -> list[TraceMeta]:
        """List all traces in the workspace.
        
        Returns:
            List of TraceMeta sorted by timestamp (newest first)
        """
        return self.trace_manager.list_traces()

    def get_trace(self, trace_id: str) -> tuple[TraceMeta | None, str | None]:
        """Get a specific trace by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            (TraceMeta, None) on success, (None, error_message) on failure
        """
        return self.trace_manager.get_trace(trace_id)

    def store_trace(
        self,
        source_path: str,
        original_filename: str | None = None,
        workspace_id: str | None = None,
    ) -> tuple[TraceMeta | None, str | None]:
        """Store a trace file in the workspace.
        
        Args:
            source_path: Path to the source trace file
            original_filename: Original name of the file (default: basename of source_path)
            workspace_id: Optional workspace identifier
            
        Returns:
            (TraceMeta, None) on success, (None, error_message) on failure
        """
        if not original_filename:
            original_filename = Path(source_path).name
        
        return self.trace_manager.store_trace(
            source_path=source_path,
            original_filename=original_filename,
            workspace_id=workspace_id,
        )

    def delete_trace(self, trace_id: str) -> tuple[bool, str | None]:
        """Delete a trace by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            (True, None) on success, (False, error_message) on failure
        """
        return self.trace_manager.delete_trace(trace_id)

    def validate_trace(self, trace_path: str) -> tuple[bool, str | None]:
        """Validate a trace file.
        
        Args:
            trace_path: Path to trace file
            
        Returns:
            (True, None) on valid, (False, error_message) on invalid
        """
        return self.trace_manager.validate_trace_file(trace_path)

    # ── Trace Processor Management ───────────────────────────────────────────

    def check_processor(self) -> TraceProcessorStatus:
        """Check trace_processor status.
        
        Returns:
            TraceProcessorStatus with availability info
        """
        return self.processor_manager.get_status()

    def ensure_processor(self) -> tuple[str | None, str | None]:
        """Ensure trace_processor binary is available.
        
        Returns:
            (binary_path, None) on success, (None, error_message) on failure
        """
        return self.processor_manager.ensure_binary()

    def start_server(
        self,
        trace_path: str,
        port: int = TRACE_PROCESSOR_PORT,
    ) -> tuple[dict | None, str | None]:
        """Start trace_processor server with a trace.
        
        Args:
            trace_path: Path to trace file to load
            port: HTTP port (default: 9001)
            
        Returns:
            ({"port": int, "pid": int}, None) on success, (None, error_message) on failure
        """
        # Validate trace first
        valid, err = self.validate_trace(trace_path)
        if err:
            return None, err
        
        server, err = self.processor_manager.start_server(trace_path, port)
        if err or not server:
            return None, err
        
        return {"port": server.port, "pid": server.pid}, None

    def stop_server(self) -> None:
        """Stop the trace_processor server."""
        self.processor_manager.stop_server()

    def get_server_status(self) -> dict:
        """Get status of running server.
        
        Returns:
            Dictionary with server status
        """
        server = self.processor_manager.get_running_server()
        if server:
            return {
                "running": True,
                "port": server.port,
                "pid": server.pid,
                "tracePath": server.trace_path,
            }
        return {"running": False}

    # ── CLI Interface ────────────────────────────────────────────────────────────


def cmd_check(args: argparse.Namespace) -> dict:
    """Check trace_processor status."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root or ".",
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
        ui_version=args.ui_version,
    )
    tool = PerfettoTool(config)
    status = tool.check_processor()
    return status.to_dict()


def cmd_list(args: argparse.Namespace) -> dict:
    """List traces in workspace."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root,
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
    )
    tool = PerfettoTool(config)
    traces = tool.list_traces()
    return {"traces": [t.to_dict() for t in traces]}


def cmd_store(args: argparse.Namespace) -> dict:
    """Store a trace file."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root,
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
    )
    tool = PerfettoTool(config)
    meta, err = tool.store_trace(
        source_path=args.file,
        original_filename=args.filename,
    )
    if err:
        return {"success": False, "error": err}
    assert meta is not None
    return {"success": True, "trace": meta.to_dict()}


def cmd_delete(args: argparse.Namespace) -> dict:
    """Delete a trace."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root,
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
    )
    tool = PerfettoTool(config)
    success, err = tool.delete_trace(args.trace_id)
    if err:
        return {"success": False, "error": err}
    return {"success": True}


def cmd_start_server(args: argparse.Namespace) -> dict:
    """Start trace_processor server."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root or ".",
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
        perfetto_source_dir=args.perfetto_source,
        build_script_path=args.build_script,
        ui_version=args.ui_version,
    )
    tool = PerfettoTool(config)
    server_info, err = tool.start_server(args.trace_path, args.port)
    if err:
        return {"success": False, "error": err}
    assert server_info is not None
    return {"success": True, **server_info}


def cmd_stop_server(args: argparse.Namespace) -> dict:
    """Stop trace_processor server."""
    config = PerfettoConfig(
        workspace_root=args.workspace_root or ".",
        storage_dir=args.storage_dir or str(Path.home() / ".wafer" / "perfetto"),
    )
    tool = PerfettoTool(config)
    tool.stop_server()
    return {"success": True}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Perfetto Tool - Chrome trace profiling and visualization"
    )
    parser.add_argument("--workspace-root", "-w", help="Workspace root directory")
    parser.add_argument("--storage-dir", "-s", help="Storage directory for trace_processor")
    parser.add_argument("--ui-version", help="Expected Perfetto UI version")
    parser.add_argument("--perfetto-source", help="Path to Perfetto source directory")
    parser.add_argument("--build-script", help="Deprecated: Python build is used automatically")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # check command
    subparsers.add_parser("check", help="Check trace_processor status")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List traces in workspace")
    list_parser.add_argument("--workspace-root", "-w", required=True, help="Workspace root directory")
    
    # store command
    store_parser = subparsers.add_parser("store", help="Store a trace file")
    store_parser.add_argument("file", help="Path to trace file")
    store_parser.add_argument("--workspace-root", "-w", required=True, help="Workspace root directory")
    store_parser.add_argument("--filename", "-f", help="Original filename")
    
    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a trace")
    delete_parser.add_argument("trace_id", help="Trace ID to delete")
    delete_parser.add_argument("--workspace-root", "-w", required=True, help="Workspace root directory")
    
    # start-server command
    start_parser = subparsers.add_parser("start-server", help="Start trace_processor server")
    start_parser.add_argument("trace_path", help="Path to trace file")
    start_parser.add_argument("--port", "-p", type=int, default=TRACE_PROCESSOR_PORT, help="HTTP port")
    
    # stop-server command
    subparsers.add_parser("stop-server", help="Stop trace_processor server")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    
    # Dispatch command
    if args.command == "check":
        result = cmd_check(args)
    elif args.command == "list":
        result = cmd_list(args)
    elif args.command == "store":
        result = cmd_store(args)
    elif args.command == "delete":
        result = cmd_delete(args)
    elif args.command == "start-server":
        result = cmd_start_server(args)
    elif args.command == "stop-server":
        result = cmd_stop_server(args)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

