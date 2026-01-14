"""Workspace file operation tools for GPU kernel environments.

Pure functions for file operations within isolated workspaces.
Provides safe file operations with validation and limits.

Tiger Style:
- Pure functions (no hidden state)
- Explicit validation
- Path safety checks
- Clear error messages
"""

import logging
from pathlib import Path

from wafer_core.rollouts.dtypes import ToolResult

logger = logging.getLogger(__name__)

# Safety limits (Tiger Style: explicit bounds)
MAX_FILE_SIZE = 100 * 1024  # 100KB - reasonable for kernel code
MAX_FILES = 20  # Prevent runaway file creation
ALLOWED_EXTENSIONS = {".py", ".txt", ".md", ".cu"}  # Explicit whitelist


def validate_path(filepath: str, workspace_dir: Path) -> tuple[Path | None, str | None]:
    """Validate path for workspace access.

    Tiger Style: Explicit bounds, fail-fast, split checks.

    Args:
        filepath: Relative path from user
        workspace_dir: Workspace root directory

    Returns:
        (resolved_path, error_message) - one will be None

    Example:
        >>> workspace = Path("/tmp/workspace")
        >>> path, err = validate_path("solution.py", workspace)
        >>> if err:
        ...     print(f"Invalid: {err}")
    """
    # Assert preconditions
    assert workspace_dir is not None, "workspace_dir must be set"
    assert workspace_dir.exists(), "workspace_dir must exist"

    # Validate not empty
    if not filepath:
        return None, "Filepath cannot be empty"

    # Reject absolute paths
    if Path(filepath).is_absolute():
        return None, f"Absolute paths not allowed: {filepath}"

    # Resolve to absolute path
    full_path = (workspace_dir / filepath).resolve()

    # Ensure within workspace (catches ../ traversal)
    try:
        full_path.relative_to(workspace_dir.resolve())
    except ValueError:
        return None, f"Path outside workspace: {filepath}"

    # Extension whitelist (if file has extension)
    if full_path.suffix and full_path.suffix not in ALLOWED_EXTENSIONS:
        return (
            None,
            f"File extension not allowed: {full_path.suffix}. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # Block hidden files
    if any(part.startswith(".") for part in Path(filepath).parts):
        return None, f"Hidden files/directories not allowed: {filepath}"

    return full_path, None


def check_workspace_limits(workspace_dir: Path) -> tuple[bool, str | None]:
    """Check workspace hasn't exceeded limits.

    Args:
        workspace_dir: Workspace root directory

    Returns:
        (ok, error_message)

    Example:
        >>> workspace = Path("/tmp/workspace")
        >>> ok, err = check_workspace_limits(workspace)
        >>> if not ok:
        ...     print(f"Limit exceeded: {err}")
    """
    assert workspace_dir is not None

    # Count files
    num_files = len(list(workspace_dir.rglob("*")))
    if num_files >= MAX_FILES:
        return False, f"Workspace file limit reached ({MAX_FILES} files)"

    return True, None


async def ls_files(dirpath: str, workspace_dir: Path) -> ToolResult:
    """List files in a workspace directory.

    Args:
        dirpath: Directory path relative to workspace (default ".")
        workspace_dir: Workspace root directory

    Returns:
        ToolResult with directory listing or error

    Example:
        >>> result = await ls_files(".", workspace_dir)
        >>> if not result.is_error:
        ...     print(result.content)
    """
    assert workspace_dir is not None, "workspace_dir must be set"
    logger.debug(f"ls_files: {dirpath} (workspace: {workspace_dir})")

    # Handle default case
    if not dirpath or dirpath == ".":
        target_dir = workspace_dir
    else:
        # Validate path (but allow directories)
        if Path(dirpath).is_absolute():
            return ToolResult(is_error=True, content="", error=f"Absolute paths not allowed: {dirpath}")

        target_dir = (workspace_dir / dirpath).resolve()

        # Ensure within workspace
        try:
            target_dir.relative_to(workspace_dir.resolve())  # noqa: ASYNC240
        except ValueError:
            return ToolResult(is_error=True, content="", error=f"Path outside workspace: {dirpath}")

    # Check directory exists
    if not target_dir.exists():
        return ToolResult(is_error=True, content="", error=f"Directory not found: {dirpath}")

    # Check it's actually a directory
    if not target_dir.is_dir():
        return ToolResult(is_error=True, content="", error=f"Not a directory: {dirpath}")

    # List files and directories
    try:
        entries = []
        for entry in sorted(target_dir.iterdir()):
            # Use relative_to on resolved paths to handle symlinks
            try:
                rel_path = entry.resolve().relative_to(workspace_dir.resolve())  # noqa: ASYNC240
            except ValueError:
                # Fallback: just use the name
                rel_path = entry.name

            if entry.is_file():
                size = entry.stat().st_size
                entries.append(f"  {rel_path} ({size} bytes)")
            elif entry.is_dir():
                entries.append(f"  {rel_path}/")

        if not entries:
            content = f"Directory '{dirpath}' is empty"
        else:
            content = f"Contents of '{dirpath}':\n" + "\n".join(entries)

        return ToolResult(is_error=False, content=content, error=None)
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to list directory: {e}")


async def read_file(filepath: str, workspace_dir: Path) -> ToolResult:
    """Read a file from workspace.

    Args:
        filepath: Relative path to read
        workspace_dir: Workspace root directory

    Returns:
        ToolResult with file contents or error

    Example:
        >>> result = await read_file("solution.py", workspace_dir)
        >>> if not result.is_error:
        ...     code = result.content
    """
    # Validate path
    path, err = validate_path(filepath, workspace_dir)
    if err:
        return ToolResult(is_error=True, content="", error=err)
    assert path is not None

    # Check file exists
    if not path.exists():
        return ToolResult(is_error=True, content="", error=f"File not found: {filepath}")

    # Check it's a file (not directory)
    if not path.is_file():
        return ToolResult(is_error=True, content="", error=f"Not a file: {filepath}")

    # Read file
    try:
        content = path.read_text()
        return ToolResult(is_error=False, content=content, error=None)
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to read file: {e}")


async def write_file(filepath: str, content: str, workspace_dir: Path) -> ToolResult:
    """Write file to workspace.

    Args:
        filepath: Relative path to write
        content: File content
        workspace_dir: Workspace root directory

    Returns:
        ToolResult with success/error

    Example:
        >>> result = await write_file("solution.py", code, workspace_dir)
        >>> if result.is_error:
        ...     print(f"Write failed: {result.error}")
    """
    # Validate path
    path, err = validate_path(filepath, workspace_dir)
    if err:
        return ToolResult(is_error=True, content="", error=err)
    assert path is not None

    # Check workspace limits before writing
    ok, err = check_workspace_limits(workspace_dir)
    if not ok:
        return ToolResult(is_error=True, content="", error=err)

    # Check content size
    content_size = len(content.encode("utf-8"))
    if content_size > MAX_FILE_SIZE:
        return ToolResult(
            is_error=True,
            content="",
            error=f"File too large: {content_size} bytes (max {MAX_FILE_SIZE})",
        )

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        path.write_text(content)
        logger.info(f"wrote file: {path} (workspace: {workspace_dir})")
        # Verify immediately
        if not path.exists():
            logger.error(f"file write succeeded but file doesn't exist! {path}")
        else:
            logger.info(f"verified file exists: {path}")
        return ToolResult(is_error=False, content=f"Wrote {content_size} bytes to {filepath}", error=None)
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to write file: {e}")


async def edit_file(
    filepath: str, old_string: str, new_string: str, workspace_dir: Path, replace_all: bool = False
) -> ToolResult:
    """Edit file by replacing exact string matches.

    Tiger Style: Explicit validation, fail-fast, single responsibility.

    Args:
        filepath: Relative path to edit
        old_string: Exact string to find
        new_string: Replacement string
        workspace_dir: Workspace root directory
        replace_all: If True, replace all occurrences. If False, fail if ambiguous.

    Returns:
        ToolResult with success/error

    Example:
        >>> result = await edit_file(
        ...     "solution.py",
        ...     "old_code",
        ...     "new_code",
        ...     workspace_dir
        ... )
        >>> if not result.is_error:
        ...     print("File edited successfully")
    """
    # Validate path
    path, err = validate_path(filepath, workspace_dir)
    if err:
        return ToolResult(is_error=True, content="", error=err)
    assert path is not None

    # Check file exists
    if not path.exists():
        return ToolResult(
            is_error=True,
            content="",
            error=f"File not found: {filepath}. Use write_file to create it first.",
        )

    # Check it's a file
    if not path.is_file():
        return ToolResult(is_error=True, content="", error=f"Not a file: {filepath}")

    # Read current content
    try:
        content = path.read_text()
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to read file: {e}")

    # Validate old_string exists
    if old_string not in content:
        return ToolResult(
            is_error=True,
            content="",
            error=f"String not found in file. The file may have been modified. Old string:\n{old_string[:200]}...",
        )

    # Check for ambiguity
    count = content.count(old_string)
    if count > 1 and not replace_all:
        return ToolResult(
            is_error=True,
            content="",
            error=f"Ambiguous edit: '{old_string[:50]}...' appears {count} times. Set replace_all=true to replace all occurrences, or provide a more specific old_string.",
        )

    # Perform replacement
    if replace_all:
        new_content = content.replace(old_string, new_string)
    else:
        new_content = content.replace(old_string, new_string, 1)

    # Validate new content size
    new_content_size = len(new_content.encode("utf-8"))
    if new_content_size > MAX_FILE_SIZE:
        return ToolResult(
            is_error=True,
            content="",
            error=f"Edited file too large: {new_content_size} bytes (max {MAX_FILE_SIZE})",
        )

    # Write updated content
    try:
        path.write_text(new_content)
        logger.info(f"edited file: {path} ({count} replacement(s), workspace: {workspace_dir})")

        return ToolResult(is_error=False, content=f"Edited {filepath}: replaced {count} occurrence(s)", error=None)
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to write edited file: {e}")
