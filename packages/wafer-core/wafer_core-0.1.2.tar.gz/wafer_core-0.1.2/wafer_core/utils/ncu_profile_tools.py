"""NCU Profile Tools - Separate profile generation from analysis.

This module provides:
1. Profile generation: Run NCU with comprehensive metrics, save raw CSV
2. Profile analysis: Parse saved profiles and return formatted insights

Tiger Style:
- Explicit separation of concerns (generate vs analyze)
- Profiles are reusable artifacts
- Rule-based insights derived from metrics
"""

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ── Comprehensive NCU Metrics ─────────────────────────────────────────────────
# These metrics give us a complete picture of kernel performance

NCU_COMPREHENSIVE_METRICS = ",".join(
    [
        # Timing
        "gpu__time_duration.sum",
        # Throughput (% of peak)
        "sm__throughput.avg.pct_of_peak_sustained_elapsed",
        "dram__throughput.avg.pct_of_peak_sustained_elapsed",
        # Occupancy and warps
        "sm__warps_active.avg.pct_of_peak_sustained_active",
        "sm__maximum_warps_per_scheduler_warp",
        "launch__occupancy_limit_registers",
        "launch__occupancy_limit_shared_mem",
        "launch__occupancy_limit_blocks",
        "launch__occupancy_limit_warps",
        # Launch config
        "launch__registers_per_thread",
        "launch__shared_mem_per_block_static",
        "launch__shared_mem_per_block_dynamic",
        "launch__block_size",
        "launch__grid_size",
        # Cache metrics
        "l1tex__t_sector_hit_rate.pct",
        "lts__t_sector_hit_rate.pct",
        # Memory throughput
        "l1tex__t_bytes_pipe_lsu_mem_global_op_ld.sum.per_second",
        "l1tex__t_bytes_pipe_lsu_mem_global_op_st.sum.per_second",
        "dram__bytes_read.sum.per_second",
        "dram__bytes_write.sum.per_second",
        # Instruction throughput
        "smsp__inst_executed.avg.per_cycle_active",
        "sm__inst_executed_pipe_tensor.avg.pct_of_peak_sustained_active",
        # Warp stalls (why warps can't make progress)
        "smsp__warps_issue_stalled_wait.avg.pct_of_peak_sustained_elapsed",
        "smsp__warps_issue_stalled_barrier.avg.pct_of_peak_sustained_elapsed",
        "smsp__warps_issue_stalled_membar.avg.pct_of_peak_sustained_elapsed",
        "smsp__warps_issue_stalled_long_scoreboard.avg.pct_of_peak_sustained_elapsed",
        "smsp__warps_issue_stalled_short_scoreboard.avg.pct_of_peak_sustained_elapsed",
    ]
)


# ── Profile Data Classes ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProfileMetrics:
    """Parsed NCU metrics for a single kernel."""

    kernel_name: str
    block_size: str
    grid_size: str

    # Timing (microseconds)
    duration_us: float

    # Throughput (% of peak)
    sm_throughput_pct: float
    dram_throughput_pct: float

    # Occupancy
    achieved_occupancy_pct: float
    occupancy_limit_registers: float
    occupancy_limit_shared_mem: float
    occupancy_limit_blocks: float

    # Launch config
    registers_per_thread: int
    shared_mem_static_bytes: int
    shared_mem_dynamic_bytes: int

    # Cache hit rates
    l1_hit_rate_pct: float
    l2_hit_rate_pct: float

    # Warp stalls (% of elapsed)
    stall_wait_pct: float
    stall_barrier_pct: float
    stall_long_scoreboard_pct: float

    # Tensor core utilization
    tensor_pipe_pct: float


@dataclass(frozen=True)
class ProfileInsights:
    """Formatted insights from a profile."""

    profile_id: str
    kernel_name: str
    formatted_output: str
    metrics: ProfileMetrics


# ── Profile ID Generation ─────────────────────────────────────────────────────


