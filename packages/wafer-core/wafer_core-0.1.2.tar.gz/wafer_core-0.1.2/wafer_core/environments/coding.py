"""
Coding environment with minimal toolset for code editing tasks.

Tools: read, write, edit, bash, wafer, analyze_kernel
Inspired by pi-mono's minimalist approach.

The 'wafer' tool provides access to wafer subcommands (ask-docs, ncu-analyze,
remote-run, etc.) while keeping them separate from general bash access.

The 'analyze_kernel' tool is provided via kernel_analyzer_tool module.
"""

import os
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import trio

from wafer_core.rollouts.dtypes import (
    AgentState,
    Message,
    RunConfig,
    Tool,
    ToolCall,
    ToolFunction,
    ToolFunctionParameter,
    ToolResult,
)

MAX_LINES = 2000
MAX_LINE_LENGTH = 2000
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB

# All wafer subcommands (used for --tools filtering)
# These can be passed to --tools like: --tools read,write,ask-docs,ncu-analyze
WAFER_SUBCOMMANDS = {
    "ask-docs",
    "ncu-analyze",
    "remote-run",
    "push",
    "evaluate",
    "targets",
}

# Blocked subcommands (require --allow-spawn)
BLOCKED_WAFER_SUBCOMMANDS = {
    "wevin",
}


def expand_path(file_path: str) -> Path:
    """Expand ~ to home directory and resolve path."""
    if file_path == "~":
        return Path.home()
    if file_path.startswith("~/"):
        return Path.home() / file_path[2:]
    return Path(file_path).resolve()


def _shorten_path(path: str) -> str:
    """Convert absolute path to tilde notation if in home directory."""
    home = os.path.expanduser("~")
    if path.startswith(home):
        return "~" + path[len(home):]
    return path


def generate_diff(old_content: str, new_content: str, context_lines: int = 3) -> str:
    """Generate unified diff string with line numbers in gutter."""
    old_lines = old_content.split("\n")
    new_lines = new_content.split("\n")

    output = []
    max_line_num = max(len(old_lines), len(new_lines))
    line_num_width = len(str(max_line_num))

    # Find common prefix
    i = 0
    while i < len(old_lines) and i < len(new_lines) and old_lines[i] == new_lines[i]:
        i += 1

    # Find common suffix
    j_old = len(old_lines) - 1
    j_new = len(new_lines) - 1
    while j_old >= i and j_new >= i and old_lines[j_old] == new_lines[j_new]:
        j_old -= 1
        j_new -= 1

    # Show context before changes
    context_start = max(0, i - context_lines)
    if context_start > 0:
        output.append("     ...")

    for line_idx in range(context_start, i):
        line_num = str(line_idx + 1).rjust(line_num_width)
        output.append(f"{line_num}   {old_lines[line_idx]}")

    # Show removed lines
    for line_idx in range(i, j_old + 1):
        line_num = str(line_idx + 1).rjust(line_num_width)
        output.append(f"{line_num} - {old_lines[line_idx]}")

    # Show added lines
    new_line_start = i
    for idx, line_idx in enumerate(range(i, j_new + 1)):
        line_num = str(new_line_start + idx + 1).rjust(line_num_width)
        output.append(f"{line_num} + {new_lines[line_idx]}")

    # Show context after changes
    context_end = min(len(new_lines), j_new + 2 + context_lines)
    for line_idx in range(j_new + 1, context_end):
        line_num = str(line_idx + 1).rjust(line_num_width)
        output.append(f"{line_num}   {new_lines[line_idx]}")

    if context_end < len(new_lines):
        output.append("     ...")

    return "\n".join(output)


# ── Tool Definitions ──────────────────────────────────────────────────────────

READ_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="read",
        description="Read the contents of a file. Defaults to first 2000 lines. Use offset/limit for large files.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "path": {"type": "string", "description": "Path to the file to read (relative or absolute)"},
                "offset": {"type": "integer", "description": "Line number to start reading from (1-indexed)"},
                "limit": {"type": "integer", "description": "Maximum number of lines to read"},
            }
        ),
        required=["path"]
    )
)

WRITE_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="write",
        description="Write content to a file. Creates the file if it doesn't exist, overwrites if it does. Automatically creates parent directories.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "path": {"type": "string", "description": "Path to the file to write (relative or absolute)"},
                "content": {"type": "string", "description": "Content to write to the file"},
            }
        ),
        required=["path", "content"]
    )
)

