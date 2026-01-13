"""Custom exceptions for crewai-fs-plus."""


class FSToolError(Exception):
    """Base exception for all filesystem tool errors."""

    pass


class PathNotAllowedError(FSToolError):
    """Raised when a path is not allowed by whitelist/blacklist rules."""

    def __init__(self, path: str, reason: str = "Path is not allowed"):
        self.path = path
        self.reason = reason
        super().__init__(f"{reason}: {path}")


class PathOutsideSandboxError(FSToolError):
    """Raised when a path is outside the configured base directory."""

    def __init__(self, path: str, base_directory: str):
        self.path = path
        self.base_directory = base_directory
        super().__init__(
            f"Path '{path}' is outside the sandbox directory '{base_directory}'"
        )


class DirectoryNotEmptyError(FSToolError):
    """Raised when trying to delete a non-empty directory without recursive flag."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(
            f"Directory '{path}' is not empty. Use recursive=True to delete."
        )
