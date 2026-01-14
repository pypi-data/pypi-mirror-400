"""Slim SSH client for remote GPU execution.

Slim SSH client for remote GPU execution.
Only includes the methods we actually use: exec, exec_stream, expand_path,
upload_files, download_files.

Usage:
    from wafer_core.ssh import SSHClient, ExecResult

    client = SSHClient("root@gpu.example.com:22", ssh_key_path="~/.ssh/id_rsa")
    result = client.exec("nvidia-smi")
    print(result.stdout)
"""

import io
import logging
import os
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import paramiko

logger = logging.getLogger(__name__)


# =============================================================================
# Types
# =============================================================================


@dataclass
class SSHConnection:
    """SSH connection information."""

    user: str
    host: str
    port: int

    @classmethod
    def from_string(cls, ssh_string: str) -> "SSHConnection":
        """Parse SSH string like 'user@host:port'."""
        if "@" not in ssh_string or ":" not in ssh_string:
            raise ValueError(
                f"Invalid SSH format: {ssh_string}. Expected: user@host:port"
            )

        user_host, port_str = ssh_string.rsplit(":", 1)
        user, host = user_host.split("@", 1)

        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port: {port_str}")

        return cls(user=user, host=host, port=port)

    def __str__(self) -> str:
        return f"{self.user}@{self.host}:{self.port}"


@dataclass
class ExecResult:
    """Result from executing a command via SSH."""

    stdout: str
    stderr: str
    exit_code: int

    @property
    def success(self) -> bool:
        return self.exit_code == 0


@dataclass
class CopyResult:
    """Result of a file copy operation."""

    success: bool
    files_copied: int
    total_bytes: int
    duration_seconds: float
    error_message: str | None = None


class SSHError(Exception):
    """SSH operation failed."""

    pass


class TransferError(SSHError):
    """File transfer failed."""

    pass


# =============================================================================
# SSH Client
# =============================================================================