EDIT_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="edit",
        description="Edit a file by replacing exact text. The old_text must match exactly (including whitespace). Use this for precise, surgical edits.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "path": {"type": "string", "description": "Path to the file to edit (relative or absolute)"},
                "old_text": {"type": "string", "description": "Exact text to find and replace (must match exactly)"},
                "new_text": {"type": "string", "description": "New text to replace the old text with"},
            }
        ),
        required=["path", "old_text", "new_text"]
    )
)

BASH_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="bash",
        description="Execute a bash command in the current working directory. Returns stdout and stderr. Do not use for wafer commands - use the 'wafer' tool instead.",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "command": {"type": "string", "description": "Bash command to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default: 120)"},
            }
        ),
        required=["command"]
    )
)

WAFER_TOOL = Tool(
    type="function",
    function=ToolFunction(
        name="wafer",
        description="Execute a wafer CLI command. Available subcommands: ask-docs (query GPU documentation), ncu-analyze (analyze NCU profiles), remote-run (run on remote GPU), push (push files to remote), evaluate (run kernel evaluation).",
        parameters=ToolFunctionParameter(
            type="object",
            properties={
                "subcommand": {"type": "string", "description": "Wafer subcommand to run (e.g., 'ask-docs', 'ncu-analyze', 'remote-run')"},
                "args": {"type": "string", "description": "Arguments to pass to the subcommand"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default: 300)"},
            }
        ),
        required=["subcommand"]
    )
)

ALL_TOOLS = {
    "read": READ_TOOL,
    "write": WRITE_TOOL,
    "edit": EDIT_TOOL,
    "bash": BASH_TOOL,
    "wafer": WAFER_TOOL,
    "analyze_kernel": ANALYZE_KERNEL_TOOL,
}


# Base tools (not wafer subcommands)
BASE_TOOLS = {"read", "write", "edit", "bash"}


