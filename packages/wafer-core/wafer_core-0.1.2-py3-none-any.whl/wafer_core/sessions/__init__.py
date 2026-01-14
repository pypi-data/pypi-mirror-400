"""Session management for agent development, training, and deployment.

DEPRECATED: This module is deprecated. Use rollouts directly:
    from wafer_core.rollouts import (
        AgentSession, SessionStore, FileSessionStore,
        EndpointConfig, EnvironmentConfig, Message, SessionStatus,
    )

This module re-exports from wafer_core.rollouts for backwards compatibility.
"""

# Re-export from wafer_core.rollouts for backwards compatibility
from wafer_core.rollouts import (
    AgentSession,
    EndpointConfig,
    EnvironmentConfig,
    FileSessionStore,
    Message,
    SessionStatus,
)
from wafer_core.rollouts.store import SessionStore

# AgentHooks and run_agent_with_session are deprecated
# Use RunConfig with session_store and session_id instead
from wafer_core.sessions.agent import run_agent_with_session  # noqa: E402
from wafer_core.sessions.hooks import AgentHooks  # noqa: E402

# Backwards compatibility aliases
Status = SessionStatus

__all__ = [
    "AgentSession",
    "AgentHooks",
    "EndpointConfig",
    "EnvironmentConfig",
    "FileSessionStore",
    "Message",
    "SessionStore",
    "Status",
    "run_agent_with_session",
    "SessionStatus",
]
