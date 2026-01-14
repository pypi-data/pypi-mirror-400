"""Telemetry decorators for automatic instrumentation.

Provides the @with_telemetry decorator for automatic tracking of
function calls, duration, success/error status, and arguments.
"""

from __future__ import annotations

import inspect
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from wafer_core.telemetry.hooks import track_event

P = ParamSpec("P")
R = TypeVar("R")


def _extract_properties(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """Extract relevant properties from function arguments.

    Extracts only serializable, non-sensitive argument values.
    Large values (strings > 200 chars) are truncated.

    Args:
        func: The function being called
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary of extracted properties
    """
    props: dict[str, Any] = {}

    # Get function signature to map args to parameter names
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # Map positional args to parameter names
        for i, arg in enumerate(args):
            if i < len(params):
                param_name = params[i]
                props[param_name] = _serialize_value(arg)

        # Add keyword args
        for key, value in kwargs.items():
            props[key] = _serialize_value(value)

    except (ValueError, TypeError):
        # Can't get signature, skip argument extraction
        pass

    return props


def _serialize_value(value: Any) -> Any:
    """Serialize a value for telemetry.

    Handles common types and truncates large strings.

    Args:
        value: Value to serialize

    Returns:
        Serialized value safe for telemetry
    """
    # Primitives
    if value is None or isinstance(value, (bool, int, float)):
        return value

    # Strings - truncate if too long
    if isinstance(value, str):
        if len(value) > 200:
            return f"{value[:200]}... (truncated)"
        return value

    # Lists/tuples - just return length
    if isinstance(value, (list, tuple)):
        return f"[{len(value)} items]"

    # Dicts - just return key count
    if isinstance(value, dict):
        return f"{{{len(value)} keys}}"

    # Objects with dataclass-like structure
    if hasattr(value, "__dataclass_fields__"):
        return f"<{type(value).__name__}>"

    # Fallback - return type name
    return f"<{type(value).__name__}>"


def with_telemetry(event_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to automatically track function calls with telemetry.

    Tracks:
    - Function name
    - Duration (milliseconds)
    - Success/error status
    - Error type and message (on failure)
    - Serialized arguments

    Args:
        event_name: Name for the telemetry event (e.g., "compile_cuda")

    Returns:
        Decorated function

    Example:
        @with_telemetry("compile_cuda")
        def compile_cuda(file_path: str, arch: str) -> CompileResult:
            ...

        # When called, automatically tracks:
        # Event: "compile_cuda"
        # Properties: {
        #     "file_path": "/path/to/file.cu",
        #     "arch": "sm_90",
        #     "success": True,
        #     "duration_ms": 1234.56
        # }
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.time()
            props = _extract_properties(func, args, kwargs)

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000

                props.update(
                    {
                        "success": True,
                        "duration_ms": round(duration_ms, 2),
                    }
                )

                track_event(event_name, props)
                return result

            except Exception as e:
                duration_ms = (time.time() - start) * 1000

                props.update(
                    {
                        "success": False,
                        "error": str(e)[:500],  # Truncate long error messages
                        "error_type": type(e).__name__,
                        "duration_ms": round(duration_ms, 2),
                    }
                )

                track_event(event_name, props)
                raise

        return wrapper

    return decorator

