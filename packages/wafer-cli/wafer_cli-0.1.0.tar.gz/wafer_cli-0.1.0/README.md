# Wafer CLI

Run commands on remote GPUs in Docker containers.

## Installation

```bash
cd apps/wafer-cli
uv sync
```

## Quick Start

```bash
# Login with GitHub
wafer login

# Run a command on remote GPU
wafer remote-run -- nvidia-smi

# Run Python script with file upload
wafer remote-run --upload-dir ./my_project -- python3 train.py

# Check who you're logged in as
wafer whoami
```

## Commands

### `wafer login`

Authenticate with GitHub OAuth. Opens browser for login flow.

```bash
wafer login
```

Credentials are stored in `~/.wafer/credentials.json`.

### `wafer remote-run`

Run any command on a remote GPU inside a Docker container.

```bash
# Basic: run a command
wafer remote-run -- nvidia-smi

# Upload files first, then run
wafer remote-run --upload-dir ./my_project -- python3 main.py

# Custom Docker image
wafer remote-run --image pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel -- python3 -c "import torch; print(torch.cuda.get_device_name())"

# With custom entrypoint (for images with non-shell defaults)
wafer remote-run --image vllm/vllm-openai:latest --docker-entrypoint bash -- python3 script.py
```

Options:
- `--upload-dir <path>` - Upload local directory before running command
- `--image <image>` - Docker image to use (default: vllm/vllm-openai:latest)
- `--docker-entrypoint <cmd>` - Override container entrypoint
- `--pull-image` - Pull image even if it exists locally
- `--require-hwc` - Require hardware counters (for NCU profiling)

### `wafer push`

Upload files to a remote workspace (for multi-command workflows).

```bash
# Push files
wafer push ./my_project

# Returns workspace_id for use with remote-run
# Example: ws_abc123
```

### `wafer logout`

Remove stored credentials.

```bash
wafer logout
```

### `wafer whoami`

Show current authenticated user.

```bash
wafer whoami
# Output: Logged in as user@example.com
```

## Examples

### Run PyTorch training

```bash
wafer remote-run --upload-dir ./training -- python3 train.py --epochs 10
```

### Profile with NCU

```bash
wafer remote-run --require-hwc --upload-dir ./kernel -- ncu --set full python3 benchmark.py
```

### Interactive debugging

```bash
# Upload once
WORKSPACE=$(wafer push ./project)

# Run multiple commands against same workspace
wafer remote-run --workspace-id $WORKSPACE -- python3 test1.py
wafer remote-run --workspace-id $WORKSPACE -- python3 test2.py
```

### Custom CUDA image

```bash
wafer remote-run \
  --image nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04 \
  --upload-dir ./cuda_kernels \
  -- nvcc -o kernel kernel.cu && ./kernel
```

---

## Architecture

```
CLI                              wafer-api                         GPU
 |                                   |                               |
 |-- POST /v1/gpu/jobs ------------->|                               |
 |   { command, files[], image }     |                               |
 |                                   |-- SSH upload + docker ------->|
 |<-- SSE stream: stdout/stderr -----|<-- stream output -------------|
 |                                   |                               |
```

### Components

- **wafer-cli** (`apps/wafer-cli/`) - Thin client that calls wafer-api
- **wafer-api** (`services/wafer-api/`) - Backend that owns GPU targets and SSH credentials
- **wafer-core** (`packages/wafer-core/`) - Internal SSH client for file upload and command execution

### Why API-backed?

- **Security**: SSH credentials stay on server, not in client config
- **Routing**: Backend picks best available GPU based on requirements
- **Multi-tenant**: Multiple users share GPU pool without credential management

## Local Target Management (Advanced)

For direct SSH access (bypassing wafer-api), you can configure local targets:

```bash
wafer targets list
wafer targets add examples/targets/my-gpu.toml
wafer targets default my-gpu
```

See `examples/targets/` for TOML format.

## Testing

### Prerequisites

1. Start the wafer-api server:
   ```bash
   cd services/wafer-api && uv run uvicorn src.main:app --port 8000
   ```

2. Authenticate (if not already logged in):
   ```bash
   cd apps/wafer-cli && uv run wafer login
   ```

### Run Integration Tests

```bash
# GPU API tests (push, jobs, cancellation)
python scripts/test_gpu_api.py --no-server

# CLI remote-run tests (basic, upload-dir, nested)
python scripts/test_cli_remote_run.py --no-server
```

### Manual Command Tests

```bash
cd apps/wafer-cli

# wafer remote-run (via API)
uv run wafer remote-run -- nvidia-smi

# wafer remote-run with file upload
uv run wafer remote-run --upload-dir ./my_project -- python script.py

# wafer ncu-analyze (via API)
uv run wafer ncu-analyze path/to/profile.ncu-rep --remote

# wafer ask-docs (requires docs-tool running on port 8002)
WAFER_DOCS_URL=http://localhost:8002 uv run wafer ask-docs "What is a Triton kernel?"

# wafer wevin with --tools and --json flags
uv run wafer wevin --ref kernel.py --desc "Optimize" --test "n=128" --tools read,write,edit --json --no-tui --max-turns 1
```

### Expected Results

- All integration tests should pass
- `wafer remote-run` executes commands on remote GPU via API
- `wafer ncu-analyze --remote` uploads profile and returns analysis
- All SSH operations use internal `wafer_core.ssh.SSHClient`

## Requirements

- Python 3.10+
- GitHub account (for authentication)
