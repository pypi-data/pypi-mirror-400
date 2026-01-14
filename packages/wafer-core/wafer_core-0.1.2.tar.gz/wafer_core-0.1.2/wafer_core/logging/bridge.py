"""Log bridge for forwarding Python logs to external systems.

Provides a callback-based system for forwarding logs from wafer-core
to external systems (e.g., VS Code extension's output channel).
"""

from __future__ import annotations

import logging
from collections.abc import Callable

# Global hook for extension to inject log forwarding
_log_bridge: Callable[[str, str], None] | None = None


def set_log_bridge(callback: Callable[[str, str], None]) -> None:
    """Set the log bridge callback.

    The callback will be called for every log record with:
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - message: Formatted log message

    Args:
        callback: Function that takes (level: str, message: str) and forwards logs

    Example:
        def my_bridge(level: str, message: str):
            print(f"[{level}] {message}")

        set_log_bridge(my_bridge)
    """
    global _log_bridge
    _log_bridge = callback


def clear_log_bridge() -> None:
    """Clear the log bridge callback.

    After calling this, logs will not be forwarded to external systems.
    """
    global _log_bridge
    _log_bridge = None


class LogBridgeHandler(logging.Handler):
    """Logging handler that forwards logs to the bridge callback."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the bridge callback."""
        if _log_bridge is not None:
            try:
                level = record.levelname
                message = self.format(record)
                _log_bridge(level, message)
            except Exception:
                # Don't let bridge failures break logging
                pass


def is_log_bridge_set() -> bool:
    """Check if log bridge callback is set.

    Returns:
        True if bridge is set, False otherwise
    """
    return _log_bridge is not None
