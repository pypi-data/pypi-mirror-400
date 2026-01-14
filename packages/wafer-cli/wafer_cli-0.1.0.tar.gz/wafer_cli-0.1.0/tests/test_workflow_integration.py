"""Integration tests for full end-to-end Wafer workflow.

Tests complete workflow from file inference to execution.
"""

import shlex
import tempfile
from pathlib import Path

import pytest

from wafer_core.ssh import SSHClient

from wafer.config import WaferConfig
from wafer.inference import infer_upload_files, resolve_environment

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

CONFIG_DIR = ".wafer"
CONFIG_FILENAME = "config.toml"
WORKSPACE_BASE = "~/.wafer/workspaces"
CONTAINER_WORKSPACE = "/workspace"

PYTHON_ENV_NAME = "pytorch"
PYTHON_SCRIPT_FILENAME = "test.py"
PYTHON_COMMAND = "python test.py"
EXPECTED_PYTHON_VERSION_PREFIX = "Python version:"
EXPECTED_SUCCESS_MESSAGE = "Wafer integration test successful!"


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


def test_full_wafer_workflow() -> None:
    """Test complete Wafer workflow end-to-end."""
    _check_ssh_available()
    
    home_dir = Path.home()
    assert home_dir.exists()
    
    config_path = home_dir / CONFIG_DIR / CONFIG_FILENAME
    if not config_path.exists():
        pytest.skip(f"Config not found: {config_path}")

    config = WaferConfig.from_toml(config_path)
    assert config is not None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        assert tmpdir_path.exists()

        script = tmpdir_path / PYTHON_SCRIPT_FILENAME
        script.write_text(f"""
import sys
print("{EXPECTED_PYTHON_VERSION_PREFIX}", sys.version)
print("{EXPECTED_SUCCESS_MESSAGE}")
""")
        assert script.exists()

        files = infer_upload_files(PYTHON_COMMAND, tmpdir_path)
        assert script in files
        assert len(files) > 0

        has_pytorch_env = PYTHON_ENV_NAME in config.environments
        env_name = PYTHON_ENV_NAME if has_pytorch_env else None
        environment = resolve_environment(config, env_name)
        assert environment is not None
        assert environment.docker is not None
        assert len(environment.docker) > 0

        client = SSHClient(VULTR_TARGET, SSH_KEY)
        cwd_name = Path.cwd().name
        workspace = f"{WORKSPACE_BASE}/wafer-test-{cwd_name}"

        mkdir_result = client.exec(f"mkdir -p {workspace}")
        assert mkdir_result.exit_code == 0
        
        expanded_workspace = client.expand_path(workspace)
        assert len(expanded_workspace) > 0

        for file_path in files:
            remote_path = f"{expanded_workspace}/{file_path.name}"
            upload_result = client.upload_files(str(file_path), remote_path)
            assert upload_result.success

        docker_cmd = _build_docker_cmd(
            image=environment.docker,
            command=PYTHON_COMMAND,
            volumes={expanded_workspace: CONTAINER_WORKSPACE},
            working_dir=CONTAINER_WORKSPACE,
        )
        
        exec_result = client.exec(docker_cmd)
        assert exec_result.exit_code == 0
        assert exec_result.stdout is not None
        assert EXPECTED_PYTHON_VERSION_PREFIX in exec_result.stdout
        assert EXPECTED_SUCCESS_MESSAGE in exec_result.stdout

        cleanup_result = client.exec(f"rm -rf {workspace}")
        assert cleanup_result.exit_code == 0