class SSHClient:
    """Slim SSH client for remote execution and file transfer.

    Provides only the methods we actually use:
    - exec(): Run command, return result
    - exec_stream(): Run command, yield output lines
    - expand_path(): Expand ~ paths on remote
    - upload_files(): SFTP upload
    - download_files(): SFTP download
    """

    def __init__(
        self,
        ssh_connection: str,
        ssh_key_path: str,
        timeout: int = 30,
    ):
        """Initialize SSH client.

        Args:
            ssh_connection: SSH connection string like 'user@host:port'
            ssh_key_path: Path to SSH private key
            timeout: Connection timeout in seconds
        """
        self.ssh = SSHConnection.from_string(ssh_connection)
        self.ssh_key_path = os.path.expanduser(ssh_key_path)
        self.timeout = timeout
        self._client: paramiko.SSHClient | None = None

    def _get_client(self) -> paramiko.SSHClient:
        """Get or create SSH client connection."""
        if self._client is not None:
            transport = self._client.get_transport()
            if transport is not None and transport.is_active():
                return self._client

        # Create new connection
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load private key
        private_key = self._load_private_key()

        # Connect
        self._client.connect(
            hostname=self.ssh.host,
            port=self.ssh.port,
            username=self.ssh.user,
            pkey=private_key,
            timeout=self.timeout,
        )

        # Enable keepalive
        transport = self._client.get_transport()
        if transport:
            transport.set_keepalive(30)

        return self._client

    def _load_private_key(self) -> paramiko.PKey:
        """Load SSH private key from file."""
        with open(self.ssh_key_path) as f:
            key_content = f.read()

        key_file = io.StringIO(key_content)

        # Try different key types
        for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
            try:
                key_file.seek(0)
                return key_class.from_private_key(key_file)
            except Exception:
                continue

        raise SSHError(f"Could not load SSH key: {self.ssh_key_path}")

    def exec(self, command: str, working_dir: str | None = None) -> ExecResult:
        """Execute command on remote.

        Args:
            command: Command to execute
            working_dir: Optional working directory

        Returns:
            ExecResult with stdout, stderr, exit_code
        """
        client = self._get_client()

        if working_dir:
            command = f"cd {working_dir} && {command}"

        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        return ExecResult(
            stdout=stdout.read().decode(),
            stderr=stderr.read().decode(),
            exit_code=exit_code,
        )

    def exec_stream(
        self, command: str, working_dir: str | None = None
    ) -> Iterator[str]:
        """Execute command and stream output line-by-line.

        Args:
            command: Command to execute
            working_dir: Optional working directory

        Yields:
            Lines of output as they're produced
        """
        client = self._get_client()

        if working_dir:
            command = f"cd {working_dir} && {command}"

        transport = client.get_transport()
        if transport is None:
            raise SSHError("SSH transport not available")

        channel = transport.open_session()
        try:
            channel.set_combine_stderr(True)
            channel.get_pty()
            channel.exec_command(command)

            buffer = ""
            while True:
                if channel.recv_ready():
                    chunk = channel.recv(4096)
                    if not chunk:
                        break

                    text = chunk.decode(errors="replace")
                    buffer += text

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        yield line.rstrip("\r")
                    continue

                if channel.exit_status_ready():
                    break

                time.sleep(0.1)

            # Drain remaining data
            while channel.recv_ready():
                chunk = channel.recv(4096)
                if not chunk:
                    break
                text = chunk.decode(errors="replace")
                buffer += text
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    yield line.rstrip("\r")

            if buffer:
                yield buffer.rstrip("\r")

            channel.recv_exit_status()
        finally:
            channel.close()

    def expand_path(self, path: str) -> str:
        """Expand ~ and env vars in path on remote.

        Args:
            path: Path to expand (may contain ~ or env vars)

        Returns:
            Absolute expanded path
        """
        result = self.exec(f"echo {path}")
        if result.exit_code != 0:
            raise SSHError(f"Failed to expand path: {result.stderr}")
        return result.stdout.strip()

    def upload_files(
        self,
        local_path: str,
        remote_path: str,
        recursive: bool = False,
        respect_gitignore: bool = True,
    ) -> CopyResult:
        """Upload files from local to remote.

        Args:
            local_path: Local file or directory path
            remote_path: Remote destination path
            recursive: Upload directories recursively
            respect_gitignore: Skip files matching .gitignore patterns (default: True)

        Returns:
            CopyResult with transfer statistics
        """
        start_time = time.time()
        local_path_obj = Path(local_path)

        if not local_path_obj.exists():
            raise TransferError(f"Local path not found: {local_path}")

        if local_path_obj.is_dir() and not recursive:
            raise TransferError(f"{local_path} is a directory. Use recursive=True")

        client = self._get_client()
        sftp = client.open_sftp()

        try:
            files_uploaded = 0
            total_bytes = 0

            if local_path_obj.is_dir():
                files_uploaded, total_bytes = self._upload_directory(
                    sftp, local_path, remote_path, respect_gitignore
                )
            else:
                total_bytes = self._upload_file(sftp, local_path, remote_path)
                files_uploaded = 1

            duration = time.time() - start_time

            return CopyResult(
                success=True,
                files_copied=files_uploaded,
                total_bytes=total_bytes,
                duration_seconds=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            return CopyResult(
                success=False,
                files_copied=0,
                total_bytes=0,
                duration_seconds=duration,
                error_message=str(e),
            )
        finally:
            sftp.close()

    def download_files(
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
        start_time = time.time()
        client = self._get_client()
        sftp = client.open_sftp()

        try:
            files_downloaded = 0
            total_bytes = 0

            # Check if remote path is directory
            try:
                stat = sftp.stat(remote_path)
                is_dir = stat.st_mode & 0o40000  # S_IFDIR
            except FileNotFoundError:
                raise TransferError(f"Remote path not found: {remote_path}")

            if is_dir and not recursive:
                raise TransferError(
                    f"{remote_path} is a directory. Use recursive=True"
                )

            if is_dir:
                files_downloaded, total_bytes = self._download_directory(
                    sftp, remote_path, local_path
                )
            else:
                total_bytes = self._download_file(sftp, remote_path, local_path)
                files_downloaded = 1

            duration = time.time() - start_time

            return CopyResult(
                success=True,
                files_copied=files_downloaded,
                total_bytes=total_bytes,
                duration_seconds=duration,
            )
        except Exception as e:
            if isinstance(e, TransferError):
                raise
            duration = time.time() - start_time
            return CopyResult(
                success=False,
                files_copied=0,
                total_bytes=0,
                duration_seconds=duration,
                error_message=str(e),
            )
        finally:
            sftp.close()

    def _upload_file(self, sftp, local_path: str, remote_path: str) -> int:
        """Upload single file, return bytes transferred."""
        # Create remote directory if needed
        remote_dir = os.path.dirname(remote_path)
        if remote_dir:
            self._mkdir_p(sftp, remote_dir)

        sftp.put(local_path, remote_path)
        return os.path.getsize(local_path)

    def _upload_directory(
        self, sftp, local_path: str, remote_path: str, respect_gitignore: bool = True
    ) -> tuple[int, int]:
        """Upload directory recursively, return (files, bytes)."""
        local_path_obj = Path(local_path)
        files_uploaded = 0
        total_bytes = 0

        # Load gitignore patterns if requested
        ignore_matcher = None
        if respect_gitignore:
            ignore_matcher = self._load_gitignore(local_path_obj)

        for local_file in local_path_obj.rglob("*"):
            if local_file.is_file():
                rel_path = local_file.relative_to(local_path_obj)

                # Skip if matches gitignore
                if ignore_matcher and ignore_matcher(str(rel_path)):
                    logger.debug(f"Skipping (gitignore): {rel_path}")
                    continue

                remote_file = f"{remote_path}/{rel_path}".replace("\\", "/")

                try:
                    file_bytes = self._upload_file(sftp, str(local_file), remote_file)
                    files_uploaded += 1
                    total_bytes += file_bytes
                except Exception as e:
                    logger.warning(f"Failed to upload {rel_path}: {e}")

        return files_uploaded, total_bytes

    def _load_gitignore(self, root_path: Path):
        """Load .gitignore patterns and return a matcher function.

        Returns a function that takes a relative path string and returns True if ignored.
        """
        gitignore_path = root_path / ".gitignore"

        # Default patterns to always ignore
        default_patterns = [
            ".git",
            ".git/**",
            "__pycache__",
            "__pycache__/**",
            "*.pyc",
            ".venv",
            ".venv/**",
            "node_modules",
            "node_modules/**",
            ".env",
            "*.egg-info",
            "*.egg-info/**",
            ".pytest_cache",
            ".pytest_cache/**",
            ".mypy_cache",
            ".mypy_cache/**",
            ".ruff_cache",
            ".ruff_cache/**",
        ]

        patterns = default_patterns.copy()

        # Load .gitignore if it exists
        if gitignore_path.exists():
            try:
                with open(gitignore_path) as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception as e:
                logger.warning(f"Failed to read .gitignore: {e}")

        # Compile patterns into a matcher
        import fnmatch

        def matches(rel_path: str) -> bool:
            # Normalize path separators
            rel_path = rel_path.replace("\\", "/")

            # Check each pattern
            for pattern in patterns:
                # Handle directory patterns (ending with /)
                if pattern.endswith("/"):
                    pattern = pattern[:-1]

                # Check if any path component matches
                parts = rel_path.split("/")
                for i, part in enumerate(parts):
                    # Check direct match
                    if fnmatch.fnmatch(part, pattern):
                        return True
                    # Check pattern against partial path
                    partial = "/".join(parts[: i + 1])
                    if fnmatch.fnmatch(partial, pattern):
                        return True

                # Check full path match
                if fnmatch.fnmatch(rel_path, pattern):
                    return True

            return False

        return matches

    def _download_file(self, sftp, remote_path: str, local_path: str) -> int:
        """Download single file, return bytes transferred."""
        # Create local directory if needed
        local_dir = os.path.dirname(local_path)
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)

        sftp.get(remote_path, local_path)
        return os.path.getsize(local_path)

    def _download_directory(
        self, sftp, remote_path: str, local_path: str
    ) -> tuple[int, int]:
        """Download directory recursively, return (files, bytes)."""
        files_downloaded = 0
        total_bytes = 0

        def download_recursive(remote_dir: str, local_dir: str) -> None:
            nonlocal files_downloaded, total_bytes

            os.makedirs(local_dir, exist_ok=True)

            for entry in sftp.listdir_attr(remote_dir):
                remote_entry = f"{remote_dir}/{entry.filename}"
                local_entry = os.path.join(local_dir, entry.filename)

                if entry.st_mode & 0o40000:  # S_IFDIR
                    download_recursive(remote_entry, local_entry)
                else:
                    try:
                        file_bytes = self._download_file(sftp, remote_entry, local_entry)
                        files_downloaded += 1
                        total_bytes += file_bytes
                    except Exception as e:
                        logger.warning(f"Failed to download {entry.filename}: {e}")

        download_recursive(remote_path, local_path)
        return files_downloaded, total_bytes

    def _mkdir_p(self, sftp, remote_dir: str) -> None:
        """Create remote directory recursively."""
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            parent = os.path.dirname(remote_dir)
            if parent and parent != remote_dir:
                self._mkdir_p(sftp, parent)
            try:
                sftp.mkdir(remote_dir)
            except OSError:
                pass  # May already exist

    def close(self) -> None:
        """Close SSH connection."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "SSHClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