def generate_profile_id(kernel_name: str) -> str:
    """Generate a unique profile ID.

    Format: profile_{kernel_name}_{timestamp}
    Example: profile_kernel_v3_20251127_143022
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize kernel name (remove extension, replace special chars)
    safe_name = Path(kernel_name).stem.replace("-", "_").replace(".", "_")
    return f"profile_{safe_name}_{timestamp}"


# ── Profile Storage ───────────────────────────────────────────────────────────


def get_profiles_dir(artifacts_dir: Path) -> Path:
    """Get the profiles directory within artifacts.

    Creates the directory if it doesn't exist.
    """
    profiles_dir = artifacts_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def save_profile(
    csv_content: str,
    profile_id: str,
    artifacts_dir: Path,
    kernel_code: str | None = None,
) -> Path:
    """Save raw NCU CSV to profiles directory.

    Args:
        csv_content: Raw NCU CSV output
        profile_id: Unique profile identifier
        artifacts_dir: Base artifacts directory
        kernel_code: Optional kernel source code to save alongside profile

    Returns:
        Path to saved CSV file
    """
    profiles_dir = get_profiles_dir(artifacts_dir)
    csv_path = profiles_dir / f"{profile_id}.csv"
    csv_path.write_text(csv_content)
    logger.info(f"📊 Saved NCU profile: {csv_path}")

    # Save kernel code if provided
    if kernel_code:
        code_path = profiles_dir / f"{profile_id}_code.py"
        code_path.write_text(kernel_code)
        logger.debug(f"   Saved kernel code: {code_path}")

    return csv_path


def load_profile(profile_id: str, artifacts_dir: Path) -> tuple[str | None, str | None]:
    """Load raw NCU CSV from profiles directory.

    Args:
        profile_id: Profile identifier
        artifacts_dir: Base artifacts directory

    Returns:
        (csv_content, error): CSV content on success, error message on failure
    """
    profiles_dir = get_profiles_dir(artifacts_dir)
    csv_path = profiles_dir / f"{profile_id}.csv"

    if not csv_path.exists():
        # List available profiles for helpful error message
        available = [p.stem for p in profiles_dir.glob("profile_*.csv")]
        available_str = ", ".join(available[:5]) if available else "none"
        return None, f"Profile '{profile_id}' not found. Available: {available_str}"

    return csv_path.read_text(), None


def load_profile_code(profile_id: str, artifacts_dir: Path) -> str | None:
    """Load kernel code associated with a profile.

    Args:
        profile_id: Profile identifier
        artifacts_dir: Base artifacts directory

    Returns:
        Kernel code if saved, None otherwise
    """
    profiles_dir = get_profiles_dir(artifacts_dir)
    code_path = profiles_dir / f"{profile_id}_code.py"

    if code_path.exists():
        return code_path.read_text()
    return None


def list_profiles(artifacts_dir: Path) -> list[str]:
    """List all available profile IDs.

    Args:
        artifacts_dir: Base artifacts directory

    Returns:
        List of profile IDs (without .csv extension)
    """
    profiles_dir = get_profiles_dir(artifacts_dir)
    return sorted([p.stem for p in profiles_dir.glob("profile_*.csv")])


# ── Profile Parsing ───────────────────────────────────────────────────────────


def _parse_metric_value(value_str: str) -> float:
    """Parse a metric value string to float, handling commas and special cases."""
    if not value_str or value_str == "N/A":
        return 0.0
    try:
        return float(value_str.replace(",", ""))
    except (ValueError, TypeError):
        return 0.0


def _find_relevant_kernel(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find the relevant kernel rows (cutlass/cutedsl, not PyTorch internals).

    Returns rows for the main kernel we care about.
    """
    # Priority 1: Look for cutlass/cutedsl kernels
    relevant = [
        r
        for r in rows
        if "cutlass" in r.get("Kernel Name", "").lower() or "cutedsl" in r.get("Kernel Name", "").lower()
    ]

    if relevant:
        return relevant

    # Priority 2: Find the longest-running kernel (likely the main one)
    kernel_times: dict[str, float] = {}
    for row in rows:
        kernel_name = row.get("Kernel Name", "")
        metric_name = row.get("Metric Name", "")
        metric_value = row.get("Metric Value", "")

        if metric_name == "gpu__time_duration.sum":
            time_ns = _parse_metric_value(metric_value)
            if kernel_name not in kernel_times or time_ns > kernel_times[kernel_name]:
                kernel_times[kernel_name] = time_ns

    if kernel_times:
        main_kernel = max(kernel_times, key=kernel_times.get)  # type: ignore
        return [r for r in rows if r.get("Kernel Name") == main_kernel]

    return []


