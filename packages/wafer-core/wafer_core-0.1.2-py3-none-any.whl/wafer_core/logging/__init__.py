"""Logging utilities for wafer.

Provides standardized logging configuration with:
- Color formatting for console output
- JSON formatting for structured logs
- Async-safe queue handlers
- File rotation with bounded sizes
- Log bridge for external forwarding (e.g., VS Code extension)
"""

from .bridge import (
    LogBridgeHandler,
    clear_log_bridge,
    is_log_bridge_set,
    set_log_bridge,
)
from .color_formatter import ColorFormatter, Colors
from .json_formatter import JSONFormatter
from .logging_config import setup_logging

__all__ = [
    "setup_logging",
    "set_log_bridge",
    "clear_log_bridge",
    "is_log_bridge_set",
    "LogBridgeHandler",
    "ColorFormatter",
    "Colors",
    "JSONFormatter",
]
