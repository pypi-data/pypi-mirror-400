"""FileDeleteTool - Delete files/directories with whitelist/blacklist and sandboxing support."""

import shutil
from typing import Any, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base import validate_path
from .exceptions import DirectoryNotEmptyError, FSToolError


def _to_bool(value: Union[str, bool]) -> bool:
    """Convert a string or bool value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on")
    return bool(value)


class FileDeleteToolSchema(BaseModel):
    """Input schema for FileDeleteTool."""

    path: str = Field(..., description="The path to the file or directory to delete")
    recursive: Union[str, bool] = Field(
        default=False,
        description="If True, delete directories and their contents recursively. Required for non-empty directories.",
    )


class FileDeleteTool(BaseTool):
    """A tool to delete files and directories with whitelist/blacklist filtering and sandboxing.

    This tool provides safe file/directory deletion with:
    - Base directory sandboxing (prevent deletes outside a root directory)
    - Whitelist patterns (only allow deletes of matching paths)
    - Blacklist patterns (deny deletes of matching paths)
    - Protection against accidental recursive deletion

    Example:
        ```python
        # Allow deletion only in temp and cache directories
        deleter = FileDeleteTool(
            base_directory="/path/to/project",
            whitelist=["temp/**", "cache/**", "*.tmp"],
            blacklist=["**/.git/**", "**/node_modules/**"]
        )
        ```
    """

    name: str = "Delete File"
    description: str = (
        "Delete a file or directory. Provide the path and optionally set "
        "recursive=True to delete non-empty directories."
    )
    args_schema: Type[BaseModel] = FileDeleteToolSchema

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
        """Initialize the FileDeleteTool.

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
        path: str,
        recursive: Union[str, bool] = False,
        **kwargs: Any,
    ) -> str:
        """Delete a file or directory.

        Args:
            path: Path to the file or directory to delete.
            recursive: If True, delete directories and their contents recursively.

        Returns:
            A success or error message.
        """
        try:
            # Validate path against sandbox and whitelist/blacklist
            resolved_path = validate_path(
                path,
                base_directory=self.base_directory,
                whitelist=self.whitelist,
                blacklist=self.blacklist,
                must_exist=True,
            )

            should_recurse = _to_bool(recursive)

            if resolved_path.is_file():
                # Delete file
                resolved_path.unlink()
                return f"Successfully deleted file: {path}"

            elif resolved_path.is_dir():
                # Check if directory is empty
                is_empty = not any(resolved_path.iterdir())

                if is_empty:
                    # Delete empty directory
                    resolved_path.rmdir()
                    return f"Successfully deleted empty directory: {path}"
                elif should_recurse:
                    # Delete directory and all contents
                    shutil.rmtree(resolved_path)
                    return f"Successfully deleted directory and contents: {path}"
                else:
                    raise DirectoryNotEmptyError(path)

            else:
                return f"Error: Path is neither a file nor a directory: {path}"

        except FileNotFoundError:
            return f"Error: Path not found: {path}"
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except DirectoryNotEmptyError as e:
            return f"Error: {e}"
        except FSToolError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error deleting path: {e}"
