"""
Kernel Analyzer Tool

Provides the analyze_kernel tool for analyzing CUDA kernel compilation artifacts
(MLIR, PTX, SASS) to extract performance insights, memory paths, pipeline structure, and layouts.
"""

from dataclasses import asdict

from wafer_core.rollouts.dtypes import (
    Tool,
    ToolCall,
    ToolFunction,
    ToolFunctionParameter,
    ToolResult,
)


ANALYZE_KERNEL_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="analyze_kernel",
        description="Analyze CUDA kernel compilation artifacts (MLIR, PTX, SASS) to extract performance insights, memory paths, pipeline structure, and layouts.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "mlir_text": {"type": "string", "description": "MLIR intermediate representation"},
                "ptx_text": {"type": "string", "description": "PTX assembly code"},
                "sass_text": {"type": "string", "description": "SASS binary disassembly"},
                "source_code": {"type": "string", "description": "Optional: original CUDA source for correlation"},
                "kernel_name": {"type": "string", "description": "Optional: kernel function name"},
            }
        ),
        required=["mlir_text", "ptx_text", "sass_text"]
    )
)


async def exec_analyze_kernel(tool_call: ToolCall) -> ToolResult:
    """Execute analyze_kernel tool.
    
    Analyzes CUDA kernel compilation artifacts (MLIR, PTX, SASS) and returns
    structured analysis including layouts, memory paths, pipeline structure.
    """
    mlir_text = tool_call.args.get("mlir_text", "")
    ptx_text = tool_call.args.get("ptx_text", "")
    sass_text = tool_call.args.get("sass_text", "")
    source_code = tool_call.args.get("source_code")
    kernel_name = tool_call.args.get("kernel_name")
    
    # Validate inputs - at least one must be provided
    if not mlir_text and not ptx_text and not sass_text:
        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=True,
            content="",
            error="At least one of mlir_text, ptx_text, or sass_text must be provided"
        )
    
    # Call pure function (business logic)
    from wafer_core.tools.cutedsl_analyzer import analyze_kernel
    
    try:
        result = analyze_kernel(
            mlir_text=mlir_text,
            ptx_text=ptx_text,
            sass_text=sass_text,
            source_code=source_code,
            kernel_name=kernel_name
        )
        
        # Format result for LLM
        result_str = format_analysis_result(result)
        
        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=False,
            content=result_str
        )
    except Exception as e:
        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=True,
            content="",
            error=f"Analysis failed: {str(e)}"
        )


def format_analysis_result(result: object) -> str:
    """Format AnalysisResult for LLM consumption."""
    # Convert dataclass to dict
    if hasattr(result, '__dataclass_fields__'):
        result_dict = asdict(result)
    elif hasattr(result, '__dict__'):
        result_dict = result.__dict__
    else:
        result_dict = {"kernel_name": str(result)}
    
    # Format as readable text
    lines = [
        f"Kernel Analysis: {result_dict.get('kernel_name', 'unknown')}",
        "",
        "=== Summary ===",
        f"Kernel Name: {result_dict.get('kernel_name', 'unknown')}",
    ]
    
    # Add parsed counts if available
    parsed_mlir = result_dict.get('parsed_mlir', {})
    parsed_ptx = result_dict.get('parsed_ptx', {})
    parsed_sass = result_dict.get('parsed_sass', {})
    
    if isinstance(parsed_mlir, dict):
        mlir_ops = parsed_mlir.get('ops', [])
        if isinstance(mlir_ops, (list, tuple)):
            lines.append(f"MLIR Operations: {len(mlir_ops)}")
    
    if isinstance(parsed_ptx, dict):
        ptx_instructions = parsed_ptx.get('instructions', [])
        if isinstance(ptx_instructions, (list, tuple)):
            lines.append(f"PTX Instructions: {len(ptx_instructions)}")
    
    if isinstance(parsed_sass, dict):
        sass_instructions = parsed_sass.get('instructions', [])
        if isinstance(sass_instructions, (list, tuple)):
            lines.append(f"SASS Instructions: {len(sass_instructions)}")
    
    lines.append("")
    
    # Add layouts if available
    layouts = result_dict.get('layouts', [])
    if layouts:
        lines.append("=== Layouts ===")
        for i, layout in enumerate(layouts[:5]):  # Limit to first 5
            if isinstance(layout, dict):
                name = layout.get('name', f'Layout {i + 1}')
                shape = layout.get('shape', [])
                lines.append(f"  - {name}: shape={shape}")
            else:
                lines.append(f"  - {layout}")
        if len(layouts) > 5:
            lines.append(f"  ... and {len(layouts) - 5} more")
        lines.append("")
    
    # Add memory paths if available
    memory_paths = result_dict.get('memory_paths', [])
    if memory_paths:
        lines.append("=== Memory Paths ===")
        for i, path in enumerate(memory_paths[:5]):  # Limit to first 5
            if isinstance(path, dict):
                desc = path.get('description', path.get('path', f'Path {i + 1}'))
                lines.append(f"  - {desc}")
            else:
                lines.append(f"  - {path}")
        if len(memory_paths) > 5:
            lines.append(f"  ... and {len(memory_paths) - 5} more")
        lines.append("")
    
    # Add pipeline stages if available
    pipeline_stages = result_dict.get('pipeline_stages', [])
    if pipeline_stages:
        lines.append("=== Pipeline Stages ===")
        for i, stage in enumerate(pipeline_stages[:5]):  # Limit to first 5
            if isinstance(stage, dict):
                stage_id = stage.get('stage_id', i)
                desc = stage.get('description', stage.get('name', f'Stage {stage_id}'))
                lines.append(f"  - Stage {stage_id}: {desc}")
            else:
                lines.append(f"  - {stage}")
        if len(pipeline_stages) > 5:
            lines.append(f"  ... and {len(pipeline_stages) - 5} more")
        lines.append("")
    
    return "\n".join(lines)
