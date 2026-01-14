"""Tool definitions for GPU benchmark environments.

Shared tool definitions that can be imported by any environment that needs them.

Tiger Style:
- Explicit tool definitions
- Single source of truth
- No dynamic generation
"""

from wafer_core.rollouts.dtypes import Tool, ToolFunction, ToolFunctionParameter

# Individual tool definitions
ls_files_tool = Tool(
    type="function",
    function=ToolFunction(
        name="ls_files",
        description="List all files and directories in the workspace. Use '.' for current directory.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "dirpath": {
                    "type": "string",
                    "description": "Directory path relative to workspace (default '.')",
                }
            },
        ),
        required=[],
    ),
)

read_file_tool = Tool(
    type="function",
    function=ToolFunction(
        name="read_file",
        description="Read the contents of a file from the workspace.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={"filepath": {"type": "string", "description": "Path to file relative to workspace"}},
        ),
        required=["filepath"],
    ),
)

write_file_tool = Tool(
    type="function",
    function=ToolFunction(
        name="write_file",
        description="Write content to a file in the workspace. Creates or overwrites the file.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "filepath": {"type": "string", "description": "Path to file relative to workspace"},
                "content": {"type": "string", "description": "Content to write to file"},
            },
        ),
        required=["filepath", "content"],
    ),
)

edit_file_tool = Tool(
    type="function",
    function=ToolFunction(
        name="edit_file",
        description="Edit a file by replacing exact string matches. Fails if string is ambiguous.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "filepath": {"type": "string", "description": "Path to file relative to workspace"},
                "old_string": {"type": "string", "description": "Exact string to find and replace"},
                "new_string": {"type": "string", "description": "Replacement string"},
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences (default false)",
                },
            },
        ),
        required=["filepath", "old_string", "new_string"],
    ),
)

submit_kernel_tool = Tool(
    type="function",
    function=ToolFunction(
        name="submit_kernel",
        description="Submit a kernel file for correctness and performance testing on remote GPU.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "filepath": {
                    "type": "string",
                    "description": "Path to kernel file relative to workspace",
                }
            },
        ),
        required=["filepath"],
    ),
)

ncu_profile_tool = Tool(
    type="function",
    function=ToolFunction(
        name="ncu_profile",
        description="Profile a kernel with NVIDIA Nsight Compute. Saves comprehensive metrics to an artifact and returns a profile_id. Use after submit_kernel passes correctness. Call get_profile_insights with the profile_id to analyze results.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "filepath": {
                    "type": "string",
                    "description": "Path to kernel file relative to workspace",
                }
            },
        ),
        required=["filepath"],
    ),
)

get_profile_insights_tool = Tool(
    type="function",
    function=ToolFunction(
        name="get_profile_insights",
        description="Get performance insights from a saved NCU profile. Returns utilization metrics, cache stats, bottleneck analysis, and optimization suggestions. Can be called multiple times on the same profile. Compare profiles by calling this tool twice with different profile_ids. Use include_code=true to see the kernel source alongside metrics for correlating slow code patterns.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "profile_id": {
                    "type": "string",
                    "description": "Profile identifier returned by ncu_profile (e.g., 'profile_kernel_v3_20251127_143022')",
                },
                "include_code": {
                    "type": "boolean",
                    "description": "Include kernel source code in output for correlating metrics with code patterns (default: false)",
                },
            },
        ),
        required=["profile_id"],
    ),
)

nsys_analyze_tool = Tool(
    type="function",
    function=ToolFunction(
        name="nsys_analyze",
        description="Analyze an NSYS system-level profile (.nsys-rep file). Uploads file to GPU server, runs analysis, and returns timeline/kernel/memory metrics. Returns report_id for retrieving detailed data. Use for system-level profiling (GPU+CPU timeline, memory transfers, kernel launches).",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "file_content": {
                    "type": "string",
                    "description": "Base64-encoded content of the .nsys-rep file",
                },
                "filename": {
                    "type": "string",
                    "description": "Original filename (must end with .nsys-rep)",
                },
            },
        ),
        required=["file_content", "filename"],
    ),
)
