"""NCU Analyze - Parse and analyze .ncu-rep profile files.

This module provides the implementation for the `wafer ncu-analyze` command.
It reuses the parsing logic from services/ncu-tool/ncu_tool.py.

TODO(Wafer-326): Migrate this to wafer-core architecture.
The NCU parsing logic should be consolidated into wafer_core/tools/ncu_parser.py,
similar to how compiler_explorer_tool.py was migrated to wafer_core/tools/compiler.py.
This will:
1. Eliminate duplicate code between this file and extension's ncu_tool.py
2. Enable automatic telemetry via @with_telemetry decorator
3. Allow both CLI and extension to use the same implementation
See wafer_core/tools/compiler.py for the migration pattern.
"""

import json
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Known NCU installation paths by platform
NCU_PATHS = {
    "linux": [
        "/usr/local/cuda/bin/ncu",
        "/opt/nvidia/nsight-compute/ncu",
        "/usr/bin/ncu",
        "/usr/local/bin/ncu",
    ],
    "darwin": [
        "/Applications/NVIDIA Nsight Compute.app/Contents/MacOS/ncu",
        "/usr/local/cuda/bin/ncu",
    ],
    "windows": [
        r"C:\Program Files\NVIDIA Corporation\Nsight Compute\ncu.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin\ncu.exe",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin\ncu.exe",
    ],
}


def _get_platform() -> str:
    """Get normalized platform name."""
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    return "linux"


def _find_ncu() -> str | None:
    """Find NCU executable on the system."""
    ncu = shutil.which("ncu")
    if ncu:
        return ncu

    plat = _get_platform()
    for path in NCU_PATHS.get(plat, []):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return None


def _get_install_command() -> str:
    """Get platform-appropriate install command."""
    plat = _get_platform()

    if plat == "linux":
        if shutil.which("apt-get") or shutil.which("apt"):
            return "sudo apt install nvidia-cuda-toolkit"
        elif shutil.which("dnf"):
            return "sudo dnf install cuda-nsight-compute"
        elif shutil.which("yum"):
            return "sudo yum install cuda-nsight-compute"
        elif shutil.which("pacman"):
            return "sudo pacman -S cuda-tools"

    if shutil.which("conda"):
        return "conda install -c nvidia nsight-compute"

    return "Download from https://developer.nvidia.com/nsight-compute"


