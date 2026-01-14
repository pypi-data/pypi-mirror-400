"""Integration tests for config loading and environment resolution.

Tests WaferConfig loading and environment resolution.
"""

from pathlib import Path

import pytest

from wafer.config import WaferConfig
from wafer.inference import resolve_environment

# Constants
CONFIG_DIR = ".wafer"
CONFIG_FILENAME = "config.toml"


def test_config_and_environment_resolution() -> None:
    """Test config loading and environment resolution."""
    home_dir = Path.home()
    assert home_dir.exists()
    
    config_path = home_dir / CONFIG_DIR / CONFIG_FILENAME
    
    if not config_path.exists():
        pytest.skip(f"Config not found: {config_path}")

    config = WaferConfig.from_toml(config_path)
    assert config is not None

    assert config.target is not None
    assert len(config.target) > 0
    assert config.ssh_key is not None
    assert len(config.ssh_key) > 0
    assert len(config.environments) > 0

    default_env = resolve_environment(config, None)
    assert default_env is not None
    assert default_env.docker is not None
    assert len(default_env.docker) > 0
    assert default_env.name is not None
    assert len(default_env.name) > 0

    env_names = list(config.environments.keys())
    assert len(env_names) > 0
    
    explicit_env_name = env_names[0]
    explicit_env = resolve_environment(config, explicit_env_name)
    assert explicit_env is not None
    assert explicit_env.name == explicit_env_name
