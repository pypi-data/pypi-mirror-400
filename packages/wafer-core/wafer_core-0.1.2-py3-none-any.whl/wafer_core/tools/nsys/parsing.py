"""NSYS NDJSON parsing and event conversion."""

from __future__ import annotations

import json
from pathlib import Path


def parse_ndjson_header(line_obj: dict) -> tuple[dict, dict]:
    """Parse first line of NDJSON containing string mappings and file references."""
    string_map = {}
    process_map = {}
    
    if 'data' in line_obj and isinstance(line_obj['data'], list):
        string_map = {i: s for i, s in enumerate(line_obj['data'])}
    
    if 'files' in line_obj and isinstance(line_obj['files'], list):
        for file_obj in line_obj['files']:
            if isinstance(file_obj, dict):
                pid = file_obj.get('GlobalProcessId')
                if pid:
                    process_map[str(pid)] = file_obj
    
    return string_map, process_map


def parse_ndjson_event(obj: dict, string_map: dict, thread_map: dict) -> dict | None:
    """Parse a single event from NDJSON format."""
    if 'CudaEvent' in obj:
        return convert_cuda_event(obj['CudaEvent'], string_map)
    
    if 'CommEvent' in obj:
        comm_event = obj['CommEvent']
        chrome_event = convert_comm_event(comm_event, string_map)
        if chrome_event:
            pid = comm_event.get('GlobalPid')
            commname = comm_event.get('Commname')
            if pid and commname:
                thread_map[str(pid)] = commname
        return chrome_event
    
    if 'TraceProcessEvent' in obj:
        return convert_trace_event(obj['TraceProcessEvent'], string_map)
    
    if 'DiagnosticEvent' in obj:
        return convert_diagnostic_event(obj['DiagnosticEvent'], string_map)
    
    return None


def parse_ndjson(file_path: Path) -> dict:
    """Parse NSYS NDJSON export format into Chrome trace format."""
    trace_events = []
    thread_map = {}
    
    with open(file_path) as f:
        first_line = True
        string_map = {}
        process_map = {}
        
        for raw_line in f:
            stripped_line = raw_line.strip()
            if not stripped_line:
                continue
            
            obj = json.loads(stripped_line)
            
            if first_line:
                string_map, process_map = parse_ndjson_header(obj)
                first_line = False
                continue
            
            chrome_event = parse_ndjson_event(obj, string_map, thread_map)
            if chrome_event:
                trace_events.append(chrome_event)
    
    return {
        "traceEvents": trace_events,
        "stringMap": string_map,
        "threadMap": thread_map,
        "processMap": process_map
    }


def convert_cuda_event(cuda_event: dict, string_map: dict) -> dict:
    """Convert NSYS CudaEvent to Chrome trace format."""
    if 'startNs' not in cuda_event:
        raise ValueError(f"CudaEvent missing 'startNs': {cuda_event}")
    if 'endNs' not in cuda_event:
        raise ValueError(f"CudaEvent missing 'endNs': {cuda_event}")
    
    start_ns = int(cuda_event['startNs'] or 0)
    end_ns = int(cuda_event['endNs'] or 0)
    duration_ns = end_ns - start_ns if end_ns > start_ns else 0
    
    event_class = cuda_event.get('eventClass', 0)
    device_id = cuda_event.get('deviceId', 0)
    stream_id = cuda_event.get('streamId', 0)
    context_id = cuda_event.get('contextId', 0)
    global_pid = cuda_event.get('globalPid', 0)
    
    category = "cuda"
    name = "CUDA Event"
    args = {
        "device_id": device_id,
        "stream_id": stream_id,
        "context_id": context_id,
        "event_class": event_class,
        "correlation_id": cuda_event.get('correlationId', 0)
    }
    
    if 'kernel' in cuda_event:
        kernel_data = cuda_event['kernel']
        category = "kernel"
        name = kernel_data.get('demangledName') or kernel_data.get('shortName') or kernel_data.get('mangledName')
        if not name:
            raise ValueError(f"Kernel missing name fields: {kernel_data}")
        args.update({
            "grid": [kernel_data.get('gridX', 1), kernel_data.get('gridY', 1), kernel_data.get('gridZ', 1)],
            "block": [kernel_data.get('blockX', 1), kernel_data.get('blockY', 1), kernel_data.get('blockZ', 1)],
            "shared_memory": kernel_data.get('sharedMemory', 0),
            "registers": kernel_data.get('registers', 0)
        })
    elif 'memcpy' in cuda_event:
        memcpy_data = cuda_event['memcpy']
        category = "memcpy"
        copy_kind = memcpy_data.get('copyKind')
        if not copy_kind:
            raise ValueError(f"Memcpy missing copyKind: {memcpy_data}")
        name = f"Memcpy ({copy_kind})"
        args.update({
            "size_bytes": memcpy_data.get('sizebytes', 0),
            "copy_kind": memcpy_data.get('copyKind'),
            "src_kind": memcpy_data.get('srcKind'),
            "dst_kind": memcpy_data.get('dstKind'),
            "copy_count": memcpy_data.get('copyCount', 1)
        })
    
    return {
        "cat": category,
        "name": name,
        "ph": "X",
        "ts": start_ns / 1000,
        "dur": duration_ns / 1000,
        "pid": int(global_pid) if global_pid else 0,
        "tid": stream_id,
        "args": args
    }


