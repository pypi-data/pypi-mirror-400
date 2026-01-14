"""Tmux session management and log streaming for remote execution.

Replaces kerbal.tmux and kerbal.job_monitor with minimal internal implementation.

Usage:
    from wafer_core.ssh import SSHClient
    from wafer_core.remote_jobs import start_tmux_session, stream_log_until_complete, LogStreamConfig

    client = SSHClient("root@gpu:22", ssh_key_path="~/.ssh/id_rsa")

    # Start job in tmux
    session, err = start_tmux_session(
        client, "training", "python train.py",
        workspace="/workspace",
        log_file="/workspace/train.log",
    )

    # Monitor with real-time streaming
    config = LogStreamConfig(
        session_name=session,
        log_file="/workspace/train.log",
        timeout_sec=7200,
    )
    success, exit_code, err = stream_log_until_complete(client, config)
"""

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer_core.ssh import SSHClient

logger = logging.getLogger(__name__)


# =============================================================================
# Types
# =============================================================================


@dataclass
class LogStreamConfig:
    """Configuration for log streaming.

    Attributes:
        session_name: Tmux session name to monitor
        log_file: Absolute path to log file on remote
        timeout_sec: Maximum time to wait for completion
        poll_interval_sec: How often to check for new output
    """

    session_name: str
    log_file: str
    timeout_sec: int = 3600
    poll_interval_sec: float = 2.0


# =============================================================================
# Tmux Session Management
# =============================================================================


def start_tmux_session(
    client: "SSHClient",
    session_name: str,
    command: str,
    workspace: str | None = None,
    log_file: str | None = None,
    env_vars: dict[str, str] | None = None,
) -> tuple[str, str | None]:
    """Start a tmux session running a command.

    Args:
        client: SSHClient instance
        session_name: Tmux session name
        command: Command to run in tmux
        workspace: Working directory (optional)
        log_file: Path to log file for capturing output (optional)
        env_vars: Environment variables to export (optional)

    Returns:
        (session_name, error_message)
        error_message is None on success

    Example:
        session, err = start_tmux_session(
            client, "training", "python train.py",
            workspace="/workspace",
            log_file="/workspace/train.log",
            env_vars={"CUDA_VISIBLE_DEVICES": "0,1"}
        )
    """
    assert client is not None, "SSHClient instance required"
    assert session_name, "session name required"
    assert command, "command required"

    logger.info(f"Starting tmux session: {session_name}")

    # Kill existing session if it exists
    client.exec(f"tmux kill-session -t {session_name} 2>/dev/null || true")

    # Build env prefix if needed
    env_prefix = ""
    if env_vars:
        exports = []
        for key, value in env_vars.items():
            escaped_value = value.replace("'", "'\\''")
            exports.append(f"{key}='{escaped_value}'")
        env_prefix = "export " + " ".join(exports) + " && "

    # Build tmux command
    tmux_cmd = f"tmux new-session -d -s {session_name}"

    if workspace:
        tmux_cmd += f" -c {workspace}"

    # Build full command with env vars
    full_command = env_prefix + command

    if log_file:
        # Use 'script' command for reliable output capture
        # -e: return exit code of child process
        # -f: flush output immediately
        escaped_command = full_command.replace("'", "'\\''")
        tmux_cmd += f" 'script -efc \"{escaped_command}\" {log_file}; echo EXIT_CODE: $? >> {log_file}'"
    else:
        tmux_cmd += f" '{full_command}'"

    result = client.exec(tmux_cmd)
    if result.exit_code != 0:
        return session_name, f"Failed to start tmux: {result.stderr}"

    logger.info(f"Tmux session started: {session_name}")
    return session_name, None


# =============================================================================
# Log Streaming
# =============================================================================


def stream_log_until_complete(
    client: "SSHClient",
    config: LogStreamConfig,
) -> tuple[bool, int | None, str | None]:
    """Stream remote log file in real-time until job completes.

    Args:
        client: SSHClient instance
        config: Log streaming configuration

    Returns:
        (success, exit_code, error_message)
        - success=True if job completed successfully
        - exit_code=int if job exited (0 = success)
        - error_message=str if failed or timeout

    Example:
        config = LogStreamConfig(
            session_name="training-job",
            log_file="/workspace/train.log",
            timeout_sec=7200,
        )
        success, exit_code, err = stream_log_until_complete(client, config)
    """
    assert client is not None, "SSHClient required"
    assert config.session_name, "session_name required"
    assert config.log_file, "log_file required"
    assert config.timeout_sec > 0, "timeout_sec must be positive"

    logger.info(f"Monitoring job: {config.session_name}")
    logger.info(f"Log: {config.log_file}")
    logger.info(f"Timeout: {config.timeout_sec}s")

    last_position = 0
    start_time = time.time()

    while time.time() - start_time < config.timeout_sec:
        # Check if tmux session still alive
        alive = _is_session_alive(client, config.session_name)

        # Stream new log content
        new_content, new_pos = _tail_log_from_position(
            client, config.log_file, last_position
        )

        if new_content:
            print(new_content, end="", flush=True)
            last_position = new_pos

        # If session died, extract exit code and return
        if not alive:
            exit_code = _extract_exit_code_from_log(client, config.log_file)
            if exit_code is not None:
                if exit_code == 0:
                    logger.info(f"Job completed (exit code: {exit_code})")
                    return True, exit_code, None
                else:
                    logger.error(f"Job failed (exit code: {exit_code})")
                    return False, exit_code, f"Exit code {exit_code}"
            else:
                return False, None, "Session exited but no exit code found"

        time.sleep(config.poll_interval_sec)

    # Timeout - kill session
    _kill_session(client, config.session_name)
    return False, None, f"Timeout after {config.timeout_sec}s"


def _is_session_alive(client: "SSHClient", session_name: str) -> bool:
    """Check if tmux session is still running."""
    result = client.exec(f"tmux has-session -t {session_name} 2>&1")
    return result.exit_code == 0


def _tail_log_from_position(
    client: "SSHClient",
    log_file: str,
    last_position: int,
) -> tuple[str, int]:
    """Tail log file from byte position.

    Returns:
        (content, new_position)
    """
    # tail -c +N reads from byte N (1-indexed)
    tail_cmd = f"tail -c +{last_position + 1} {log_file} 2>/dev/null || true"
    result = client.exec(tail_cmd)

    if result.stdout:
        new_content = result.stdout
        new_position = last_position + len(new_content.encode("utf-8"))
        return new_content, new_position
    else:
        return "", last_position


def _extract_exit_code_from_log(client: "SSHClient", log_file: str) -> int | None:
    """Extract exit code from log file.

    Looks for "EXIT_CODE: N" marker.
    """
    exit_code_cmd = (
        f"grep -E 'EXIT_CODE:' {log_file} 2>/dev/null | "
        f"tail -1 | awk '{{print $NF}}'"
    )
    result = client.exec(exit_code_cmd)

    if result.stdout:
        exit_code_str = result.stdout.strip()
        if exit_code_str.isdigit():
            return int(exit_code_str)

    return None


def _kill_session(client: "SSHClient", session_name: str) -> None:
    """Kill tmux session."""
    client.exec(f"tmux kill-session -t {session_name} 2>/dev/null || true")
    logger.warning(f"Killed session: {session_name}")
