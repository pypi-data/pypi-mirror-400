"""Tests for wafer_core.telemetry module."""

from __future__ import annotations

import time
from typing import Any

import pytest

from wafer_core.telemetry.decorators import with_telemetry
from wafer_core.telemetry.hooks import (
    clear_telemetry_hook,
    set_telemetry_hook,
    track_event,
)


class TestTelemetryHooks:
    """Tests for telemetry hook system."""

    def setup_method(self) -> None:
        """Clear any existing hooks before each test."""
        clear_telemetry_hook()

    def teardown_method(self) -> None:
        """Clear hooks after each test."""
        clear_telemetry_hook()

    def test_track_event_does_nothing_without_hook(self) -> None:
        # Should not raise
        track_event("test_event", {"key": "value"})

    def test_track_event_calls_hook(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)
        track_event("test_event", {"key": "value"})

        assert len(captured) == 1
        assert captured[0] == ("test_event", {"key": "value"})

    def test_clear_hook_stops_tracking(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)
        track_event("event1", {})

        clear_telemetry_hook()
        track_event("event2", {})

        assert len(captured) == 1

    def test_hook_exception_is_silently_caught(self) -> None:
        def bad_hook(event_name: str, properties: dict[str, Any]) -> None:
            raise ValueError("Hook error")

        set_telemetry_hook(bad_hook)
        # Should not raise
        track_event("test_event", {})


class TestWithTelemetryDecorator:
    """Tests for @with_telemetry decorator."""

    def setup_method(self) -> None:
        """Clear any existing hooks before each test."""
        clear_telemetry_hook()

    def teardown_method(self) -> None:
        """Clear hooks after each test."""
        clear_telemetry_hook()

    def test_decorator_calls_function(self) -> None:
        @with_telemetry("test_func")
        def my_func(x: int, y: int) -> int:
            return x + y

        result = my_func(1, 2)
        assert result == 3

    def test_decorator_tracks_success(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("test_func")
        def my_func(x: int, y: int) -> int:
            return x + y

        my_func(1, 2)

        assert len(captured) == 1
        event_name, props = captured[0]
        assert event_name == "test_func"
        assert props["success"] is True
        assert "duration_ms" in props
        assert props["x"] == 1
        assert props["y"] == 2

    def test_decorator_tracks_error(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("failing_func")
        def my_func() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError):
            my_func()

        assert len(captured) == 1
        event_name, props = captured[0]
        assert event_name == "failing_func"
        assert props["success"] is False
        assert props["error_type"] == "ValueError"
        assert "test error" in props["error"]

    def test_decorator_measures_duration(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("slow_func")
        def my_func() -> str:
            time.sleep(0.05)  # 50ms
            return "done"

        my_func()

        assert len(captured) == 1
        duration = captured[0][1]["duration_ms"]
        assert duration >= 40  # Should be at least 40ms (allowing some margin)

    def test_decorator_handles_kwargs(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("kwargs_func")
        def my_func(name: str, count: int = 10) -> str:
            return f"{name}: {count}"

        my_func("test", count=5)

        assert len(captured) == 1
        props = captured[0][1]
        assert props["name"] == "test"
        assert props["count"] == 5

    def test_decorator_truncates_long_strings(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("long_string_func")
        def my_func(data: str) -> None:
            pass

        long_string = "x" * 500
        my_func(long_string)

        assert len(captured) == 1
        props = captured[0][1]
        assert len(props["data"]) < 300  # Should be truncated
        assert "truncated" in props["data"]

    def test_decorator_handles_complex_args(self) -> None:
        captured: list[tuple[str, dict[str, Any]]] = []

        def hook(event_name: str, properties: dict[str, Any]) -> None:
            captured.append((event_name, properties))

        set_telemetry_hook(hook)

        @with_telemetry("complex_args_func")
        def my_func(items: list[int], config: dict[str, str]) -> None:
            pass

        my_func([1, 2, 3], {"key": "value"})

        assert len(captured) == 1
        props = captured[0][1]
        assert "3 items" in props["items"]
        assert "1 keys" in props["config"]

