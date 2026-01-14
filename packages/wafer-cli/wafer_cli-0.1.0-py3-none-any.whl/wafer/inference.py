"""Pure functions for inferring what files to upload and which environment to use.

All functions are pure: same input = same output, no side effects.
"""

import shlex
from pathlib import Path

from .config import WaferConfig, WaferEnvironment


def infer_upload_files(command: str, cwd: Path) -> list[Path]:
    """Infer which files to upload based on command.

    Pure function: command + directory -> list of paths.

    Strategy:
    1. Extract file references from command tokens
    2. Add common build files (Makefile, pyproject.toml, etc.)
    3. Add source files matching common patterns

    Args:
        command: Command to execute
        cwd: Current working directory

    Returns:
        Sorted list of file paths to upload

    Example:
        >>> infer_upload_files("nvcc kernel.cu -o kernel", Path("/home/user/cuda"))
        [Path("/home/user/cuda/kernel.cu"), Path("/home/user/cuda/Makefile"), ...]
    """
    assert cwd.exists(), f"cwd does not exist: {cwd}"
    assert isinstance(command, str), "command must be a string"
    assert isinstance(cwd, Path), "cwd must be a Path"

    files = set()

    # Extract file references from command
    try:
        tokens = shlex.split(command)
    except ValueError:
        # If command has unmatched quotes, just split on spaces
        tokens = command.split()

    # File extensions we care about
    file_extensions = {
        ".cu",
        ".cuh",
        ".py",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".rs",
        ".go",
    }

    for token in tokens:
        token_path = Path(token)
        if token_path.suffix in file_extensions:
            full_path = cwd / token_path
            if full_path.exists() and full_path.is_file():
                files.add(full_path)

    # Add common build files if they exist
    common_files = [
        "Makefile",
        "CMakeLists.txt",
        "pyproject.toml",
        "setup.py",
        "Cargo.toml",
        "go.mod",
        "requirements.txt",
    ]
    for filename in common_files:
        path = cwd / filename
        if path.exists() and path.is_file():
            files.add(path)

    # Add all source files in current directory (not recursive)
    source_extensions = [".cu", ".cuh", ".h", ".hpp", ".c", ".cpp"]
    for ext in source_extensions:
        for path in cwd.glob(f"*{ext}"):
            if path.is_file():
                files.add(path)

    result = sorted(files)
    return result


def resolve_environment(
    config: WaferConfig,
    env_name: str | None,
) -> WaferEnvironment:
    """Resolve which environment to use.

    Pure function: config + name -> environment.

    Priority:
    1. Explicit env_name argument
    2. Config default_environment
    3. Only environment if there's exactly one

    Args:
        config: Wafer configuration
        env_name: Optional environment name from CLI

    Returns:
        WaferEnvironment to use

    Raises:
        ValueError: If environment cannot be determined

    Example:
        >>> config = WaferConfig(...)
        >>> env = resolve_environment(config, "pytorch")
        >>> env.docker
        'pytorch/pytorch:2.5'
    """
    assert isinstance(config, WaferConfig), "config must be WaferConfig"
    assert env_name is None or isinstance(env_name, str), "env_name must be None or str"

    # Priority 1: Explicit env_name
    if env_name:
        if env_name not in config.environments:
            available = ", ".join(config.environments.keys())
            raise ValueError(f"Unknown environment: {env_name}. Available: {available}")
        return config.environments[env_name]

    # Priority 2: Config default
    if config.default_environment:
        assert (
            config.default_environment in config.environments
        ), "default_environment validated in WaferConfig"
        return config.environments[config.default_environment]

    # Priority 3: Only one environment
    if len(config.environments) == 1:
        return next(iter(config.environments.values()))

    # Cannot determine
    available = ", ".join(config.environments.keys())
    raise ValueError(
        f"No environment specified and no default configured. "
        f"Available: {available}. "
        f"Use --env to specify or set default.environment in config."
    )
