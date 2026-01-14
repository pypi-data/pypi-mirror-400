"""GPU availability validation and checking.

Tiger Style: Assert preconditions, explicit error handling, fail-fast.

Copied from ~/wafer_stuff/qwen3_next/deploy/gpu_validation.py
Adapted for use in async-wevin pluggable targets system.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer_core.ssh import SSHClient

logger = logging.getLogger(__name__)

# GPU availability thresholds
DEFAULT_MEMORY_THRESHOLD_MB = 1000  # Consider GPU busy if > 1GB used
DEFAULT_UTIL_THRESHOLD_PCT = 5  # Consider GPU busy if > 5% utilized


def check_gpus_available(
    ssh_client: "SSHClient",
    gpu_ids: list[int],
    memory_threshold_mb: int = DEFAULT_MEMORY_THRESHOLD_MB,
    util_threshold_pct: int = DEFAULT_UTIL_THRESHOLD_PCT,
) -> tuple[bool, str]:
    """Check if specified GPUs are free.

    Tiger Style: Assert preconditions.

    Args:
        ssh_client: Connected SSH client
        gpu_ids: List of GPU IDs to check
        memory_threshold_mb: Memory threshold in MB
        util_threshold_pct: Utilization threshold %

    Returns:
        (True, "") if all GPUs are free
        (False, error_message) if any GPU is busy
    """
    assert len(gpu_ids) > 0, "Must specify at least one GPU to check"

    try:
        result = ssh_client.exec(
            "nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits"
        )

        if result.exit_code != 0:
            return False, f"Failed to run nvidia-smi: {result.stderr}"

        # Parse nvidia-smi output
        gpu_stats = {}
        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 3:
                continue

            try:
                gpu_id = int(parts[0])
                memory_mb = int(parts[1])
                util_pct = int(parts[2])
                gpu_stats[gpu_id] = {"memory_mb": memory_mb, "util_pct": util_pct}
            except ValueError:
                continue

        # Check if requested GPUs are free
        for gpu_id in gpu_ids:
            if gpu_id not in gpu_stats:
                return (
                    False,
                    f"GPU {gpu_id} not found on remote (available: {list(gpu_stats.keys())})",
                )

            stats = gpu_stats[gpu_id]
            mem_mb = stats["memory_mb"]
            util = stats["util_pct"]

            if mem_mb > memory_threshold_mb or util > util_threshold_pct:
                return False, f"GPU {gpu_id} is busy ({mem_mb}MB used, {util}% util)"

    except Exception as e:
        return False, f"GPU availability check failed: {e}"
    else:
        return True, ""


def validate_remote_gpu_count(ssh_client: "SSHClient", required_gpus: int) -> bool:
    """Validate remote node has enough GPUs.

    Tiger Style: Assert preconditions.

    Args:
        ssh_client: Connected SSH client
        required_gpus: Number of GPUs required by config

    Returns:
        True if validation passes, False otherwise
    """
    assert required_gpus > 0, f"Required GPUs must be positive, got {required_gpus}"

    try:
        result = ssh_client.exec("nvidia-smi --list-gpus | wc -l")
        if result.exit_code != 0:
            logger.warning("Failed to count GPUs on remote")
            return False

        actual_gpus = int(result.stdout.strip())

        if actual_gpus < required_gpus:
            logger.error(f"Config requires {required_gpus} GPUs but remote has {actual_gpus}")
            return False

    except Exception as e:
        logger.warning(f"GPU count validation failed: {e}")
        return False
    else:
        logger.info(f"✅ Remote has {actual_gpus} GPUs (required: {required_gpus})")
        return True
