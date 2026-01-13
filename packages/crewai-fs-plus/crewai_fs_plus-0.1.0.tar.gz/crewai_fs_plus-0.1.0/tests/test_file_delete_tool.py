"""Tests for FileDeleteTool."""

from pathlib import Path

import pytest

from crewai_fs_plus import FileDeleteTool


class TestFileDeleteToolBasic:
    """Basic functionality tests for FileDeleteTool."""

    def test_delete_file(self, sample_files: Path):
        """Test deleting a file."""
        file_path = sample_files / "file1.txt"
        assert file_path.exists()

        tool = FileDeleteTool()
        result = tool._run(path=str(file_path))
        assert "Successfully" in result
        assert not file_path.exists()

    def test_delete_nonexistent_file(self, temp_dir: Path):
        """Test deleting a file that doesn't exist."""
        tool = FileDeleteTool()
        result = tool._run(path=str(temp_dir / "nonexistent.txt"))
        assert "Error" in result

    def test_delete_empty_directory(self, empty_dir: Path):
        """Test deleting an empty directory."""
        tool = FileDeleteTool()
        result = tool._run(path=str(empty_dir))
        assert "Successfully" in result
        assert not empty_dir.exists()

    def test_delete_nonempty_directory_without_recursive(self, sample_files: Path):
        """Test that deleting non-empty directory fails without recursive."""
        docs_dir = sample_files / "docs"
        assert docs_dir.exists()
        assert any(docs_dir.iterdir())  # Not empty

        tool = FileDeleteTool()
        result = tool._run(path=str(docs_dir), recursive=False)
        assert "Error" in result
        assert "not empty" in result.lower() or "recursive" in result.lower()
        assert docs_dir.exists()

    def test_delete_nonempty_directory_with_recursive(self, sample_files: Path):
        """Test deleting non-empty directory with recursive=True."""
        docs_dir = sample_files / "docs"
        assert docs_dir.exists()

        tool = FileDeleteTool()
        result = tool._run(path=str(docs_dir), recursive=True)
        assert "Successfully" in result
        assert not docs_dir.exists()

    def test_recursive_string_true(self, sample_files: Path):
        """Test recursive with string 'true'."""
        docs_dir = sample_files / "docs"
        tool = FileDeleteTool()
        result = tool._run(path=str(docs_dir), recursive="true")
        assert "Successfully" in result

    def test_recursive_string_yes(self, sample_files: Path):
        """Test recursive with string 'yes'."""
        src_dir = sample_files / "src"
        tool = FileDeleteTool()
        result = tool._run(path=str(src_dir), recursive="yes")
        assert "Successfully" in result


class TestFileDeleteToolSandbox:
    """Sandbox/base_directory tests for FileDeleteTool."""

    def test_delete_within_sandbox(self, sample_files: Path):
        """Test deleting within the sandbox."""
        tool = FileDeleteTool(base_directory=str(sample_files))
        result = tool._run(path="file1.txt")
        assert "Successfully" in result
        assert not (sample_files / "file1.txt").exists()

    def test_delete_outside_sandbox_blocked(self, temp_dir: Path):
        """Test that deleting outside sandbox is blocked."""
        # Create sandbox and outside file
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()
        (sandbox / "inside.txt").write_text("inside")

        outside_file = temp_dir / "outside.txt"
        outside_file.write_text("outside")

        tool = FileDeleteTool(base_directory=str(sandbox))
        result = tool._run(path=str(outside_file))
        assert "Error" in result
        assert outside_file.exists()

    def test_path_escape_blocked(self, sample_files: Path):
        """Test that ../ path escapes are blocked."""
        tool = FileDeleteTool(base_directory=str(sample_files / "src"))
        result = tool._run(path="../file1.txt")
        assert "Error" in result
        assert (sample_files / "file1.txt").exists()


class TestFileDeleteToolWhitelist:
    """Whitelist tests for FileDeleteTool."""

    def test_whitelist_allows_matching_path(self, sample_files: Path):
        """Test that whitelist allows matching paths."""
        tool = FileDeleteTool(whitelist=["*.txt"])
        result = tool._run(path=str(sample_files / "file1.txt"))
        assert "Successfully" in result

    def test_whitelist_blocks_non_matching_path(self, sample_files: Path):
        """Test that whitelist blocks non-matching paths."""
        tool = FileDeleteTool(whitelist=["*.txt"])
        result = tool._run(path=str(sample_files / "file2.py"))
        assert "Error" in result
        assert (sample_files / "file2.py").exists()


class TestFileDeleteToolBlacklist:
    """Blacklist tests for FileDeleteTool."""

    def test_blacklist_blocks_matching_path(self, sample_files: Path):
        """Test that blacklist blocks matching paths."""
        tool = FileDeleteTool(blacklist=["*secret*"])
        result = tool._run(path=str(sample_files / "secret.txt"))
        assert "Error" in result
        assert (sample_files / "secret.txt").exists()

    def test_blacklist_allows_non_matching_path(self, sample_files: Path):
        """Test that blacklist allows non-matching paths."""
        tool = FileDeleteTool(blacklist=["*secret*"])
        result = tool._run(path=str(sample_files / "file1.txt"))
        assert "Successfully" in result

    def test_blacklist_precedence_over_whitelist(self, sample_files: Path):
        """Test that blacklist takes precedence over whitelist."""
        tool = FileDeleteTool(
            whitelist=["*.txt"],
            blacklist=["*secret*"],
        )
        result = tool._run(path=str(sample_files / "secret.txt"))
        assert "Error" in result
        assert (sample_files / "secret.txt").exists()

    def test_blacklist_protects_important_directories(self, sample_files: Path):
        """Test protecting important directories with blacklist."""
        tool = FileDeleteTool(blacklist=["src/**", "src"])
        result = tool._run(path=str(sample_files / "src"), recursive=True)
        assert "Error" in result
        assert (sample_files / "src").exists()
