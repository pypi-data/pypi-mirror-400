"""
Minimal GPU provisioning for wafer.

Supports:
- RunPod (NVIDIA GPUs)
- DigitalOcean AMD Developer Cloud (AMD MI300X)

Provides just the hotpaths:
1. Provision a GPU instance
2. Wait for SSH
3. Execute commands (sync and streaming)
4. Push code via rsync
5. Terminate

Usage:
    from wafer_core.gpu import provision_gpu, GPUInstance

    # RunPod (NVIDIA)
    instance = provision_gpu(
        gpu_type="A100",
        api_key=os.environ["RUNPOD_API_KEY"],
    )
    
    # DigitalOcean AMD
    instance = provision_gpu(
        gpu_type="MI300X",
        api_key=os.environ["AMD_DIGITALOCEAN_API_KEY"],
        provider="digitalocean_amd",
    )
    
    try:
        instance.wait_until_ssh_ready()
        
        # Push code
        workspace = instance.push("./my_project", "~/.wafer/workspace")
        
        # Run commands
        result = instance.exec("nvidia-smi")  # or rocm-smi for AMD
        print(result.stdout)
        
        # Stream output
        for line in instance.exec_stream("python train.py"):
            print(line)
    finally:
        instance.terminate()
"""

from __future__ import annotations

import logging
import os
import shlex
import stat
import subprocess
import tempfile
import time
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

import paramiko
import requests

logger = logging.getLogger(__name__)

RUNPOD_API_URL = "https://api.runpod.io/graphql"


# =============================================================================
# Data Types
# =============================================================================


class InstanceStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    FAILED = "failed"


