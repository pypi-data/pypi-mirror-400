"""NSYS discovery and installation checking."""

from __future__ import annotations

import os
import shutil
import subprocess


def find_nsys() -> str | None:
    """Find NSYS executable on the system."""
    nsys = shutil.which("nsys")
    if nsys:
        return nsys
    
    common_paths = [
        "/usr/local/cuda/bin/nsys",
        "/opt/nvidia/nsight-systems/nsys",
        "/usr/bin/nsys"
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None


def check_nsys() -> dict:
    """Check if NSYS is installed and return status."""
    nsys_path = find_nsys()
    
    if nsys_path:
        result = subprocess.run(
            [nsys_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        if not result.stdout:
            raise ValueError("NSYS --version returned no output")
        version = result.stdout.strip().split('\n')[0]
        return {
            "installed": True,
            "path": nsys_path,
            "version": version
        }
    else:
        return {
            "installed": False,
            "install_command": "Install NSYS from NVIDIA Nsight Systems"
        }
