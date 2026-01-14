"""Wafer Core - utilities and environments for GPU kernel optimization.

Main exports:
- CodingEnvironment: Pi-coding-agent style environment with read/write/edit/bash/wafer tools
- GPUModeSimpleEnvironment: Environment for GPU kernel optimization
- Target configs: ModalTarget, BaremetalTarget, VMTarget
- Sessions: AgentSession, SessionStore, FileSessionStore
- Logging: setup_logging, ColorFormatter, JSONFormatter
- Retry: retry, async_retry, RetryState
- SSH: SSHClient
- Utils: Remote execution, kernel utilities, etc.
- Tools: Perfetto (trace profiling), NCU (profiler tools)
- rollouts: LLM evaluation and agentic RL framework (wafer_core.rollouts)

Note: Imports are lazy to avoid pulling in heavy dependencies for code that only
needs utility modules (e.g., evaluate.py only needs wafer_core.utils.*).
"""

__all__ = [
    "CodingEnvironment",
    "GPUModeSimpleEnvironment",
    "ModalTarget",
    "BaremetalTarget",
    "VMTarget",
    "TargetConfig",
    # Sessions
    "AgentHooks",
    "AgentSession",
    "EndpointConfig",
    "EnvironmentConfig",
    "FileSessionStore",
    "Message",
    "SessionStore",
    "Status",
    "run_agent_with_session",
    # Logging
    "setup_logging",
    "ColorFormatter",
    "JSONFormatter",
    # Retry
    "retry",
    "retry_v2",
    "async_retry",
    "RetryState",
    # Tools
    "PerfettoTool",
    "PerfettoConfig",
    "TraceManager",
    "TraceProcessorManager",
]


def __getattr__(name: str):
    """Lazy import to avoid loading rollouts for utility-only usage."""
    if name == "CodingEnvironment":
        from wafer_core.environments.coding import CodingEnvironment

        return CodingEnvironment

    if name == "GPUModeSimpleEnvironment":
        from wafer_core.environments.gpumode import GPUModeSimpleEnvironment

        return GPUModeSimpleEnvironment

    if name in (
        "AgentHooks",
        "AgentSession",
        "EndpointConfig",
        "EnvironmentConfig",
        "FileSessionStore",
        "Message",
        "SessionStore",
        "Status",
        "run_agent_with_session",
    ):
        from wafer_core import sessions

        return getattr(sessions, name)

    if name in ("BaremetalTarget", "ModalTarget", "TargetConfig", "VMTarget"):
        from wafer_core.utils.kernel_utils import targets

        return getattr(targets, name)

    if name in ("setup_logging", "ColorFormatter", "JSONFormatter"):
        from wafer_core import logging

        return getattr(logging, name)

    if name in ("retry", "retry_v2", "async_retry", "RetryState"):
        from wafer_core import retry

        return getattr(retry, name)

    # Tools
    if name in ("PerfettoTool", "PerfettoConfig"):
        from wafer_core.tools.perfetto import PerfettoConfig, PerfettoTool

        if name == "PerfettoTool":
            return PerfettoTool
        return PerfettoConfig

    if name in ("TraceManager", "TraceProcessorManager"):
        from wafer_core.tools.perfetto import TraceManager, TraceProcessorManager

        if name == "TraceManager":
            return TraceManager
        return TraceProcessorManager

    raise AttributeError(f"module 'wafer_core' has no attribute {name!r}")
