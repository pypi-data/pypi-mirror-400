"""Event streaming utilities for frontend live updates.

Provides utilities for emitting structured events to JSONL files for frontend consumption.
Used across all benchmarks for real-time evaluation monitoring.
"""

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path


def create_event_emitter(events_file: Path) -> Callable:
    """Create an emit_event callback that writes structured events to JSONL.

    Used for frontend live streaming - writes sample/turn/token events.

    Args:
        events_file: Path to events.jsonl file

    Returns:
        Async callback function that emits events
    """
    f = events_file.open("a", buffering=1)

    async def emit_event(event_type: str, data: dict) -> None:
        """Emit a structured event to events.jsonl."""
        assert event_type is not None and isinstance(event_type, str)
        assert data is not None and isinstance(data, dict)

        event = {"type": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), **data}
        f.write(json.dumps(event) + "\n")
        f.flush()

    return emit_event


def create_streaming_on_chunk(emit_event: Callable, original_on_chunk: Callable | None = None) -> Callable:
    """Wrap on_chunk to emit token events to events.jsonl while preserving original behavior.

    Args:
        emit_event: Event emitter created by create_event_emitter()
        original_on_chunk: Optional existing on_chunk handler to wrap

    Returns:
        Async on_chunk handler that emits events
    """
    from wafer_core.rollouts.dtypes import StreamChunk

    async def on_chunk(chunk: StreamChunk) -> None:
        # Call original handler if provided
        if original_on_chunk is not None:
            await original_on_chunk(chunk)

        # Emit event for frontend
        if chunk.type == "token":
            await emit_event("token", {"content": chunk.data["text"]})
        elif chunk.type == "tool_call_complete":
            await emit_event("tool_call", {"name": chunk.data["name"], "args": chunk.data["args"]})
        elif chunk.type == "tool_result":
            await emit_event("tool_result", {"ok": chunk.data["ok"], "content": chunk.data["content"]})

    return on_chunk
