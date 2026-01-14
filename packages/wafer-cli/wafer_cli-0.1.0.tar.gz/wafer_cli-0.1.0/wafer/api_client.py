"""Wafer API client for remote GPU operations.

Thin client that calls wafer-api endpoints instead of direct SSH.
"""

import base64
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

# Default API URL (can be overridden via environment variable)
DEFAULT_API_URL = "http://localhost:8000"


@dataclass(frozen=True)
class PushResult:
    """Result of pushing files to GPU."""

    workspace_id: str
    workspace_path: str
    files_uploaded: list[str]


@dataclass(frozen=True)
class ApiConfig:
    """API client configuration."""

    base_url: str = DEFAULT_API_URL
    timeout: float = 60.0


def get_api_url() -> str:
    """Get API URL from environment or default."""
    import os

    return os.environ.get("WAFER_API_URL", DEFAULT_API_URL)


def _get_auth_headers() -> dict[str, str]:
    """Get auth headers from stored credentials (lazy import to avoid circular)."""
    from .auth import get_auth_headers

    return get_auth_headers()


def push_directory(local_path: Path, workspace_name: str | None = None) -> PushResult:
    """Push local directory to GPU via wafer-api.

    Args:
        local_path: Local directory to upload
        workspace_name: Optional workspace name (defaults to directory name)

    Returns:
        PushResult with workspace_id and uploaded files

    Raises:
        FileNotFoundError: If local_path doesn't exist
        ValueError: If local_path is not a directory
        httpx.HTTPError: If API request fails
    """
    if not local_path.exists():
        raise FileNotFoundError(f"Path not found: {local_path}")
    if not local_path.is_dir():
        raise ValueError(f"Not a directory: {local_path}")

    # Collect files and encode as base64
    files = []
    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(local_path)
            content = file_path.read_bytes()
            files.append({
                "path": str(relative_path),
                "content": base64.b64encode(content).decode(),
            })

    # Build request
    request_body = {
        "files": files,
        "workspace_name": workspace_name or local_path.name,
    }

    # Call API
    api_url = get_api_url()
    headers = _get_auth_headers()
    with httpx.Client(timeout=60.0, headers=headers) as client:
        response = client.post(f"{api_url}/v1/gpu/push", json=request_body)
        response.raise_for_status()
        data = response.json()

    return PushResult(
        workspace_id=data["workspace_id"],
        workspace_path=data["workspace_path"],
        files_uploaded=data["files_uploaded"],
    )


def _collect_files(local_path: Path) -> list[dict]:
    """Collect files from directory as base64-encoded dicts."""
    files = []
    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(local_path)
            content = file_path.read_bytes()
            files.append({
                "path": str(relative_path),
                "content": base64.b64encode(content).decode(),
            })
    return files


def run_command_stream(
    command: str,
    upload_dir: Path | None = None,
    workspace_id: str | None = None,
    gpu_id: int | None = None,
    docker_image: str | None = None,
    docker_entrypoint: str | None = None,
    pull_image: bool = False,
    require_hardware_counters: bool = False,
    target: str | None = None,
) -> int:
    """Run command on GPU via wafer-api, streaming output.

    Two modes (mutually exclusive):
    - upload_dir: Upload files and run (stateless, high-level)
    - workspace_id: Use existing workspace (low-level)

    Args:
        command: Command to execute inside container
        upload_dir: Directory to upload (stateless mode)
        workspace_id: Workspace ID from push (low-level mode)
        gpu_id: GPU ID to use (optional)
        docker_image: Docker image override (optional)
        docker_entrypoint: Docker entrypoint override (optional, e.g., "bash")
        pull_image: Pull image if not available (optional, default False)
        require_hardware_counters: Require baremetal for ncu profiling (optional)
        target: Target name to use (optional, defaults to user's default)

    Returns:
        Exit code (0 = success, non-zero = failure)

    Raises:
        httpx.HTTPError: If API request fails
    """
    request_body: dict = {
        "command": command,
    }

    # Add files or workspace_id (mutually exclusive)
    if upload_dir is not None:
        files = _collect_files(upload_dir)
        request_body["files"] = files
        request_body["workspace_name"] = upload_dir.name
    elif workspace_id is not None:
        request_body["workspace_id"] = workspace_id
    # else: no files, no workspace (run command in temp workspace)

    if gpu_id is not None:
        request_body["gpu_id"] = gpu_id
    if docker_image is not None:
        request_body["docker_image"] = docker_image
    if docker_entrypoint is not None:
        request_body["docker_entrypoint"] = docker_entrypoint
    if pull_image:
        request_body["pull_image"] = True
    if require_hardware_counters:
        request_body["require_hardware_counters"] = True
    if target is not None:
        request_body["target"] = target

    api_url = get_api_url()
    headers = _get_auth_headers()
    exit_code = 0

    with httpx.Client(timeout=None, headers=headers) as client:  # No timeout for streaming
        with client.stream("POST", f"{api_url}/v1/gpu/jobs", json=request_body) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                # Parse SSE format: "data: <content>"
                if line.startswith("data: "):
                    content = line[6:]  # Strip "data: " prefix

                    if content == "[DONE]":
                        break
                    elif content.startswith("[ERROR]"):
                        print(content[8:], file=sys.stderr)  # Strip "[ERROR] "
                        exit_code = 1
                        break
                    else:
                        print(content)

    return exit_code


