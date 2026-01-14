"""Integration tests for file inference, upload, and streaming.

Tests file inference, upload to remote, and streaming output.
"""

import shlex
import tempfile
from pathlib import Path

import pytest

from wafer_core.ssh import SSHClient

from wafer.inference import infer_upload_files

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

WORKSPACE_BASE = "~/.wafer/workspaces"
TEST_WORKSPACE = f"{WORKSPACE_BASE}/wafer-integration-test"

CUDA_DEVEL_IMAGE = "nvidia/cuda:12.6.0-devel-ubuntu22.04"
UBUNTU_IMAGE = "ubuntu:22.04"
CONTAINER_WORKSPACE = "/workspace"
ALL_GPUS = "all"

KERNEL_CU_FILENAME = "test_kernel.cu"
MAKEFILE_FILENAME = "Makefile"
EXPECTED_CPU_OUTPUT = "Hello from CPU!"
EXPECTED_GPU_OUTPUT = "Hello from GPU!"

MIN_STREAM_LINES = 3
STREAM_LINE_PREFIX = "Line "


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
    
    parts = ["docker", "run", "--rm"]
    
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


def test_file_inference_and_upload() -> None:
    """Test file inference, upload, and execution."""
    _check_ssh_available()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        assert tmpdir_path.exists()

        kernel_cu = tmpdir_path / KERNEL_CU_FILENAME
        kernel_cu.write_text("""
#include <stdio.h>

__global__ void hello_kernel() {
    printf("Hello from GPU!\\n");
}

int main() {
    printf("Hello from CPU!\\n");
    hello_kernel<<<1, 1>>>();
    cudaDeviceSynchronize();
    return 0;
}
""")
        assert kernel_cu.exists()

        makefile = tmpdir_path / MAKEFILE_FILENAME
        makefile.write_text("""
all: test_kernel

test_kernel: test_kernel.cu
\tnvcc test_kernel.cu -o test_kernel

clean:
\trm -f test_kernel

.PHONY: all clean
""")
        assert makefile.exists()

        command = "make && ./test_kernel"
        inferred_files = infer_upload_files(command, tmpdir_path)
        
        assert kernel_cu in inferred_files
        assert makefile in inferred_files
        assert len(inferred_files) >= 2

        client = SSHClient(VULTR_TARGET, SSH_KEY)
        workspace = TEST_WORKSPACE

        mkdir_result = client.exec(f"mkdir -p {workspace}")
        assert mkdir_result.exit_code == 0
        
        expanded_workspace = client.expand_path(workspace)
        assert len(expanded_workspace) > 0

        for file_path in inferred_files:
            remote_path = f"{expanded_workspace}/{file_path.name}"
            upload_result = client.upload_files(str(file_path), remote_path)
            assert upload_result.success
            assert upload_result.error_message is not None

        list_cmd = f"ls -la {workspace}"
        verify_result = client.exec(list_cmd)
        assert verify_result.exit_code == 0
        assert verify_result.stdout is not None
        assert KERNEL_CU_FILENAME in verify_result.stdout
        assert MAKEFILE_FILENAME in verify_result.stdout

        docker_cmd = _build_docker_cmd(
            image=CUDA_DEVEL_IMAGE,
            command="ls -la && make && ./test_kernel",
            volumes={expanded_workspace: CONTAINER_WORKSPACE},
            working_dir=CONTAINER_WORKSPACE,
            gpus=ALL_GPUS,
        )
        
        exec_result = client.exec(docker_cmd)
        assert exec_result.exit_code == 0
        assert exec_result.stdout is not None
        assert EXPECTED_CPU_OUTPUT in exec_result.stdout
        assert EXPECTED_GPU_OUTPUT in exec_result.stdout

        cleanup_result = client.exec(f"rm -rf {workspace}")
        assert cleanup_result.exit_code == 0


def test_streaming_output() -> None:
    """Test streaming output works correctly."""
    _check_ssh_available()

    client = SSHClient(VULTR_TARGET, SSH_KEY)

    stream_command = "for i in 1 2 3; do echo 'Line '$i; sleep 0.1; done"
    docker_cmd = _build_docker_cmd(
        image=UBUNTU_IMAGE,
        command=stream_command,
    )
    assert len(docker_cmd) > 0

    lines = list(client.exec_stream(docker_cmd))
    assert len(lines) >= MIN_STREAM_LINES

    line_1_found = any(f"{STREAM_LINE_PREFIX}1" in line for line in lines)
    line_2_found = any(f"{STREAM_LINE_PREFIX}2" in line for line in lines)
    line_3_found = any(f"{STREAM_LINE_PREFIX}3" in line for line in lines)
    
    assert line_1_found
    assert line_2_found
    assert line_3_found
