"""Telemetry hooks for wafer-core.

Provides a callback-based system for forwarding telemetry events
to external systems (e.g., VS Code extension's PostHog client).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Global hook for extension to inject telemetry
_telemetry_hook: Callable[[str, dict[str, Any]], None] | None = None


def set_telemetry_hook(hook: Callable[[str, dict[str, Any]], None]) -> None:
    """Set the telemetry hook callback.

    The hook will be called for every tracked event with:
    - event_name: Name of the event (e.g., "compile_cuda")
    - properties: Dictionary of event properties

    Args:
        hook: Callback function to handle telemetry events

    Example:
        def my_hook(event_name, properties):
            print(f"Event: {event_name}, Props: {properties}")

        set_telemetry_hook(my_hook)
    """
    global _telemetry_hook
    _telemetry_hook = hook


def clear_telemetry_hook() -> None:
    """Clear the telemetry hook callback.

    After calling this, telemetry events will be silently ignored.
    """
    global _telemetry_hook
    _telemetry_hook = None


def track_event(event_name: str, properties: dict[str, Any]) -> None:
    """Track a telemetry event.

    If a telemetry hook is set, the event will be forwarded to it.
    Otherwise, the event is silently ignored.

    Args:
        event_name: Name of the event (e.g., "compile_cuda")
        properties: Dictionary of event properties
    """
    if _telemetry_hook is not None:
        try:
            _telemetry_hook(event_name, properties)
        except Exception:
            # Don't let telemetry failures break the application
            pass

