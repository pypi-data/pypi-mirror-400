"""Metrics extraction from stdout and profiler files."""

import logging
import re
from pathlib import Path

import trio

from wafer_core.capture.dtypes import MetricsResult

logger = logging.getLogger(__name__)


# Common metric patterns to extract from stdout
METRIC_PATTERNS = [
    # Latency patterns
    (r"latency[:\s]+(\d+\.?\d*)\s*(us|μs|microseconds?)", "latency_us", 1.0),
    (r"latency[:\s]+(\d+\.?\d*)\s*(ms|milliseconds?)", "latency_us", 1000.0),
    (r"latency[:\s]+(\d+\.?\d*)\s*(s|seconds?)", "latency_us", 1_000_000.0),
    # Throughput patterns
    (r"throughput[:\s]+(\d+\.?\d*)\s*(gb/s|gbps)", "throughput_gb_s", 1.0),
    (r"throughput[:\s]+(\d+\.?\d*)\s*(mb/s|mbps)", "throughput_gb_s", 0.001),
    (r"throughput[:\s]+(\d+\.?\d*)\s*(tb/s|tbps)", "throughput_gb_s", 1000.0),
    # Bandwidth patterns
    (r"bandwidth[:\s]+(\d+\.?\d*)\s*(gb/s|gbps)", "bandwidth_gb_s", 1.0),
    (r"bandwidth[:\s]+(\d+\.?\d*)\s*(mb/s|mbps)", "bandwidth_gb_s", 0.001),
    (r"bandwidth[:\s]+(\d+\.?\d*)\s*(tb/s|tbps)", "bandwidth_gb_s", 1000.0),
    # Speedup patterns
    (r"speedup[:\s]+(\d+\.?\d*)x?", "speedup", 1.0),
    # FLOPS patterns
    (r"(\d+\.?\d*)\s*(tflops|tflop/s)", "tflops", 1.0),
    (r"(\d+\.?\d*)\s*(gflops|gflop/s)", "tflops", 0.001),
    # Time patterns
    (r"time[:\s]+(\d+\.?\d*)\s*(ms|milliseconds?)", "time_ms", 1.0),
    (r"time[:\s]+(\d+\.?\d*)\s*(s|seconds?)", "time_ms", 1000.0),
    (r"time[:\s]+(\d+\.?\d*)\s*(us|μs|microseconds?)", "time_ms", 0.001),
    # Kernel time patterns
    (r"kernel\s+time[:\s]+(\d+\.?\d*)\s*(ms|milliseconds?)", "kernel_time_ms", 1.0),
    (r"kernel\s+time[:\s]+(\d+\.?\d*)\s*(us|μs|microseconds?)", "kernel_time_ms", 0.001),
    # Memory patterns
    (r"memory[:\s]+(\d+\.?\d*)\s*(gb|gigabytes?)", "memory_gb", 1.0),
    (r"memory[:\s]+(\d+\.?\d*)\s*(mb|megabytes?)", "memory_gb", 0.001),
    # Efficiency patterns
    (r"efficiency[:\s]+(\d+\.?\d*)%?", "efficiency_percent", 1.0),
    # Error patterns
    (r"error[:\s]+(\d+\.?\d*)%?", "error_percent", 1.0),
    (r"(mse|rmse|mae)[:\s]+(\d+\.?\d*)", lambda m: m.group(1).lower(), 1.0),
]


def extract_metrics_from_stdout(stdout: str) -> dict[str, float]:
    """Extract metrics from command stdout using regex patterns.

    Args:
        stdout: Standard output from command execution

    Returns:
        Dictionary of extracted metrics (metric_name -> value)
    """
    logger.debug("Extracting metrics from stdout")

    metrics: dict[str, float] = {}

    # Make stdout lowercase for case-insensitive matching
    stdout_lower = stdout.lower()

    for pattern_tuple in METRIC_PATTERNS:
        if len(pattern_tuple) == 3:
            pattern, metric_name, multiplier = pattern_tuple
        else:
            continue

        # Compile pattern
        regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

        # Find all matches
        for match in regex.finditer(stdout_lower):
            try:
                # Extract numeric value (group 1)
                value_str = match.group(1)
                value = float(value_str)

                # Apply multiplier for unit conversion
                if callable(metric_name):
                    # Dynamic metric name from match
                    name = metric_name(match)
                else:
                    name = metric_name

                # Apply multiplier
                if callable(multiplier):
                    value = multiplier(value)
                else:
                    value *= multiplier

                # Store metric (keep last occurrence if multiple)
                metrics[name] = value

                logger.debug(f"Extracted metric: {name} = {value}")

            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse metric from match: {e}")
                continue

    logger.info(f"Extracted {len(metrics)} metrics from stdout")
    return metrics