def parse_ncu_csv(csv_content: str) -> tuple[ProfileMetrics | None, str | None]:
    """Parse NCU CSV into structured ProfileMetrics.

    Args:
        csv_content: Raw NCU CSV content

    Returns:
        (ProfileMetrics, None) on success, (None, error_message) on failure
    """
    lines = csv_content.strip().split("\n")

    # Skip header lines (==PROF== messages)
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('"ID"'):
            data_start = i
            break

    if data_start == 0 and not lines[0].startswith('"ID"'):
        return None, "Could not parse NCU CSV (no header found)"

    # Parse CSV
    reader = csv.DictReader(lines[data_start:])
    rows = list(reader)

    if not rows:
        return None, "No data rows in NCU CSV"

    # Find relevant kernel
    relevant_rows = _find_relevant_kernel(rows)

    if not relevant_rows:
        kernel_names = set(r.get("Kernel Name", "")[:60] for r in rows)
        return None, f"No relevant kernel found. Kernels: {list(kernel_names)[:3]}"

    # Extract metrics from relevant kernel rows
    metrics: dict[str, float] = {}
    kernel_info: dict[str, str] = {}

    for row in relevant_rows:
        metric_name = row.get("Metric Name", "")
        metric_value = row.get("Metric Value", "")

        # Store kernel info (same for all rows of same kernel)
        if not kernel_info:
            kernel_info = {
                "kernel_name": row.get("Kernel Name", "unknown"),
                "block_size": row.get("Block Size", "?"),
                "grid_size": row.get("Grid Size", "?"),
            }

        metrics[metric_name] = _parse_metric_value(metric_value)

    # Build ProfileMetrics with safe defaults
    def get_metric(name: str, default: float = 0.0) -> float:
        return metrics.get(name, default)

    # Calculate duration in microseconds
    duration_ns = get_metric("gpu__time_duration.sum")
    duration_us = duration_ns / 1000.0

    return ProfileMetrics(
        kernel_name=kernel_info.get("kernel_name", "unknown"),
        block_size=kernel_info.get("block_size", "?"),
        grid_size=kernel_info.get("grid_size", "?"),
        duration_us=duration_us,
        sm_throughput_pct=get_metric("sm__throughput.avg.pct_of_peak_sustained_elapsed"),
        dram_throughput_pct=get_metric("dram__throughput.avg.pct_of_peak_sustained_elapsed"),
        achieved_occupancy_pct=get_metric("sm__warps_active.avg.pct_of_peak_sustained_active"),
        occupancy_limit_registers=get_metric("launch__occupancy_limit_registers"),
        occupancy_limit_shared_mem=get_metric("launch__occupancy_limit_shared_mem"),
        occupancy_limit_blocks=get_metric("launch__occupancy_limit_blocks"),
        registers_per_thread=int(get_metric("launch__registers_per_thread")),
        shared_mem_static_bytes=int(get_metric("launch__shared_mem_per_block_static")),
        shared_mem_dynamic_bytes=int(get_metric("launch__shared_mem_per_block_dynamic")),
        l1_hit_rate_pct=get_metric("l1tex__t_sector_hit_rate.pct"),
        l2_hit_rate_pct=get_metric("lts__t_sector_hit_rate.pct"),
        stall_wait_pct=get_metric("smsp__warps_issue_stalled_wait.avg.pct_of_peak_sustained_elapsed"),
        stall_barrier_pct=get_metric("smsp__warps_issue_stalled_barrier.avg.pct_of_peak_sustained_elapsed"),
        stall_long_scoreboard_pct=get_metric(
            "smsp__warps_issue_stalled_long_scoreboard.avg.pct_of_peak_sustained_elapsed"
        ),
        tensor_pipe_pct=get_metric("sm__inst_executed_pipe_tensor.avg.pct_of_peak_sustained_active"),
    ), None


# ── Insight Generation ────────────────────────────────────────────────────────


def _determine_bottleneck(metrics: ProfileMetrics) -> tuple[str, str]:
    """Determine the primary bottleneck and explanation.

    Returns:
        (bottleneck_type, explanation)
    """
    sm = metrics.sm_throughput_pct
    dram = metrics.dram_throughput_pct

    # Strong memory bound: DRAM >> SM
    if dram > sm * 1.5 and dram > 30:
        return "MEMORY BOUND", "DRAM throughput significantly higher than SM compute"

    # Strong compute bound: SM >> DRAM
    if sm > dram * 1.5 and sm > 30:
        return "COMPUTE BOUND", "SM throughput significantly higher than DRAM bandwidth"

    # Both low - latency bound (likely stalls)
    if sm < 30 and dram < 30:
        return "LATENCY BOUND", "Both SM and DRAM utilization low - check for stalls"

    # Balanced
    return "BALANCED", "SM compute and DRAM bandwidth roughly balanced"


