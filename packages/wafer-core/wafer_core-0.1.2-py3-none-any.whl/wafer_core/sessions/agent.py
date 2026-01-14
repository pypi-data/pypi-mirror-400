"""Agent runner with session persistence.

DEPRECATED: This module is deprecated. Use rollouts.run_agent with
run_config.session_store and run_config.session_id instead.

This module provides run_agent_with_session, which wraps rollouts.run_agent
and automatically persists messages to a SessionStore.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wafer_core.rollouts import SessionMessage, SessionStatus
from wafer_core.rollouts.agents import run_agent
from wafer_core.rollouts.dtypes import AgentState, StopReason, StreamEvent
from wafer_core.rollouts.dtypes import Message as RolloutsMessage
from wafer_core.sessions.hooks import AgentHooks

if TYPE_CHECKING:
    from wafer_core.rollouts.store import SessionStore


def _rollouts_message_to_session_message(msg: RolloutsMessage) -> SessionMessage:
    """Convert rollouts Message to session Message."""
    # Handle different content types
    if isinstance(msg.content, str):
        content: str | list[dict[str, Any]] = msg.content
    elif isinstance(msg.content, list):
        # Content blocks - serialize to dicts
        content = []
        for block in msg.content:
            if hasattr(block, "to_dict"):
                content.append(block.to_dict())
            elif hasattr(block, "__dict__"):
                content.append(vars(block))
            else:
                content.append({"type": "unknown", "value": str(block)})
    else:
        content = str(msg.content)

    return SessionMessage(
        role=msg.role,
        content=content,
        tool_call_id=getattr(msg, "tool_call_id", None),
    )


async def run_agent_with_session(
    initial_state: AgentState,
    hooks: AgentHooks,
) -> list[AgentState]:
    """Run agent loop with session persistence.

    This wraps rollouts.run_agent and:
    1. Appends messages to session_store as they're generated
    2. Updates session status on completion
    3. Saves environment state at the end

    Args:
        initial_state: Initial AgentState
        hooks: AgentHooks with session_store and session_id configured

    Returns:
        List of AgentStates from the run

    Raises:
        ValueError: If session_store is set but session_id is not
    """
    session_store = hooks.session_store
    session_id = hooks.session_id

    if session_store is not None and session_id is None:
        msg = "session_id required when session_store is provided"
        raise ValueError(msg)

    # Track message count to know what's new
    initial_message_count = len(initial_state.actor.trajectory.messages)

    # Create wrapped on_chunk that also persists messages
    original_on_chunk = hooks.on_chunk
    messages_persisted = initial_message_count

    async def on_chunk_with_persistence(chunk: StreamEvent) -> None:
        nonlocal messages_persisted

        # Call original handler first
        await original_on_chunk(chunk)

        # Check if we have new messages to persist
        # This is a bit hacky - we check the trajectory after each chunk
        # A better approach would be to hook into run_agent's message creation

    # Convert to RunConfig for rollouts
    run_config = hooks.to_run_config()

    # Run the agent
    states = await run_agent(initial_state, run_config)

    # Persist any new messages
    if session_store is not None and session_id is not None:
        final_state = states[-1] if states else initial_state
        final_messages = final_state.actor.trajectory.messages

        # Persist messages that were added during this run
        for msg in final_messages[initial_message_count:]:
            session_msg = _rollouts_message_to_session_message(msg)
            await session_store.append_message(session_id, session_msg)

        # Determine final status
        if final_state.stop == StopReason.TASK_COMPLETED:
            status = SessionStatus.COMPLETED
        elif final_state.stop == StopReason.ABORTED:
            status = SessionStatus.ABORTED
        elif final_state.stop in (StopReason.MAX_TURNS, StopReason.MAX_TOKENS):
            status = SessionStatus.TRUNCATED
        else:
            status = SessionStatus.PENDING

        # Save environment state and update status
        env_state = None
        if final_state.environment is not None:
            env_state = await final_state.environment.serialize()

        await session_store.update(
            session_id,
            status=status,
            environment_state=env_state,
        )

    return states


async def resume_session(
    session_store: SessionStore,
    session_id: str,
    hooks: AgentHooks,
    branch_point: int | None = None,
) -> tuple[AgentState | None, str | None]:
    """Resume a session from a saved state.

    Args:
        session_store: SessionStore to load from
        session_id: Session ID to resume
        hooks: AgentHooks for the resumed run
        branch_point: Optional message index to branch from (default: resume from end)

    Returns:
        (initial_state, None) on success, (None, error) on failure
    """
    # Load parent session
    parent, err = await session_store.get(session_id)
    if err or parent is None:
        return None, err or f"Session not found: {session_id}"

    # Determine branch point
    if branch_point is None:
        branch_point = len(parent.messages)

    # If branching (not resuming from end), create child session
    if branch_point < len(parent.messages) or hooks.session_id != session_id:
        # This is a branch - caller should create a new session first
        pass

    # TODO: Reconstruct AgentState from session
    # This requires:
    # 1. Creating Actor from endpoint config and messages
    # 2. Deserializing environment from environment_state
    # 3. Setting up proper turn_idx

    # For now, return error indicating this needs more work
    return None, "resume_session not fully implemented - need environment deserialization"
