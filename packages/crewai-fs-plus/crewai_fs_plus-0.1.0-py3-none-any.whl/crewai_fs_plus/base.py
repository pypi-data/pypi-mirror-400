"""Base configuration and utilities for filesystem tools."""

from fnmatch import fnmatch
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from .exceptions import PathNotAllowedError, PathOutsideSandboxError


class FSToolConfig(BaseModel):
    """Configuration for filesystem tools with whitelist/blacklist and sandboxing."""

    base_directory: Optional[str] = Field(
        default=None,
        description="Base directory that acts as sandbox root. Paths outside this directory are not allowed.",
    )
    whitelist: list[str] = Field(
        default_factory=list,
        description="List of glob patterns for allowed paths. Empty list means all paths are allowed.",
    )
    blacklist: list[str] = Field(
        default_factory=list,
        description="List of glob patterns for denied paths. Takes precedence over whitelist.",
    )

    model_config = {"extra": "allow"}


def matches_any_pattern(path: str, patterns: list[str]) -> bool:
    """Check if a path matches any of the given glob patterns.

    Args:
        path: The path to check (should be relative to base_directory or absolute).
        patterns: List of glob patterns to match against.

    Returns:
        True if the path matches any pattern, False otherwise.
    """
    if not patterns:
        return False

    path_obj = Path(path)

    for pattern in patterns:
        # Try matching the full path
        if fnmatch(path, pattern):
            return True
        # Try matching just the filename
        if fnmatch(path_obj.name, pattern):
            return True
        # Try matching with forward slashes normalized
        normalized_path = path.replace("\\", "/")
        normalized_pattern = pattern.replace("\\", "/")
        if fnmatch(normalized_path, normalized_pattern):
            return True

    return False


def resolve_path(path: str, base_directory: Optional[str] = None) -> Path:
    """Resolve a path to an absolute path, optionally relative to base_directory.

    Args:
        path: The path to resolve.
        base_directory: Optional base directory to resolve relative paths against.

    Returns:
        The resolved absolute path.
    """
    path_obj = Path(path)

    if not path_obj.is_absolute():
        if base_directory:
            path_obj = Path(base_directory) / path_obj
        else:
            path_obj = Path.cwd() / path_obj

    # Resolve to get canonical path (resolves symlinks and ..)
    return path_obj.resolve()


def validate_path(
    path: str,
    base_directory: Optional[str] = None,
    whitelist: Optional[list[str]] = None,
    blacklist: Optional[list[str]] = None,
    must_exist: bool = False,
) -> Path:
    """Validate a path against sandbox and whitelist/blacklist rules.

    Args:
        path: The path to validate.
        base_directory: Optional sandbox root directory.
        whitelist: Optional list of glob patterns for allowed paths.
        blacklist: Optional list of glob patterns for denied paths.
        must_exist: If True, the path must exist.

    Returns:
        The resolved absolute path.

    Raises:
        PathOutsideSandboxError: If path is outside base_directory.
        PathNotAllowedError: If path is denied by whitelist/blacklist rules.
        FileNotFoundError: If must_exist is True and path doesn't exist.
    """
    whitelist = whitelist or []
    blacklist = blacklist or []

    resolved = resolve_path(path, base_directory)

    # Check if path exists if required
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")

    # Check sandbox constraint
    if base_directory:
        base_resolved = Path(base_directory).resolve()
        try:
            resolved.relative_to(base_resolved)
        except ValueError:
            raise PathOutsideSandboxError(str(resolved), str(base_resolved))

    # Get the path relative to base_directory for pattern matching
    if base_directory:
        base_resolved = Path(base_directory).resolve()
        try:
            relative_path = str(resolved.relative_to(base_resolved))
        except ValueError:
            relative_path = str(resolved)
    else:
        relative_path = str(resolved)

    # Check blacklist first (takes precedence)
    if matches_any_pattern(relative_path, blacklist):
        raise PathNotAllowedError(str(resolved), "Path matches blacklist pattern")

    # Check whitelist (if non-empty, path must match at least one pattern)
    if whitelist and not matches_any_pattern(relative_path, whitelist):
        raise PathNotAllowedError(str(resolved), "Path does not match any whitelist pattern")

    return resolved


def get_relative_path(path: Path, base_directory: Optional[str]) -> str:
    """Get the path relative to base_directory, or the absolute path if no base.

    Args:
        path: The absolute path.
        base_directory: Optional base directory.

    Returns:
        The relative or absolute path as a string.
    """
    if base_directory:
        base_resolved = Path(base_directory).resolve()
        try:
            return str(path.relative_to(base_resolved))
        except ValueError:
            pass
    return str(path)
