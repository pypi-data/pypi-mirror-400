"""Remote kernel evaluation for Wafer CLI.

Runs evaluate.py on a remote GPU target with the same interface as local execution.
"""

import json
import shlex
from dataclasses import dataclass
from pathlib import Path

from wafer_core.utils.kernel_utils.targets.config import (
    BaremetalTarget,
    ModalTarget,
    VMTarget,
)


def _build_docker_run_command(
    image: str,
    command: str,
    *,
    working_dir: str | None = None,
    env: dict[str, str] | None = None,
    gpus: str = "all",
    volumes: dict[str, str] | None = None,
    cap_add: list[str] | None = None,
) -> str:
    """Build a docker run command string.

    Pure function: string in, string out. No side effects.

    Args:
        image: Docker image name (e.g., "nvcr.io/nvidia/cutlass:4.3-devel")
        command: Command to run inside container
        working_dir: Container working directory (optional)
        env: Environment variables as dict (optional)
        gpus: GPU access string ("all", "device=0", "device=0,1", etc.)
        volumes: Host:container volume mappings (optional)
        cap_add: Linux capabilities to add (e.g., ["SYS_ADMIN"] for NCU profiling)

    Returns:
        Complete docker run command string
    """
    parts = ["docker", "run", "--rm"]

    # Add capabilities (needed for NCU profiling)
    if cap_add:
        for cap in cap_add:
            parts.extend(["--cap-add", cap])

    # GPU access - use single quotes for the device spec to avoid shell escaping issues
    if gpus:
        parts.extend(["--gpus", f"'{gpus}'"])

    # Volume mounts
    if volumes:
        for host_path, container_path in volumes.items():
            parts.extend(["-v", f"{host_path}:{container_path}"])

    # Working directory
    if working_dir:
        parts.extend(["-w", working_dir])

    # Environment variables
    if env:
        for key, value in env.items():
            parts.extend(["-e", f"{key}={shlex.quote(value)}"])

    # Image and command
    parts.append(image)
    parts.append(f"bash -c {shlex.quote(command)}")

    return " ".join(parts)


@dataclass(frozen=True)
class EvaluateArgs:
    """Arguments for evaluate command.

    Mirrors evaluate.py's CLI args.
    """

    implementation: Path
    reference: Path
    test_cases: Path
    target_name: str
    benchmark: bool = False
    profile: bool = False
    sync_artifacts: bool = True
    gpu_id: int | None = None


@dataclass(frozen=True)
class EvaluateResult:
    """Result from remote evaluation."""

    success: bool
    all_correct: bool
    correctness_score: float
    geomean_speedup: float
    passed_tests: int
    total_tests: int
    error_message: str | None = None
    artifact_path: Path | None = None


def _validate_files(args: EvaluateArgs) -> str | None:
    """Validate that all input files exist.

    Returns:
        Error message if validation fails, None if all valid
    """
    if not args.implementation.exists():
        return f"Implementation file not found: {args.implementation}"
    if not args.reference.exists():
        return f"Reference file not found: {args.reference}"
    if not args.test_cases.exists():
        return f"Test cases file not found: {args.test_cases}"
    return None


def _select_gpu_id(
    target: BaremetalTarget | VMTarget | ModalTarget, gpu_id_override: int | None
) -> int:
    """Select GPU ID to use.

    Args:
        target: Target config
        gpu_id_override: Optional explicit GPU ID

    Returns:
        GPU ID to use
    """
    if gpu_id_override is not None:
        return gpu_id_override

    # Use first GPU from target's list
    if isinstance(target, BaremetalTarget | VMTarget):
        return target.gpu_ids[0]

    # Modal doesn't have explicit GPU IDs
    return 0


