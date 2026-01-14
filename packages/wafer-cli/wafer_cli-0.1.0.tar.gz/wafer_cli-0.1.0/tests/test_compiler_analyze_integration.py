"""Integration tests for wafer compiler-analyze CLI command.

Tests the compiler-analyze command end-to-end, verifying:
- CLI command execution
- JSON output format
- Error handling
- Various input combinations
"""

import json
import subprocess

import pytest

# Constants
CLI_TIMEOUT_SECONDS = 30
CLI_COMMAND = "wafer"
COMPILER_ANALYZE_SUBCOMMAND = "compiler-analyze"
JSON_FLAG = "--json"
MLIR_FLAG = "--mlir-text"
PTX_FLAG = "--ptx-text"
SASS_FLAG = "--sass-text"
SOURCE_FLAG = "--source-text"
KERNEL_NAME_FLAG = "--kernel-name"

SUCCESS_KEY = "success"
DATA_KEY = "data"
ERROR_KEY = "error"
KERNEL_NAME_KEY = "kernel_name"
MLIR_TEXT_KEY = "mlir_text"
PTX_TEXT_KEY = "ptx_text"
SASS_TEXT_KEY = "sass_text"
SOURCE_CODE_KEY = "source_code"
PARSED_MLIR_KEY = "parsed_mlir"
PARSED_PTX_KEY = "parsed_ptx"
PARSED_SASS_KEY = "parsed_sass"
LAYOUTS_KEY = "layouts"
MEMORY_PATHS_KEY = "memory_paths"
PIPELINE_STAGES_KEY = "pipeline_stages"


def test_compiler_analyze_basic() -> None:
    """Test basic compiler-analyze with minimal inputs."""
    mlir_text = "module { func @kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80\n.entry kernel() { ret; }"
    sass_text = "// SASS code"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stderr is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    assert output_json.get(SUCCESS_KEY) is True
    assert DATA_KEY in output_json
    
    data = output_json[DATA_KEY]
    assert isinstance(data, dict)
    assert KERNEL_NAME_KEY in data
    assert MLIR_TEXT_KEY in data
    assert PTX_TEXT_KEY in data
    assert SASS_TEXT_KEY in data


def test_compiler_analyze_with_source_code() -> None:
    """Test compiler-analyze with optional source code."""
    mlir_text = "module { func @test_kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80"
    sass_text = "// SASS"
    source_code = "__global__ void test_kernel() { }"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
        SOURCE_FLAG, source_code,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stderr is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    assert output_json.get(SUCCESS_KEY) is True
    assert DATA_KEY in output_json
    
    data = output_json[DATA_KEY]
    assert isinstance(data, dict)
    assert data.get(SOURCE_CODE_KEY) == source_code


def test_compiler_analyze_with_kernel_name() -> None:
    """Test compiler-analyze with explicit kernel name."""
    mlir_text = "module { func @my_kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80"
    sass_text = "// SASS"
    kernel_name = "my_custom_kernel"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
        KERNEL_NAME_FLAG, kernel_name,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stderr is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    assert output_json.get(SUCCESS_KEY) is True
    assert DATA_KEY in output_json
    
    data = output_json[DATA_KEY]
    assert isinstance(data, dict)
    assert data.get(KERNEL_NAME_KEY) == kernel_name


def test_compiler_analyze_missing_required_args() -> None:
    """Test compiler-analyze fails gracefully when required args are missing."""
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    stdout_has_content = len(result.stdout.strip()) > 0
    
    if stdout_has_content:
        output_json = json.loads(result.stdout)
        assert isinstance(output_json, dict)
        success_value = output_json.get(SUCCESS_KEY)
        has_error = ERROR_KEY in output_json
        assert success_value is False or has_error
    else:
        has_nonzero_exit = result.returncode != 0
        has_stderr = len(result.stderr) > 0
        assert has_nonzero_exit or has_stderr


def test_compiler_analyze_partial_inputs() -> None:
    """Test compiler-analyze with only some inputs provided."""
    mlir_text = "module { func @kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80"
    empty_sass = ""
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, empty_sass,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stderr is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    has_success = SUCCESS_KEY in output_json
    has_error = ERROR_KEY in output_json
    assert has_success or has_error


def test_compiler_analyze_output_structure() -> None:
    """Test compiler-analyze output has expected structure."""
    mlir_text = "module { func @kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80"
    sass_text = "// SASS"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stdout is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    
    data = output_json.get(DATA_KEY, {})
    assert isinstance(data, dict)
    
    expected_fields = [
        KERNEL_NAME_KEY,
        MLIR_TEXT_KEY,
        PTX_TEXT_KEY,
        SASS_TEXT_KEY,
        PARSED_MLIR_KEY,
        PARSED_PTX_KEY,
        PARSED_SASS_KEY,
        LAYOUTS_KEY,
        MEMORY_PATHS_KEY,
        PIPELINE_STAGES_KEY,
    ]
    
    for field in expected_fields:
        assert field in data


def test_compiler_analyze_error_handling() -> None:
    """Test compiler-analyze handles invalid inputs gracefully."""
    invalid_mlir = "{ invalid json }"
    ptx_text = ".version 8.0"
    sass_text = "// SASS"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, invalid_mlir,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
        JSON_FLAG
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.stdout is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
    
    has_success = SUCCESS_KEY in output_json
    has_error = ERROR_KEY in output_json
    assert has_success or has_error


def test_compiler_analyze_no_json_flag() -> None:
    """Test compiler-analyze without --json flag (should still work)."""
    mlir_text = "module { func @kernel() { } }"
    ptx_text = ".version 8.0\n.target sm_80"
    sass_text = "// SASS"
    
    args = [
        CLI_COMMAND,
        COMPILER_ANALYZE_SUBCOMMAND,
        MLIR_FLAG, mlir_text,
        PTX_FLAG, ptx_text,
        SASS_FLAG, sass_text,
    ]
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0
    assert result.stdout is not None
    
    output_json = json.loads(result.stdout)
    assert isinstance(output_json, dict)