def _generate_suggestions(metrics: ProfileMetrics, bottleneck: str) -> list[str]:
    """Generate actionable suggestions based on metrics.

    Returns:
        List of suggestion strings
    """
    suggestions = []

    # Bottleneck-specific suggestions
    if bottleneck == "MEMORY BOUND":
        suggestions.append("• Memory-bound: Focus on memory coalescing, caching, reducing data movement")
        if metrics.l1_hit_rate_pct < 50:
            suggestions.append(f"• L1 cache hit rate is {metrics.l1_hit_rate_pct:.1f}% - consider data reuse patterns")
        if metrics.l2_hit_rate_pct < 50:
            suggestions.append(f"• L2 cache hit rate is {metrics.l2_hit_rate_pct:.1f}% - check memory access locality")

    elif bottleneck == "COMPUTE BOUND":
        suggestions.append("• Compute-bound: Focus on reducing instruction count, improving ILP")
        if metrics.tensor_pipe_pct < 10 and metrics.duration_us > 10:
            suggestions.append("• Low tensor core utilization - consider using tensor cores if applicable")

    elif bottleneck == "LATENCY BOUND":
        if metrics.stall_long_scoreboard_pct > 20:
            suggestions.append(
                f"• High long scoreboard stalls ({metrics.stall_long_scoreboard_pct:.1f}%) - likely waiting for memory"
            )
        if metrics.stall_barrier_pct > 20:
            suggestions.append(
                f"• High barrier stalls ({metrics.stall_barrier_pct:.1f}%) - thread synchronization overhead"
            )
        if metrics.stall_wait_pct > 20:
            suggestions.append(f"• High wait stalls ({metrics.stall_wait_pct:.1f}%) - dependency issues")

    # Occupancy suggestions
    if metrics.achieved_occupancy_pct < 50:
        suggestions.append(f"• Achieved occupancy is {metrics.achieved_occupancy_pct:.1f}% - consider:")
        if metrics.registers_per_thread > 64:
            suggestions.append(f"  - Register usage ({metrics.registers_per_thread}/thread) may limit occupancy")
        if metrics.shared_mem_static_bytes > 16384:
            suggestions.append(f"  - Shared memory ({metrics.shared_mem_static_bytes} bytes) may limit occupancy")

    return suggestions if suggestions else ["• Kernel is reasonably optimized for this workload"]


def format_profile_insights(
    profile_id: str,
    metrics: ProfileMetrics,
) -> str:
    """Format ProfileMetrics into human-readable insights.

    Args:
        profile_id: The profile identifier
        metrics: Parsed profile metrics

    Returns:
        Formatted multi-line string with insights
    """
    bottleneck, bottleneck_reason = _determine_bottleneck(metrics)
    suggestions = _generate_suggestions(metrics, bottleneck)

    # Truncate kernel name for display
    kernel_display = metrics.kernel_name[:60]
    if len(metrics.kernel_name) > 60:
        kernel_display += "..."

    lines = [
        f"=== Profile: {profile_id} ===",
        f"Kernel: {kernel_display}",
        "",
        "LAUNCH CONFIG:",
        f"  Grid: {metrics.grid_size}, Block: {metrics.block_size}",
        f"  Registers/thread: {metrics.registers_per_thread}",
        f"  Shared memory: {metrics.shared_mem_static_bytes + metrics.shared_mem_dynamic_bytes} bytes",
        "",
        "UTILIZATION:",
        f"  SM Compute:     {metrics.sm_throughput_pct:.1f}% of peak",
        f"  DRAM Bandwidth: {metrics.dram_throughput_pct:.1f}% of peak",
        f"  Occupancy:      {metrics.achieved_occupancy_pct:.1f}%",
        "",
        "CACHE:",
        f"  L1 Hit Rate: {metrics.l1_hit_rate_pct:.1f}%",
        f"  L2 Hit Rate: {metrics.l2_hit_rate_pct:.1f}%",
        "",
        f"TIMING: {metrics.duration_us:.2f} µs",
        "",
        f"BOTTLENECK: {bottleneck}",
        f"  ({bottleneck_reason})",
        "",
        "SUGGESTIONS:",
    ]

    lines.extend(suggestions)

    return "\n".join(lines)


def get_profile_insights(
    profile_id: str,
    artifacts_dir: Path,
    include_code: bool = False,
) -> tuple[ProfileInsights | None, str | None]:
    """Get formatted insights for a saved profile.

    This is the main entry point for the get_profile_insights tool.

    Args:
        profile_id: Profile identifier
        artifacts_dir: Base artifacts directory
        include_code: Whether to include kernel source code in output

    Returns:
        (ProfileInsights, None) on success, (None, error_message) on failure
    """
    # Load the raw CSV
    csv_content, load_err = load_profile(profile_id, artifacts_dir)
    if load_err:
        return None, load_err

    assert csv_content is not None  # load_profile returns content when no error

    # Parse into metrics
    metrics, parse_err = parse_ncu_csv(csv_content)
    if parse_err:
        return None, parse_err

    assert metrics is not None  # parse_ncu_csv returns metrics when no error

    # Format insights
    formatted = format_profile_insights(profile_id, metrics)

    # Optionally include kernel code
    if include_code:
        kernel_code = load_profile_code(profile_id, artifacts_dir)
        if kernel_code:
            formatted = f"{formatted}\n\n{'=' * 60}\nKERNEL SOURCE CODE:\n{'=' * 60}\n\n{kernel_code}"
        else:
            formatted = f"{formatted}\n\n(Kernel source code not saved with this profile)"

    return ProfileInsights(
        profile_id=profile_id,
        kernel_name=metrics.kernel_name,
        formatted_output=formatted,
        metrics=metrics,
    ), None