def _parse_ncu_output(session_output: str, details_output: str) -> dict:
    """Parse NCU session and details output into structured data."""
    import re

    summary: dict = {
        "gpu": "Unknown",
        "kernels": [],
        "recommendations": [],
    }

    # Parse session output for GPU name
    if session_output:
        for line in session_output.split("\n"):
            if "display_name" in line:
                parts = line.split()
                if len(parts) >= 2:
                    summary["gpu"] = " ".join(parts[1:])
                break

    # Parse details output for kernel metrics and recommendations
    if details_output:
        lines = details_output.split("\n")
        current_kernel: dict | None = None
        current_section: str | None = None
        in_recommendation = False
        recommendation_lines: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Detect kernel header
            if (
                line.startswith("  ")
                and not line.startswith("    ")
                and "Context" in line
                and "Device" in line
            ):
                match = re.match(
                    r"^  (.+?)\s+\(\d+,\s*\d+,\s*\d+\)x\(\d+,\s*\d+,\s*\d+\)", line
                )
                if match:
                    kernel_name = match.group(1).strip()
                    current_kernel = {
                        "name": kernel_name,
                        "duration_us": 0,
                        "duration_ms": 0,
                        "memory_throughput_pct": 0,
                        "compute_throughput_pct": 0,
                        "achieved_occupancy_pct": 0,
                        "registers_per_thread": 0,
                        "block_size": 0,
                        "grid_size": 0,
                        "estimated_speedup_pct": 0,
                        "recommendations": [],
                    }
                    summary["kernels"].append(current_kernel)

            # Detect section headers
            if stripped.startswith("Section:"):
                current_section = stripped.replace("Section:", "").strip()

            # Parse metrics from table rows
            if current_kernel and "          " in line:
                parts = line.split()
                if len(parts) >= 2:
                    metric_line = stripped

                    # Duration (in us)
                    if metric_line.startswith("Duration") and "us" in metric_line:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel["duration_us"] = value
                            current_kernel["duration_ms"] = value / 1000
                        except (ValueError, IndexError):
                            pass

                    # Memory Throughput (%)
                    elif "Memory Throughput" in metric_line and "%" in metric_line:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel["memory_throughput_pct"] = value
                        except (ValueError, IndexError):
                            pass

                    # Compute (SM) Throughput (%)
                    elif (
                        "Compute (SM) Throughput" in metric_line
                        or "Compute Throughput" in metric_line
                    ):
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel["compute_throughput_pct"] = value
                        except (ValueError, IndexError):
                            pass

                    # Achieved Occupancy (%)
                    elif "Achieved Occupancy" in metric_line and "%" in metric_line:
                        try:
                            value = float(parts[-1].replace(",", ""))
                            current_kernel["achieved_occupancy_pct"] = value
                        except (ValueError, IndexError):
                            pass

                    # Registers Per Thread
                    elif "Registers Per Thread" in metric_line:
                        try:
                            value = int(float(parts[-1].replace(",", "")))
                            current_kernel["registers_per_thread"] = value
                        except (ValueError, IndexError):
                            pass

                    # Block Size
                    elif (
                        metric_line.startswith("Block Size")
                        and current_section == "Launch Statistics"
                    ):
                        try:
                            value = int(float(parts[-1].replace(",", "")))
                            current_kernel["block_size"] = value
                        except (ValueError, IndexError):
                            pass

                    # Grid Size
                    elif (
                        metric_line.startswith("Grid Size")
                        and current_section == "Launch Statistics"
                    ):
                        try:
                            value = int(float(parts[-1].replace(",", "")))
                            current_kernel["grid_size"] = value
                        except (ValueError, IndexError):
                            pass

            # Parse recommendations (OPT and INF markers)
            if stripped.startswith("OPT") or stripped.startswith("INF"):
                in_recommendation = True
                recommendation_lines = [stripped]

                # Extract estimated speedup
                if current_kernel and "Est. Speedup:" in stripped:
                    speedup_match = re.search(r"Est\. Speedup:\s*([\d.]+)%", stripped)
                    if speedup_match:
                        try:
                            speedup = float(speedup_match.group(1))
                            if speedup > current_kernel["estimated_speedup_pct"]:
                                current_kernel["estimated_speedup_pct"] = speedup
                        except ValueError:
                            pass

                if current_kernel and "Est. Local Speedup:" in stripped:
                    speedup_match = re.search(
                        r"Est\. Local Speedup:\s*([\d.]+)%", stripped
                    )
                    if speedup_match:
                        try:
                            speedup = float(speedup_match.group(1))
                            if speedup > current_kernel["estimated_speedup_pct"]:
                                current_kernel["estimated_speedup_pct"] = speedup
                        except ValueError:
                            pass
            elif in_recommendation:
                if line.startswith("          ") and stripped:
                    recommendation_lines.append(stripped)
                elif (
                    stripped.startswith("Section:")
                    or stripped.startswith("---")
                    or (stripped and not line.startswith(" "))
                ):
                    if recommendation_lines:
                        full_rec = " ".join(recommendation_lines)
                        if full_rec not in summary["recommendations"]:
                            summary["recommendations"].append(full_rec)
                        if (
                            current_kernel
                            and full_rec not in current_kernel["recommendations"]
                        ):
                            current_kernel["recommendations"].append(full_rec)
                    in_recommendation = False
                    recommendation_lines = []

            i += 1

        # Capture last recommendation if any
        if recommendation_lines:
            full_rec = " ".join(recommendation_lines)
            if full_rec not in summary["recommendations"]:
                summary["recommendations"].append(full_rec)
            if current_kernel and full_rec not in current_kernel["recommendations"]:
                current_kernel["recommendations"].append(full_rec)

    return summary


