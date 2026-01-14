"""Tests for file system utilities."""
from __future__ import annotations

from pathlib import Path

import pytest

from adr_builder.fs import (
    ensure_dir,
    slugify,
    parse_adr_filename,
    get_existing_adrs,
    next_index,
    format_index,
)


class TestSlugify:
    """Tests for the slugify function."""

    def test_simple(self) -> None:
        """Test simple title conversion."""
        assert slugify("Database Selection") == "database-selection"

    def test_special_characters(self) -> None:
        """Test handling of special characters."""
        assert slugify("API v2.0 Design!") == "api-v2-0-design"

    def test_multiple_spaces(self) -> None:
        """Test handling of multiple spaces."""
        assert slugify("Hello   World") == "hello-world"

    def test_leading_trailing_spaces(self) -> None:
        """Test trimming of spaces."""
        assert slugify("  Test  ") == "test"

    def test_uppercase(self) -> None:
        """Test case conversion."""
        assert slugify("ALL UPPERCASE") == "all-uppercase"

    def test_empty_string(self) -> None:
        """Test empty string returns default."""
        assert slugify("") == "adr"
        assert slugify("   ") == "adr"

    def test_numbers_preserved(self) -> None:
        """Test that numbers are preserved."""
        assert slugify("Version 123") == "version-123"

    def test_multiple_hyphens_collapsed(self) -> None:
        """Test that multiple hyphens are collapsed."""
        assert slugify("A---B") == "a-b"


class TestParseAdrFilename:
    """Tests for the parse_adr_filename function."""

    def test_valid_md(self) -> None:
        """Test parsing valid markdown filename."""
        result = parse_adr_filename("001-database-selection.md")
        assert result == (1, "database-selection", "md")

    def test_valid_docx(self) -> None:
        """Test parsing valid docx filename."""
        result = parse_adr_filename("042-api-design.docx")
        assert result == (42, "api-design", "docx")

    def test_three_digit_index(self) -> None:
        """Test three-digit index."""
        result = parse_adr_filename("123-test-adr.md")
        assert result == (123, "test-adr", "md")

    def test_four_digit_index(self) -> None:
        """Test four-digit index."""
        result = parse_adr_filename("1234-test-adr.md")
        assert result == (1234, "test-adr", "md")

    def test_invalid_no_index(self) -> None:
        """Test invalid filename without index."""
        assert parse_adr_filename("no-index.md") is None

    def test_invalid_short_index(self) -> None:
        """Test invalid filename with short index."""
        assert parse_adr_filename("01-too-short.md") is None

    def test_invalid_extension(self) -> None:
        """Test invalid file extension."""
        assert parse_adr_filename("001-test.txt") is None

    def test_invalid_uppercase(self) -> None:
        """Test that uppercase slug is invalid."""
        assert parse_adr_filename("001-Test-Adr.md") is None


class TestEnsureDir:
    """Tests for the ensure_dir function."""

    def test_creates_directory(self, temp_dir: Path) -> None:
        """Test creating a new directory."""
        new_dir = temp_dir / "new" / "nested" / "dir"
        assert not new_dir.exists()
        ensure_dir(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory(self, temp_dir: Path) -> None:
        """Test with existing directory (no error)."""
        ensure_dir(temp_dir)  # Should not raise


class TestGetExistingAdrs:
    """Tests for the get_existing_adrs function."""

    def test_empty_directory(self, temp_dir: Path) -> None:
        """Test with empty directory."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        result = get_existing_adrs(adr_dir)
        assert result == []

    def test_nonexistent_directory(self, temp_dir: Path) -> None:
        """Test with nonexistent directory."""
        adr_dir = temp_dir / "nonexistent"
        result = get_existing_adrs(adr_dir)
        assert result == []

    def test_finds_md_files(self, temp_dir: Path) -> None:
        """Test finding markdown files."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-first.md").write_text("# First")
        (adr_dir / "002-second.md").write_text("# Second")

        result = get_existing_adrs(adr_dir)
        assert len(result) == 2
        assert result[0][0] == 1
        assert result[1][0] == 2

    def test_finds_docx_files(self, temp_dir: Path) -> None:
        """Test finding docx files."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-first.docx").write_text("")  # Empty for test
        (adr_dir / "002-second.docx").write_text("")

        result = get_existing_adrs(adr_dir)
        assert len(result) == 2

    def test_deduplicates_same_index(self, temp_dir: Path) -> None:
        """Test that same index is deduplicated (md and docx with same number)."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-test.md").write_text("# Test")
        (adr_dir / "001-test.docx").write_text("")

        result = get_existing_adrs(adr_dir)
        # Should only return one entry for index 1
        assert len(result) == 1
        assert result[0][0] == 1
        assert result[0][2].suffix == ".md"

    def test_filter_by_extension(self, temp_dir: Path) -> None:
        """Test filtering by extension."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-test.md").write_text("# Test")
        (adr_dir / "002-test.docx").write_text("")

        md_only = get_existing_adrs(adr_dir, extension="md")
        assert len(md_only) == 1
        assert md_only[0][2].suffix == ".md"

        docx_only = get_existing_adrs(adr_dir, extension="docx")
        assert len(docx_only) == 1
        assert docx_only[0][2].suffix == ".docx"

    def test_sorted_by_index(self, temp_dir: Path) -> None:
        """Test results are sorted by index."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "003-third.md").write_text("")
        (adr_dir / "001-first.md").write_text("")
        (adr_dir / "002-second.md").write_text("")

        result = get_existing_adrs(adr_dir)
        indices = [r[0] for r in result]
        assert indices == [1, 2, 3]

    def test_ignores_invalid_files(self, temp_dir: Path) -> None:
        """Test that invalid files are ignored."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-valid.md").write_text("")
        (adr_dir / "invalid.md").write_text("")
        (adr_dir / "README.md").write_text("")

        result = get_existing_adrs(adr_dir)
        assert len(result) == 1


class TestNextIndex:
    """Tests for the next_index function."""

    def test_empty_directory(self, temp_dir: Path) -> None:
        """Test next index in empty directory."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        assert next_index(adr_dir) == 1

    def test_with_existing(self, temp_dir: Path) -> None:
        """Test next index with existing ADRs."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-first.md").write_text("")
        (adr_dir / "002-second.md").write_text("")

        assert next_index(adr_dir) == 3

    def test_with_gaps(self, temp_dir: Path) -> None:
        """Test next index with gaps in numbering."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-first.md").write_text("")
        (adr_dir / "005-fifth.md").write_text("")

        # Should be 6, not 2 (continues from highest)
        assert next_index(adr_dir) == 6

    def test_considers_docx(self, temp_dir: Path) -> None:
        """Test that docx files affect next index."""
        adr_dir = temp_dir / "adr"
        adr_dir.mkdir()
        (adr_dir / "001-first.md").write_text("")
        (adr_dir / "003-third.docx").write_text("")

        assert next_index(adr_dir) == 4


class TestFormatIndex:
    """Tests for the format_index function."""

    def test_single_digit(self) -> None:
        """Test formatting single digit."""
        assert format_index(1) == "001"

    def test_double_digit(self) -> None:
        """Test formatting double digit."""
        assert format_index(42) == "042"

    def test_triple_digit(self) -> None:
        """Test formatting triple digit."""
        assert format_index(123) == "123"

    def test_four_digit(self) -> None:
        """Test formatting four digit."""
        assert format_index(1234) == "1234"
