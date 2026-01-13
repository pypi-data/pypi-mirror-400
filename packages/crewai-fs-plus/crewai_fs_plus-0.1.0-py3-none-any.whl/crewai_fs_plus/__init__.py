"""CrewAI FS Plus - Enhanced filesystem tools for CrewAI.

This package provides filesystem tools with additional security features:
- Base directory sandboxing
- Whitelist/blacklist filtering with glob patterns
- Safe file operations

Example:
    ```python
    from crewai_fs_plus import FileReadTool, FileWriteTool, FileDeleteTool, DirectoryReadTool

    # Create sandboxed tools
    reader = FileReadTool(
        base_directory="/path/to/project",
        whitelist=["*.py", "*.md"],
        blacklist=["**/secret*"]
    )

    writer = FileWriteTool(
        base_directory="/path/to/project",
        whitelist=["output/**"]
    )
    ```
"""

from .directory_read_tool import DirectoryReadTool
from .exceptions import (
    DirectoryNotEmptyError,
    FSToolError,
    PathNotAllowedError,
    PathOutsideSandboxError,
)
from .file_delete_tool import FileDeleteTool
from .file_read_tool import FileReadTool
from .file_write_tool import FileWriteTool

__version__ = "0.1.0"

__all__ = [
    # Tools
    "FileReadTool",
    "FileWriteTool",
    "FileDeleteTool",
    "DirectoryReadTool",
    # Exceptions
    "FSToolError",
    "PathNotAllowedError",
    "PathOutsideSandboxError",
    "DirectoryNotEmptyError",
]