def _generate_text_output(filename: str, summary: dict) -> str:
    """Generate human-readable markdown text from summary."""
    timestamp = datetime.now().isoformat()

    lines = [
        "# NCU Profiling Analysis",
        f"Source: {filename}",
        f"Generated: {timestamp}",
        "",
        "## GPU Information",
        f"- Device: {summary.get('gpu', 'Unknown')}",
        "",
        "## Kernel Summary",
        "",
    ]

    for kernel in summary.get("kernels", []):
        lines.extend(
            [
                f"### {kernel['name']}",
                f"- Duration: {kernel.get('duration_us', 0):.2f} us ({kernel.get('duration_ms', 0):.3f} ms)",
                f"- Achieved Occupancy: {kernel.get('achieved_occupancy_pct', 0):.1f}%",
                f"- Compute (SM) Throughput: {kernel.get('compute_throughput_pct', 0):.1f}%",
                f"- Memory Throughput: {kernel.get('memory_throughput_pct', 0):.1f}%",
                f"- Registers/Thread: {kernel.get('registers_per_thread', 0)}",
                f"- Block Size: {kernel.get('block_size', 0)}",
                f"- Grid Size: {kernel.get('grid_size', 0)}",
                "",
            ]
        )

    if summary.get("recommendations"):
        lines.extend(
            [
                "## Recommendations",
                "",
            ]
        )
        for i, rec in enumerate(summary["recommendations"], 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    return "\n".join(lines)


def _analyze_local(
    filepath: Path,
    ncu_path: str,
    output_dir: Path | None = None,
    json_output: bool = False,
) -> str:
    """Analyze NCU profile locally using installed NCU."""
    # Run NCU to get session and details
    try:
        session_result = subprocess.run(
            [ncu_path, "--import", str(filepath), "--page", "session"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        details_result = subprocess.run(
            [ncu_path, "--import", str(filepath), "--page", "details"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("NCU command timed out (120s limit)") from e

    # Parse the outputs
    summary = _parse_ncu_output(session_result.stdout, details_result.stdout)

    # Save to output directory if specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        txt_filename = f"ncu_analysis_{filepath.stem}_{timestamp}.txt"
        txt_path = output_dir / txt_filename
        txt_path.write_text(_generate_text_output(filepath.name, summary))

    if json_output:
        return json.dumps(summary, indent=2)
    else:
        return _generate_text_output(filepath.name, summary)


def _analyze_remote_direct(
    filepath: Path,
    target_name: str,
    json_output: bool = False,
) -> str:
    """Analyze NCU profile remotely via direct SSH to target.

    Uploads the .ncu-rep file and runs NCU analysis on the target machine.
    """
    import sys
    import tempfile

    from .gpu_run import push_directory, run_command_capture
    from .targets import load_target

    # Load target
    try:
        target = load_target(target_name)
    except FileNotFoundError as e:
        raise RuntimeError(f"Target not found: {target_name}") from e

    # Create temp directory with just the .ncu-rep file
    # Use a unique name based on the file
    workspace_name = f"ncu_analyze_{filepath.stem}"

    with tempfile.TemporaryDirectory() as tmpdir:
        import shutil
        # Create a directory with the workspace name
        tmp_path = Path(tmpdir) / workspace_name
        tmp_path.mkdir()
        shutil.copy(filepath, tmp_path / filepath.name)

        # Push the file
        print(f"Uploading {filepath.name} to {target_name}...", file=sys.stderr)
        push_directory(tmp_path, target)

    # Run NCU commands - workspace_name is used (not full path)
    ncu_cmd = f"/usr/local/cuda/bin/ncu --import {filepath.name} --page session && echo '---NCU_SEPARATOR---' && /usr/local/cuda/bin/ncu --import {filepath.name} --page details"

    print("Running NCU analysis...", file=sys.stderr)
    exit_code, output = run_command_capture(ncu_cmd, workspace_name, target)

    if exit_code != 0:
        raise RuntimeError(f"NCU command failed with exit code {exit_code}")

    # Split session and details output
    if "---NCU_SEPARATOR---" in output:
        parts = output.split("---NCU_SEPARATOR---")
        session_output = parts[0].strip()
        details_output = parts[1].strip() if len(parts) > 1 else ""
    else:
        session_output = ""
        details_output = output

    # Parse the outputs
    summary = _parse_ncu_output(session_output, details_output)

    if json_output:
        return json.dumps(summary, indent=2)
    else:
        return _generate_text_output(filepath.name, summary)


def _analyze_remote_api(
    filepath: Path,
    json_output: bool = False,
) -> str:
    """Analyze NCU profile remotely via wafer-api.

    Uploads the .ncu-rep file and runs NCU analysis on a remote GPU machine.
    """
    import base64

    import httpx

    from .api_client import get_api_url
    from .auth import get_auth_headers

    # Read and encode the file
    file_content = filepath.read_bytes()
    file_b64 = base64.b64encode(file_content).decode()

    # Build request - upload file and run ncu commands
    request_body = {
        "files": [
            {
                "path": filepath.name,
                "content": file_b64,
            }
        ],
        "workspace_name": f"ncu_analyze_{filepath.stem}",
        # Run NCU to get session and details output
        "command": f"/usr/local/cuda/bin/ncu --import {filepath.name} --page session && echo '---NCU_SEPARATOR---' && /usr/local/cuda/bin/ncu --import {filepath.name} --page details",
    }

    api_url = get_api_url()
    headers = get_auth_headers()

    # Collect all output
    output_lines: list[str] = []

    try:
        with httpx.Client(timeout=None, headers=headers) as client:
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
                            raise RuntimeError(content[8:])  # Strip "[ERROR] "
                        else:
                            output_lines.append(content)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise RuntimeError("Not authenticated. Run: wafer login") from e
        raise RuntimeError(f"API error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"Could not reach API: {e}") from e

    # Parse the combined output
    full_output = "\n".join(output_lines)

    # Split session and details output
    if "---NCU_SEPARATOR---" in full_output:
        parts = full_output.split("---NCU_SEPARATOR---")
        session_output = parts[0].strip()
        details_output = parts[1].strip() if len(parts) > 1 else ""
    else:
        # Fallback: treat all as details
        session_output = ""
        details_output = full_output

    # Parse the outputs
    summary = _parse_ncu_output(session_output, details_output)

    if json_output:
        return json.dumps(summary, indent=2)
    else:
        return _generate_text_output(filepath.name, summary)


def analyze_ncu_profile(
    filepath: Path,
    output_dir: Path | None = None,
    json_output: bool = False,
    remote: bool | None = None,
    target: str | None = None,
) -> str:
    """Analyze an NCU profile file and return results.

    Args:
        filepath: Path to .ncu-rep file
        output_dir: Optional directory to save analysis files
        json_output: If True, return raw JSON; otherwise return formatted text
        remote: If True, force remote analysis via API. If False, force local.
                If None (default), auto-detect: use local if NCU available, else remote.
        target: Target name for direct SSH mode (e.g., "vultr-b200"). If provided,
                uses direct SSH instead of API for remote analysis.

    Returns:
        Analysis results as string (JSON or markdown)

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If NCU parsing fails
    """
    ncu_path = _find_ncu()

    # If target is provided, use direct SSH mode
    if target is not None:
        if output_dir:
            import sys
            print("Warning: --output-dir not supported for remote analysis", file=sys.stderr)
        return _analyze_remote_direct(filepath, target, json_output)

    # Determine whether to use local or remote
    use_remote = remote
    if use_remote is None:
        # Auto-detect: use remote if NCU not available locally
        use_remote = ncu_path is None

    if use_remote:
        # Note: output_dir not supported for remote (would need to download results)
        if output_dir:
            import sys
            print("Warning: --output-dir not supported for remote analysis", file=sys.stderr)
        return _analyze_remote_api(filepath, json_output)
    else:
        if ncu_path is None:
            install_cmd = _get_install_command()
            raise FileNotFoundError(
                f"NCU not installed. Install with: {install_cmd}"
            )
        return _analyze_local(filepath, ncu_path, output_dir, json_output)