def _build_docker_pip_install_cmd(target: BaremetalTarget | VMTarget) -> str:
    """Build pip install command for Docker container.

    Installs uv first, then uses uv to install packages (Modal-like approach).
    Uses --system flag to install to container's system Python (not any venv).

    Handles base CUDA images that may not have pip pre-installed.

    Args:
        target: Target config with pip_packages, torch_package, torch_index_url

    Returns:
        Shell command string to install dependencies
    """
    commands = []

    # Some base images (like nvidia/cuda) don't have pip or git, install them first
    # Use apt for Debian/Ubuntu-based images, with noninteractive to avoid prompts
    commands.append(
        "(which pip > /dev/null 2>&1 && which git > /dev/null 2>&1) || "
        "(apt-get update && "
        "DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip git > /dev/null)"
    )

    # Install uv (fast, reliable) - use pip3 for compatibility
    commands.append("pip3 install uv")

    # Install torch with custom index if specified (like Modal's two-phase install)
    # Use --system --break-system-packages to install to container's Python
    # (needed for Python 3.12+ with PEP 668 externally managed environments)
    if target.torch_package:
        if target.torch_index_url:
            commands.append(
                f"uv pip install --system --break-system-packages --index-url {target.torch_index_url} "
                f"--extra-index-url https://pypi.org/simple {target.torch_package}"
            )
        else:
            commands.append(f"uv pip install --system --break-system-packages {target.torch_package}")

    # Install other packages
    if target.pip_packages:
        packages_str = " ".join(target.pip_packages)
        commands.append(f"uv pip install --system --break-system-packages {packages_str}")

    return " && ".join(commands)


