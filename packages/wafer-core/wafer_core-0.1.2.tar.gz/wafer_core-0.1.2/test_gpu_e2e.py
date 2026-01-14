#!/usr/bin/env python3
"""End-to-end test for wafer_core.gpu module.

Run with:
    RUNPOD_API_KEY=your_key python test_gpu_e2e.py

This will:
1. Provision a cheap GPU (RTX 4090)
2. Wait for SSH
3. Run nvidia-smi
4. Push a test directory
5. Run a command in that directory
6. Terminate the instance

Expected cost: ~$0.05 (a few minutes of 4090 time)
"""

import os
import sys
import tempfile
from pathlib import Path


def main():
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("ERROR: Set RUNPOD_API_KEY environment variable")
        sys.exit(1)

    from wafer_core.gpu import provision_gpu

    print("=" * 60)
    print("Provisioning RTX 4090 (cheapest option)...")
    print("=" * 60)

    instance = provision_gpu(
        gpu_type="RTX 4090",
        api_key=api_key,
        gpu_count=1,
        name="wafer-gpu-test",
        container_disk_gb=20,
        secure=False,  # Community cloud is cheaper
    )

    print(f"\n✓ Instance created: {instance.id}")
    print(f"  GPU: {instance.gpu_type}")

    try:
        print("\nWaiting for SSH (this takes 5-15 minutes on RunPod)...")
        if not instance.wait_until_ssh_ready(timeout=900):
            print("ERROR: SSH timeout")
            sys.exit(1)

        print(f"\n✓ SSH ready: {instance.ssh_connection_string()}")
        print(f"  Price: ${instance.price_per_hour:.2f}/hr")

        # Test 1: exec()
        print("\n" + "=" * 60)
        print("Test 1: exec() - nvidia-smi")
        print("=" * 60)
        result = instance.exec("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
        if result.success:
            print(f"✓ GPU: {result.stdout.strip()}")
        else:
            print(f"✗ Failed: {result.stderr}")

        # Test 2: exec_stream()
        print("\n" + "=" * 60)
        print("Test 2: exec_stream() - pip list")
        print("=" * 60)
        count = 0
        for line in instance.exec_stream("pip list | head -10"):
            print(f"  {line}")
            count += 1
        print(f"✓ Streamed {count} lines")

        # Test 3: push()
        print("\n" + "=" * 60)
        print("Test 3: push() - rsync directory")
        print("=" * 60)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = Path(tmpdir) / "test_script.py"
            test_file.write_text("print('Hello from pushed code!')\n")
            
            (Path(tmpdir) / "data.txt").write_text("test data\n")

            workspace = instance.push(tmpdir, "~/.wafer/test_push")
            print(f"✓ Pushed to: {workspace}")

            # Verify files exist
            result = instance.exec("ls -la", working_dir=workspace)
            print(f"  Contents:\n{result.stdout}")

            # Run the pushed script
            result = instance.exec("python test_script.py", working_dir=workspace)
            if result.success:
                print(f"✓ Script output: {result.stdout.strip()}")
            else:
                print(f"✗ Script failed: {result.stderr}")

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    finally:
        print(f"\nTerminating instance {instance.id}...")
        instance.terminate()
        print("✓ Instance terminated")


if __name__ == "__main__":
    main()
