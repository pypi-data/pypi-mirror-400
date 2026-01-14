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
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
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
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
        assert len(md_files) == 1
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
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
        assert len(md_files) == 0
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


class TestQuickCommand:
    """Tests for quick command."""

    def test_quick_creates_adr_md_only(self, temp_dir: Path) -> None:
        """Test quick creates ADR (md format only)."""
        # Initialize first
        runner.invoke(app, ["init", str(temp_dir)])

        result = runner.invoke(
            app, ["quick", "Test Decision", "--directory", str(temp_dir), "-f", "md"]
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
        assert len(md_files) == 1
        assert "test-decision" in md_files[0].name

    def test_quick_with_options(self, temp_dir: Path) -> None:
        """Test quick with status and author options."""
        runner.invoke(app, ["init", str(temp_dir)])

        result = runner.invoke(
            app,
            [
                "quick",
                "Auth Decision",
                "--status",
                "Accepted",
                "--author",
                "Jane Doe",
                "--directory",
                str(temp_dir),
                "-f",
                "md",
            ],
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
        assert len(md_files) == 1

        content = md_files[0].read_text()
        assert "Accepted" in content
        assert "Jane Doe" in content

    def test_quick_with_decision(self, temp_dir: Path) -> None:
        """Test quick with decision rationale."""
        runner.invoke(app, ["init", str(temp_dir)])

        result = runner.invoke(
            app,
            [
                "quick",
                "Use REST",
                "-d",
                "Simpler than GraphQL",
                "--directory",
                str(temp_dir),
                "-f",
                "md",
            ],
        )
        assert result.exit_code == 0

        adr_dir = temp_dir / "docs" / "adr"
        md_files = [f for f in adr_dir.glob("*.md") if f.name != "index.md"]
        content = md_files[0].read_text()
        assert "Simpler than GraphQL" in content

    def test_quick_invalid_status(self, temp_dir: Path) -> None:
        """Test quick fails with invalid status."""
        runner.invoke(app, ["init", str(temp_dir)])

        result = runner.invoke(
            app,
            [
                "quick",
                "Test",
                "--status",
                "Invalid",
                "--directory",
                str(temp_dir),
            ],
        )
        assert result.exit_code == 1
        assert "Invalid status" in result.stdout


class TestStatusCommand:
    """Tests for status command."""

    def test_status_view(self, temp_dir: Path) -> None:
        """Test viewing ADR status."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (temp_dir / ".adr").mkdir(parents=True)
        (temp_dir / ".adr" / "adr.config.yaml").write_text(
            "status_values: [Proposed, Accepted, Superseded, Rejected]\n"
        )
        (adr_dir / "001-test-adr.md").write_text("# Test\n\n- Status: Proposed\n")

        result = runner.invoke(app, ["status", "001", "--directory", str(temp_dir)])
        assert result.exit_code == 0
        assert "Proposed" in result.stdout

    def test_status_change(self, temp_dir: Path) -> None:
        """Test changing ADR status."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (temp_dir / ".adr").mkdir(parents=True)
        (temp_dir / ".adr" / "adr.config.yaml").write_text(
            "status_values: [Proposed, Accepted, Superseded, Rejected]\n"
        )
        adr_file = adr_dir / "001-test-adr.md"
        adr_file.write_text("# Test\n\n- Status: Proposed\n")

        result = runner.invoke(
            app, ["status", "001", "Accepted", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert "Accepted" in result.stdout

        # Verify file was updated
        content = adr_file.read_text()
        assert "- Status: Accepted" in content

    def test_status_not_found(self, temp_dir: Path) -> None:
        """Test status command with non-existent ADR."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (temp_dir / ".adr").mkdir(parents=True)
        (temp_dir / ".adr" / "adr.config.yaml").write_text(
            "status_values: [Proposed, Accepted]\n"
        )

        result = runner.invoke(app, ["status", "999", "--directory", str(temp_dir)])
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_status_invalid_status(self, temp_dir: Path) -> None:
        """Test status command with invalid status value."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (temp_dir / ".adr").mkdir(parents=True)
        (temp_dir / ".adr" / "adr.config.yaml").write_text(
            "status_values: [Proposed, Accepted, Superseded, Rejected]\n"
        )
        (adr_dir / "001-test-adr.md").write_text("# Test\n\n- Status: Proposed\n")

        result = runner.invoke(
            app, ["status", "001", "Invalid", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "Invalid status" in result.stdout


class TestSearchCommand:
    """Tests for search command."""

    def test_search_finds_keyword(self, temp_dir: Path) -> None:
        """Test search finds keyword in ADRs."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-database-selection.md").write_text(
            "# Database Selection\n\nWe chose PostgreSQL for our database.\n"
        )

        result = runner.invoke(
            app, ["search", "PostgreSQL", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert "PostgreSQL" in result.stdout
        assert "001" in result.stdout

    def test_search_case_insensitive(self, temp_dir: Path) -> None:
        """Test search is case insensitive."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-test.md").write_text("# Test\n\nDATABASE selection.\n")

        result = runner.invoke(
            app, ["search", "database", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert "DATABASE" in result.stdout or "match" in result.stdout.lower()

    def test_search_no_results(self, temp_dir: Path) -> None:
        """Test search with no matches."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-test.md").write_text("# Test ADR\n")

        result = runner.invoke(
            app, ["search", "nonexistent", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert "No results" in result.stdout

    def test_search_with_limit(self, temp_dir: Path) -> None:
        """Test search with result limit."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-test.md").write_text("# Test\n\ntest line 1\ntest line 2\n")

        result = runner.invoke(
            app, ["search", "test", "--limit", "1", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert "1 match" in result.stdout

    def test_search_no_adr_directory(self, temp_dir: Path) -> None:
        """Test search when ADR directory doesn't exist."""
        result = runner.invoke(app, ["search", "test", "--directory", str(temp_dir)])
        assert result.exit_code == 1
        assert "No ADR directory" in result.stdout


class TestPublishCommand:
    """Tests for publish command."""

    def test_publish_adr_not_found(self, temp_dir: Path) -> None:
        """Test publish when ADR doesn't exist."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)

        result = runner.invoke(
            app, ["publish", "999", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_publish_invalid_number(self, temp_dir: Path) -> None:
        """Test publish with invalid ADR number."""
        result = runner.invoke(
            app, ["publish", "abc", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "Invalid ADR number" in result.stdout

    def test_publish_no_gh_auth(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test publish when gh CLI is not authenticated."""
        adr_dir = temp_dir / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "001-test-adr.md").write_text("# Test ADR\n\n- Status: Proposed\n")

        # Mock _get_gh_username to return None (not authenticated)
        from adr_builder import cli
        monkeypatch.setattr(cli, "_get_gh_username", lambda: None)

        result = runner.invoke(
            app, ["publish", "001", "--directory", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "not authenticated" in result.stdout or "gh auth login" in result.stdout