@dataclass
class SSHResult:
    """Result of SSH command execution."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int


@dataclass
class GPUInstance:
    """A provisioned GPU instance."""

    id: str
    status: InstanceStatus
    gpu_type: str
    gpu_count: int
    price_per_hour: float
    name: str | None = None
    public_ip: str | None = None
    ssh_port: int | None = None
    ssh_username: str | None = None
    api_key: str | None = None
    _provider: str = "runpod"  # "runpod" or "digitalocean_amd"

    def ssh_connection_string(self) -> str:
        """Get SSH connection string (user@host:port)."""
        if not self.public_ip or not self.ssh_username:
            raise ValueError("SSH details not available")
        return f"{self.ssh_username}@{self.public_ip}:{self.ssh_port}"

    def exec(
        self,
        command: str,
        ssh_key_path: str | None = None,
        timeout: int = 30,
        working_dir: str | None = None,
    ) -> SSHResult:
        """Execute command via SSH.
        
        Args:
            command: Command to execute
            ssh_key_path: Path to SSH private key
            timeout: Command timeout in seconds
            working_dir: Working directory (optional)
        """
        if not self.public_ip or not self.ssh_username:
            raise ValueError("SSH details not available - instance may not be running")

        # Load SSH key
        key_content = None
        if ssh_key_path:
            with open(os.path.expanduser(ssh_key_path)) as f:
                key_content = f.read()

        # Wrap command with cd if working_dir specified
        if working_dir:
            command = f"cd {shlex.quote(working_dir)} && {command}"

        exit_code, stdout, stderr = _ssh_exec(
            hostname=self.public_ip,
            port=self.ssh_port or 22,
            username=self.ssh_username,
            command=command,
            key_content=key_content,
            timeout=timeout,
        )

        return SSHResult(
            success=exit_code == 0,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )

    def exec_stream(
        self,
        command: str,
        ssh_key_path: str | None = None,
        working_dir: str | None = None,
    ) -> Iterator[str]:
        """Execute command and stream output line by line.
        
        Args:
            command: Command to execute
            ssh_key_path: Path to SSH private key  
            working_dir: Working directory (optional)
            
        Yields:
            Lines of output as they're produced
        """
        if not self.public_ip or not self.ssh_username:
            raise ValueError("SSH details not available - instance may not be running")

        # Wrap command with cd if working_dir specified
        if working_dir:
            command = f"cd {shlex.quote(working_dir)} && {command}"

        # Load SSH key
        key_content = None
        if ssh_key_path:
            with open(os.path.expanduser(ssh_key_path)) as f:
                key_content = f.read()

        yield from _ssh_exec_stream(
            hostname=self.public_ip,
            port=self.ssh_port or 22,
            username=self.ssh_username,
            command=command,
            key_content=key_content,
        )

    def push(
        self,
        local_path: str,
        remote_path: str,
        ssh_key_path: str | None = None,
        exclude: list[str] | None = None,
    ) -> str:
        """Push local directory to remote via rsync.
        
        Args:
            local_path: Local directory to push
            remote_path: Remote destination path
            ssh_key_path: Path to SSH private key
            exclude: Patterns to exclude (e.g., [".git", "__pycache__", ".venv"])
            
        Returns:
            Absolute path to remote directory
        """
        if not self.public_ip or not self.ssh_username:
            raise ValueError("SSH details not available - instance may not be running")

        local_path = os.path.expanduser(local_path)
        if not os.path.isdir(local_path):
            raise ValueError(f"Local path is not a directory: {local_path}")

        # Default excludes
        if exclude is None:
            exclude = [".git", "__pycache__", ".venv", "*.pyc", ".ruff_cache"]

        # Build rsync command
        ssh_cmd = f"ssh -p {self.ssh_port or 22}"
        if ssh_key_path:
            ssh_cmd += f" -i {os.path.expanduser(ssh_key_path)}"
        ssh_cmd += " -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

        rsync_cmd = [
            "rsync",
            "-avz",
            "--delete",
            "-e", ssh_cmd,
        ]

        for pattern in exclude:
            rsync_cmd.extend(["--exclude", pattern])

        # Ensure local_path ends with / to copy contents
        if not local_path.endswith("/"):
            local_path += "/"

        rsync_cmd.append(local_path)
        rsync_cmd.append(f"{self.ssh_username}@{self.public_ip}:{remote_path}")

        # Create remote directory first
        self.exec(f"mkdir -p {remote_path}", ssh_key_path=ssh_key_path)

        # Run rsync
        result = subprocess.run(rsync_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"rsync failed: {result.stderr}")

        # Expand remote path to absolute
        expand_result = self.exec(f"echo {remote_path}", ssh_key_path=ssh_key_path)
        if expand_result.success:
            return expand_result.stdout.strip()
        return remote_path

    def wait_until_ssh_ready(self, timeout: int = 900) -> bool:
        """Wait until SSH is ready."""
        assert self.api_key, "Instance missing API key"

        if self._provider == "digitalocean_amd":
            return self._wait_ssh_digitalocean(timeout)
        return self._wait_ssh_runpod(timeout)

    def _wait_ssh_digitalocean(self, timeout: int) -> bool:
        """DigitalOcean AMD SSH wait - simpler, just wait for IP."""
        start_time = time.time()

        logger.debug(f"Waiting for DO AMD droplet {self.id}...")
        while time.time() - start_time < timeout:
            fresh = _do_amd_get_instance(self.id, self.api_key)
            if not fresh:
                logger.error("Droplet disappeared")
                return False

            if fresh.status == InstanceStatus.RUNNING and fresh.public_ip:
                self._update_from(fresh)
                elapsed = int(time.time() - start_time)
                logger.debug(f"Droplet ready: {self.public_ip} ({elapsed}s)")
                
                # Wait for SSH daemon
                logger.debug("Waiting 15s for SSH daemon...")
                time.sleep(15)
                return True

            elif fresh.status in [InstanceStatus.FAILED, InstanceStatus.TERMINATED]:
                logger.error(f"Droplet terminal state: {fresh.status}")
                return False

            time.sleep(10)

        logger.error(f"Timeout after {timeout}s")
        return False

    def _wait_ssh_runpod(self, timeout: int) -> bool:
        """RunPod SSH wait - needs to wait for direct SSH (not proxy)."""
        start_time = time.time()

        # Phase 1: Wait for RUNNING status
        logger.debug(f"Waiting for instance {self.id} to reach RUNNING...")
        while time.time() - start_time < timeout:
            fresh = _get_instance(self.id, self.api_key)
            if not fresh:
                logger.error("Instance disappeared")
                return False

            if fresh.status == InstanceStatus.RUNNING:
                self._update_from(fresh)
                logger.info(f"Instance {self.id} is RUNNING")
                break
            elif fresh.status in [InstanceStatus.FAILED, InstanceStatus.TERMINATED]:
                logger.error(f"Instance terminal state: {fresh.status}")
                return False

            time.sleep(15)
        else:
            logger.error(f"Timeout waiting for RUNNING after {timeout}s")
            return False

        # Phase 2: Wait for direct SSH (RunPod-specific, takes 5-15 min)
        logger.debug("Waiting for direct SSH assignment...")
        while time.time() - start_time < timeout:
            fresh = _get_instance(self.id, self.api_key)
            if fresh and fresh.public_ip and fresh.public_ip != "ssh.runpod.io":
                self._update_from(fresh)
                elapsed = int(time.time() - start_time)
                logger.debug(f"Direct SSH ready: {self.public_ip}:{self.ssh_port} ({elapsed}s)")
                break

            time.sleep(10)
        else:
            logger.error("Timeout waiting for direct SSH")
            return False

        # Phase 3: Wait for SSH daemon and test connectivity
        logger.debug("Waiting 30s for SSH daemon startup...")
        time.sleep(30)

        try:
            result = self.exec("echo 'ssh_ready'", timeout=30)
            if result.success and "ssh_ready" in result.stdout:
                logger.debug("SSH connectivity confirmed!")
                return True
            else:
                logger.warning(f"SSH test failed: {result.stderr}")
                return False
        except Exception as e:
            logger.exception(f"SSH connection error: {e}")
            return False

    def terminate(self) -> bool:
        """Terminate this instance."""
        if not self.api_key:
            raise ValueError("Cannot terminate: no API key")
        if self._provider == "digitalocean_amd":
            return _do_amd_terminate(self.id, self.api_key)
        return _terminate_instance(self.id, self.api_key)

    def _update_from(self, other: GPUInstance) -> None:
        """Update this instance with data from another."""
        self.status = other.status
        self.public_ip = other.public_ip
        self.ssh_port = other.ssh_port
        self.ssh_username = other.ssh_username
        self.gpu_type = other.gpu_type
        self.price_per_hour = other.price_per_hour


# =============================================================================
# SSH Helpers
# =============================================================================


@contextmanager
def _secure_temp_key(key_content: str) -> Generator[str, None, None]:
    """Create a temporary SSH key file with secure permissions."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
            f.write(key_content)
            temp_path = f.name
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 600
        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def _ssh_exec(
    hostname: str,
    port: int,
    username: str,
    command: str,
    key_content: str | None = None,
    timeout: int = 30,
) -> tuple[int, str, str]:
    """Execute SSH command using paramiko."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Try SSH agent first
        try:
            client.connect(
                hostname=hostname,
                port=port,
                username=username,
                timeout=timeout,
                look_for_keys=True,
                allow_agent=True,
            )
        except Exception:
            # Fallback to key file
            if key_content:
                with _secure_temp_key(key_content) as key_path:
                    client.connect(
                        hostname=hostname,
                        port=port,
                        username=username,
                        key_filename=key_path,
                        timeout=timeout,
                        look_for_keys=False,
                        allow_agent=False,
                    )
            else:
                raise

        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()

    except Exception as e:
        return -1, "", str(e)
    finally:
        client.close()


def _ssh_exec_stream(
    hostname: str,
    port: int,
    username: str,
    command: str,
    key_content: str | None = None,
) -> Iterator[str]:
    """Execute SSH command and stream output line by line."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Try SSH agent first
        try:
            client.connect(
                hostname=hostname,
                port=port,
                username=username,
                timeout=30,
                look_for_keys=True,
                allow_agent=True,
            )
        except Exception:
            # Fallback to key file
            if key_content:
                with _secure_temp_key(key_content) as key_path:
                    client.connect(
                        hostname=hostname,
                        port=port,
                        username=username,
                        key_filename=key_path,
                        timeout=30,
                        look_for_keys=False,
                        allow_agent=False,
                    )
            else:
                raise

        # Use a channel for streaming
        transport = client.get_transport()
        if transport is None:
            raise RuntimeError("SSH transport not available")

        channel = transport.open_session()
        channel.set_combine_stderr(True)
        channel.get_pty()
        channel.exec_command(command)

        buffer = ""
        while True:
            if channel.recv_ready():
                chunk = channel.recv(4096)
                if not chunk:
                    break
                text = chunk.decode(errors="replace")
                buffer += text

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    yield line.rstrip("\r")
                continue

            if channel.exit_status_ready():
                break

            time.sleep(0.1)

        # Drain remaining data
        while channel.recv_ready():
            chunk = channel.recv(4096)
            if not chunk:
                break
            text = chunk.decode(errors="replace")
            buffer += text
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line.rstrip("\r")

        if buffer:
            yield buffer.rstrip("\r")

        channel.close()

    finally:
        client.close()


