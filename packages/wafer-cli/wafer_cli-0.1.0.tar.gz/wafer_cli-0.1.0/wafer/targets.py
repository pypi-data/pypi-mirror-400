"""Target management for Wafer CLI.

CRUD operations for GPU targets stored in ~/.wafer/targets/.
"""

import tomllib
from dataclasses import asdict
from pathlib import Path
from typing import Any

from wafer_core.utils.kernel_utils.targets.config import (
    BaremetalTarget,
    ModalTarget,
    TargetConfig,
    VMTarget,
)

# Default paths
WAFER_DIR = Path.home() / ".wafer"
TARGETS_DIR = WAFER_DIR / "targets"
CONFIG_FILE = WAFER_DIR / "config.toml"


def _ensure_dirs() -> None:
    """Ensure ~/.wafer/targets/ exists."""
    TARGETS_DIR.mkdir(parents=True, exist_ok=True)


def _target_path(name: str) -> Path:
    """Get path to target config file."""
    return TARGETS_DIR / f"{name}.toml"


def _parse_target(data: dict[str, Any]) -> TargetConfig:
    """Parse TOML dict into target dataclass.

    Args:
        data: Parsed TOML data

    Returns:
        TargetConfig (BaremetalTarget, VMTarget, or ModalTarget)

    Raises:
        ValueError: If target type is unknown or required fields missing
    """
    target_type = data.get("type")
    if not target_type:
        raise ValueError("Target must have 'type' field (baremetal, vm, or modal)")

    # Remove type field before passing to dataclass
    data_copy = {k: v for k, v in data.items() if k != "type"}

    # Convert pip_packages list to tuple (TOML parses as list, dataclass expects tuple)
    if "pip_packages" in data_copy and isinstance(data_copy["pip_packages"], list):
        data_copy["pip_packages"] = tuple(data_copy["pip_packages"])

    if target_type == "baremetal":
        return BaremetalTarget(**data_copy)
    elif target_type == "vm":
        return VMTarget(**data_copy)
    elif target_type == "modal":
        return ModalTarget(**data_copy)
    else:
        raise ValueError(f"Unknown target type: {target_type}. Must be baremetal, vm, or modal")


def _serialize_target(target: TargetConfig) -> dict[str, Any]:
    """Serialize target dataclass to TOML-compatible dict.

    Args:
        target: Target config

    Returns:
        Dict with 'type' field added
    """
    data = asdict(target)

    # Add type field
    if isinstance(target, BaremetalTarget):
        data["type"] = "baremetal"
    elif isinstance(target, VMTarget):
        data["type"] = "vm"
    elif isinstance(target, ModalTarget):
        data["type"] = "modal"

    # Convert pip_packages tuple to list for TOML serialization
    if "pip_packages" in data and isinstance(data["pip_packages"], tuple):
        data["pip_packages"] = list(data["pip_packages"])

    # Remove empty pip_packages to keep config clean
    if "pip_packages" in data and not data["pip_packages"]:
        del data["pip_packages"]

    return data


def _write_toml(path: Path, data: dict[str, Any]) -> None:
    """Write dict as TOML file.

    Simple TOML writer - handles flat dicts and lists.
    """
    lines = []
    for key, value in data.items():
        if value is None:
            continue  # Skip None values
        if isinstance(value, bool):
            lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, int | float):
            lines.append(f"{key} = {value}")
        elif isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, list):
            # Format list
            if all(isinstance(v, int) for v in value):
                lines.append(f"{key} = {value}")
            else:
                formatted = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                lines.append(f"{key} = [{formatted}]")

    path.write_text("\n".join(lines) + "\n")


def load_target(name: str) -> TargetConfig:
    """Load target config by name.

    Args:
        name: Target name (filename without .toml)

    Returns:
        Target config

    Raises:
        FileNotFoundError: If target doesn't exist
        ValueError: If target config is invalid
    """
    path = _target_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Target not found: {name} (looked in {path})")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    return _parse_target(data)


def save_target(target: TargetConfig) -> None:
    """Save target config.

    Args:
        target: Target config to save

    Creates ~/.wafer/targets/{name}.toml
    """
    _ensure_dirs()
    data = _serialize_target(target)
    path = _target_path(target.name)
    _write_toml(path, data)


def add_target_from_file(file_path: Path) -> TargetConfig:
    """Add target from TOML file.

    Args:
        file_path: Path to TOML file

    Returns:
        Parsed and saved target

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    target = _parse_target(data)
    save_target(target)
    return target


def list_targets() -> list[str]:
    """List all configured target names.

    Returns:
        Sorted list of target names
    """
    _ensure_dirs()
    return sorted(p.stem for p in TARGETS_DIR.glob("*.toml"))


def remove_target(name: str) -> None:
    """Remove target config.

    Args:
        name: Target name to remove

    Raises:
        FileNotFoundError: If target doesn't exist
    """
    path = _target_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Target not found: {name}")
    path.unlink()


def get_default_target() -> str | None:
    """Get default target name from config.

    Returns:
        Default target name, or None if not set
    """
    if not CONFIG_FILE.exists():
        return None

    with open(CONFIG_FILE, "rb") as f:
        data = tomllib.load(f)

    return data.get("default_target")


def set_default_target(name: str) -> None:
    """Set default target.

    Args:
        name: Target name (must exist)

    Raises:
        FileNotFoundError: If target doesn't exist
    """
    # Verify target exists
    if name not in list_targets():
        raise FileNotFoundError(f"Target not found: {name}")

    _ensure_dirs()

    # Load existing config or create new
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)
    else:
        data = {}

    data["default_target"] = name

    # Write back (simple TOML)
    _write_toml(CONFIG_FILE, data)


def get_target_info(target: TargetConfig) -> dict[str, str]:
    """Get human-readable info about target.

    Args:
        target: Target config

    Returns:
        Dict of field name -> display value
    """
    info = {}

    if isinstance(target, BaremetalTarget):
        info["Type"] = "Baremetal"
        info["SSH"] = target.ssh_target
        info["GPUs"] = ", ".join(str(g) for g in target.gpu_ids)
        info["NCU"] = "Yes" if target.ncu_available else "No"
        # Docker info
        if target.docker_image:
            info["Docker"] = target.docker_image
            if target.pip_packages:
                info["Packages"] = ", ".join(target.pip_packages)
            if target.torch_package:
                info["Torch"] = target.torch_package
    elif isinstance(target, VMTarget):
        info["Type"] = "VM"
        info["SSH"] = target.ssh_target
        info["GPUs"] = ", ".join(str(g) for g in target.gpu_ids)
        info["NCU"] = "Yes" if target.ncu_available else "No"
        # Docker info
        if target.docker_image:
            info["Docker"] = target.docker_image
            if target.pip_packages:
                info["Packages"] = ", ".join(target.pip_packages)
            if target.torch_package:
                info["Torch"] = target.torch_package
    elif isinstance(target, ModalTarget):
        info["Type"] = "Modal"
        info["App"] = target.modal_app_name
        info["GPU"] = target.gpu_type
        info["Timeout"] = f"{target.timeout_seconds}s"
        info["NCU"] = "No (Modal)"

    info["Compute"] = target.compute_capability

    return info
