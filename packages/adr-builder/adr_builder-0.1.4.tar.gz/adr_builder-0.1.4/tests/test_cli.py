"""Tests for CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from adr_builder.cli import app
from adr_builder import __version__


runner = CliRunner()

try:
    import docx  # noqa: F401
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class TestVersionCommand:
    """Tests for version option."""

    def test_version_flag(self) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.stdout

    def test_version_short_flag(self) -> None:
        """Test -v flag."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.stdout


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_directories(self, temp_dir: Path) -> None:
        """Test that init creates required directories."""
        result = runner.invoke(app, ["init", str(temp_dir)])
        assert result.exit_code == 0

        assert (temp_dir / "docs" / "adr").exists()
        assert (temp_dir / ".adr").exists()
        assert (temp_dir / ".adr" / "adr.config.yaml").exists()

    def test_init_default_directory(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test init with default (current) directory."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (temp_dir / "docs" / "adr").exists()

    def test_init_preserves_existing_config(self, temp_dir: Path) -> None:
        """Test that existing config is not overwritten."""
        config_dir = temp_dir / ".adr"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "adr.config.yaml"
        config_file.write_text("template: custom\n", encoding="utf-8")

        result = runner.invoke(app, ["init", str(temp_dir)])
        assert result.exit_code == 0

        # Config should be preserved
        assert config_file.read_text() == "template: custom\n"


class TestGenerateCommand:
    """Tests for generate command."""

    @pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
    def test_generate_creates_files(
        self, temp_dir: Path, sample_yaml_content: str
    ) -> None:
        """Test that generate creates both md and docx files."""
        # Setup
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text(sample_yaml_content, encoding="utf-8")

        result = runner.invoke(
            app, ["generate", "-i", str(criteria_file), "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        md_files = list(adr_dir.glob("*.md"))
        docx_files = list(adr_dir.glob("*.docx"))

        assert len(md_files) == 1
        assert len(docx_files) == 1

    def test_generate_md_only(
        self, temp_dir: Path, sample_yaml_content: str
    ) -> None:
        """Test generating markdown only."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text(sample_yaml_content, encoding="utf-8")

        result = runner.invoke(
            app,
            ["generate", "-i", str(criteria_file), "--directory", str(temp_dir), "-f", "md"],
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        assert len(list(adr_dir.glob("*.md"))) == 1
        assert len(list(adr_dir.glob("*.docx"))) == 0

    @pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
    def test_generate_docx_only(
        self, temp_dir: Path, sample_yaml_content: str
    ) -> None:
        """Test generating docx only."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text(sample_yaml_content, encoding="utf-8")

        result = runner.invoke(
            app,
            ["generate", "-i", str(criteria_file), "--directory", str(temp_dir), "-f", "docx"],
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        assert len(list(adr_dir.glob("*.md"))) == 0
        assert len(list(adr_dir.glob("*.docx"))) == 1

    @pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
    def test_generate_from_json(
        self, temp_dir: Path, sample_json_content: str
    ) -> None:
        """Test generating from JSON file."""
        criteria_file = temp_dir / "criteria.json"
        criteria_file.write_text(sample_json_content, encoding="utf-8")

        result = runner.invoke(
            app, ["generate", "-i", str(criteria_file), "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0

    def test_generate_invalid_input(self, temp_dir: Path) -> None:
        """Test error with invalid input file."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text("invalid: yaml: [", encoding="utf-8")

        result = runner.invoke(
            app, ["generate", "-i", str(criteria_file), "--directory", str(temp_dir)]
        )
        assert result.exit_code != 0

    def test_generate_validation_error(self, temp_dir: Path) -> None:
        """Test error with validation failure."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text("title: Test\nstatus: Invalid\n", encoding="utf-8")

        result = runner.invoke(
            app, ["generate", "-i", str(criteria_file), "--directory", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "status" in result.stdout.lower()


class TestValidateCommand:
    """Tests for validate command."""

    def test_validate_valid_file(
        self, temp_dir: Path, sample_yaml_content: str
    ) -> None:
        """Test validating a valid file."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text(sample_yaml_content, encoding="utf-8")

        result = runner.invoke(app, ["validate", "-i", str(criteria_file)])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_validate_invalid_file(self, temp_dir: Path) -> None:
        """Test validating an invalid file."""
        criteria_file = temp_dir / "criteria.yaml"
        criteria_file.write_text("title: AB\nstatus: Invalid\n", encoding="utf-8")

        result = runner.invoke(app, ["validate", "-i", str(criteria_file)])
        assert result.exit_code == 1
        assert "failed" in result.stdout.lower()


class TestListCommand:
    """Tests for list command."""

    def test_list_empty(self, temp_dir: Path) -> None:
        """Test listing with no ADRs."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)

        result = runner.invoke(app, ["list", "--directory", str(temp_dir)])
        assert result.exit_code == 0

    def test_list_with_adrs(self, temp_dir: Path) -> None:
        """Test listing existing ADRs."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-first-adr.md").write_text("# First")
        (adr_dir / "002-second-adr.md").write_text("# Second")

        result = runner.invoke(app, ["list", "--directory", str(temp_dir)])
        assert result.exit_code == 0
        assert "first-adr" in result.stdout
        assert "second-adr" in result.stdout
