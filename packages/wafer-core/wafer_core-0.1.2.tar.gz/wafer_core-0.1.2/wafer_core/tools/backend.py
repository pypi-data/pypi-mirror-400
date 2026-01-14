"""Backend integration via wafer-api for capture storage."""

import gzip
import hashlib
import logging
import os
from pathlib import Path

import httpx
import trio

logger = logging.getLogger(__name__)

# File size thresholds
COMPRESSION_THRESHOLD_BYTES = 5 * 1024 * 1024  # 5MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

# Default API URL
# Use localhost:8000 for development (matches dev server), production should set WAFER_API_URL explicitly
DEFAULT_API_URL = "http://localhost:8000"


def get_api_url() -> str:
    """Get API URL from environment or default."""
    return os.environ.get("WAFER_API_URL", DEFAULT_API_URL)


def get_auth_token() -> str | None:
    """Get auth token from environment.

    Returns:
        Auth token or None if not configured (dev mode)

    Note:
        In local dev mode (localhost), no token is required.
        The API will use LOCAL_DEV_MODE to bypass auth.
    """
    return os.environ.get("WAFER_AUTH_TOKEN")


async def upload_capture(
    label: str,
    variant: str | None,
    command: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    duration_seconds: float,
    working_dir: Path,
    git_repo: str | None,
    git_commit: str | None,
    git_branch: str | None,
    git_dirty: bool,
    hostname: str | None,
    gpu_model: str | None,
    gpu_driver: str | None,
    cuda_version: str | None,
    environment_variables: dict[str, str],
    code_files: dict[Path, str],
    metrics: dict[str, float],
    tags: list[str],
) -> str:
    """Upload capture metadata to wafer-api.

    Args:
        (many parameters - see CaptureResult)

    Returns:
        Capture ID (UUID)

    Raises:
        RuntimeError: If upload fails
        httpx.HTTPError: If API request fails
    """
    logger.info(f"Uploading capture: {label}")

    def _prepare_data() -> dict:
        """Prepare capture data for upload."""
        # Prepare code_files as JSON array
        code_files_json = [
            {
                "path": str(path),
                "content": content,
                "checksum": hashlib.sha256(content.encode()).hexdigest(),
            }
            for path, content in code_files.items()
        ]

        # Prepare data
        return {
            "label": label,
            "variant": variant,
            "command": command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_seconds": duration_seconds,
            "working_dir": str(working_dir),
            "git_repo": git_repo,
            "git_commit": git_commit,
            "git_branch": git_branch,
            "git_dirty": git_dirty,
            "hostname": hostname,
            "gpu_model": gpu_model,
            "gpu_driver": gpu_driver,
            "cuda_version": cuda_version,
            "environment_variables": environment_variables,
            "code_files": code_files_json,
            "metrics": metrics,
            "tags": tags,
        }

    async def _upload() -> str:
        """Upload data via API."""
        api_url = get_api_url()
        token = get_auth_token()

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        data = _prepare_data()

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{api_url}/v1/captures", json=data, headers=headers
                )
                response.raise_for_status()
                result = response.json()

            capture_id = result["id"]
            logger.info(f"Capture uploaded successfully: {capture_id}")
            return capture_id
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise RuntimeError(f"Upload failed: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            logger.error(f"Upload failed: {type(e).__name__}: {e}")
            raise

    return await _upload()


async def upload_artifact(
    capture_id: str,
    artifact_path: Path,
    working_dir: Path,
    artifact_type: str | None = None,
) -> str:
    """Upload artifact file to wafer-api.

    Args:
        capture_id: Capture ID
        artifact_path: Path to artifact file (relative to working_dir)
        working_dir: Working directory
        artifact_type: Optional artifact type classification

    Returns:
        Storage path of uploaded file

    Raises:
        RuntimeError: If file too large or upload fails
        httpx.HTTPError: If API request fails
    """
    full_path = working_dir / artifact_path
    file_name = artifact_path.name

    logger.debug(f"Uploading artifact: {artifact_path}")

    def _prepare_file() -> tuple[bytes, bool, int, str]:
        """Prepare file for upload.

        Returns:
            Tuple of (file_content, compressed, original_size, checksum)
        """
        # Check file size
        file_size = full_path.stat().st_size

        # Compute checksum
        hasher = hashlib.sha256()
        with open(full_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        checksum = hasher.hexdigest()

        # Read file content
        with open(full_path, "rb") as f:
            file_content = f.read()

        # Check if compression needed
        compressed = False
        original_size = file_size

        if file_size > COMPRESSION_THRESHOLD_BYTES:
            logger.debug(f"Compressing file (size={file_size / 1024 / 1024:.2f}MB)")
            file_content = gzip.compress(file_content, compresslevel=6)
            compressed = True
            file_size = len(file_content)
            logger.debug(
                f"Compressed to {file_size / 1024 / 1024:.2f}MB "
                f"({file_size / original_size * 100:.1f}%)"
            )

        # Check if file still too large after compression
        if file_size > MAX_FILE_SIZE_BYTES:
            logger.warning(
                f"Artifact too large after compression: {file_size / 1024 / 1024:.2f}MB > 50MB"
            )
            raise RuntimeError(
                f"File too large to upload: {file_size / 1024 / 1024:.2f}MB > 50MB"
            )

        return file_content, compressed, original_size, checksum

    async def _upload() -> str:
        """Upload file via API."""
        file_content, compressed, original_size, checksum = await trio.to_thread.run_sync(
            _prepare_file
        )

        api_url = get_api_url()
        token = get_auth_token()

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Prepare multipart form data
        files = {
            "file": (file_name, file_content, "application/octet-stream"),
        }

        data = {
            "capture_id": capture_id,
            "file_path": str(artifact_path),
            "file_name": file_name,
            "checksum": checksum,
            "compressed": str(compressed).lower(),
            "original_size": str(original_size) if compressed else "",
            "artifact_type": artifact_type or "other",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{api_url}/v1/captures/{capture_id}/artifacts",
                files=files,
                data=data,
                headers=headers if headers else None,
            )
            response.raise_for_status()
            result = response.json()

        storage_path = result["storage_path"]
        logger.info(f"Artifact uploaded: {storage_path}")
        return storage_path

    return await _upload()


async def list_captures(
    label: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """List captures from API.

    Args:
        label: Optional label filter
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of capture dictionaries

    Raises:
        httpx.HTTPError: If API request fails
    """
    logger.debug(f"Listing captures: label={label}, limit={limit}, offset={offset}")

    api_url = get_api_url()
    token = get_auth_token()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {
        "limit": limit,
        "offset": offset,
    }

    if label:
        params["label"] = label

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{api_url}/v1/captures", params=params, headers=headers
        )
        response.raise_for_status()
        result = response.json()

    captures = result["captures"]
    logger.info(f"Found {len(captures)} captures")
    return captures
