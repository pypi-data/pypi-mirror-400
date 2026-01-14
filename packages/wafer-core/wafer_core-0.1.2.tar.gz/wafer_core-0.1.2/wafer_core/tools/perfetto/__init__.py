"""Perfetto Tool - Chrome trace profiling and visualization.

This module provides:
1. Trace management: Store, list, delete Chrome JSON traces
2. trace_processor management: Download/build binary, version checking
3. trace_processor server: Start/stop HTTP RPC server for Perfetto UI
4. Build from source: Pure Python builder for trace_processor

Architecture:
- This is the "backend" logic for the Perfetto tool
- Frontend apps (wevin-extension, wafer-cli) call this module
- Similar pattern to ncu_profile_tools.py

Usage:
    from wafer_core.tools.perfetto import (
        PerfettoTool,
        TraceManager,
        TraceProcessorManager,
        build_trace_processor,  # For manual builds
    )
"""

from wafer_core.tools.perfetto.build_trace_processor import (
    BuildConfig,
    BuildResult,
    TraceProcessorBuilder,
    build_trace_processor,
)
from wafer_core.tools.perfetto.perfetto_tool import (
    PerfettoConfig,
    PerfettoTool,
)
from wafer_core.tools.perfetto.trace_manager import (
    TraceManager,
    TraceMeta,
)
from wafer_core.tools.perfetto.trace_processor import (
    TraceProcessorManager,
    TraceProcessorStatus,
)

__all__ = [
    "PerfettoTool",
    "PerfettoConfig",
    "TraceManager",
    "TraceMeta",
    "TraceProcessorManager",
    "TraceProcessorStatus",
    "TraceProcessorBuilder",
    "BuildConfig",
    "BuildResult",
    "build_trace_processor",
]

