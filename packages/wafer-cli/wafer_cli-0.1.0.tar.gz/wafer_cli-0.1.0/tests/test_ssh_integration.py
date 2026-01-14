"""Integration tests for SSH connectivity and Docker/GPU access.

Tests SSH connection, Docker availability, and GPU accessibility.
"""

import shlex
from pathlib import Path

import pytest

from wafer_core.ssh import SSHClient

# Constants
VULTR_TARGET = "chiraag@45.76.244.62:22"
SSH_KEY = "~/.ssh/id_ed25519"


def _check_ssh_available() -> None:
    """Check if SSH credentials are available and skip test if not."""
    ssh_key_path = Path(SSH_KEY).expanduser()
    if not ssh_key_path.exists():
        pytest.skip(f"SSH key not found: {SSH_KEY}")
    
    # Try to connect and skip if authentication fails
    try:
        client = SSHClient(VULTR_TARGET, SSH_KEY)
        # Try a simple command to verify connectivity
        result = client.exec("echo test")
        if result.exit_code != 0:
            pytest.skip(f"SSH connection failed: {VULTR_TARGET}")
    except Exception as e:
        pytest.skip(f"SSH connection unavailable: {e}")

DOCKER_GROUP_NAME = "docker"
DOCKER_COMMAND = "docker"
DOCKER_VERSION_COMMAND = "docker --version"
DOCKER_VERSION_PREFIX = "Docker version"

TEST_MESSAGE = "wafer integration test"
ECHO_COMMAND = f"echo '{TEST_MESSAGE}'"

CUDA_BASE_IMAGE = "nvidia/cuda:12.6.0-base-ubuntu22.04"
GPU_QUERY_COMMAND = "nvidia-smi --query-gpu=name --format=csv,noheader"
ALL_GPUS = "all"


def _build_docker_cmd(
    image: str,
    command: str,
    volumes: dict[str, str] | None = None,
    working_dir: str | None = None,
    gpus: str | None = None,
) -> str:
    """Build docker run command string."""
    assert image is not None
    assert command is not None
    
    parts = [DOCKER_COMMAND, "run", "--rm"]
    
    if gpus is not None:
        parts.extend(["--gpus", f"'{gpus}'"])
    
    if volumes is not None:
        for host_path, container_path in volumes.items():
            parts.extend(["-v", f"{host_path}:{container_path}"])
    
    if working_dir is not None:
        parts.extend(["-w", working_dir])
    
    parts.append(image)
    parts.append(f"bash -c {shlex.quote(command)}")
    
    cmd_str = " ".join(parts)
    assert len(cmd_str) > 0
    return cmd_str


def test_ssh_connectivity() -> None:
    """Test basic SSH connectivity to B200 node."""
    _check_ssh_available()
    
    client = SSHClient(VULTR_TARGET, SSH_KEY)
    result = client.exec(ECHO_COMMAND)
    
    assert result.exit_code == 0
    assert result.stdout is not None
    assert TEST_MESSAGE in result.stdout


def test_docker_available() -> None:
    """Test Docker is installed and accessible."""
    _check_ssh_available()
    
    client = SSHClient(VULTR_TARGET, SSH_KEY)
    result = client.exec(DOCKER_VERSION_COMMAND)
    
    assert result.exit_code == 0
    assert result.stdout is not None
    assert DOCKER_VERSION_PREFIX in result.stdout


def test_gpu_accessible() -> None:
    """Test GPU is accessible from Docker."""
    _check_ssh_available()
    
    client = SSHClient(VULTR_TARGET, SSH_KEY)
    
    groups_result = client.exec("groups")
    assert groups_result.exit_code == 0
    assert groups_result.stdout is not None
    
    has_docker_group = DOCKER_GROUP_NAME in groups_result.stdout
    
    if not has_docker_group:
        groups = groups_result.stdout.strip()
        pytest.fail(
            f"User must be in '{DOCKER_GROUP_NAME}' group. Current groups: {groups}\n"
            f"Fix: SSH to {VULTR_TARGET} and run:\n"
            f"  sudo usermod -aG {DOCKER_GROUP_NAME} chiraag\n"
            f"Then logout and login for changes to take effect."
        )
    
    docker_cmd = _build_docker_cmd(
        image=CUDA_BASE_IMAGE,
        command=GPU_QUERY_COMMAND,
        gpus=ALL_GPUS,
    )
    
    result = client.exec(docker_cmd)
    assert result.exit_code == 0
    assert result.stdout is not None
    
    stdout_stripped = result.stdout.strip()
    assert len(stdout_stripped) > 0