def _get_wafer_root() -> Path:
    """Get wafer monorepo root directory.

    Walks up from this file to find the wafer repo root (contains apps/, packages/).
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "apps").is_dir() and (parent / "packages").is_dir():
            return parent
    raise RuntimeError(f"Could not find wafer root from {__file__}")


async def run_evaluate_docker(
    args: EvaluateArgs,
    target: BaremetalTarget | VMTarget,
) -> EvaluateResult:
    """Run evaluation in Docker container on SSH-based target.

    Uses async SSH client for true non-blocking I/O.
    Uploads wafer-core and runs evaluate.py directly with PYTHONPATH.
    No package installation needed - avoids rollouts dependency.

    Args:
        args: Evaluate arguments
        target: SSH target config with docker_image set

    Returns:
        Evaluation result
    """
    from datetime import datetime

    from wafer_core.async_ssh import AsyncSSHClient

    CONTAINER_WORKSPACE = "/workspace"
    REMOTE_WORKSPACE_BASE = "~/.wafer/workspaces"

    if not target.docker_image:
        raise ValueError("docker_image must be set for Docker execution")

    # Select GPU
    gpu_id = _select_gpu_id(target, args.gpu_id)

    print(f"Connecting to {target.ssh_target}...")

    async with AsyncSSHClient(target.ssh_target, target.ssh_key) as client:
        # Upload wafer-core to remote
        try:
            wafer_root = _get_wafer_root()
            wafer_core_path = wafer_root / "packages" / "wafer-core"
            print(f"Uploading wafer-core from {wafer_core_path}...")

            # Create workspace and upload
            workspace_name = wafer_core_path.name
            remote_workspace = f"{REMOTE_WORKSPACE_BASE}/{workspace_name}"
            await client.exec(f"mkdir -p {remote_workspace}")
            wafer_core_workspace = await client.expand_path(remote_workspace)

            upload_result = await client.upload_files(
                str(wafer_core_path), wafer_core_workspace, recursive=True
            )
            print(f"Uploaded {upload_result.files_copied} files")
        except Exception as e:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to upload wafer-core: {e}",
            )

        print(f"Using Docker image: {target.docker_image}")
        print(f"Using GPU {gpu_id}...")

        # Read local files
        impl_code = args.implementation.read_text()
        ref_code = args.reference.read_text()
        test_cases_data = json.loads(args.test_cases.read_text())

        # Create a unique run directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = f"wafer_eval_{timestamp}"
        run_path = f"{wafer_core_workspace}/{run_dir}"

        print("Uploading evaluation files...")

        # Create run directory
        mkdir_result = await client.exec(f"mkdir -p {run_path}")
        if mkdir_result.exit_code != 0:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to create run directory: {mkdir_result.stderr}",
            )

        # Write implementation
        impl_path = f"{run_path}/implementation.py"
        write_result = await client.exec(
            f"cat > '{impl_path}' << 'IMPL_EOF'\n{impl_code}\nIMPL_EOF"
        )
        if write_result.exit_code != 0:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to write implementation: {write_result.stderr}",
            )

        # Write reference
        ref_path = f"{run_path}/reference.py"
        write_result = await client.exec(
            f"cat > '{ref_path}' << 'REF_EOF'\n{ref_code}\nREF_EOF"
        )
        if write_result.exit_code != 0:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to write reference: {write_result.stderr}",
            )

        # Also write as reference_kernel.py (evaluate.py imports generate_input from this)
        ref_kernel_path = f"{run_path}/reference_kernel.py"
        write_result = await client.exec(
            f"cat > '{ref_kernel_path}' << 'REF_EOF'\n{ref_code}\nREF_EOF"
        )
        if write_result.exit_code != 0:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to write reference_kernel: {write_result.stderr}",
            )

        # Write test cases
        test_cases_path = f"{run_path}/test_cases.json"
        test_cases_json = json.dumps(test_cases_data, indent=2)
        write_result = await client.exec(
            f"cat > '{test_cases_path}' << 'TESTS_EOF'\n{test_cases_json}\nTESTS_EOF"
        )
        if write_result.exit_code != 0:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to write test cases: {write_result.stderr}",
            )

        print("Running evaluation in Docker container...")

        # Paths inside container (workspace mounted at /workspace)
        container_run_path = f"{CONTAINER_WORKSPACE}/{run_dir}"
        container_impl_path = f"{container_run_path}/implementation.py"
        container_ref_path = f"{container_run_path}/reference.py"
        container_test_cases_path = f"{container_run_path}/test_cases.json"
        container_evaluate_script = (
            f"{CONTAINER_WORKSPACE}/wafer_core/utils/kernel_utils/evaluate.py"
        )

        # Build pip install command for torch and other deps (no wafer-core install needed)
        pip_install_cmd = _build_docker_pip_install_cmd(target)

        # Build evaluate command - use PYTHONPATH instead of installing wafer-core
        python_cmd_parts = [
            f"PYTHONPATH={CONTAINER_WORKSPACE}:$PYTHONPATH",
            f"python3 {container_evaluate_script}",
            f"--implementation {container_impl_path}",
            f"--reference {container_ref_path}",
            f"--test-cases {container_test_cases_path}",
            f"--run-dir {container_run_path}",
        ]

        if args.benchmark:
            python_cmd_parts.append("--benchmark")
        if args.profile:
            python_cmd_parts.append("--profile")

        eval_cmd = " ".join(python_cmd_parts)

        # Full command: install torch deps, then run evaluate with PYTHONPATH
        full_cmd = f"{pip_install_cmd} && cd {container_run_path} && {eval_cmd}"

        # Build Docker run command
        # Add SYS_ADMIN capability when profiling (needed for NCU GPU performance counters)
        docker_cmd = _build_docker_run_command(
            image=target.docker_image,
            command=full_cmd,
            working_dir=container_run_path,
            env={"CUDA_VISIBLE_DEVICES": str(gpu_id), "PYTHONUNBUFFERED": "1"},
            gpus="all",
            volumes={wafer_core_workspace: CONTAINER_WORKSPACE},
            cap_add=["SYS_ADMIN"] if args.profile else None,
        )

        print(f"Docker command: {docker_cmd[:100]}...")

        # Run Docker command and stream output
        log_lines = []
        async for line in client.exec_stream(docker_cmd):
            print(line)
            log_lines.append(line)

        # Read results
        results_path = f"{run_path}/results.json"
        cat_result = await client.exec(f"cat {results_path}")

        if cat_result.exit_code != 0:
            log_tail = "\n".join(log_lines[-50:])
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Evaluation failed. Log tail:\n{log_tail}",
            )

        # Parse results
        try:
            results_data = json.loads(cat_result.stdout)
        except json.JSONDecodeError as e:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=f"Failed to parse results: {e}",
            )

        # Extract backend results
        backends = results_data.get("backends", [])
        if not backends:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message="No backend results found",
            )

        backend = backends[0]
        correctness_tests = backend.get("correctness_tests", [])
        passed = sum(1 for t in correctness_tests if t.get("is_correct", False))
        total = len(correctness_tests)

        # Sync artifacts if requested
        artifact_path = None
        if args.sync_artifacts:
            local_artifact_dir = Path.cwd() / "wafer_artifacts" / run_dir
            local_artifact_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Download results.json
                download_result = await client.download_files(
                    remote_path=f"{run_path}/results.json",
                    local_path=str(local_artifact_dir / "results.json"),
                )
                if download_result.success:
                    artifact_path = local_artifact_dir
                    print(f"Artifacts saved to: {artifact_path}")
                else:
                    print(f"Warning: Failed to sync results.json: {download_result.error_message}")

                # Download NCU profiles if they exist (from --profile flag)
                # NCU profiles are stored in artifact/ncu/ subdirectory
                ncu_check = await client.exec(f"test -d {run_path}/artifact/ncu")
                if ncu_check.exit_code == 0:
                    local_ncu_dir = local_artifact_dir / "ncu"
                    local_ncu_dir.mkdir(parents=True, exist_ok=True)
                    ncu_result = await client.download_files(
                        remote_path=f"{run_path}/artifact/ncu",
                        local_path=str(local_ncu_dir),
                        recursive=True,
                    )
                    if ncu_result.success:
                        print(f"NCU profiles synced: {ncu_result.files_copied} files")
                    else:
                        print(f"Warning: Failed to sync NCU profiles: {ncu_result.error_message}")
            except Exception as e:
                print(f"Warning: Failed to sync artifacts: {e}")

        return EvaluateResult(
            success=True,
            all_correct=backend.get("all_correct", False),
            correctness_score=backend.get("correctness_score", 0.0),
            geomean_speedup=backend.get("geomean_speedup", 0.0),
            passed_tests=passed,
            total_tests=total,
            artifact_path=artifact_path,
        )


async def run_evaluate_ssh(
    args: EvaluateArgs,
    target: BaremetalTarget | VMTarget,
) -> EvaluateResult:
    """Run evaluation on SSH-based target (Baremetal or VM).

    Routes to Docker or venv execution based on target.docker_image.

    If docker_image is set:
    - Uses Docker container with GPU passthrough
    - Installs deps via uv inside container (Modal-like)

    If docker_image is not set:
    - Uses the existing venv-based deployment infrastructure

    Args:
        args: Evaluate arguments
        target: SSH target config

    Returns:
        Evaluation result
    """
    # Route to Docker execution if docker_image is set
    if target.docker_image:
        return await run_evaluate_docker(args, target)

    # Otherwise, use venv-based execution (existing path)
    from datetime import datetime

    from wafer_core.remote_jobs import (
        LogStreamConfig,
        start_tmux_session,
        stream_log_until_complete,
    )
    from wafer_core.utils.kernel_utils.deployment import (
        DeploymentConfig,
        setup_deployment,
    )

    # Select GPU
    gpu_id = _select_gpu_id(target, args.gpu_id)

    # Create deployment config
    config = DeploymentConfig(
        ssh_target=target.ssh_target,
        ssh_key=target.ssh_key,
        gpu_id=gpu_id,
    )

    print(f"Connecting to {target.ssh_target}...")

    # Setup deployment (expensive - deploys monorepo + creates venv)
    state, err = await setup_deployment(config)
    if err:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Deployment setup failed: {err}",
        )

    assert state is not None

    print(f"Using GPU {gpu_id}...")

    # Read local files
    impl_code = args.implementation.read_text()
    ref_code = args.reference.read_text()
    test_cases_data = json.loads(args.test_cases.read_text())

    # Create a unique run directory within the deployed workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"wafer_eval_{timestamp}"

    # workspace_path is the project path (e.g., .../research/async-wevin/benchmarks/gpumode)
    workspace = state.workspace_path
    run_path = f"{workspace}/{run_dir}"

    # Get SSH client from deployment state
    client = state.ssh_client

    print("Uploading files...")

    # Create run directory
    mkdir_result = client.exec(f"mkdir -p {run_path}")
    if mkdir_result.exit_code != 0:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to create run directory: {mkdir_result.stderr}",
        )

    # Write implementation (must define custom_kernel function)
    impl_path = f"{run_path}/implementation.py"
    write_result = client.exec(f"cat > '{impl_path}' << 'IMPL_EOF'\n{impl_code}\nIMPL_EOF")
    if write_result.exit_code != 0:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to write implementation: {write_result.stderr}",
        )

    # Write reference (must define ref_kernel function)
    ref_path = f"{run_path}/reference.py"
    write_result = client.exec(f"cat > '{ref_path}' << 'REF_EOF'\n{ref_code}\nREF_EOF")
    if write_result.exit_code != 0:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to write reference: {write_result.stderr}",
        )

    # Also write as reference_kernel.py (evaluate.py imports generate_input from this)
    ref_kernel_path = f"{run_path}/reference_kernel.py"
    write_result = client.exec(f"cat > '{ref_kernel_path}' << 'REF_EOF'\n{ref_code}\nREF_EOF")
    if write_result.exit_code != 0:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to write reference_kernel: {write_result.stderr}",
        )

    # Write test cases
    test_cases_path = f"{run_path}/test_cases.json"
    test_cases_json = json.dumps(test_cases_data, indent=2)
    write_result = client.exec(
        f"cat > '{test_cases_path}' << 'TESTS_EOF'\n{test_cases_json}\nTESTS_EOF"
    )
    if write_result.exit_code != 0:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to write test cases: {write_result.stderr}",
        )

    print("Running evaluation...")

    # Build evaluate command
    # The deployment deploys to research/async-wevin/benchmarks/gpumode
    # evaluate.py is at research/async-wevin/wafer_utils/kernel_utils/evaluate.py
    # So we need to go up 2 levels from workspace to find async-wevin root
    # workspace = .../research/async-wevin/benchmarks/gpumode
    # async_wevin_root = .../research/async-wevin
    async_wevin_root = "/".join(workspace.rstrip("/").split("/")[:-2])
    evaluate_script = f"{async_wevin_root}/wafer_utils/kernel_utils/evaluate.py"

    env_state = state.env_state

    eval_cmd_parts = [
        f"cd {run_path} &&",
        f"PATH={env_state.venv_bin}:$PATH",
        f"{env_state.venv_python} {evaluate_script}",
        f"--implementation {impl_path}",
        f"--reference {ref_path}",
        f"--test-cases {test_cases_path}",
        f"--run-dir {run_path}",
    ]

    if args.benchmark:
        eval_cmd_parts.append("--benchmark")
    if args.profile:
        eval_cmd_parts.append("--profile")

    eval_cmd = " ".join(eval_cmd_parts)

    # Run via tmux for streaming output
    session_name = f"wafer_eval_{datetime.now().strftime('%H%M%S')}"
    log_file = f"{run_path}/evaluate.log"

    _, err = start_tmux_session(
        client=client,
        session_name=session_name,
        command=eval_cmd,
        workspace=run_path,
        log_file=log_file,
        env_vars={
            "CUDA_VISIBLE_DEVICES": str(gpu_id),
            "PYTHONUNBUFFERED": "1",
        },
    )

    if err:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to start evaluation: {err}",
        )

    # Stream logs until completion
    stream_config = LogStreamConfig(
        session_name=session_name,
        log_file=log_file,
        timeout_sec=600,  # 10 minutes max
        poll_interval_sec=2.0,
    )

    _ = stream_log_until_complete(client=client, config=stream_config)

    # Read results
    results_path = f"{run_path}/results.json"
    cat_result = client.exec(f"cat {results_path}")

    if cat_result.exit_code != 0:
        # Try to get error from log
        log_result = client.exec(f"tail -50 {log_file}")
        log_tail = log_result.stdout if log_result.exit_code == 0 else ""
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Evaluation failed. Log tail:\n{log_tail}",
        )

    # Parse results
    try:
        results_data = json.loads(cat_result.stdout)
    except json.JSONDecodeError as e:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Failed to parse results: {e}",
        )

    # Extract backend results
    # Results format: {"backends": [{"backend_name": ..., "correctness_score": ..., ...}]}
    backends = results_data.get("backends", [])
    if not backends:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message="No backend results found",
        )

    backend = backends[0]
    correctness_tests = backend.get("correctness_tests", [])
    passed = sum(1 for t in correctness_tests if t.get("is_correct", False))
    total = len(correctness_tests)

    # Sync artifacts if requested
    artifact_path = None
    if args.sync_artifacts:
        local_artifact_dir = Path.cwd() / "wafer_artifacts" / run_dir
        local_artifact_dir.mkdir(parents=True, exist_ok=True)

        # Download results and logs
        try:
            client.download_files(
                remote_path=f"{run_path}/results.json",
                local_path=str(local_artifact_dir / "results.json"),
            )
            client.download_files(
                remote_path=log_file,
                local_path=str(local_artifact_dir / "evaluate.log"),
            )
            artifact_path = local_artifact_dir
            print(f"Artifacts saved to: {artifact_path}")
        except Exception as e:
            print(f"Warning: Failed to sync artifacts: {e}")

    return EvaluateResult(
        success=True,
        all_correct=backend.get("all_correct", False),
        correctness_score=backend.get("correctness_score", 0.0),
        geomean_speedup=backend.get("geomean_speedup", 0.0),
        passed_tests=passed,
        total_tests=total,
        artifact_path=artifact_path,
    )


async def run_evaluate_modal(
    args: EvaluateArgs,
    target: ModalTarget,
) -> EvaluateResult:
    """Run evaluation on Modal target.

    Args:
        args: Evaluate arguments
        target: Modal target config

    Returns:
        Evaluation result
    """
    # TODO: Implement Modal execution path
    # For now, return error
    return EvaluateResult(
        success=False,
        all_correct=False,
        correctness_score=0.0,
        geomean_speedup=0.0,
        passed_tests=0,
        total_tests=0,
        error_message="Modal targets not yet implemented. Use baremetal or VM target.",
    )


async def run_evaluate(args: EvaluateArgs) -> EvaluateResult:
    """Run evaluation on configured target.

    Args:
        args: Evaluate arguments

    Returns:
        Evaluation result
    """
    from .targets import get_default_target, load_target

    # Validate input files
    err = _validate_files(args)
    if err:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=err,
        )

    # Load target
    target_name = args.target_name
    if not target_name:
        target_name = get_default_target()
        if not target_name:
            return EvaluateResult(
                success=False,
                all_correct=False,
                correctness_score=0.0,
                geomean_speedup=0.0,
                passed_tests=0,
                total_tests=0,
                error_message=(
                    "No target specified and no default set. "
                    "Use --target or run: wafer targets default <name>"
                ),
            )

    try:
        target = load_target(target_name)
    except FileNotFoundError:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Target not found: {target_name}. Run: wafer targets list",
        )

    print(f"Using target: {target_name}")

    # Dispatch to appropriate executor
    if isinstance(target, BaremetalTarget | VMTarget):
        return await run_evaluate_ssh(args, target)
    elif isinstance(target, ModalTarget):
        return await run_evaluate_modal(args, target)
    else:
        return EvaluateResult(
            success=False,
            all_correct=False,
            correctness_score=0.0,
            geomean_speedup=0.0,
            passed_tests=0,
            total_tests=0,
            error_message=f"Unknown target type: {type(target)}",
        )
