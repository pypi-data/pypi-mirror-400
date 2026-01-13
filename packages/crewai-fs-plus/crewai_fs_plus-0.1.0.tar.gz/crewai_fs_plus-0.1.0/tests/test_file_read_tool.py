"""Tests for FileReadTool."""

from pathlib import Path

import pytest

from crewai_fs_plus import FileReadTool


class TestFileReadToolBasic:
    """Basic functionality tests for FileReadTool."""

    def test_read_entire_file(self, sample_files: Path):
        """Test reading an entire file."""
        tool = FileReadTool()
        result = tool._run(file_path=str(sample_files / "file1.txt"))
        assert "Hello World" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_read_with_start_line(self, sample_files: Path):
        """Test reading from a specific line."""
        tool = FileReadTool()
        result = tool._run(file_path=str(sample_files / "file1.txt"), start_line=2)
        assert "Hello World" not in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_read_with_line_count(self, sample_files: Path):
        """Test reading a specific number of lines."""
        tool = FileReadTool()
        result = tool._run(
            file_path=str(sample_files / "file1.txt"),
            start_line=1,
            line_count=2,
        )
        assert "Hello World" in result
        assert "Line 2" in result
        assert "Line 3" not in result

    def test_read_nonexistent_file(self, temp_dir: Path):
        """Test reading a file that doesn't exist."""
        tool = FileReadTool()
        result = tool._run(file_path=str(temp_dir / "nonexistent.txt"))
        assert "Error" in result
        assert "not found" in result.lower() or "not exist" in result.lower()

    def test_read_with_default_file_path(self, sample_files: Path):
        """Test reading with pre-configured file path."""
        tool = FileReadTool(file_path=str(sample_files / "file1.txt"))
        result = tool._run()
        assert "Hello World" in result

    def test_no_file_path_error(self):
        """Test error when no file path is provided."""
        tool = FileReadTool()
        result = tool._run()
        assert "Error" in result


class TestFileReadToolSandbox:
    """Sandbox/base_directory tests for FileReadTool."""

    def test_read_within_sandbox(self, sample_files: Path):
        """Test reading a file within the sandbox."""
        tool = FileReadTool(base_directory=str(sample_files))
        result = tool._run(file_path="file1.txt")
        assert "Hello World" in result

    def test_read_outside_sandbox_blocked(self, sample_files: Path, temp_dir: Path):
        """Test that reading outside sandbox is blocked."""
        # Create a file outside the sandbox
        outside_file = temp_dir / "outside.txt"
        outside_file.write_text("outside content")

        sandbox = sample_files / "src"
        tool = FileReadTool(base_directory=str(sandbox))
        result = tool._run(file_path=str(outside_file))
        assert "Error" in result
        assert "outside" in result.lower() or "sandbox" in result.lower()

    def test_path_escape_blocked(self, sample_files: Path):
        """Test that ../ path escapes are blocked."""
        tool = FileReadTool(base_directory=str(sample_files / "src"))
        result = tool._run(file_path="../file1.txt")
        assert "Error" in result


class TestFileReadToolWhitelist:
    """Whitelist tests for FileReadTool."""

    def test_whitelist_allows_matching_file(self, sample_files: Path):
        """Test that whitelist allows matching files."""
        tool = FileReadTool(whitelist=["*.txt"])
        result = tool._run(file_path=str(sample_files / "file1.txt"))
        assert "Hello World" in result

    def test_whitelist_blocks_non_matching_file(self, sample_files: Path):
        """Test that whitelist blocks non-matching files."""
        tool = FileReadTool(whitelist=["*.txt"])
        result = tool._run(file_path=str(sample_files / "file2.py"))
        assert "Error" in result
        assert "not allowed" in result.lower() or "whitelist" in result.lower()

    def test_multiple_whitelist_patterns(self, sample_files: Path):
        """Test multiple whitelist patterns."""
        tool = FileReadTool(whitelist=["*.py", "*.md"])

        # Should work for .py
        result = tool._run(file_path=str(sample_files / "file2.py"))
        assert "print" in result

        # Should work for .md
        result = tool._run(file_path=str(sample_files / "docs/readme.md"))
        assert "Documentation" in result


class TestFileReadToolBlacklist:
    """Blacklist tests for FileReadTool."""

    def test_blacklist_blocks_matching_file(self, sample_files: Path):
        """Test that blacklist blocks matching files."""
        tool = FileReadTool(blacklist=["*secret*"])
        result = tool._run(file_path=str(sample_files / "secret.txt"))
        assert "Error" in result

    def test_blacklist_allows_non_matching_file(self, sample_files: Path):
        """Test that blacklist allows non-matching files."""
        tool = FileReadTool(blacklist=["*secret*"])
        result = tool._run(file_path=str(sample_files / "file1.txt"))
        assert "Hello World" in result

    def test_blacklist_precedence_over_whitelist(self, sample_files: Path):
        """Test that blacklist takes precedence over whitelist."""
        tool = FileReadTool(whitelist=["*.txt"], blacklist=["*secret*"])
        result = tool._run(file_path=str(sample_files / "secret.txt"))
        assert "Error" in result

    def test_env_file_blacklist(self, sample_files: Path):
        """Test blacklisting .env files."""
        tool = FileReadTool(blacklist=["*.env", ".env"])
        result = tool._run(file_path=str(sample_files / ".env"))
        assert "Error" in result
