"""Tests for FileWriteTool."""

from pathlib import Path

import pytest

from crewai_fs_plus import FileWriteTool


class TestFileWriteToolBasic:
    """Basic functionality tests for FileWriteTool."""

    def test_write_new_file(self, temp_dir: Path):
        """Test writing a new file."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(temp_dir / "new_file.txt"),
            content="Hello World",
        )
        assert "Successfully" in result
        assert (temp_dir / "new_file.txt").read_text() == "Hello World"

    def test_write_existing_file_without_overwrite(self, sample_files: Path):
        """Test that writing to existing file fails without overwrite."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(sample_files / "file1.txt"),
            content="New content",
            overwrite=False,
        )
        assert "Error" in result
        assert "exists" in result.lower()
        # Original content should be unchanged
        assert "Hello World" in (sample_files / "file1.txt").read_text()

    def test_write_existing_file_with_overwrite(self, sample_files: Path):
        """Test that writing to existing file works with overwrite."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(sample_files / "file1.txt"),
            content="New content",
            overwrite=True,
        )
        assert "Successfully" in result
        assert (sample_files / "file1.txt").read_text() == "New content"

    def test_write_creates_parent_directories(self, temp_dir: Path):
        """Test that parent directories are created automatically."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(temp_dir / "new_dir" / "subdir" / "file.txt"),
            content="Content",
        )
        assert "Successfully" in result
        assert (temp_dir / "new_dir" / "subdir" / "file.txt").exists()

    def test_overwrite_string_true(self, sample_files: Path):
        """Test overwrite with string 'true'."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(sample_files / "file1.txt"),
            content="Overwritten",
            overwrite="true",
        )
        assert "Successfully" in result

    def test_overwrite_string_yes(self, sample_files: Path):
        """Test overwrite with string 'yes'."""
        tool = FileWriteTool()
        result = tool._run(
            file_path=str(sample_files / "file1.txt"),
            content="Overwritten",
            overwrite="yes",
        )
        assert "Successfully" in result


class TestFileWriteToolSandbox:
    """Sandbox/base_directory tests for FileWriteTool."""

    def test_write_within_sandbox(self, temp_dir: Path):
        """Test writing within the sandbox."""
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()

        tool = FileWriteTool(base_directory=str(sandbox))
        result = tool._run(file_path="test.txt", content="Hello")
        assert "Successfully" in result
        assert (sandbox / "test.txt").read_text() == "Hello"

    def test_write_outside_sandbox_blocked(self, temp_dir: Path):
        """Test that writing outside sandbox is blocked."""
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()

        tool = FileWriteTool(base_directory=str(sandbox))
        result = tool._run(
            file_path=str(temp_dir / "outside.txt"),
            content="Should fail",
        )
        assert "Error" in result
        assert not (temp_dir / "outside.txt").exists()

    def test_path_escape_blocked(self, temp_dir: Path):
        """Test that ../ path escapes are blocked."""
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()

        tool = FileWriteTool(base_directory=str(sandbox))
        result = tool._run(file_path="../escape.txt", content="Should fail")
        assert "Error" in result


class TestFileWriteToolWhitelist:
    """Whitelist tests for FileWriteTool."""

    def test_whitelist_allows_matching_path(self, temp_dir: Path):
        """Test that whitelist allows matching paths."""
        tool = FileWriteTool(whitelist=["*.txt", "output/**"])
        result = tool._run(
            file_path=str(temp_dir / "allowed.txt"),
            content="Content",
        )
        assert "Successfully" in result

    def test_whitelist_blocks_non_matching_path(self, temp_dir: Path):
        """Test that whitelist blocks non-matching paths."""
        tool = FileWriteTool(whitelist=["*.txt"])
        result = tool._run(
            file_path=str(temp_dir / "blocked.py"),
            content="Content",
        )
        assert "Error" in result
        assert not (temp_dir / "blocked.py").exists()


class TestFileWriteToolBlacklist:
    """Blacklist tests for FileWriteTool."""

    def test_blacklist_blocks_matching_path(self, temp_dir: Path):
        """Test that blacklist blocks matching paths."""
        tool = FileWriteTool(blacklist=["*secret*", "*.env"])
        result = tool._run(
            file_path=str(temp_dir / "secret.txt"),
            content="Secret content",
        )
        assert "Error" in result
        assert not (temp_dir / "secret.txt").exists()

    def test_blacklist_blocks_env_file(self, temp_dir: Path):
        """Test that blacklist blocks .env files."""
        tool = FileWriteTool(blacklist=["*.env", ".env"])
        result = tool._run(
            file_path=str(temp_dir / ".env"),
            content="API_KEY=secret",
        )
        assert "Error" in result

    def test_blacklist_precedence_over_whitelist(self, temp_dir: Path):
        """Test that blacklist takes precedence over whitelist."""
        tool = FileWriteTool(
            whitelist=["*.txt"],
            blacklist=["*secret*"],
        )
        result = tool._run(
            file_path=str(temp_dir / "secret.txt"),
            content="Content",
        )
        assert "Error" in result
