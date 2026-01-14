"""Data types for session management.

DEPRECATED: Use rollouts directly:
    from wafer_core.rollouts import Message, AgentSession, SessionStatus, EndpointConfig, EnvironmentConfig

This module re-exports from wafer_core.rollouts for backwards compatibility.
"""

from wafer_core.rollouts.dtypes import (
    AgentSession,
    EndpointConfig,
    EnvironmentConfig,
    Message,
    SessionStatus,
)

# Backwards compatibility alias
Status = SessionStatus

__all__ = [
    "AgentSession",
    "EndpointConfig",
    "EnvironmentConfig",
    "Message",
    "SessionStatus",
    "Status",
]
