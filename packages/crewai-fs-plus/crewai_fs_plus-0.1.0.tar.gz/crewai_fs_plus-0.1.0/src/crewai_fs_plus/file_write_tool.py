"""FileWriteTool - Write files with whitelist/blacklist and sandboxing support."""

import os
from typing import Any, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base import validate_path
from .exceptions import FSToolError


def _to_bool(value: Union[str, bool]) -> bool:
    """Convert a string or bool value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on")
    return bool(value)


class FileWriteToolSchema(BaseModel):
    """Input schema for FileWriteTool."""

    file_path: str = Field(..., description="The path to the file to write")
    content: str = Field(..., description="The content to write to the file")
    overwrite: Union[str, bool] = Field(
        default=False,
        description="Whether to overwrite if file exists. Default is False.",
    )


class FileWriteTool(BaseTool):
    """A tool to write file contents with whitelist/blacklist filtering and sandboxing.

    This tool extends CrewAI's file writing capabilities with:
    - Base directory sandboxing (prevent writes outside a root directory)
    - Whitelist patterns (only allow writes to matching paths)
    - Blacklist patterns (deny writes to matching paths)
    - Automatic parent directory creation (within sandbox)

    Example:
        ```python
        # Write only to output and logs directories
        writer = FileWriteTool(
            base_directory="/path/to/project",
            whitelist=["output/**", "logs/**"],
            blacklist=["**/.env", "**/secrets*"]
        )
        ```
    """

    name: str = "Write File"
    description: str = (
        "Write content to a file. Provide the file path, content, and optionally "
        "whether to overwrite existing files."
    )
    args_schema: Type[BaseModel] = FileWriteToolSchema

    # Configuration
    base_directory: Optional[str] = None
    whitelist: list[str] = []
    blacklist: list[str] = []

    def __init__(
        self,
        base_directory: Optional[str] = None,
        whitelist: Optional[list[str]] = None,
        blacklist: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        """Initialize the FileWriteTool.

        Args:
            base_directory: Optional sandbox root directory.
            whitelist: Optional list of glob patterns for allowed paths.
            blacklist: Optional list of glob patterns for denied paths.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.base_directory = base_directory
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []

    def _run(
        self,
        file_path: str,
        content: str,
        overwrite: Union[str, bool] = False,
        **kwargs: Any,
    ) -> str:
        """Write content to a file.

        Args:
            file_path: Path to the file to write.
            content: Content to write to the file.
            overwrite: Whether to overwrite if file exists.

        Returns:
            A success or error message.
        """
        try:
            # Validate path against sandbox and whitelist/blacklist
            resolved_path = validate_path(
                file_path,
                base_directory=self.base_directory,
                whitelist=self.whitelist,
                blacklist=self.blacklist,
                must_exist=False,
            )

            # Create parent directories if needed
            parent_dir = resolved_path.parent
            if not parent_dir.exists():
                # Validate parent directory is within sandbox
                if self.base_directory:
                    validate_path(
                        str(parent_dir),
                        base_directory=self.base_directory,
                        whitelist=self.whitelist,
                        blacklist=self.blacklist,
                        must_exist=False,
                    )
                parent_dir.mkdir(parents=True, exist_ok=True)

            # Check if file exists and handle overwrite
            should_overwrite = _to_bool(overwrite)
            if resolved_path.exists() and not should_overwrite:
                return f"Error: File already exists: {file_path}. Set overwrite=True to overwrite."

            # Write the file
            mode = "w" if should_overwrite or not resolved_path.exists() else "x"
            with open(resolved_path, mode, encoding="utf-8") as f:
                f.write(content)

            return f"Successfully wrote to {file_path}"

        except FileExistsError:
            return f"Error: File already exists: {file_path}. Set overwrite=True to overwrite."
        except PermissionError:
            return f"Error: Permission denied: {file_path}"
        except FSToolError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error writing file: {e}"