def convert_comm_event(comm_event: dict, string_map: dict) -> dict:
    """Convert NSYS CommEvent to Chrome trace format."""
    if 'Timestamp' not in comm_event:
        raise ValueError(f"CommEvent missing 'Timestamp': {comm_event}")
    if 'GlobalPid' not in comm_event:
        raise ValueError(f"CommEvent missing 'GlobalPid': {comm_event}")
    if 'Commname' not in comm_event:
        raise ValueError(f"CommEvent missing 'Commname': {comm_event}")
    
    timestamp_ns = comm_event['Timestamp']
    global_pid = comm_event['GlobalPid']
    commname = comm_event['Commname']
    
    return {
        "cat": "metadata",
        "name": "thread_name",
        "ph": "M",
        "ts": timestamp_ns / 1000,
        "pid": int(global_pid) if global_pid else 0,
        "tid": int(global_pid) if global_pid else 0,
        "args": {
            "name": commname
        }
    }


def convert_trace_event(trace_event: dict, string_map: dict) -> dict:
    """Convert NSYS TraceProcessEvent to Chrome trace format."""
    if 'startNs' not in trace_event:
        raise ValueError(f"TraceEvent missing 'startNs': {trace_event}")
    if 'name' not in trace_event:
        raise ValueError(f"TraceEvent missing 'name': {trace_event}")
    
    start_ns = int(trace_event['startNs'] or 0)
    end_ns = int(trace_event.get('endNs', start_ns) or start_ns)
    duration_ns = end_ns - start_ns if end_ns > start_ns else 0
    
    name_id = trace_event['name']
    name = string_map.get(name_id, f"Event_{name_id}") if isinstance(name_id, int) else str(name_id)
    global_tid = trace_event.get('globalTid', 0)
    event_class = trace_event.get('eventClass', 0)
    
    category = "cpu"
    if event_class in [3, 6, 8]:
        category = "nvtx"
    elif event_class in [1, 2]:
        category = "os_runtime"
    
    return {
        "cat": category,
        "name": name,
        "ph": "X" if duration_ns > 0 else "i",
        "ts": start_ns / 1000,
        "dur": duration_ns / 1000 if duration_ns > 0 else 0,
        "pid": 0,
        "tid": int(global_tid) if global_tid else 0,
        "args": {
            "event_class": event_class,
            "correlation_id": trace_event.get('correlationId', 0),
            "nesting_level": trace_event.get('nestingLevel', 0)
        }
    }


def convert_diagnostic_event(diag_event: dict, string_map: dict) -> dict:
    """Convert NSYS DiagnosticEvent to Chrome trace format."""
    if 'Source' not in diag_event:
        raise ValueError(f"DiagnosticEvent missing 'Source': {diag_event}")
    if 'Level' not in diag_event:
        raise ValueError(f"DiagnosticEvent missing 'Level': {diag_event}")
    if 'GlobalProcess' not in diag_event:
        raise ValueError(f"DiagnosticEvent missing 'GlobalProcess': {diag_event}")
    
    timestamp_obj = diag_event.get('Timestamp', {})
    timestamp_ns = int(timestamp_obj.get('ns', 0) or 0) if isinstance(timestamp_obj, dict) else 0
    text = diag_event.get('Text', '')
    source = diag_event['Source']
    level = diag_event['Level']
    global_process = diag_event['GlobalProcess']
    
    is_overhead = is_profiler_overhead_event(source, text)
    
    return {
        "cat": "diagnostic",
        "name": f"[{level}] {source}",
        "ph": "i",
        "ts": timestamp_ns / 1000,
        "pid": int(global_process) if global_process else 0,
        "tid": 0,
        "args": {
            "text": text,
            "source": source,
            "level": level,
            "is_overhead": is_overhead
        }
    }


def is_profiler_overhead_event(source: str, text: str) -> bool:
    """Determine if a diagnostic event represents profiler overhead."""
    if "CUPTI" in text or "cupti" in text.lower():
        return True
    
    if source == "Injection":
        return True
    
    overhead_keywords = [
        "profiler",
        "injection",
        "instrumentation",
        "trace data",
        "buffers holding"
    ]
    
    text_lower = text.lower()
    for keyword in overhead_keywords:
        if keyword in text_lower:
            return True
    
    return False
