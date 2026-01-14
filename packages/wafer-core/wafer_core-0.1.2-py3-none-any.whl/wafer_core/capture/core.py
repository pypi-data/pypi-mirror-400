import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from wafer_core.capture.artifacts import (
    collect_file_contents,
    diff_snapshots,
    snapshot_directory,
)
from wafer_core.capture.context import collect_capture_context
from wafer_core.capture.dtypes import (
    CaptureConfig,
    CaptureContext,
    CaptureResult,
    DirectorySnapshot,
    ExecutionResult,
)
from wafer_core.capture.metrics import collect_all_metrics
from wafer_core.tools import backend

logger = logging.getLogger(__name__)

RunnerFunction = Callable[[str, Path, dict[str, str]], Awaitable[ExecutionResult]]


async def capture(
    config: CaptureConfig,
    runner: RunnerFunction,
    progress_callback: Callable[[str], None] | None = None,
) -> CaptureResult:
    logger.info(f"Starting capture: {config.label}")

    def _progress(message: str) -> None:
        logger.debug(f"Progress: {message}")
        if progress_callback:
            progress_callback(message)

    _progress("Capturing pre-execution state...")
    snapshot_before = await snapshot_directory(
        root=config.working_dir, denylist=config.artifact_denylist
    )

    _progress("Collecting execution context...")
    context = await collect_capture_context(
        working_dir=config.working_dir,
        env_var_patterns=None,
    )

    _progress(f"Executing command: {config.command}")
    execution_result = await runner(
        config.command,
        config.working_dir,
        config.env_vars or {},
    )

    _progress(
        f"Command completed with exit code {execution_result.exit_code} "
        f"in {execution_result.duration_seconds:.2f}s"
    )

    _progress("Capturing post-execution state...")
    snapshot_after = await snapshot_directory(
        root=config.working_dir, denylist=config.artifact_denylist
    )

    return await _capture_from_execution_result(
        config=config,
        execution_result=execution_result,
        snapshot_before=snapshot_before,
        snapshot_after=snapshot_after,
        context=context,
        progress_callback=progress_callback,
    )


def _config_from_dict(data: dict) -> CaptureConfig:
    return CaptureConfig(
        label=data["label"],
        command=data["command"],
        working_dir=Path(data["working_dir"]),
        variant=data.get("variant"),
        tags=data.get("tags", []),
        code_denylist=data.get("code_denylist", []),
        artifact_denylist=data.get("artifact_denylist", []),
        env_vars=data.get("env_vars", {}),
    )


def _execution_result_from_dict(data: dict) -> ExecutionResult:
    from datetime import datetime
    return ExecutionResult(
        exit_code=data["exit_code"],
        stdout=data["stdout"],
        stderr=data["stderr"],
        duration_seconds=data["duration_seconds"],
        start_time=datetime.fromisoformat(data["start_time"].replace("Z", "+00:00")),
        end_time=datetime.fromisoformat(data["end_time"].replace("Z", "+00:00")),
    )


def _snapshot_from_dict(data: dict) -> DirectorySnapshot:
    from datetime import datetime

    from wafer_core.capture.dtypes import FileInfo
    return DirectorySnapshot(
        files={
            Path(k): FileInfo(
                path=Path(k),
                size=v["size"],
                mtime=v["mtime"],
                checksum=v.get("checksum"),
            )
            for k, v in data["files"].items()
        },
        timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
        root=Path(data["root"]),
    )