async def detect_ncu_files(working_dir: Path) -> list[Path]:
    """Detect NCU profile files in working directory.

    Args:
        working_dir: Directory to search

    Returns:
        List of .ncu-rep file paths (relative to working_dir)
    """
    logger.debug(f"Detecting NCU files in: {working_dir}")

    def _scan() -> list[Path]:
        """Scan for .ncu-rep files."""
        ncu_files: list[Path] = []
        for file in working_dir.rglob("*.ncu-rep"):
            try:
                rel_path = file.relative_to(working_dir)
                ncu_files.append(rel_path)
            except ValueError:
                continue
        return ncu_files

    ncu_files = await trio.to_thread.run_sync(_scan)

    logger.info(f"Found {len(ncu_files)} NCU profile files")
    return ncu_files


async def parse_ncu_file(ncu_file: Path) -> dict[str, float]:
    """Parse NCU profile file and extract metrics.

    Uses NCU command-line tool to parse .ncu-rep binary files and extract
    key performance metrics (duration, occupancy, throughput, etc.).

    Args:
        ncu_file: Path to .ncu-rep file

    Returns:
        Dictionary of metrics extracted from NCU profile
        Keys include:
        - ncu_duration_us: Kernel duration in microseconds
        - ncu_duration_ms: Kernel duration in milliseconds
        - ncu_occupancy_pct: Achieved occupancy percentage
        - ncu_memory_throughput_pct: Memory throughput % of peak
        - ncu_compute_throughput_pct: Compute (SM) throughput % of peak
        - ncu_estimated_speedup_pct: Estimated speedup from recommendations

    Note:
        Requires NCU (NVIDIA Nsight Compute) to be installed locally.
        Falls back gracefully with warning if NCU not available.
    """
    logger.debug(f"Parsing NCU file: {ncu_file}")

    # Import _parse_ncu_file_impl to run in thread
    def _parse_ncu_file_sync(file_path: Path) -> dict[str, float]:
        """Synchronous NCU parsing to run in thread pool."""
        import os
        import platform
        import shutil
        import subprocess

        # Find NCU executable
        def find_ncu() -> str | None:
            """Find NCU executable on the system."""
            ncu = shutil.which("ncu")
            if ncu:
                return ncu

            # Check known installation paths
            system = platform.system().lower()
            ncu_paths = {
                "linux": [
                    "/usr/local/cuda/bin/ncu",
                    "/opt/nvidia/nsight-compute/ncu",
                    "/usr/bin/ncu",
                    "/usr/local/bin/ncu",
                ],
                "darwin": [
                    "/Applications/NVIDIA Nsight Compute.app/Contents/MacOS/ncu",
                    "/usr/local/cuda/bin/ncu",
                ],
                "windows": [
                    r"C:\Program Files\NVIDIA Corporation\Nsight Compute\ncu.exe",
                    r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin\ncu.exe",
                ],
            }

            plat = "linux" if system == "linux" else "darwin" if system == "darwin" else "windows"
            for path_str in ncu_paths.get(plat, []):
                if os.path.isfile(path_str) and os.access(path_str, os.X_OK):
                    return path_str

            return None

        ncu_path = find_ncu()
        if not ncu_path:
            logger.warning(
                "NCU not installed - skipping NCU metric extraction. "
                "Install from: https://developer.nvidia.com/nsight-compute"
            )
            return {}

        try:
            # Run NCU to get session and details output
            # Increased timeout to 300s for large profiling runs
            session_result = subprocess.run(
                [ncu_path, "--import", str(file_path), "--page", "session"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            details_result = subprocess.run(
                [ncu_path, "--import", str(file_path), "--page", "details"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse NCU output to extract metrics
            metrics = {}
            details_lines = details_result.stdout.split("\n")

            current_kernel_metrics: dict[str, float] = {}

            for i, line in enumerate(details_lines):
                stripped = line.strip()

                # Detect kernel header
                if (
                    line.startswith("  ")
                    and not line.startswith("    ")
                    and "Context" in line
                    and "Device" in line
                ):
                    # New kernel found - if we have previous kernel metrics, use them
                    if current_kernel_metrics:
                        # Use first kernel's metrics (usually the main one)
                        metrics = current_kernel_metrics
                        break
                    current_kernel_metrics = {}

                # Extract metrics from table rows
                if "          " in line:  # Multiple spaces = table format
                    parts = line.split()
                    if len(parts) < 2:
                        continue

                    # Duration in microseconds
                    if "Duration" in stripped and "us" in stripped:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel_metrics["ncu_duration_us"] = value
                            current_kernel_metrics["ncu_duration_ms"] = value / 1000.0
                        except (ValueError, IndexError):
                            pass

                    # Memory Throughput %
                    elif "Memory Throughput" in stripped and "%" in stripped:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel_metrics["ncu_memory_throughput_pct"] = value
                        except (ValueError, IndexError):
                            pass

                    # Compute (SM) Throughput %
                    elif (
                        "Compute (SM) Throughput" in stripped or "Compute Throughput" in stripped
                    ):
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel_metrics["ncu_compute_throughput_pct"] = value
                        except (ValueError, IndexError):
                            pass

                    # Achieved Occupancy %
                    elif "Achieved Occupancy" in stripped and "%" in stripped:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel_metrics["ncu_occupancy_pct"] = value
                        except (ValueError, IndexError):
                            pass

                # Extract estimated speedup from recommendations
                if "Est. Speedup:" in stripped or "Est. Local Speedup:" in stripped:
                    import re

                    speedup_match = re.search(r"Speedup:\s*([\d.]+)%", stripped)
                    if speedup_match:
                        try:
                            speedup = float(speedup_match.group(1))
                            if "ncu_estimated_speedup_pct" not in current_kernel_metrics:
                                current_kernel_metrics["ncu_estimated_speedup_pct"] = speedup
                            else:
                                # Keep maximum speedup
                                current_kernel_metrics["ncu_estimated_speedup_pct"] = max(
                                    current_kernel_metrics["ncu_estimated_speedup_pct"], speedup
                                )
                        except (ValueError, IndexError):
                            pass

            # If we finished parsing and have metrics from last kernel
            if current_kernel_metrics and not metrics:
                metrics = current_kernel_metrics

            if metrics:
                logger.info(
                    f"Extracted {len(metrics)} NCU metrics: "
                    f"duration={metrics.get('ncu_duration_us', 0):.1f}us, "
                    f"occupancy={metrics.get('ncu_occupancy_pct', 0):.1f}%"
                )
            else:
                logger.warning("No metrics extracted from NCU output")

            return metrics

        except subprocess.TimeoutExpired:
            logger.error("NCU parsing timed out (120s limit)")
            return {}
        except Exception as e:
            logger.error(f"Failed to parse NCU file: {e}")
            return {}

    # Run synchronous parsing in thread pool
    try:
        metrics = await trio.to_thread.run_sync(_parse_ncu_file_sync, ncu_file)
        return metrics
    except Exception as e:
        logger.error(f"NCU parsing failed: {e}")
        return {}


async def collect_all_metrics(
    stdout: str, working_dir: Path
) -> MetricsResult:
    """Collect all available metrics from stdout and NCU profiles.

    Args:
        stdout: Standard output from command
        working_dir: Working directory (for finding NCU files)

    Returns:
        MetricsResult with all extracted metrics
    """
    logger.info("Collecting all metrics")

    # Extract from stdout
    stdout_metrics = extract_metrics_from_stdout(stdout)

    # Detect NCU files
    ncu_files = await detect_ncu_files(working_dir)

    ncu_metrics = None
    ncu_file_path = None

    if ncu_files:
        # Use first NCU file found
        ncu_file_path = working_dir / ncu_files[0]
        logger.info(f"Parsing NCU file: {ncu_file_path}")

        try:
            ncu_metrics = await parse_ncu_file(ncu_file_path)
        except Exception as e:
            logger.error(f"Failed to parse NCU file: {e}")
            ncu_metrics = None

    return MetricsResult(
        stdout_metrics=stdout_metrics,
        ncu_metrics=ncu_metrics,
        ncu_file_path=ncu_file_path,
    )
