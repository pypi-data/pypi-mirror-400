"""Telemetry module for wafer-core.

Provides automatic instrumentation via decorators and a hook system
for forwarding telemetry events to external systems (e.g., PostHog).
"""

from wafer_core.telemetry.decorators import with_telemetry
from wafer_core.telemetry.hooks import (
    clear_telemetry_hook,
    set_telemetry_hook,
    track_event,
)

__all__ = [
    "with_telemetry",
    "set_telemetry_hook",
    "clear_telemetry_hook",
    "track_event",
]