async def capture_from_execution_result(
    config: CaptureConfig | dict,
    execution_result: ExecutionResult | dict,
    snapshot_before: DirectorySnapshot | dict | None = None,
    snapshot_after: DirectorySnapshot | dict | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> CaptureResult:
    def _progress(message: str) -> None:
        logger.debug(f"Progress: {message}")
        if progress_callback:
            progress_callback(message)

    if isinstance(config, dict):
        config = _config_from_dict(config)

    if isinstance(execution_result, dict):
        execution_result = _execution_result_from_dict(execution_result)

    if snapshot_before is None:
        _progress("Capturing pre-execution state...")
        snapshot_before = await snapshot_directory(
            root=config.working_dir, denylist=config.artifact_denylist
        )
    elif isinstance(snapshot_before, dict):
        snapshot_before = _snapshot_from_dict(snapshot_before)

    _progress("Collecting execution context...")
    context = await collect_capture_context(
        working_dir=config.working_dir,
        env_var_patterns=None,
    )

    if snapshot_after is None:
        _progress("Capturing post-execution state...")
        snapshot_after = await snapshot_directory(
            root=config.working_dir, denylist=config.artifact_denylist
        )
    elif isinstance(snapshot_after, dict):
        snapshot_after = _snapshot_from_dict(snapshot_after)

    return await _capture_from_execution_result(
        config=config,
        execution_result=execution_result,
        snapshot_before=snapshot_before,
        snapshot_after=snapshot_after,
        context=context,
        progress_callback=progress_callback,
    )


async def _capture_from_execution_result(
    config: CaptureConfig,
    execution_result: ExecutionResult,
    snapshot_before: DirectorySnapshot,
    snapshot_after: DirectorySnapshot,
    context: CaptureContext,
    progress_callback: Callable[[str], None] | None = None,
) -> CaptureResult:
    def _progress(message: str) -> None:
        logger.debug(f"Progress: {message}")
        if progress_callback:
            progress_callback(message)

    _progress("Detecting generated artifacts...")
    artifact_diff = diff_snapshots(snapshot_before, snapshot_after)

    all_artifacts = artifact_diff.new_files + artifact_diff.modified_files
    logger.info(f"Detected {len(all_artifacts)} artifacts")

    _progress("Extracting metrics...")
    metrics_result = await collect_all_metrics(
        stdout=execution_result.stdout, working_dir=config.working_dir
    )

    all_metrics = dict(metrics_result.stdout_metrics)
    if metrics_result.ncu_metrics:
        all_metrics.update(metrics_result.ncu_metrics)

    logger.info(f"Extracted {len(all_metrics)} metrics")

    _progress("Collecting code files...")

    code_file_paths = [
        path
        for path in snapshot_before.files.keys()
        if not _matches_denylist_simple(path, config.code_denylist)
        and _is_code_file(path)
    ]

    MAX_CODE_FILES = 50
    MAX_FILE_SIZE = 100 * 1024

    if len(code_file_paths) > MAX_CODE_FILES:
        logger.warning(
            f"Too many code files ({len(code_file_paths)}), limiting to {MAX_CODE_FILES}"
        )
        code_file_paths_sorted = sorted(
            code_file_paths,
            key=lambda p: (len(p.parts), snapshot_before.files[p].size),
        )
        code_file_paths = code_file_paths_sorted[:MAX_CODE_FILES]

    logger.info(f"Collecting {len(code_file_paths)} code files")

    code_files_all = await collect_file_contents(
        root=config.working_dir, paths=code_file_paths
    )

    code_files = {}
    for path, content in code_files_all.items():
        if len(content.encode("utf-8")) > MAX_FILE_SIZE:
            logger.debug(f"Skipping large file: {path} ({len(content)} chars)")
            continue
        code_files[path] = content

    _progress("Uploading to backend...")

    capture_id = await backend.upload_capture(
        label=config.label,
        variant=config.variant,
        command=config.command,
        exit_code=execution_result.exit_code,
        stdout=execution_result.stdout,
        stderr=execution_result.stderr,
        duration_seconds=execution_result.duration_seconds,
        working_dir=config.working_dir,
        git_repo=context.git.repo_url,
        git_commit=context.git.commit_hash,
        git_branch=context.git.branch,
        git_dirty=context.git.is_dirty,
        hostname=context.system.hostname,
        gpu_model=context.gpu.model,
        gpu_driver=context.gpu.driver_version,
        cuda_version=context.gpu.cuda_version,
        environment_variables=context.environment_variables,
        code_files=code_files,
        metrics=all_metrics,
        tags=config.tags,
    )

    logger.info(f"Capture metadata uploaded: {capture_id}")

    _progress(f"Uploading {len(all_artifacts)} artifacts...")

    uploaded_artifacts: list[Path] = []
    skipped_artifacts: list[Path] = []

    for artifact_path in all_artifacts:
        try:
            artifact_type = _classify_artifact(artifact_path)

            await backend.upload_artifact(
                capture_id=capture_id,
                artifact_path=artifact_path,
                working_dir=config.working_dir,
                artifact_type=artifact_type,
            )
            uploaded_artifacts.append(artifact_path)
        except RuntimeError as e:
            logger.warning(f"Skipped artifact {artifact_path}: {e}")
            skipped_artifacts.append(artifact_path)
            continue

    if skipped_artifacts:
        logger.warning(
            f"Skipped {len(skipped_artifacts)} artifacts (too large or failed)"
        )

    _progress("Capture complete!")

    return CaptureResult(
        id=capture_id,
        label=config.label,
        variant=config.variant,
        command=config.command,
        exit_code=execution_result.exit_code,
        duration_seconds=execution_result.duration_seconds,
        stdout=execution_result.stdout,
        stderr=execution_result.stderr,
        context=context,
        metrics=metrics_result,
        artifacts=uploaded_artifacts,
        code_files=code_files,
        created_at=execution_result.start_time,
        tags=config.tags,
    )


def _matches_denylist_simple(path: Path, denylist: list[str]) -> bool:
    from fnmatch import fnmatch

    path_str = str(path)
    for pattern in denylist:
        if fnmatch(path_str, pattern):
            return True
    return False


def _is_code_file(path: Path) -> bool:
    code_extensions = {
        ".py", ".cu", ".cuh", ".c", ".cpp", ".h", ".hpp", ".rs", ".go",
        ".js", ".ts", ".java", ".sh", ".bash", ".yaml", ".yml", ".toml", ".json",
    }
    return path.suffix.lower() in code_extensions


def _classify_artifact(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".ncu-rep":
        return "ncu_profile"
    if suffix in {".log", ".txt"}:
        return "log"
    if suffix in {".csv", ".json", ".yaml", ".yml"}:
        return "output"
    if suffix in {".npy", ".npz", ".pt", ".pth"}:
        return "data"

    return "other"
