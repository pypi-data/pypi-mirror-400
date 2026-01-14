"""Tests for ADR generation."""
from __future__ import annotations

from pathlib import Path

import pytest

from adr_builder.generator import (
    render_madr,
    write_adr,
    write_adr_docx,
    prepare_adr_output,
    get_default_template_dir,
    AdrOutputInfo,
)
from adr_builder.models import CriteriaModel


class TestGetDefaultTemplateDir:
    """Tests for get_default_template_dir function."""

    def test_returns_templates_dir(self) -> None:
        """Test that default template dir exists."""
        template_dir = get_default_template_dir()
        assert template_dir.exists()
        assert template_dir.is_dir()
        assert (template_dir / "madr.md.j2").exists()


class TestAdrOutputInfo:
    """Tests for AdrOutputInfo dataclass."""

    def test_md_path(self, temp_dir: Path) -> None:
        """Test markdown path generation."""
        info = AdrOutputInfo(index=1, slug="test-adr", adr_dir=temp_dir)
        assert info.md_path() == temp_dir / "001-test-adr.md"

    def test_docx_path(self, temp_dir: Path) -> None:
        """Test docx path generation."""
        info = AdrOutputInfo(index=42, slug="my-decision", adr_dir=temp_dir)
        assert info.docx_path() == temp_dir / "042-my-decision.docx"


class TestPrepareAdrOutput:
    """Tests for prepare_adr_output function."""

    def test_creates_adr_dir(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that adr directory is created."""
        docs_dir = temp_dir / "docs"
        info = prepare_adr_output(minimal_criteria, docs_dir)
        assert (docs_dir / "adr").exists()

    def test_returns_correct_info(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that correct info is returned."""
        docs_dir = temp_dir / "docs"
        info = prepare_adr_output(minimal_criteria, docs_dir)
        assert info.index == 1
        assert info.slug == "test-adr"
        assert info.adr_dir == docs_dir / "adr"

    def test_increments_index(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that index increments with existing ADRs."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-existing.md").write_text("# Existing")

        info = prepare_adr_output(minimal_criteria, temp_dir / "docs")
        assert info.index == 2


class TestRenderMadr:
    """Tests for render_madr function."""

    def test_renders_title(self, minimal_criteria: CriteriaModel) -> None:
        """Test that title is rendered."""
        content = render_madr(minimal_criteria)
        assert "Test ADR" in content

    def test_renders_status(self, minimal_criteria: CriteriaModel) -> None:
        """Test that status is rendered."""
        content = render_madr(minimal_criteria)
        assert "Proposed" in content

    def test_adds_date_if_missing(self, minimal_criteria: CriteriaModel) -> None:
        """Test that date is added if not provided."""
        content = render_madr(minimal_criteria)
        # Should contain a date in ISO format
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", content)

    def test_uses_provided_date(self) -> None:
        """Test that provided date is used."""
        criteria = CriteriaModel(title="Test", status="Proposed", date="2024-01-15")
        content = render_madr(criteria)
        assert "2024-01-15" in content

    def test_renders_full_criteria(self, full_criteria: CriteriaModel) -> None:
        """Test rendering of full criteria."""
        content = render_madr(full_criteria)
        assert "Database Selection" in content
        assert "PostgreSQL" in content
        assert "MySQL" in content
        assert "John Doe" in content


class TestWriteAdr:
    """Tests for write_adr function."""

    def test_creates_file(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that file is created."""
        docs_dir = temp_dir / "docs"
        output_path = write_adr(minimal_criteria, docs_dir)
        assert output_path.exists()
        assert output_path.suffix == ".md"

    def test_correct_filename(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that filename is correct."""
        docs_dir = temp_dir / "docs"
        output_path = write_adr(minimal_criteria, docs_dir)
        assert output_path.name == "001-test-adr.md"

    def test_uses_shared_output_info(
        self, temp_dir: Path, minimal_criteria: CriteriaModel
    ) -> None:
        """Test using pre-computed output info."""
        docs_dir = temp_dir / "docs"
        info = prepare_adr_output(minimal_criteria, docs_dir)

        # Create first ADR (changes next_index)
        (docs_dir / "adr" / "001-first.md").write_text("# First")

        # Should still use the pre-computed info
        output_path = write_adr(minimal_criteria, docs_dir, output_info=info)
        assert output_path.name == "001-test-adr.md"  # Uses info.index, not next_index

    def test_file_content(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that file content is correct."""
        docs_dir = temp_dir / "docs"
        output_path = write_adr(minimal_criteria, docs_dir)
        content = output_path.read_text()
        assert "Test ADR" in content


class TestWriteAdrDocx:
    """Tests for write_adr_docx function."""

    def test_creates_file(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that file is created."""
        docs_dir = temp_dir / "docs"
        output_path = write_adr_docx(minimal_criteria, docs_dir)
        assert output_path.exists()
        assert output_path.suffix == ".docx"

    def test_correct_filename(self, temp_dir: Path, minimal_criteria: CriteriaModel) -> None:
        """Test that filename is correct."""
        docs_dir = temp_dir / "docs"
        output_path = write_adr_docx(minimal_criteria, docs_dir)
        assert output_path.name == "001-test-adr.docx"

    def test_uses_shared_output_info(
        self, temp_dir: Path, minimal_criteria: CriteriaModel
    ) -> None:
        """Test using pre-computed output info for consistent indexing."""
        docs_dir = temp_dir / "docs"
        info = prepare_adr_output(minimal_criteria, docs_dir)

        # Create an ADR that would change next_index
        (docs_dir / "adr" / "001-first.md").write_text("# First")

        # Should still use the pre-computed info
        output_path = write_adr_docx(minimal_criteria, docs_dir, output_info=info)
        assert output_path.name == "001-test-adr.docx"


class TestDualFormatGeneration:
    """Tests for generating both formats with consistent indexing."""

    def test_same_index_for_both_formats(
        self, temp_dir: Path, minimal_criteria: CriteriaModel
    ) -> None:
        """Test that both formats get the same index when using shared info."""
        docs_dir = temp_dir / "docs"
        info = prepare_adr_output(minimal_criteria, docs_dir)

        md_path = write_adr(minimal_criteria, docs_dir, output_info=info)
        docx_path = write_adr_docx(minimal_criteria, docs_dir, output_info=info)

        # Both should have the same index
        assert md_path.stem == docx_path.stem
        assert "001-test-adr" in md_path.name
        assert "001-test-adr" in docx_path.name

    def test_next_generation_increments(
        self, temp_dir: Path, minimal_criteria: CriteriaModel
    ) -> None:
        """Test that next generation gets incremented index."""
        docs_dir = temp_dir / "docs"

        # First generation
        info1 = prepare_adr_output(minimal_criteria, docs_dir)
        write_adr(minimal_criteria, docs_dir, output_info=info1)

        # Second generation
        info2 = prepare_adr_output(minimal_criteria, docs_dir)
        assert info2.index == 2
