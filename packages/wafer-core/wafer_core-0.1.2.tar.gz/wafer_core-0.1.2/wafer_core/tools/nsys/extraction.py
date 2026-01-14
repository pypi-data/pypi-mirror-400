"""Extract structured data from NSYS exports."""

from __future__ import annotations


def extract_kernels(kernels_data: dict) -> list[dict]:
    """Extract kernel information from kernels data."""
    kernels = []
    if "GPU Kernel Summary" not in kernels_data:
        raise ValueError("Missing 'GPU Kernel Summary' in kernels data")
    
    for kernel in kernels_data["GPU Kernel Summary"]:
        if "Name" not in kernel:
            raise ValueError(f"Kernel missing 'Name' field: {kernel}")
        if "Start" not in kernel:
            raise ValueError(f"Kernel missing 'Start' field: {kernel}")
        if "End" not in kernel:
            raise ValueError(f"Kernel missing 'End' field: {kernel}")
        if "Duration" not in kernel:
            raise ValueError(f"Kernel missing 'Duration' field: {kernel}")
        
        kernels.append({
            "name": kernel["Name"],
            "start_time_ms": kernel["Start"] / 1_000_000,
            "end_time_ms": kernel["End"] / 1_000_000,
            "duration_ms": kernel["Duration"] / 1_000_000,
            "grid_size": [
                kernel.get("Grid X", 1),
                kernel.get("Grid Y", 1),
                kernel.get("Grid Z", 1)
            ],
            "block_size": [
                kernel.get("Block X", 1),
                kernel.get("Block Y", 1),
                kernel.get("Block Z", 1)
            ],
            "memory_throughput_gb_s": kernel.get("Memory Throughput", 0) / 1_000_000_000
        })
    return kernels


def extract_timeline_events(timeline_data: dict) -> tuple[list[dict], list[dict], set[int], set[int]]:
    """Extract timeline events and diagnostics from timeline data."""
    timeline = []
    diagnostics = []
    unique_threads = set()
    unique_processes = set()
    
    if "traceEvents" not in timeline_data:
        return timeline, diagnostics, unique_threads, unique_processes
    
    for event in timeline_data["traceEvents"]:
        event_category = event.get("cat")
        event_name = event.get("name")
        if not event_category:
            raise ValueError(f"Event missing 'cat' field: {event}")
        if not event_name:
            raise ValueError(f"Event missing 'name' field: {event}")
        
        if "ts" not in event:
            raise ValueError(f"Event missing 'ts' field: {event}")
        
        ts_us = event["ts"]
        dur_us = event.get("dur", 0)
        
        timeline_event = {
            "type": event_category,
            "name": event_name,
            "phase": event.get("ph", "X"),
            "start_time_ms": ts_us / 1000,
            "end_time_ms": (ts_us + dur_us) / 1000 if dur_us > 0 else ts_us / 1000,
            "duration_ms": dur_us / 1000,
            "tid": event.get("tid", 0),
            "pid": event.get("pid", 0),
            "args": event.get("args", {})
        }
        
        if timeline_event["tid"]:
            unique_threads.add(timeline_event["tid"])
        if timeline_event["pid"]:
            unique_processes.add(timeline_event["pid"])
        
        args = event.get("args", {})
        if "device_id" in args:
            timeline_event["device_id"] = args["device_id"]
        if "stream_id" in args:
            timeline_event["stream_id"] = args["stream_id"]
        
        if event_category == "diagnostic":
            diag_args = args
            if "source" not in diag_args:
                raise ValueError(f"Diagnostic event missing 'source' in args: {diag_args}")
            
            diagnostics.append({
                "source": diag_args["source"],
                "level": diag_args.get("level", "Info"),
                "text": diag_args.get("text", ""),
                "processId": timeline_event["pid"],
                "time_ms": timeline_event["start_time_ms"],
                "timestamp": ts_us / 1000
            })
            diag_is_overhead = diag_args.get("is_overhead", False)
            if diag_is_overhead:
                timeline_event["is_overhead"] = True
                timeline.append(timeline_event)
        else:
            timeline_event["is_overhead"] = (event_category == "cupti")
            timeline.append(timeline_event)
    
    return timeline, diagnostics, unique_threads, unique_processes


def extract_memory_usage(memory_data: dict) -> list[dict]:
    """Extract memory usage snapshots from memory data."""
    memory_usage = []
    if "GPU Memory Time Series" not in memory_data:
        return memory_usage
    
    for snapshot in memory_data["GPU Memory Time Series"]:
        if "Time" not in snapshot:
            raise ValueError(f"Memory snapshot missing 'Time' field: {snapshot}")
        if "Allocated" not in snapshot:
            raise ValueError(f"Memory snapshot missing 'Allocated' field: {snapshot}")
        if "Free" not in snapshot:
            raise ValueError(f"Memory snapshot missing 'Free' field: {snapshot}")
        
        memory_usage.append({
            "timestamp_ms": snapshot["Time"] / 1_000_000,
            "allocated_mb": snapshot["Allocated"] / 1_000_000,
            "free_mb": snapshot["Free"] / 1_000_000
        })
    return memory_usage


def calculate_summary(timeline: list[dict], kernels: list[dict], timeline_data: dict) -> dict:
    """Calculate summary statistics from timeline and kernels."""
    total_duration = 0
    if timeline:
        max_end = max(e["end_time_ms"] for e in timeline if e["end_time_ms"] > 0)
        min_start = min(e["start_time_ms"] for e in timeline if e["start_time_ms"] > 0)
        total_duration = max_end - min_start if max_end > min_start else 0
    
    if not total_duration and kernels:
        max_end = max(k["end_time_ms"] for k in kernels)
        min_start = min(k["start_time_ms"] for k in kernels)
        total_duration = max_end - min_start
    
    if "systemInfo" not in timeline_data:
        raise ValueError("Missing systemInfo in timeline data")
    
    gpu_name = timeline_data["systemInfo"].get("gpuName")
    if not gpu_name:
        raise ValueError("Missing gpuName in systemInfo")
    
    event_counts = {}
    for event in timeline:
        if "type" not in event:
            raise ValueError(f"Event missing 'type' field: {event}")
        cat = event["type"]
        event_counts[cat] = event_counts.get(cat, 0) + 1
    
    overhead_events = [e for e in timeline if e.get("is_overhead", False)]
    overhead_duration = sum(e["duration_ms"] for e in overhead_events)
    profiler_overhead_percent = (overhead_duration / total_duration * 100) if total_duration > 0 else 0
    
    return {
        "gpu": gpu_name,
        "duration_ms": total_duration,
        "kernel_count": len(kernels),
        "memory_transfers": len([e for e in timeline if e["type"] in ["memcpy", "memset"]]),
        "event_counts": event_counts,
        "total_events": len(timeline),
        "profiler_overhead_percent": profiler_overhead_percent
    }
