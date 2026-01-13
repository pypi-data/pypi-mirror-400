"""DirectoryReadTool - List directory contents with whitelist/blacklist and sandboxing support."""

import os
from typing import Any, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base import get_relative_path, matches_any_pattern, validate_path
from .exceptions import FSToolError


def _to_bool(value: Union[str, bool]) -> bool:
    """Convert a string or bool value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on")
    return bool(value)


class DirectoryReadToolSchema(BaseModel):
    """Input schema for DirectoryReadTool."""

    directory: str = Field(..., description="The directory path to list contents of")
    recursive: Union[str, bool] = Field(
        default=True,
        description="If True, list contents recursively. Default is True.",
    )


class FixedDirectoryReadToolSchema(BaseModel):
    """Input schema for DirectoryReadTool when directory is pre-configured."""

    recursive: Union[str, bool] = Field(
        default=True,
        description="If True, list contents recursively. Default is True.",
    )


class DirectoryReadTool(BaseTool):
    """A tool to list directory contents with whitelist/blacklist filtering and sandboxing.

    This tool extends CrewAI's directory reading capabilities with:
    - Base directory sandboxing (prevent access outside a root directory)
    - Whitelist patterns (only show matching paths in results)
    - Blacklist patterns (hide matching paths from results)
    - Optional recursive listing

    Example:
        ```python
        # List only .py files, excluding tests and cache
        reader = DirectoryReadTool(
            base_directory="/path/to/project",
            whitelist=["*.py", "**/*.py"],
            blacklist=["**/test_*", "**/__pycache__/**"]
        )
        ```
    """

    name: str = "List Directory"
    description: str = "List the contents of a directory. Provide the directory path."
    args_schema: Type[BaseModel] = DirectoryReadToolSchema

    # Configuration
    base_directory: Optional[str] = None
    whitelist: list[str] = []
    blacklist: list[str] = []

    # Optional default directory
    directory: Optional[str] = None

    def __init__(
        self,
        directory: Optional[str] = None,
        base_directory: Optional[str] = None,
        whitelist: Optional[list[str]] = None,
        blacklist: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        """Initialize the DirectoryReadTool.

        Args:
            directory: Optional default directory to list.
            base_directory: Optional sandbox root directory.
            whitelist: Optional list of glob patterns for allowed paths.
            blacklist: Optional list of glob patterns for denied paths.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.directory = directory
        self.base_directory = base_directory
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []

        # Update schema and description if a default directory is set
        if directory:
            self.description = f"List the contents of the directory at {directory}"
            self.args_schema = FixedDirectoryReadToolSchema

    def _run(
        self,
        directory: Optional[str] = None,
        recursive: Union[str, bool] = True,
        **kwargs: Any,
    ) -> str:
        """List contents of a directory.

        Args:
            directory: Path to the directory to list.
            recursive: If True, list contents recursively.

        Returns:
            A formatted list of file paths or an error message.
        """
        # Use provided directory or default
        target_dir = directory or self.directory
        if not target_dir:
            return "Error: No directory path provided."

        try:
            # Validate directory path against sandbox and whitelist/blacklist
            resolved_dir = validate_path(
                target_dir,
                base_directory=self.base_directory,
                whitelist=None,  # Don't filter the directory itself
                blacklist=None,
                must_exist=True,
            )

            if not resolved_dir.is_dir():
                return f"Error: Path is not a directory: {target_dir}"

            should_recurse = _to_bool(recursive)
            file_paths = []

            if should_recurse:
                # Recursive walk
                for root, dirs, files in os.walk(resolved_dir):
                    for filename in files:
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, resolved_dir)
                        file_paths.append(rel_path)
            else:
                # Non-recursive listing
                for item in resolved_dir.iterdir():
                    rel_path = item.name
                    if item.is_dir():
                        rel_path += "/"
                    file_paths.append(rel_path)

            # Apply whitelist/blacklist filtering to results
            filtered_paths = []
            for path in file_paths:
                # Check blacklist first
                if self.blacklist and matches_any_pattern(path, self.blacklist):
                    continue
                # Check whitelist (if non-empty, must match)
                if self.whitelist and not matches_any_pattern(path, self.whitelist):
                    continue
                filtered_paths.append(path)

            # Sort paths for consistent output
            filtered_paths.sort()

            if not filtered_paths:
                return f"Directory is empty or no files match filters: {target_dir}"

            # Format output
            result = f"Files in {target_dir}:\n"
            result += "\n".join(f"- {path}" for path in filtered_paths)
            return result

        except FileNotFoundError:
            return f"Error: Directory not found: {target_dir}"
        except PermissionError:
            return f"Error: Permission denied: {target_dir}"
        except FSToolError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error listing directory: {e}"
