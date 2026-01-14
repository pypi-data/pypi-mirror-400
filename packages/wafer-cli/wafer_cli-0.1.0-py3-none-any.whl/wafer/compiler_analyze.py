"""Compiler Analyzer - Analyze MLIR/PTX/SASS kernels.

This module provides the implementation for the `wafer compiler-analyze` command.
"""

import json
from pathlib import Path


def analyze_kernel(
    mlir_text: str,
    ptx_text: str,
    sass_text: str,
    source_code: str | None = None,
    kernel_name: str | None = None,
    json_output: bool = True,
) -> dict:
    """Analyze kernel using wafer_core.tools.cutedsl_analyzer.analyze_kernel.

    Returns dict representation of AnalysisResult for JSON serialization.
    """
    from dataclasses import asdict

    from wafer_core.tools.cutedsl_analyzer import analyze_kernel as core_analyze
    
    result = core_analyze(mlir_text, ptx_text, sass_text, source_code, kernel_name)

    if hasattr(result, "__dataclass_fields__"):
        return asdict(result)
    elif hasattr(result, "__dict__"):
        return result.__dict__
    return result


def analyze_compiler_kernel(
    mlir_file: Path | None = None,
    ptx_file: Path | None = None,
    sass_file: Path | None = None,
    source_file: Path | None = None,
    mlir_text: str | None = None,
    ptx_text: str | None = None,
    sass_text: str | None = None,
    source_text: str | None = None,
    kernel_name: str | None = None,
    json_output: bool = True,
) -> str:
    mlir_content = mlir_text or (mlir_file.read_text() if mlir_file else "")
    ptx_content = ptx_text or (ptx_file.read_text() if ptx_file else "")
    sass_content = sass_text or (sass_file.read_text() if sass_file else "")
    source_content = source_text or (source_file.read_text() if source_file else None)

    assert mlir_content or ptx_content or sass_content, (
        "At least one of --mlir-text, --ptx-text, or --sass-text must be provided"
    )

    result = analyze_kernel(
        mlir_content, ptx_content, sass_content, source_content, kernel_name, json_output
    )

    if json_output:
        return json.dumps({"success": True, "data": result}, indent=2, default=str)
    else:
        return str(result)