@dataclass
class CodingEnvironment:
    """Local filesystem environment with read, write, edit, bash, wafer, analyze_kernel tools.

    Args:
        working_dir: Working directory for file operations and commands.
        enabled_tools: List of tool names to enable. If None, all tools enabled.
            Can include base tools (read, write, edit, bash), analyze_kernel, and wafer subcommands
            (ask-docs, ncu-analyze, remote-run, push, evaluate, targets).
            The 'wafer' tool is automatically enabled if any wafer subcommand is enabled.
        allow_spawn: Allow wafer tool to spawn sub-wevin agents (wevin subcommand).
    """

    working_dir: Path = field(default_factory=Path.cwd)
    enabled_tools: list[str] | None = None
    allow_spawn: bool = False

    def _get_enabled_subcommands(self) -> set[str]:
        """Get the set of enabled wafer subcommands."""
        if self.enabled_tools is None:
            # All subcommands enabled by default
            return WAFER_SUBCOMMANDS.copy()

        # Filter to only wafer subcommands that are in enabled_tools
        return {t for t in self.enabled_tools if t in WAFER_SUBCOMMANDS}

    def get_name(self) -> str:
        """Return environment name identifier."""
        return "coding"

    async def serialize(self) -> dict:
        return {
            "working_dir": str(self.working_dir),
            "enabled_tools": self.enabled_tools,
            "allow_spawn": self.allow_spawn,
        }

    @staticmethod
    async def deserialize(data: dict) -> 'CodingEnvironment':
        return CodingEnvironment(
            working_dir=Path(data["working_dir"]),
            enabled_tools=data.get("enabled_tools"),
            allow_spawn=data.get("allow_spawn", False),
        )

    def requires_confirmation(self, tool_call: ToolCall) -> bool:
        """Only bash commands require confirmation by default."""
        return tool_call.name == "bash"

    def get_tools(self) -> list[Tool]:
        """Return enabled tools.

        If enabled_tools contains wafer subcommands (ask-docs, ncu-analyze, etc.),
        the wafer tool is automatically included with a description listing
        only the enabled subcommands.
        """
        if self.enabled_tools is None:
            return list(ALL_TOOLS.values())

        tools = []
        enabled_set = set(self.enabled_tools)

        # Add base tools that are explicitly enabled
        for name in self.enabled_tools:
            if name in BASE_TOOLS and name in ALL_TOOLS:
                tools.append(ALL_TOOLS[name])
        
        # Add analyze_kernel if enabled
        if "analyze_kernel" in enabled_set and "analyze_kernel" in ALL_TOOLS:
            tools.append(ALL_TOOLS["analyze_kernel"])

        # Check if any wafer subcommands are enabled
        enabled_subcommands = self._get_enabled_subcommands()
        if enabled_subcommands:
            # Create wafer tool with filtered description
            subcommand_list = ", ".join(sorted(enabled_subcommands))
            wafer_tool = Tool(
                type="function",
                function=ToolFunction(
                    name="wafer",
                    description=f"Execute a wafer CLI command. Available subcommands: {subcommand_list}.",
                    parameters=WAFER_TOOL.function.parameters,
                    required=WAFER_TOOL.function.required,
                )
            )
            tools.append(wafer_tool)

        return tools

    async def on_assistant_message(self, message: Message, state: AgentState) -> AgentState:
        """No feedback needed for coding environment."""
        return state

    async def exec_tool(
        self,
        tool_call: ToolCall,
        current_state: 'AgentState',
        run_config: 'RunConfig',
        cancel_scope: trio.CancelScope | None = None,
    ) -> ToolResult:
        """Execute tool call."""
        # Check if tool is enabled
        if self.enabled_tools is not None:
            # For wafer tool, check if any subcommand is enabled
            if tool_call.name == "wafer":
                if not self._get_enabled_subcommands():
                    return ToolResult(
                        tool_call_id=tool_call.id,
                        is_error=True,
                        content="",
                        error=f"No wafer subcommands are enabled. Enabled tools: {', '.join(self.enabled_tools)}"
                    )
            # For base tools, check directly
            elif tool_call.name not in self.enabled_tools:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content="",
                    error=f"Tool '{tool_call.name}' is not enabled. Enabled tools: {', '.join(self.enabled_tools)}"
                )

        try:
            if tool_call.name == "read":
                return await self._exec_read(tool_call)
            elif tool_call.name == "write":
                return await self._exec_write(tool_call)
            elif tool_call.name == "edit":
                return await self._exec_edit(tool_call)
            elif tool_call.name == "bash":
                return await self._exec_bash(tool_call, cancel_scope)
            elif tool_call.name == "wafer":
                return await self._exec_wafer(tool_call, cancel_scope)
            elif tool_call.name == "analyze_kernel":
                return await exec_analyze_kernel(tool_call)
            else:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content="",
                    error=f"Unknown tool: {tool_call.name}"
                )
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=str(e)
            )

    async def _exec_read(self, tool_call: ToolCall) -> ToolResult:
        """Read file contents."""
        path_str = tool_call.args["path"]
        offset = tool_call.args.get("offset")
        limit = tool_call.args.get("limit")

        abs_path = expand_path(path_str)

        if not abs_path.exists():
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"File not found: {path_str}"
            )

        if not abs_path.is_file():
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Not a file: {path_str}"
            )

        try:
            content = abs_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Cannot read binary file: {path_str}"
            )

        lines = content.split("\n")

        # Apply offset and limit
        start_line = (offset - 1) if offset else 0  # 1-indexed to 0-indexed
        max_lines = limit or MAX_LINES
        end_line = min(start_line + max_lines, len(lines))

        if start_line >= len(lines):
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Offset {offset} is beyond end of file ({len(lines)} lines total)"
            )

        selected_lines = lines[start_line:end_line]

        # Truncate long lines
        had_truncated = False
        formatted_lines = []
        for line in selected_lines:
            if len(line) > MAX_LINE_LENGTH:
                had_truncated = True
                formatted_lines.append(line[:MAX_LINE_LENGTH])
            else:
                formatted_lines.append(line)

        output_text = "\n".join(formatted_lines)

        # Add notices
        notices = []
        if had_truncated:
            notices.append(f"Some lines were truncated to {MAX_LINE_LENGTH} characters")
        if end_line < len(lines):
            remaining = len(lines) - end_line
            notices.append(f"{remaining} more lines not shown. Use offset={end_line + 1} to continue")

        if notices:
            output_text += f"\n\n... ({'. '.join(notices)})"

        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=False,
            content=output_text
        )

    async def _exec_write(self, tool_call: ToolCall) -> ToolResult:
        """Write content to file."""
        path_str = tool_call.args["path"]
        content = tool_call.args["content"]

        abs_path = expand_path(path_str)

        # Create parent directories
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        abs_path.write_text(content, encoding="utf-8")

        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=False,
            content=f"Successfully wrote {len(content)} bytes to {path_str}"
        )

    async def _exec_edit(self, tool_call: ToolCall) -> ToolResult:
        """Edit file by replacing exact text."""
        path_str = tool_call.args["path"]
        old_text = tool_call.args["old_text"]
        new_text = tool_call.args["new_text"]

        abs_path = expand_path(path_str)

        if not abs_path.exists():
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"File not found: {path_str}"
            )

        try:
            content = abs_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Cannot read binary file: {path_str}"
            )

        # Check if old text exists
        if old_text not in content:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Could not find the exact text in {path_str}. The old text must match exactly including all whitespace and newlines."
            )

        # Count occurrences
        occurrences = content.count(old_text)
        if occurrences > 1:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Found {occurrences} occurrences of the text in {path_str}. The text must be unique. Please provide more context to make it unique."
            )

        # Perform replacement
        index = content.find(old_text)
        new_content = content[:index] + new_text + content[index + len(old_text):]

        if content == new_content:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"No changes made to {path_str}. The replacement produced identical content."
            )

        abs_path.write_text(new_content, encoding="utf-8")

        # Generate diff for UI display
        diff_str = generate_diff(content, new_content)

        return ToolResult(
            tool_call_id=tool_call.id,
            is_error=False,
            content=f"Successfully replaced text in {path_str}. Changed {len(old_text)} characters to {len(new_text)} characters.",
            details={"diff": diff_str}
        )

    async def _exec_bash(self, tool_call: ToolCall, cancel_scope: trio.CancelScope | None = None) -> ToolResult:
        """Execute bash command."""
        command = tool_call.args["command"]
        timeout = tool_call.args.get("timeout", 120)

        # Block wafer commands in bash - use the wafer tool instead
        if re.search(r'\bwafer\b', command):
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error="Use the 'wafer' tool for wafer commands, not bash."
            )

        try:
            result = await trio.to_thread.run_sync(
                lambda: subprocess.run(
                    ["sh", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.working_dir),
                ),
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"
                output += result.stderr

            # Truncate if too large
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + "\n\n... (output truncated)"

            if result.returncode != 0:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content=output or "(no output)",
                    error=f"Command exited with code {result.returncode}"
                )

            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=False,
                content=output or "(no output)"
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Command timed out after {timeout} seconds"
            )
        except trio.Cancelled:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error="Command aborted"
            )

    async def _exec_wafer(self, tool_call: ToolCall, cancel_scope: trio.CancelScope | None = None) -> ToolResult:
        """Execute wafer subcommand."""
        subcommand = tool_call.args["subcommand"]
        args = tool_call.args.get("args", "")
        timeout = tool_call.args.get("timeout", 300)

        # Check for blocked subcommands (wevin requires --allow-spawn)
        if subcommand in BLOCKED_WAFER_SUBCOMMANDS and not self.allow_spawn:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"Subcommand '{subcommand}' is blocked. Use --allow-spawn to enable spawning sub-agents."
            )

        # Get enabled subcommands based on --tools flag
        enabled_subcommands = self._get_enabled_subcommands()

        # Check if subcommand is enabled
        if subcommand not in enabled_subcommands and subcommand not in BLOCKED_WAFER_SUBCOMMANDS:
            if subcommand in WAFER_SUBCOMMANDS:
                # Valid subcommand but not enabled
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content="",
                    error=f"Subcommand '{subcommand}' is not enabled. Enabled: {', '.join(sorted(enabled_subcommands))}"
                )
            else:
                # Unknown subcommand
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content="",
                    error=f"Unknown wafer subcommand: '{subcommand}'. Available: {', '.join(sorted(WAFER_SUBCOMMANDS))}"
                )

        # Build command - handle args based on subcommand
        cmd_parts = ["wafer", subcommand]
        if args:
            # For ask-docs, the args is typically a single query string
            # For other commands, try to parse as shell arguments
            if subcommand == "ask-docs":
                # Treat entire args as the query (single positional argument)
                cmd_parts.append(args)
            else:
                # Use shlex.split for commands with multiple args
                try:
                    cmd_parts.extend(shlex.split(args))
                except ValueError:
                    # If shlex.split fails, treat as single argument
                    cmd_parts.append(args)

        try:
            result = await trio.to_thread.run_sync(
                lambda: subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.working_dir),
                ),
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"
                output += result.stderr

            # Truncate if too large
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + "\n\n... (output truncated)"

            if result.returncode != 0:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    is_error=True,
                    content=output or "(no output)",
                    error=f"wafer {subcommand} exited with code {result.returncode}"
                )

            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=False,
                content=output or "(no output)"
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error=f"wafer {subcommand} timed out after {timeout} seconds"
            )
        except trio.Cancelled:
            return ToolResult(
                tool_call_id=tool_call.id,
                is_error=True,
                content="",
                error="Command aborted"
            )
