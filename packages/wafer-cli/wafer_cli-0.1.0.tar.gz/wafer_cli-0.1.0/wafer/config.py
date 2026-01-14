"""Configuration management for Wafer CLI.

Immutable dataclasses for config with TOML parsing.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WaferEnvironment:
    """Docker environment configuration. Immutable."""

    name: str
    docker: str
    description: str = ""

    def __post_init__(self) -> None:
        """Validate environment configuration."""
        assert self.name, "environment name cannot be empty"
        assert self.docker, "docker image cannot be empty"


@dataclass(frozen=True)
class WaferConfig:
    """Wafer CLI configuration. Immutable."""

    target: str
    ssh_key: str
    environments: dict[str, WaferEnvironment]
    default_environment: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration."""
        assert self.target, "target cannot be empty"
        assert self.ssh_key, "ssh_key cannot be empty"
        assert self.environments, "at least one environment must be defined"

        # Validate default_environment exists if specified
        if self.default_environment:
            assert (
                self.default_environment in self.environments
            ), f"default_environment '{self.default_environment}' not found in environments"

    @classmethod
    def from_toml(cls, path: Path) -> "WaferConfig":
        """Parse config from TOML file.

        Args:
            path: Path to config file

        Returns:
            WaferConfig instance

        Raises:
            AssertionError: If config is invalid or missing required fields
            FileNotFoundError: If config file doesn't exist

        Example config file (~/.wafer/config.toml):

            [default]
            target = "root@b200:22"
            ssh_key = "~/.ssh/id_ed25519"
            environment = "cutlass"  # Optional default

            [environments.cutlass]
            docker = "nvcr.io/nvidia/cutlass:4.3-devel"
            description = "CUDA 13 + Cutlass 4.3"

            [environments.pytorch]
            docker = "pytorch/pytorch:2.5-cuda12.4"
            description = "PyTorch with CUDA 12.4"
        """
        assert path.exists(), f"Config file not found: {path}"

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Validate required sections
        assert "default" in data, "Config must have [default] section"
        assert "target" in data["default"], "Config must have default.target"
        assert "ssh_key" in data["default"], "Config must have default.ssh_key"

        # Parse environments
        environments = {}
        env_data = data.get("environments", {})
        assert env_data, "Config must have at least one environment defined"

        for name, env_config in env_data.items():
            assert isinstance(env_config, dict), f"Environment {name} must be a table/dict"
            assert "docker" in env_config, f"Environment {name} must have docker image"

            environments[name] = WaferEnvironment(
                name=name,
                docker=env_config["docker"],
                description=env_config.get("description", ""),
            )

        return cls(
            target=data["default"]["target"],
            ssh_key=data["default"]["ssh_key"],
            environments=environments,
            default_environment=data["default"].get("environment"),
        )
