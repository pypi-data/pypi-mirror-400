"""Extract analysis summary information from NSYS data."""

from __future__ import annotations

import datetime


def format_file_size(file_size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if file_size_bytes < 1024:
        return f"{file_size_bytes} B"
    elif file_size_bytes < 1024 * 1024:
        return f"{file_size_bytes / 1024:.2f} KiB"
    else:
        return f"{file_size_bytes / 1024 / 1024:.2f} MiB"


def extract_host_computer(timeline_data: dict) -> dict:
    """Extract host computer information."""
    host_computer = {
        "hostname": timeline_data.get("hostname"),
        "platform": timeline_data.get("platform"),
        "os": timeline_data.get("os"),
        "hardware_platform": timeline_data.get("hardware_platform"),
        "cpu_description": timeline_data.get("cpu_description")
    }
    
    missing_fields = [k for k, v in host_computer.items() if v is None]
    if missing_fields:
        raise ValueError(f"Missing host computer fields: {missing_fields}")
    
    return host_computer


def extract_target_system(timeline_data: dict) -> dict:
    """Extract target system information."""
    target_system = {
        "hostname": timeline_data.get("target_hostname"),
        "local_time_at_t0": timeline_data.get("local_time_at_t0"),
        "utc_time_at_t0": timeline_data.get("utc_time_at_t0"),
        "tsc_value_at_t0": timeline_data.get("tsc_value_at_t0"),
        "platform": timeline_data.get("target_platform"),
        "os": timeline_data.get("target_os"),
        "hardware_platform": timeline_data.get("target_hardware_platform"),
        "serial_number": timeline_data.get("serial_number"),
        "cpu_description": timeline_data.get("target_cpu_description")
    }
    
    required_fields = ["hostname", "platform", "os", "hardware_platform", "serial_number", "cpu_description"]
    missing_fields = [k for k in required_fields if target_system.get(k) is None]
    if missing_fields:
        raise ValueError(f"Missing target system fields: {missing_fields}")
    
    gpu_devices = set()
    if "traceEvents" in timeline_data:
        for event in timeline_data["traceEvents"]:
            args = event.get("args", {})
            device_id = args.get("device_id")
            if device_id is not None:
                gpu_devices.add(device_id)
    
    target_system["gpu_devices"] = [{"device_id": d, "name": f"NVIDIA GPU {d}"} for d in sorted(gpu_devices)]
    
    return target_system


def extract_session_activities(timeline_data: dict) -> list[dict]:
    """Extract session activities from diagnostic events."""
    session_activities = []
    
    if "traceEvents" not in timeline_data:
        return session_activities
    
    for event in timeline_data["traceEvents"]:
        if event.get("cat") != "diagnostic":
            continue
        
        args = event.get("args", {})
        text = args.get("text", "")
        time_ms = event.get("ts", 0) / 1000
        
        if "Profiling has started" in text:
            session_activities.append({"type": "start", "message": text, "time_ms": time_ms})
        elif "Profiling has stopped" in text or "stopped" in text.lower():
            session_activities.append({"type": "stop", "message": text, "time_ms": time_ms})
        elif "Process was launched" in text:
            session_activities.append({"type": "launch", "message": text, "time_ms": time_ms})
        elif "exit code" in text.lower():
            session_activities.append({"type": "exit", "message": text, "time_ms": time_ms})
    
    return session_activities


def extract_analysis_summary(
    timeline_data: dict,
    file_path: str,
    file_size_bytes: int,
    capture_time: float,
    total_events: int,
    total_threads: int
) -> dict:
    """Extract analysis summary information from NSYS data."""
    if capture_time <= 0:
        raise ValueError(f"Invalid capture_time: {capture_time}")
    
    file_size_str = format_file_size(file_size_bytes)
    capture_time_str = datetime.datetime.fromtimestamp(capture_time).strftime("%m/%d/%Y, %I:%M:%S %p")
    
    host_computer = extract_host_computer(timeline_data)
    target_system = extract_target_system(timeline_data)
    session_activities = extract_session_activities(timeline_data)
    
    return {
        "report_file": file_path,
        "report_size": file_size_str,
        "report_size_bytes": file_size_bytes,
        "capture_time": capture_time_str,
        "capture_timestamp": capture_time,
        "event_count": total_events,
        "thread_count": total_threads,
        "host_computer": host_computer,
        "target_system": target_system,
        "session_activities": session_activities
    }
