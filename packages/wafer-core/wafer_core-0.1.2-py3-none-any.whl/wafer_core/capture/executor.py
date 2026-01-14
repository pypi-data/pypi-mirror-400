import logging
from datetime import datetime, timezone
from pathlib import Path

import trio

from wafer_core.capture.dtypes import ExecutionResult

logger = logging.getLogger(__name__)


async def execute_command(
    command: str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> ExecutionResult:
    logger.info(f"Executing command: {command}")
    logger.info(f"Working directory: {cwd}")

    import os
    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)

    start_time = datetime.now(timezone.utc)

    process = await trio.run_process(
        command,
        cwd=str(cwd),
        env=exec_env,
        shell=True,
        capture_stdout=True,
        capture_stderr=True,
        check=False,
    )

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    stdout = process.stdout.decode("utf-8", errors="replace")
    stderr = process.stderr.decode("utf-8", errors="replace")
    exit_code = process.returncode

    logger.info(f"Command exited with code: {exit_code}")
    logger.debug(f"Duration: {duration:.2f}s")

    # Wait for file system to flush any pending writes
    # This prevents race conditions where artifacts are still being written
    # after the process exits (especially for long-running profiling commands)
    logger.debug("Waiting for file system flush...")
    await trio.sleep(1.0)

    return ExecutionResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        start_time=start_time,
        end_time=end_time,
    )
