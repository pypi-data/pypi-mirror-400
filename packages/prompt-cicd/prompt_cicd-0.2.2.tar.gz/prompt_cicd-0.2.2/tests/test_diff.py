"""Tests for promptops.diff module."""

import pytest
import tempfile
from pathlib import Path

from promptops.diff import (
    diff_prompts,
    side_by_side_diff,
    inline_diff,
    diff_summary,
    diff_files,
    diff_objects,
)


class TestDiffPrompts:
    """Tests for diff_prompts function."""

    def test_identical_prompts(self):
        """Test diff of identical prompts."""
        text = "Hello, World!"
        result = diff_prompts(text, text)
        # No diff lines for identical content
        assert result == ""

    def test_unified_diff(self):
        """Test unified diff mode."""
        old = "line 1\nline 2\nline 3"
        new = "line 1\nline 2 modified\nline 3"
        result = diff_prompts(old, new, mode="unified")
        assert "-line 2" in result
        assert "+line 2 modified" in result

    def test_side_by_side_mode(self):
        """Test side-by-side diff mode."""
        old = "old text"
        new = "new text"
        result = diff_prompts(old, new, mode="side-by-side")
        assert "|" in result  # Side-by-side separator

    def test_inline_mode(self):
        """Test inline diff mode."""
        old = "line one\nline two"
        new = "line one\nline three"
        result = diff_prompts(old, new, mode="inline")
        assert "- line two" in result
        assert "+ line three" in result

    def test_unknown_mode_raises(self):
        """Test that unknown mode raises ValueError."""
        with pytest.raises(ValueError, match="Unknown diff mode"):
            diff_prompts("a", "b", mode="unknown")

    def test_color_option(self):
        """Test diff with color option."""
        old = "old"
        new = "new"
        result = diff_prompts(old, new, mode="unified", color=True)
        # Result should still contain the diff content
        assert "old" in result or "new" in result


class TestSideBySideDiff:
    """Tests for side_by_side_diff function."""

    def test_equal_length_lists(self):
        """Test side-by-side diff with equal length lists."""
        old = ["line 1", "line 2"]
        new = ["line 1 mod", "line 2 mod"]
        result = side_by_side_diff(old, new)
        assert "|" in result

    def test_different_length_lists(self):
        """Test side-by-side diff with different length lists."""
        old = ["line 1", "line 2", "line 3"]
        new = ["line 1"]
        result = side_by_side_diff(old, new)
        assert "line 1" in result


class TestInlineDiff:
    """Tests for inline_diff function."""

    def test_additions(self):
        """Test inline diff shows additions."""
        old = ["line 1"]
        new = ["line 1", "line 2"]
        result = inline_diff(old, new)
        assert "+ line 2" in result

    def test_deletions(self):
        """Test inline diff shows deletions."""
        old = ["line 1", "line 2"]
        new = ["line 1"]
        result = inline_diff(old, new)
        assert "- line 2" in result


class TestDiffSummary:
    """Tests for diff_summary function."""

    def test_no_changes(self):
        """Test summary for identical content."""
        result = diff_summary("same", "same")
        assert result["added"] == 0
        assert result["removed"] == 0

    def test_additions(self):
        """Test summary counts additions."""
        old = "line 1"
        new = "line 1\nline 2"
        result = diff_summary(old, new)
        assert result["added"] == 1

    def test_removals(self):
        """Test summary counts removals."""
        old = "line 1\nline 2"
        new = "line 1"
        result = diff_summary(old, new)
        assert result["removed"] == 1

    def test_mixed_changes(self):
        """Test summary with mixed changes."""
        old = "line 1\nline 2\nline 3"
        new = "line 1\nline 2 modified\nline 4"
        result = diff_summary(old, new)
        assert result["added"] >= 1
        assert result["removed"] >= 1


class TestDiffFiles:
    """Tests for diff_files function."""

    def test_diff_two_files(self, temp_dir):
        """Test diffing two files."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        
        file1.write_text("old content")
        file2.write_text("new content")
        
        result = diff_files(str(file1), str(file2))
        assert "old content" in result or "new content" in result


class TestDiffObjects:
    """Tests for diff_objects function."""

    def test_diff_strings(self):
        """Test diffing string objects."""
        result = diff_objects("object 1", "object 2")
        assert "object" in result

    def test_diff_dicts(self):
        """Test diffing dict objects via their string representation."""
        obj1 = {"key": "value1"}
        obj2 = {"key": "value2"}
        result = diff_objects(obj1, obj2)
        assert "value" in result
