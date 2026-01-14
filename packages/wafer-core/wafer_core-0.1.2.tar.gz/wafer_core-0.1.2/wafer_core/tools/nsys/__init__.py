"""NSYS Tool - NVIDIA Nsight Systems analysis for system-level profiling.

Provides functions to check NSYS installation and parse .nsys-rep files.
Can be used as a module or run as a standalone script.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

from .analysis import extract_analysis_summary
from .discovery import check_nsys, find_nsys
from .export import export_kernels, export_memory, export_timeline, load_exported_data
from .extraction import (
    calculate_summary,
    extract_kernels,
    extract_memory_usage,
    extract_timeline_events,
)


def parse_nsys_report(
    file_path: str,
    output_dir: str | None = None
) -> dict:
    """Parse an .nsys-rep file and extract timeline/kernel data.
    
    Args:
        file_path: Path to .nsys-rep file
        output_dir: Optional output directory (defaults to /tmp/nsys-analysis)
    
    Returns:
        Dictionary with success status and parsed data or error message
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}
    
    if path.suffix != ".nsys-rep":
        return {"success": False, "error": f"Expected .nsys-rep file, got: {path.suffix}"}
    
    file_stat = path.stat()
    file_size_bytes = file_stat.st_size
    capture_time = file_stat.st_mtime
    
    nsys_path = find_nsys()
    if not nsys_path:
        return {"success": False, "error": "NSYS not installed. Run 'check' command for install instructions."}
    
    out_path = Path(output_dir) if output_dir else Path("/tmp/nsys-analysis")
    out_path.mkdir(parents=True, exist_ok=True)
    
    try:
        import sys

        def log_progress(message: str):
            print(f"[NSYS_PROGRESS] {message}", file=sys.stderr, flush=True)
        
        log_progress("Exporting kernel data...")
        kernel_path = export_kernels(nsys_path, path, out_path)
        
        log_progress("Exporting timeline data...")
        timeline_path = export_timeline(nsys_path, path, out_path)
        
        log_progress("Exporting memory usage data...")
        memory_path = export_memory(nsys_path, path, out_path)
        
        log_progress("Loading exported data...")
        kernels_data, timeline_data, memory_data = load_exported_data(kernel_path, timeline_path, memory_path)
        
        log_progress("Extracting kernels...")
        kernels = extract_kernels(kernels_data)
        
        log_progress("Extracting timeline events...")
        timeline, diagnostics, unique_threads, unique_processes = extract_timeline_events(timeline_data)
        
        log_progress("Extracting memory usage...")
        memory_usage = extract_memory_usage(memory_data)
        
        log_progress("Calculating summary...")
        summary = calculate_summary(timeline, kernels, timeline_data)
        
        log_progress("Generating analysis summary...")
        analysis_summary = extract_analysis_summary(
            timeline_data,
            file_path=str(path),
            file_size_bytes=file_size_bytes,
            capture_time=capture_time,
            total_events=len(timeline) + len(diagnostics),
            total_threads=len(unique_threads)
        )
        
        parsed = {
            "summary": summary,
            "kernels": kernels,
            "timeline": timeline,
            "memory_usage": memory_usage,
            "analysis_summary": analysis_summary,
            "diagnostics": diagnostics
        }
        
        result_path = out_path / "report.json"
        result_path.write_text(json.dumps(parsed, indent=2))
        
        return {
            "success": True,
            "output_file": str(result_path),
            "summary": parsed["summary"],
            "kernels": parsed["kernels"],
            "timeline": parsed["timeline"],
            "memory_usage": parsed["memory_usage"],
            "analysis_summary": parsed["analysis_summary"],
            "diagnostics": parsed["diagnostics"]
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "NSYS command timed out"}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"NSYS command failed: {e.stderr}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = ["find_nsys", "check_nsys", "parse_nsys_report"]
