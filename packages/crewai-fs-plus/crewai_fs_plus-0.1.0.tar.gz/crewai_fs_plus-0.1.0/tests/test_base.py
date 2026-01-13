"""Tests for base module functionality."""

import os
from pathlib import Path

import pytest

from crewai_fs_plus.base import (
    matches_any_pattern,
    resolve_path,
    validate_path,
)
from crewai_fs_plus.exceptions import PathNotAllowedError, PathOutsideSandboxError


class TestMatchesAnyPattern:
    """Tests for matches_any_pattern function."""

    def test_matches_simple_glob(self):
        """Test matching simple glob patterns."""
        assert matches_any_pattern("test.txt", ["*.txt"])
        assert matches_any_pattern("file.py", ["*.py"])
        assert not matches_any_pattern("test.txt", ["*.py"])

    def test_matches_filename_pattern(self):
        """Test matching against filename only."""
        assert matches_any_pattern("path/to/file.txt", ["*.txt"])
        assert matches_any_pattern("deep/nested/path/script.py", ["*.py"])

    def test_matches_directory_pattern(self):
        """Test matching directory patterns."""
        assert matches_any_pattern("docs/readme.md", ["docs/*"])
        assert matches_any_pattern("src/main.py", ["src/*.py"])

    def test_matches_double_star_pattern(self):
        """Test matching ** patterns."""
        assert matches_any_pattern("a/b/c/file.txt", ["**/*.txt"])
        assert matches_any_pattern("deep/path/secret.txt", ["**/secret*"])

    def test_empty_patterns_returns_false(self):
        """Test that empty pattern list returns False."""
        assert not matches_any_pattern("any/file.txt", [])

    def test_multiple_patterns(self):
        """Test matching against multiple patterns."""
        patterns = ["*.py", "*.txt", "*.md"]
        assert matches_any_pattern("script.py", patterns)
        assert matches_any_pattern("readme.md", patterns)
        assert not matches_any_pattern("data.json", patterns)


class TestResolvePath:
    """Tests for resolve_path function."""

    def test_absolute_path_unchanged(self, temp_dir: Path):
        """Test that absolute paths are returned as-is (resolved)."""
        abs_path = str(temp_dir / "file.txt")
        result = resolve_path(abs_path)
        assert result == Path(abs_path).resolve()

    def test_relative_path_with_base(self, temp_dir: Path):
        """Test relative path resolution with base directory."""
        result = resolve_path("subdir/file.txt", str(temp_dir))
        expected = (temp_dir / "subdir/file.txt").resolve()
        assert result == expected

    def test_relative_path_without_base(self):
        """Test relative path resolution without base directory."""
        result = resolve_path("file.txt")
        expected = (Path.cwd() / "file.txt").resolve()
        assert result == expected


class TestValidatePath:
    """Tests for validate_path function."""

    def test_valid_path_no_restrictions(self, sample_files: Path):
        """Test validation with no restrictions."""
        result = validate_path(str(sample_files / "file1.txt"), must_exist=True)
        assert result == (sample_files / "file1.txt").resolve()

    def test_path_outside_sandbox_raises(self, temp_dir: Path):
        """Test that paths outside sandbox raise error."""
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()

        with pytest.raises(PathOutsideSandboxError):
            validate_path(
                str(temp_dir / "outside.txt"),
                base_directory=str(sandbox),
            )

    def test_path_escape_attempt_blocked(self, temp_dir: Path):
        """Test that ../ escape attempts are blocked."""
        sandbox = temp_dir / "sandbox"
        sandbox.mkdir()
        (sandbox / "file.txt").write_text("test")

        with pytest.raises(PathOutsideSandboxError):
            validate_path(
                "../outside.txt",
                base_directory=str(sandbox),
            )

    def test_whitelist_allows_matching_path(self, sample_files: Path):
        """Test that whitelist allows matching paths."""
        result = validate_path(
            str(sample_files / "file1.txt"),
            whitelist=["*.txt"],
            must_exist=True,
        )
        assert result.exists()

    def test_whitelist_blocks_non_matching_path(self, sample_files: Path):
        """Test that whitelist blocks non-matching paths."""
        with pytest.raises(PathNotAllowedError):
            validate_path(
                str(sample_files / "file2.py"),
                whitelist=["*.txt"],
                must_exist=True,
            )

    def test_blacklist_blocks_matching_path(self, sample_files: Path):
        """Test that blacklist blocks matching paths."""
        with pytest.raises(PathNotAllowedError):
            validate_path(
                str(sample_files / "secret.txt"),
                blacklist=["*secret*"],
                must_exist=True,
            )

    def test_blacklist_takes_precedence(self, sample_files: Path):
        """Test that blacklist takes precedence over whitelist."""
        with pytest.raises(PathNotAllowedError):
            validate_path(
                str(sample_files / "secret.txt"),
                whitelist=["*.txt"],
                blacklist=["*secret*"],
                must_exist=True,
            )

    def test_empty_whitelist_allows_all(self, sample_files: Path):
        """Test that empty whitelist allows all paths."""
        result = validate_path(
            str(sample_files / "file2.py"),
            whitelist=[],
            must_exist=True,
        )
        assert result.exists()

    def test_must_exist_raises_for_missing_file(self, temp_dir: Path):
        """Test that must_exist=True raises for missing files."""
        with pytest.raises(FileNotFoundError):
            validate_path(
                str(temp_dir / "nonexistent.txt"),
                must_exist=True,
            )

    def test_must_exist_false_allows_missing_file(self, temp_dir: Path):
        """Test that must_exist=False allows missing files."""
        result = validate_path(
            str(temp_dir / "nonexistent.txt"),
            must_exist=False,
        )
        assert result == (temp_dir / "nonexistent.txt").resolve()
