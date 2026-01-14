"""Async SSH client for remote GPU execution.

Uses asyncssh with trio-asyncio bridge for compatibility with trio.
"""

import logging
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

import asyncssh
import trio
import trio_asyncio

logger = logging.getLogger(__name__)


def _trio_wrap(coro_func):
    """Wrap asyncio coroutine for trio-asyncio."""
    return trio_asyncio.aio_as_trio(coro_func)


class AsyncSSHError(Exception):
    """Base exception for async SSH operations."""

    pass


class ConnectionError(AsyncSSHError):
    """SSH connection failed."""

    pass


class TransferError(AsyncSSHError):
    """File transfer failed."""

    pass


@dataclass(frozen=True)
class ExecResult:
    """Result of command execution."""

    stdout: str
    stderr: str
    exit_code: int


@dataclass(frozen=True)
class CopyResult:
    """Result of file transfer operation."""

    success: bool
    files_copied: int
    total_bytes: int
    duration_seconds: float
    error_message: str | None = None


class AsyncSSHClient:
    """Async SSH client for remote GPU execution.

    Uses asyncssh for true async I/O, bridged to trio via trio-asyncio.

    Example:
        async with AsyncSSHClient("user@host:22", "~/.ssh/id_ed25519") as client:
            result = await client.exec("nvidia-smi")
            print(result.stdout)

            async for line in client.exec_stream("python train.py"):
                print(line)
    """

    def __init__(
        self,
        ssh_target: str,
        ssh_key: str,
        timeout: int = 30,
    ) -> None:
        """Initialize async SSH client.

        Args:
            ssh_target: SSH target as "user@host:port" or "user@host"
            ssh_key: Path to SSH private key
            timeout: Connection timeout in seconds
        """
        # Parse SSH target
        if "@" not in ssh_target:
            raise ValueError(f"Invalid ssh_target format: {ssh_target}. Expected user@host:port")

        user_host, _, port_str = ssh_target.partition(":")
        user, _, host = user_host.partition("@")

        self.user = user
        self.host = host
        self.port = int(port_str) if port_str else 22
        self.ssh_key = os.path.expanduser(ssh_key)
        self.timeout = timeout

        self._conn: asyncssh.SSHClientConnection | None = None

    async def _establish_connection(self) -> asyncssh.SSHClientConnection:
        """Establish SSH connection with retry logic."""
        max_attempts = 3
        delay = 2
        backoff = 2

        for attempt in range(max_attempts):
            try:
                conn = await _trio_wrap(asyncssh.connect)(
                    host=self.host,
                    port=self.port,
                    username=self.user,
                    client_keys=[self.ssh_key],
                    connect_timeout=self.timeout,
                    keepalive_interval=30,
                    known_hosts=None,
                )
                logger.debug(f"Connected to {self.user}@{self.host}:{self.port}")
                return conn

            except Exception as e:
                if attempt < max_attempts - 1:
                    wait_time = delay * (backoff**attempt)
                    logger.debug(
                        f"Connection attempt {attempt + 1} failed, retrying in {wait_time}s..."
                    )
                    await trio.sleep(wait_time)
                else:
                    raise ConnectionError(
                        f"Failed to connect to {self.user}@{self.host}:{self.port} "
                        f"after {max_attempts} attempts: {e}"
                    ) from e

        raise ConnectionError(f"Failed to connect to {self.user}@{self.host}:{self.port}")

    async def _get_connection(self) -> asyncssh.SSHClientConnection:
        """Get or create SSH connection."""
        if self._conn is None:
            self._conn = await self._establish_connection()
            return self._conn

        # Check if connection is still alive
        if self._conn._transport.is_closing():
            logger.debug("SSH connection inactive, reconnecting...")
            self._conn = await self._establish_connection()

        return self._conn

    async def exec(
        self,
        command: str,
        working_dir: str | None = None,
    ) -> ExecResult:
        """Execute command on remote.

        Args:
            command: Command to execute
            working_dir: Optional working directory

        Returns:
            ExecResult with stdout, stderr, exit_code
        """
        conn = await self._get_connection()

        if working_dir:
            command = f"cd {working_dir} && {command}"

        result = await _trio_wrap(conn.run)(command, check=False)

        return ExecResult(
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            exit_code=result.exit_status or 0,
        )

    async def exec_stream(
        self,
        command: str,
        working_dir: str | None = None,
    ) -> AsyncIterator[str]:
        """Execute command and stream output line-by-line.

        Args:
            command: Command to execute
            working_dir: Optional working directory

        Yields:
            Lines of output as they're produced
        """
        conn = await self._get_connection()

        if working_dir:
            command = f"cd {working_dir} && {command}"

        # Use PTY to combine stdout/stderr
        process = await _trio_wrap(conn.create_process)(command, term_type="ansi")
        try:
            while True:
                try:
                    line = await _trio_wrap(process.stdout.readline)()
                    if not line:
                        break
                    yield line.rstrip("\r\n")
                except EOFError:
                    break
        finally:
            process.close()

    async def expand_path(self, path: str) -> str:
        """Expand ~ and env vars in path on remote."""
        result = await self.exec(f"echo {path}")
        return result.stdout.strip()

    async def upload_files(
        self,
        local_path: str,
        remote_path: str,
        recursive: bool = False,
    ) -> CopyResult:
        """Upload files from local to remote.

        Args:
            local_path: Local file or directory path
            remote_path: Remote destination path
            recursive: Upload directories recursively

        Returns:
            CopyResult with transfer statistics
        """
        import time

        start_time = time.time()

        try:
            conn = await self._get_connection()

            local_path_obj = trio.Path(local_path)
            if not await local_path_obj.exists():
                raise TransferError(f"Local path not found: {local_path}")

            is_directory = await local_path_obj.is_dir()
            if is_directory and not recursive:
                raise TransferError(f"{local_path} is a directory. Use recursive=True")

            sftp = await _trio_wrap(conn.start_sftp_client)()
            try:
                files_uploaded = 0
                total_bytes = 0

                if is_directory:
                    files_uploaded, total_bytes = await self._upload_directory(
                        sftp, local_path, remote_path
                    )
                else:
                    total_bytes = await self._upload_file(sftp, local_path, remote_path)
                    files_uploaded = 1

                duration = time.time() - start_time

                return CopyResult(
                    success=True,
                    files_copied=files_uploaded,
                    total_bytes=total_bytes,
                    duration_seconds=duration,
                )
            finally:
                sftp.exit()

        except (ConnectionError, TransferError):
            raise
        except Exception as e:
            duration = time.time() - start_time
            return CopyResult(
                success=False,
                files_copied=0,
                total_bytes=0,
                duration_seconds=duration,
                error_message=str(e),
            )

    async def _upload_file(self, sftp, local_path: str, remote_path: str) -> int:
        """Upload single file and return bytes transferred."""
        remote_dir = os.path.dirname(remote_path)
        if remote_dir and remote_dir != ".":
            await self._create_remote_dir(sftp, remote_dir)

        file_stat = await trio.Path(local_path).stat()
        await _trio_wrap(sftp.put)(local_path, remote_path)
        return file_stat.st_size

    async def _create_remote_dir(self, sftp, remote_dir: str) -> None:
        """Create remote directory recursively."""
        try:
            await _trio_wrap(sftp.stat)(remote_dir)
        except FileNotFoundError:
            parent_dir = os.path.dirname(remote_dir)
            if parent_dir and parent_dir != remote_dir:
                await self._create_remote_dir(sftp, parent_dir)
            try:
                await _trio_wrap(sftp.mkdir)(remote_dir)
            except OSError:
                pass  # Directory might have been created by another process

    async def _upload_directory(self, sftp, local_path: str, remote_path: str) -> tuple[int, int]:
        """Upload directory recursively using parallel uploads."""
        local_path_obj = trio.Path(local_path)
        # Skip __pycache__, .pyc files, and .git
        all_files = []
        async for f in local_path_obj.rglob("*"):
            if (
                await f.is_file()
                and "__pycache__" not in f.parts
                and not f.suffix == ".pyc"
                and ".git" not in f.parts
            ):
                all_files.append(f)

        files_uploaded = 0
        total_bytes = 0

        async def upload_one_file(local_file: Path) -> None:
            nonlocal files_uploaded, total_bytes

            rel_path = local_file.relative_to(local_path_obj)
            remote_file = f"{remote_path}/{rel_path}".replace("\\", "/")

            try:
                file_bytes = await self._upload_file(sftp, str(local_file), remote_file)
                files_uploaded += 1
                total_bytes += file_bytes
            except Exception as e:
                logger.warning(f"Failed to upload {rel_path}: {e}")

        # Upload files in parallel
        async with trio.open_nursery() as nursery:
            for local_file in all_files:
                nursery.start_soon(upload_one_file, local_file)

        return files_uploaded, total_bytes

    async def download_files(
        self,
        remote_path: str,
        local_path: str,
        recursive: bool = False,
    ) -> CopyResult:
        """Download files from remote to local.

        Args:
            remote_path: Remote file or directory path
            local_path: Local destination path
            recursive: Download directories recursively

        Returns:
            CopyResult with transfer statistics
        """
        import time

        start_time = time.time()

        try:
            conn = await self._get_connection()

            # Check if remote path exists
            result = await self.exec(f"test -e {remote_path}")
            if result.exit_code != 0:
                raise TransferError(f"Remote path not found: {remote_path}")

            # Check if directory
            result = await self.exec(f"test -d {remote_path}")
            is_directory = result.exit_code == 0

            if is_directory and not recursive:
                raise TransferError(f"{remote_path} is a directory. Use recursive=True")

            sftp = await _trio_wrap(conn.start_sftp_client)()
            try:
                files_copied = 0
                total_bytes = 0

                if is_directory:
                    files_copied, total_bytes = await self._download_directory(
                        sftp, conn, remote_path, local_path
                    )
                else:
                    total_bytes = await self._download_file(sftp, remote_path, local_path)
                    files_copied = 1

                duration = time.time() - start_time

                return CopyResult(
                    success=True,
                    files_copied=files_copied,
                    total_bytes=total_bytes,
                    duration_seconds=duration,
                )
            finally:
                sftp.exit()

        except (ConnectionError, TransferError):
            raise
        except Exception as e:
            duration = time.time() - start_time
            return CopyResult(
                success=False,
                files_copied=0,
                total_bytes=0,
                duration_seconds=duration,
                error_message=str(e),
            )

    async def _download_file(self, sftp, remote_path: str, local_path: str) -> int:
        """Download single file and return bytes transferred."""
        local_dir = Path(local_path).parent
        local_dir.mkdir(parents=True, exist_ok=True)

        attrs = await _trio_wrap(sftp.stat)(remote_path)
        file_size = attrs.size

        await _trio_wrap(sftp.get)(remote_path, local_path)
        return file_size

    async def _download_directory(
        self, sftp, conn, remote_path: str, local_path: str
    ) -> tuple[int, int]:
        """Download directory recursively using parallel downloads."""
        result = await _trio_wrap(conn.run)(f"find {remote_path} -type f", check=True)
        file_list = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        files_copied = 0
        total_bytes = 0

        async def download_one_file(remote_file: str) -> None:
            nonlocal files_copied, total_bytes

            rel_path = Path(remote_file).relative_to(remote_path)
            local_file = str(Path(local_path) / rel_path)

            try:
                file_bytes = await self._download_file(sftp, remote_file, local_file)
                files_copied += 1
                total_bytes += file_bytes
            except Exception as e:
                logger.warning(f"Failed to download {rel_path}: {e}")

        # Download files in parallel
        async with trio.open_nursery() as nursery:
            for remote_file in file_list:
                nursery.start_soon(download_one_file, remote_file)

        return files_copied, total_bytes

    async def close(self) -> None:
        """Close SSH connection."""
        if self._conn:
            self._conn.close()
            await _trio_wrap(self._conn.wait_closed)()
            self._conn = None

    async def __aenter__(self) -> "AsyncSSHClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
