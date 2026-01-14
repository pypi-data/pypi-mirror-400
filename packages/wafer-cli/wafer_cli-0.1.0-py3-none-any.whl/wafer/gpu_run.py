"""Remote execution on GPU targets.

Provides push/run primitives for remote GPU execution via SSH and Docker.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

from wafer_core.ssh import SSHClient
from wafer_core.utils.kernel_utils.targets.config import BaremetalTarget, VMTarget

# Constants
REMOTE_WORKSPACE_BASE = "~/.wafer/workspaces"
CONTAINER_WORKSPACE = "/workspace"


@dataclass(frozen=True)
class PushResult:
    """Result of pushing a directory to remote target."""

    workspace_path: str  # Absolute path on remote (tilde-expanded)
    files_uploaded: list[str]  # Relative paths of uploaded files


def push_directory(
    local_path: Path,
    target: BaremetalTarget | VMTarget,
) -> PushResult:
    """Push local directory to remote target.

    Uploads directory to ~/.wafer/workspaces/<dirname> on target.

    Args:
        local_path: Local directory to upload
        target: Remote target configuration

    Returns:
        PushResult with workspace path and list of uploaded files

    Raises:
        FileNotFoundError: If local_path doesn't exist
        ValueError: If local_path is not a directory
    """
    # Validate inputs
    if not local_path.exists():
        raise FileNotFoundError(f"Path not found: {local_path}")
    if not local_path.is_dir():
        raise ValueError(f"Not a directory: {local_path}")
    if target.ssh_target is None:
        raise ValueError(f"Target '{target.name}' must have ssh_target configured")
    if target.ssh_key is None:
        raise ValueError(f"Target '{target.name}' must have ssh_key configured")

    client = SSHClient(target.ssh_target, target.ssh_key)

    workspace_name = local_path.name
    remote_workspace = f"{REMOTE_WORKSPACE_BASE}/{workspace_name}"

    # Create workspace directory
    client.exec(f"mkdir -p {remote_workspace}")
    expanded_workspace = client.expand_path(remote_workspace)

    # Upload directory recursively
    client.upload_files(str(local_path), expanded_workspace, recursive=True)

    # Get list of uploaded files (relative paths)
    files_uploaded = []
    for file in local_path.rglob("*"):
        if file.is_file():
            files_uploaded.append(str(file.relative_to(local_path)))

    return PushResult(
        workspace_path=expanded_workspace,
        files_uploaded=files_uploaded,
    )


def run_command(
    command: str,
    workspace: str,
    target: BaremetalTarget | VMTarget,
    gpu_id: int | None = None,
) -> int:
    """Run command in Docker on remote target, streaming output.

    Args:
        command: Command to execute inside container
        workspace: Workspace name (subdirectory under ~/.wafer/workspaces/)
        target: Remote target configuration (must have docker_image)
        gpu_id: GPU ID to use (defaults to first in target.gpu_ids)

    Returns:
        Exit code from command (0 = success)

    Raises:
        ValueError: If target is missing required configuration
    """
    if target.docker_image is None:
        raise ValueError(f"Target '{target.name}' must have docker_image configured")
    if target.ssh_target is None:
        raise ValueError(f"Target '{target.name}' must have ssh_target configured")
    if target.ssh_key is None:
        raise ValueError(f"Target '{target.name}' must have ssh_key configured")

    client = SSHClient(target.ssh_target, target.ssh_key)

    effective_gpu_id = gpu_id if gpu_id is not None else target.gpu_ids[0]

    # Get expanded workspace path
    remote_workspace = f"{REMOTE_WORKSPACE_BASE}/{workspace}"
    expanded_workspace = client.expand_path(remote_workspace)

    # Build docker command with workspace mounted
    volumes = {expanded_workspace: CONTAINER_WORKSPACE}
    docker_cmd = _build_docker_command(
        image=target.docker_image,
        inner_cmd=command,
        gpu_id=effective_gpu_id,
        volumes=volumes,
    )

    # Stream execution
    exit_code = 0
    try:
        for line in client.exec_stream(docker_cmd):
            print(line)
    except Exception as e:
        print(f"\nExecution failed: {e}", file=sys.stderr)
        exit_code = 1

    return exit_code


def run_command_capture(
    command: str,
    workspace: str,
    target: BaremetalTarget | VMTarget,
) -> tuple[int, str]:
    """Run command on remote target (without Docker) and capture output.

    This is useful for commands that don't need GPU access, like running
    NCU to analyze a profile file.

    Args:
        command: Command to execute on the remote host
        workspace: Workspace name (subdirectory under ~/.wafer/workspaces/)
        target: Remote target configuration

    Returns:
        Tuple of (exit_code, output_text)

    Raises:
        ValueError: If target is missing required configuration
    """
    if target.ssh_target is None:
        raise ValueError(f"Target '{target.name}' must have ssh_target configured")
    if target.ssh_key is None:
        raise ValueError(f"Target '{target.name}' must have ssh_key configured")

    client = SSHClient(target.ssh_target, target.ssh_key)

    # Get expanded workspace path
    remote_workspace = f"{REMOTE_WORKSPACE_BASE}/{workspace}"
    expanded_workspace = client.expand_path(remote_workspace)

    # Run command in workspace directory
    full_cmd = f"cd {expanded_workspace} && {command}"

    # Capture output
    output_lines = []
    exit_code = 0
    try:
        for line in client.exec_stream(full_cmd):
            output_lines.append(line)
    except Exception as e:
        print(f"\nExecution failed: {e}", file=sys.stderr)
        exit_code = 1

    return exit_code, "\n".join(output_lines)


def _build_docker_command(
    image: str,
    inner_cmd: str,
    gpu_id: int,
    volumes: dict[str, str],
) -> str:
    """Build docker run command string."""
    import shlex

    parts = ["docker", "run", "--rm"]
    parts.extend(["--gpus", f"'device={gpu_id}'"])

    for host_path, container_path in volumes.items():
        parts.extend(["-v", f"{host_path}:{container_path}"])

    parts.extend(["-w", CONTAINER_WORKSPACE])
    parts.append(image)
    parts.append(f"bash -c {shlex.quote(inner_cmd)}")

    return " ".join(parts)


def _build_uv_install_cmd() -> str:
    """Build command to ensure uv is available."""
    ensure_curl = (
        "which curl > /dev/null 2>&1 || "
        "(apt-get update -qq && apt-get install -qq -y curl > /dev/null)"
    )
    install_uv = "which uv > /dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh"
    source_uv = "export PATH=$HOME/.local/bin:$PATH"
    return f"{ensure_curl} && {install_uv} && {source_uv}"


def run_python_docker(
    file_path: Path,
    args: list[str],
    target: BaremetalTarget | VMTarget,
    gpu_id: int,
) -> int:
    """Run Python file in Docker container on remote GPU."""
    if target.docker_image is None:
        raise ValueError(f"Target '{target.name}' must have docker_image configured")
    if target.ssh_target is None:
        raise ValueError(f"Target '{target.name}' must have ssh_target configured")
    if target.ssh_key is None:
        raise ValueError(f"Target '{target.name}' must have ssh_key configured")

    print(f"Connecting to {target.ssh_target}...")
    client = SSHClient(target.ssh_target, target.ssh_key)

    # Setup workspace
    remote_workspace = f"{REMOTE_WORKSPACE_BASE}/python_run"
    client.exec(f"mkdir -p {remote_workspace}")
    expanded_workspace = client.expand_path(remote_workspace)

    # Upload file
    remote_file = f"{expanded_workspace}/{file_path.name}"
    print(f"Uploading {file_path.name}...")
    client.upload_files(str(file_path), remote_file)

    # Build inner command: install uv, run script with inline deps
    script_args = " ".join(args) if args else ""
    uv_setup = _build_uv_install_cmd()
    inner_cmd = f"{uv_setup} && uv run --script {file_path.name} {script_args}"

    # Build docker command
    volumes = {expanded_workspace: CONTAINER_WORKSPACE}
    docker_cmd = _build_docker_command(
        image=target.docker_image,
        inner_cmd=inner_cmd,
        gpu_id=gpu_id,
        volumes=volumes,
    )

    print(f"Running on GPU {gpu_id} with {target.docker_image}...")
    print("-" * 60)

    # Stream execution
    exit_code = 0
    try:
        for line in client.exec_stream(docker_cmd):
            print(line)
    except Exception as e:
        print(f"\nExecution failed: {e}", file=sys.stderr)
        exit_code = 1

    return exit_code


def run_python_file(
    file_path: Path,
    args: list[str],
    target: BaremetalTarget | VMTarget,
    gpu_id: int | None = None,
) -> int:
    """Run Python file on remote GPU in Docker container.

    Args:
        file_path: Path to Python script
        args: Arguments to pass to script
        target: Remote target configuration (must have docker_image)
        gpu_id: GPU ID to use (defaults to first in target.gpu_ids)

    Returns:
        Exit code from script

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file or target has no docker_image
    """
    # Validate inputs
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if not target.docker_image:
        raise ValueError(f"Target '{target.name}' has no docker_image configured")

    effective_gpu_id = gpu_id if gpu_id is not None else target.gpu_ids[0]

    return run_python_docker(file_path, args, target, effective_gpu_id)