# =============================================================================
# RunPod API
# =============================================================================


def _graphql(query: str, variables: dict | None = None, api_key: str | None = None) -> dict:
    """Make GraphQL request to RunPod."""
    if not api_key:
        raise ValueError("RunPod API key required")

    resp = requests.post(
        RUNPOD_API_URL,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=(10, 30),
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")

    return data["data"]


def _get_instance(instance_id: str, api_key: str) -> GPUInstance | None:
    """Get instance details from RunPod."""
    query = """
    query pod($input: PodFilter!) {
        pod(input: $input) {
            id
            name
            desiredStatus
            gpuCount
            costPerHr
            machine {
                podHostId
                gpuType { displayName }
            }
            runtime {
                ports {
                    ip
                    isIpPublic
                    privatePort
                    publicPort
                    type
                }
            }
        }
    }
    """

    try:
        data = _graphql(query, {"input": {"podId": instance_id}}, api_key)
        pod = data.get("pod")
        if not pod:
            return None

        # Extract SSH info
        public_ip, ssh_port, ssh_username = None, None, None

        # Try direct SSH first
        runtime = pod.get("runtime") or {}
        for port in runtime.get("ports") or []:
            if port.get("privatePort") == 22 and port.get("isIpPublic") and port.get("type") == "tcp":
                public_ip = port.get("ip")
                ssh_port = port.get("publicPort")
                ssh_username = "root"
                break

        # Fallback to proxy SSH
        if not public_ip:
            machine = pod.get("machine") or {}
            pod_host_id = machine.get("podHostId")
            if pod_host_id:
                public_ip = "ssh.runpod.io"
                ssh_port = 22
                ssh_username = pod_host_id

        # Extract GPU type
        gpu_type = "unknown"
        machine = pod.get("machine") or {}
        gpu_type_obj = machine.get("gpuType") or {}
        if gpu_type_obj.get("displayName"):
            gpu_type = gpu_type_obj["displayName"]

        # Map status
        status_map = {
            "RUNNING": InstanceStatus.RUNNING,
            "PENDING": InstanceStatus.PENDING,
            "STOPPED": InstanceStatus.STOPPED,
            "TERMINATED": InstanceStatus.TERMINATED,
            "FAILED": InstanceStatus.FAILED,
        }
        status = status_map.get(pod.get("desiredStatus", ""), InstanceStatus.PENDING)

        return GPUInstance(
            id=pod["id"],
            status=status,
            gpu_type=gpu_type,
            gpu_count=pod.get("gpuCount", 0),
            price_per_hour=pod.get("costPerHr", 0.0),
            name=pod.get("name"),
            public_ip=public_ip,
            ssh_port=ssh_port,
            ssh_username=ssh_username,
            api_key=api_key,
        )

    except Exception as e:
        logger.exception(f"Failed to get instance: {e}")
        return None


def _terminate_instance(instance_id: str, api_key: str) -> bool:
    """Terminate a RunPod instance."""
    mutation = """
    mutation podTerminate($input: PodTerminateInput!) {
        podTerminate(input: $input)
    }
    """

    try:
        _graphql(mutation, {"input": {"podId": instance_id}}, api_key)
        return True
    except Exception as e:
        logger.exception(f"Failed to terminate: {e}")
        return False


# =============================================================================
# DigitalOcean AMD API
# =============================================================================

DIGITALOCEAN_AMD_API_URL = "https://api-amd.digitalocean.com/v2"


def _do_amd_request(
    method: str,
    endpoint: str,
    api_key: str,
    data: dict | None = None,
) -> dict:
    """Make REST API request to DigitalOcean AMD."""
    resp = requests.request(
        method=method,
        url=f"{DIGITALOCEAN_AMD_API_URL}{endpoint}",
        json=data,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=(10, 30),
    )
    
    if not resp.ok:
        # Try to get error message from response
        try:
            err_data = resp.json()
            err_msg = err_data.get("message", resp.text)
        except Exception:
            err_msg = resp.text
        raise requests.HTTPError(f"{resp.status_code}: {err_msg}", response=resp)
    
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def _do_amd_get_instance(instance_id: str, api_key: str) -> GPUInstance | None:
    """Get DigitalOcean AMD droplet details."""
    try:
        resp = _do_amd_request("GET", f"/droplets/{instance_id}", api_key)
        droplet = resp.get("droplet")
        if not droplet:
            return None

        # Map status
        status_map = {
            "new": InstanceStatus.PENDING,
            "active": InstanceStatus.RUNNING,
            "off": InstanceStatus.STOPPED,
            "archive": InstanceStatus.TERMINATED,
        }
        status = status_map.get(droplet.get("status", "new"), InstanceStatus.PENDING)

        # Get public IP
        public_ip = None
        for net in droplet.get("networks", {}).get("v4", []):
            if net.get("type") == "public":
                public_ip = net.get("ip_address")
                break

        # Get GPU info
        size = droplet.get("size", {})
        gpu_info = size.get("gpu_info", {})
        gpu_count = gpu_info.get("count", 1)
        gpu_model = gpu_info.get("model", "unknown")
        
        # Normalize GPU name
        gpu_names = {"amd_mi300x": "MI300X", "amd_mi325x": "MI325X"}
        gpu_type = gpu_names.get(gpu_model, gpu_model)

        return GPUInstance(
            id=str(droplet["id"]),
            status=status,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            price_per_hour=size.get("price_hourly", 0.0),
            name=droplet.get("name"),
            public_ip=public_ip,
            ssh_port=22,
            ssh_username="root",
            api_key=api_key,
            _provider="digitalocean_amd",
        )

    except Exception as e:
        logger.exception(f"Failed to get DO AMD instance: {e}")
        return None


def _do_amd_terminate(instance_id: str, api_key: str) -> bool:
    """Terminate DigitalOcean AMD droplet."""
    try:
        _do_amd_request("DELETE", f"/droplets/{instance_id}", api_key)
        return True
    except Exception as e:
        logger.exception(f"Failed to terminate DO AMD: {e}")
        return False


def _do_amd_provision(
    gpu_type: str,
    api_key: str,
    name: str | None = None,
    region: str = "atl1",  # Atlanta - only region with MI300X
) -> GPUInstance:
    """Provision DigitalOcean AMD GPU droplet."""
    # Map friendly names to size slugs
    size_map = {
        "MI300X": "gpu-h100x1-80gb",  # Actually MI300X despite the name
        "mi300x": "gpu-h100x1-80gb",
    }
    
    size_slug = size_map.get(gpu_type)
    if not size_slug:
        # Try as direct slug
        size_slug = gpu_type if gpu_type.startswith("gpu-") else f"gpu-{gpu_type}"

    # Get SSH keys from account
    ssh_key_ids = []
    try:
        keys_resp = _do_amd_request("GET", "/account/keys", api_key)
        ssh_key_ids = [k["id"] for k in keys_resp.get("ssh_keys", [])]
    except Exception as e:
        logger.warning(f"Failed to fetch SSH keys: {e}")

    instance_name = name or f"wafer-amd-{int(time.time())}"

    create_data = {
        "name": instance_name,
        "region": region,
        "size": size_slug,
        "image": "gpu-amd-base",  # AMD AI/ML Ready image with ROCm
        "ssh_keys": ssh_key_ids,
        "backups": False,
        "ipv6": True,
        "monitoring": True,
    }

    try:
        resp = _do_amd_request("POST", "/droplets", api_key, data=create_data)
        droplet = resp.get("droplet")
        
        if not droplet:
            raise Exception("No droplet returned")

        return GPUInstance(
            id=str(droplet["id"]),
            status=InstanceStatus.PENDING,
            gpu_type=gpu_type,
            gpu_count=1,
            price_per_hour=0.0,
            name=instance_name,
            api_key=api_key,
            _provider="digitalocean_amd",
        )

    except Exception as e:
        raise Exception(f"Failed to provision DO AMD: {e}") from e


# =============================================================================
# Public API
# =============================================================================


def provision_gpu(
    gpu_type: str,
    api_key: str,
    gpu_count: int = 1,
    image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
    name: str | None = None,
    container_disk_gb: int = 50,
    secure: bool = True,
    provider: str = "runpod",
    region: str = "tor1",
) -> GPUInstance:
    """
    Provision a GPU instance.

    Args:
        gpu_type: GPU type (e.g., "A100", "H100", "4090", "MI300X")
        api_key: Provider API key
        gpu_count: Number of GPUs (RunPod only)
        image: Docker image (RunPod only)
        name: Instance name
        container_disk_gb: Container disk size in GB (RunPod only)
        secure: Use secure cloud (RunPod only)
        provider: "runpod" or "digitalocean_amd"
        region: Region for DigitalOcean AMD (default: "atl1" - Atlanta)

    Returns:
        GPUInstance ready for use

    Raises:
        Exception: If provisioning fails

    Example:
        # RunPod (NVIDIA)
        instance = provision_gpu("A100", os.environ["RUNPOD_API_KEY"])
        
        # DigitalOcean AMD
        instance = provision_gpu(
            "MI300X",
            os.environ["AMD_DIGITALOCEAN_API_KEY"],
            provider="digitalocean_amd",
        )
    """
    if provider == "digitalocean_amd":
        return _do_amd_provision(gpu_type, api_key, name=name, region=region)

    # Default: RunPod
    mutation = """
    mutation podFindAndDeployOnDemand($input: PodFindAndDeployOnDemandInput!) {
        podFindAndDeployOnDemand(input: $input) {
            id
            machineId
        }
    }
    """

    pod_input = {
        "gpuCount": gpu_count,
        "gpuTypeId": gpu_type,
        "cloudType": "SECURE" if secure else "COMMUNITY",
        "name": name or f"wafer-{gpu_type}-{int(time.time())}",
        "imageName": image,
        "containerDiskInGb": container_disk_gb,
        "supportPublicIp": True,
        "startSsh": True,
        "ports": "22/tcp",
        "minVcpuCount": 1,
        "minMemoryInGb": 4,
    }

    try:
        data = _graphql(mutation, {"input": pod_input}, api_key)
        pod = data.get("podFindAndDeployOnDemand")

        if not pod:
            raise Exception("No pod returned from deployment")

        return GPUInstance(
            id=pod["id"],
            status=InstanceStatus.PENDING,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            price_per_hour=0.0,
            name=name,
            api_key=api_key,
            _provider="runpod",
        )

    except Exception as e:
        raise Exception(f"Failed to provision GPU: {e}") from e


def get_gpu(instance_id: str, api_key: str, provider: str = "runpod") -> GPUInstance | None:
    """
    Get an existing GPU instance by ID.

    Args:
        instance_id: Instance ID
        api_key: Provider API key
        provider: "runpod" or "digitalocean_amd"

    Returns:
        GPUInstance or None if not found
    """
    if provider == "digitalocean_amd":
        return _do_amd_get_instance(instance_id, api_key)
    return _get_instance(instance_id, api_key)
