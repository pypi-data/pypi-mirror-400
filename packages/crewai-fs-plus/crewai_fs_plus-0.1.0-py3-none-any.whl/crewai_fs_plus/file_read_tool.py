"""FileReadTool - Read files with whitelist/blacklist and sandboxing support."""

from typing import Any, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base import FSToolConfig, validate_path
from .exceptions import FSToolError


class FileReadToolSchema(BaseModel):
    """Input schema for FileReadTool."""

    file_path: str = Field(..., description="The path to the file to read")
    start_line: int = Field(
        default=1, description="Line number to start reading from (1-indexed)"
    )
    line_count: Optional[int] = Field(
        default=None, description="Number of lines to read. None means read all."
    )


class FileReadTool(BaseTool):
    """A tool to read file contents with whitelist/blacklist filtering and sandboxing.

    This tool extends CrewAI's file reading capabilities with:
    - Base directory sandboxing (prevent access outside a root directory)
    - Whitelist patterns (only allow access to matching paths)
    - Blacklist patterns (deny access to matching paths)

    Example:
        ```python
        # Read only .py and .md files from a project directory
        reader = FileReadTool(
            base_directory="/path/to/project",
            whitelist=["*.py", "*.md"],
            blacklist=["**/secret*"]
        )
        ```
    """

    name: str = "Read File"
    description: str = "Read content from a file. Provide the file path to read."
    args_schema: Type[BaseModel] = FileReadToolSchema

    # Configuration
    base_directory: Optional[str] = None
    whitelist: list[str] = []
    blacklist: list[str] = []

    # Optional default file path
    file_path: Optional[str] = None

    def __init__(
        self,
        file_path: Optional[str] = None,
        base_directory: Optional[str] = None,
        whitelist: Optional[list[str]] = None,
        blacklist: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        """Initialize the FileReadTool.

        Args:
            file_path: Optional default file path to read.
            base_directory: Optional sandbox root directory.
            whitelist: Optional list of glob patterns for allowed paths.
            blacklist: Optional list of glob patterns for denied paths.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.file_path = file_path
        self.base_directory = base_directory
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []

        # Update description if a default file path is set
        if file_path:
            self.description = f"Read content from the file at {file_path}"

    def _run(
        self,
        file_path: Optional[str] = None,
        start_line: int = 1,
        line_count: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Read content from a file.

        Args:
            file_path: Path to the file to read.
            start_line: Line number to start reading from (1-indexed).
            line_count: Number of lines to read. None means read all.

        Returns:
            The file content as a string.
        """
        # Use provided path or default
        target_path = file_path or self.file_path
        if not target_path:
            return "Error: No file path provided."

        try:
            # Validate path against sandbox and whitelist/blacklist
            resolved_path = validate_path(
                target_path,
                base_directory=self.base_directory,
                whitelist=self.whitelist,
                blacklist=self.blacklist,
                must_exist=True,
            )

            # Read the file
            with open(resolved_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Apply line range
            start_idx = max(0, start_line - 1)  # Convert to 0-indexed
            if line_count is not None:
                end_idx = start_idx + line_count
                lines = lines[start_idx:end_idx]
            else:
                lines = lines[start_idx:]

            return "".join(lines)

        except FileNotFoundError:
            return f"Error: File not found: {target_path}"
        except PermissionError:
            return f"Error: Permission denied: {target_path}"
        except FSToolError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error reading file: {e}"
