"""Agent hooks with session support.

DEPRECATED: This module is deprecated. Use rollouts.RunConfig with
session_store and session_id fields instead.

This module provides AgentHooks, which wraps rollouts.RunConfig and adds
session persistence via SessionStore.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable

    import trio

    from wafer_core.rollouts.dtypes import RunConfig
    from wafer_core.rollouts.store import SessionStore


@dataclass
class AgentHooks:
    """Runtime hooks for agent behavior with session persistence.

    This wraps rollouts.RunConfig and adds session_store/session_id for persistence.
    NOT serializable (contains callables) - for reproducibility, endpoint/environment
    are stored in AgentSession.

    Usage:
        session = await session_store.create(endpoint=..., environment=...)
        hooks = AgentHooks(
            on_chunk=my_stream_handler,
            session_store=session_store,
            session_id=session.session_id,
        )
        # Pass to run_agent_with_session() or convert to RunConfig
    """

    # === Callbacks/Hooks (from RunConfig) ===
    on_chunk: Callable[[Any], Awaitable[None]]  # StreamChunk -> None
    on_input: Callable[[str], Awaitable[str]] | None = None
    confirm_tool: Callable[[Any, Any, Any], Awaitable[tuple[Any, Any]]] | None = None
    handle_tool_error: Callable[[Any, Any], Any] | None = None
    on_step_start: Callable[[Any], Any] | None = None
    handle_stop: Callable[[Any], Any] | None = None
    handle_no_tool: Callable[[Any, Any], Awaitable[Any]] | None = None

    # === Thinking config (from RunConfig) ===
    user_message_for_thinking: str | None = None
    inline_thinking: str | None = None

    # === UI ===
    show_progress: bool = False

    # === Cancellation ===
    cancel_scope: trio.CancelScope | None = None

    # === Session Persistence (NEW) ===
    session_store: SessionStore | None = None
    session_id: str | None = None

    def to_run_config(self) -> RunConfig:  # noqa: ANN401
        """Convert to rollouts.RunConfig for compatibility.

        Drops session_store/session_id since RunConfig doesn't have them.
        """
        from wafer_core.rollouts.dtypes import RunConfig

        kwargs: dict[str, Any] = {"on_chunk": self.on_chunk}

        if self.on_input is not None:
            kwargs["on_input"] = self.on_input
        if self.confirm_tool is not None:
            kwargs["confirm_tool"] = self.confirm_tool
        if self.handle_tool_error is not None:
            kwargs["handle_tool_error"] = self.handle_tool_error
        if self.on_step_start is not None:
            kwargs["on_step_start"] = self.on_step_start
        if self.handle_stop is not None:
            kwargs["handle_stop"] = self.handle_stop
        if self.handle_no_tool is not None:
            kwargs["handle_no_tool"] = self.handle_no_tool
        if self.user_message_for_thinking is not None:
            kwargs["user_message_for_thinking"] = self.user_message_for_thinking
        if self.inline_thinking is not None:
            kwargs["inline_thinking"] = self.inline_thinking

        kwargs["show_progress"] = self.show_progress

        return RunConfig(**kwargs)

    @classmethod
    def from_run_config(
        cls,
        run_config: RunConfig,  # noqa: ANN401
        session_store: SessionStore | None = None,
        session_id: str | None = None,
    ) -> AgentHooks:
        """Create AgentHooks from existing RunConfig, adding session support."""
        return cls(
            on_chunk=run_config.on_chunk,
            on_input=run_config.on_input,
            confirm_tool=run_config.confirm_tool,
            handle_tool_error=run_config.handle_tool_error,
            on_step_start=run_config.on_step_start,
            handle_stop=run_config.handle_stop,
            handle_no_tool=run_config.handle_no_tool,
            user_message_for_thinking=run_config.user_message_for_thinking,
            inline_thinking=run_config.inline_thinking,
            show_progress=run_config.show_progress,
            session_store=session_store,
            session_id=session_id,
        )
