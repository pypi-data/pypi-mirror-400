"""Tests for DirectoryReadTool."""

from pathlib import Path

import pytest

from crewai_fs_plus import DirectoryReadTool


class TestDirectoryReadToolBasic:
    """Basic functionality tests for DirectoryReadTool."""

    def test_list_directory_recursive(self, sample_files: Path):
        """Test listing directory recursively."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(sample_files), recursive=True)

        assert "file1.txt" in result
        assert "file2.py" in result
        assert "readme.md" in result or "docs" in result

    def test_list_directory_non_recursive(self, sample_files: Path):
        """Test listing directory non-recursively."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(sample_files), recursive=False)

        # Top-level files should be present
        assert "file1.txt" in result
        # Nested files should not be directly listed
        assert "readme.md" not in result or "docs/" in result

    def test_list_nonexistent_directory(self, temp_dir: Path):
        """Test listing a directory that doesn't exist."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(temp_dir / "nonexistent"))
        assert "Error" in result

    def test_list_file_as_directory(self, sample_files: Path):
        """Test listing a file (should fail)."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(sample_files / "file1.txt"))
        assert "Error" in result
        assert "not a directory" in result.lower()

    def test_list_empty_directory(self, empty_dir: Path):
        """Test listing an empty directory."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(empty_dir))
        assert "empty" in result.lower() or "no files" in result.lower()

    def test_list_with_default_directory(self, sample_files: Path):
        """Test listing with pre-configured directory."""
        tool = DirectoryReadTool(directory=str(sample_files))
        result = tool._run()
        assert "file1.txt" in result

    def test_no_directory_error(self):
        """Test error when no directory is provided."""
        tool = DirectoryReadTool()
        result = tool._run()
        assert "Error" in result

    def test_recursive_string_true(self, sample_files: Path):
        """Test recursive with string 'true'."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(sample_files), recursive="true")
        assert "readme.md" in result or "main.py" in result

    def test_recursive_string_false(self, sample_files: Path):
        """Test recursive with string 'false'."""
        tool = DirectoryReadTool()
        result = tool._run(directory=str(sample_files), recursive="false")
        # Should show directories with trailing slash
        assert "docs/" in result or "src/" in result


class TestDirectoryReadToolSandbox:
    """Sandbox/base_directory tests for DirectoryReadTool."""

    def test_list_within_sandbox(self, sample_files: Path):
        """Test listing within the sandbox."""
        tool = DirectoryReadTool(base_directory=str(sample_files))
        result = tool._run(directory="docs")
        assert "readme.md" in result

    def test_list_outside_sandbox_blocked(self, sample_files: Path, temp_dir: Path):
        """Test that listing outside sandbox is blocked."""
        sandbox = sample_files / "src"
        tool = DirectoryReadTool(base_directory=str(sandbox))
        result = tool._run(directory=str(sample_files / "docs"))
        assert "Error" in result


class TestDirectoryReadToolWhitelist:
    """Whitelist tests for DirectoryReadTool."""

    def test_whitelist_filters_results(self, sample_files: Path):
        """Test that whitelist filters listing results."""
        tool = DirectoryReadTool(whitelist=["*.py"])
        result = tool._run(directory=str(sample_files), recursive=True)

        # Python files should be present
        assert ".py" in result
        # Non-Python files should be filtered out
        assert "file1.txt" not in result
        assert "readme.md" not in result

    def test_whitelist_multiple_patterns(self, sample_files: Path):
        """Test whitelist with multiple patterns."""
        tool = DirectoryReadTool(whitelist=["*.py", "*.md"])
        result = tool._run(directory=str(sample_files), recursive=True)

        assert "main.py" in result or ".py" in result
        assert "readme.md" in result or ".md" in result
        assert "file1.txt" not in result


class TestDirectoryReadToolBlacklist:
    """Blacklist tests for DirectoryReadTool."""

    def test_blacklist_filters_results(self, sample_files: Path):
        """Test that blacklist filters listing results."""
        tool = DirectoryReadTool(blacklist=["*secret*", "*.env"])
        result = tool._run(directory=str(sample_files), recursive=True)

        # Regular files should be present
        assert "file1.txt" in result
        # Blacklisted files should be filtered out
        assert "secret.txt" not in result
        assert ".env" not in result

    def test_blacklist_precedence_over_whitelist(self, sample_files: Path):
        """Test that blacklist takes precedence over whitelist."""
        tool = DirectoryReadTool(
            whitelist=["*.txt"],
            blacklist=["*secret*"],
        )
        result = tool._run(directory=str(sample_files), recursive=True)

        # Regular .txt files should be present
        assert "file1.txt" in result
        # Blacklisted .txt files should be filtered
        assert "secret.txt" not in result

    def test_blacklist_directory_pattern(self, sample_files: Path):
        """Test blacklisting files in specific directories."""
        tool = DirectoryReadTool(blacklist=["src/*", "output/*"])
        result = tool._run(directory=str(sample_files), recursive=True)

        # Files in blacklisted directories should be filtered
        assert "main.py" not in result
        assert "result.txt" not in result
        # Other files should be present
        assert "file1.txt" in result


class TestDirectoryReadToolCombined:
    """Combined configuration tests for DirectoryReadTool."""

    def test_sandbox_with_whitelist(self, sample_files: Path):
        """Test sandbox with whitelist."""
        tool = DirectoryReadTool(
            base_directory=str(sample_files),
            whitelist=["*.py"],
        )
        result = tool._run(directory="src")
        assert "main.py" in result
        assert "utils.py" in result

    def test_sandbox_with_blacklist(self, sample_files: Path):
        """Test sandbox with blacklist."""
        tool = DirectoryReadTool(
            base_directory=str(sample_files),
            blacklist=["*secret*", "*.env"],
        )
        result = tool._run(directory=".")
        assert "file1.txt" in result
        assert "secret.txt" not in result

    def test_full_configuration(self, sample_files: Path):
        """Test with sandbox, whitelist, and blacklist."""
        tool = DirectoryReadTool(
            base_directory=str(sample_files),
            whitelist=["*.txt", "*.md"],
            blacklist=["*secret*"],
        )
        result = tool._run(directory=".", recursive=True)

        # Allowed files
        assert "file1.txt" in result
        assert "readme.md" in result

        # Blocked by extension filter
        assert "main.py" not in result

        # Blocked by blacklist
        assert "secret.txt" not in result
