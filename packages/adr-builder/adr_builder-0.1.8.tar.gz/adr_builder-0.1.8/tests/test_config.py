"""Tests for configuration loading."""
from __future__ import annotations

from pathlib import Path

import pytest

from adr_builder.config import AdrConfig, DEFAULT_STATUS_VALUES, DEFAULT_TEMPLATE


class TestAdrConfig:
    """Tests for the AdrConfig class."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = AdrConfig()
        assert config.template == DEFAULT_TEMPLATE
        assert config.status_values == DEFAULT_STATUS_VALUES

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = AdrConfig(
            template="custom",
            status_values=["Draft", "Final", "Archived"],
        )
        assert config.template == "custom"
        assert config.status_values == ["Draft", "Final", "Archived"]

    def test_is_valid_status(self) -> None:
        """Test status validation."""
        config = AdrConfig()
        assert config.is_valid_status("Proposed")
        assert config.is_valid_status("Accepted")
        assert not config.is_valid_status("Invalid")
        assert not config.is_valid_status("proposed")  # case sensitive

    def test_is_valid_status_custom(self) -> None:
        """Test status validation with custom values."""
        config = AdrConfig(status_values=["Draft", "Final"])
        assert config.is_valid_status("Draft")
        assert config.is_valid_status("Final")
        assert not config.is_valid_status("Proposed")


class TestAdrConfigLoad:
    """Tests for loading configuration from file."""

    def test_load_nonexistent(self) -> None:
        """Test loading from nonexistent file returns defaults."""
        config = AdrConfig.load(config_path=Path("/nonexistent/path.yaml"))
        assert config.template == DEFAULT_TEMPLATE
        assert config.status_values == DEFAULT_STATUS_VALUES

    def test_load_from_project_root(self, temp_dir: Path) -> None:
        """Test loading from project root."""
        config_dir = temp_dir / ".adr"
        config_dir.mkdir()
        config_file = config_dir / "adr.config.yaml"
        config_file.write_text(
            "template: custom-template\n"
            "status_values: [Draft, Review, Final]\n",
            encoding="utf-8",
        )

        config = AdrConfig.load(project_root=temp_dir)
        assert config.template == "custom-template"
        assert config.status_values == ["Draft", "Review", "Final"]

    def test_load_direct_path(self, temp_dir: Path) -> None:
        """Test loading from direct path."""
        config_file = temp_dir / "my-config.yaml"
        config_file.write_text(
            "template: my-template\n"
            "status_values: [New, Done]\n",
            encoding="utf-8",
        )

        config = AdrConfig.load(config_path=config_file)
        assert config.template == "my-template"
        assert config.status_values == ["New", "Done"]

    def test_load_partial_config(self, temp_dir: Path) -> None:
        """Test loading config with only some values."""
        config_file = temp_dir / "partial.yaml"
        config_file.write_text("template: custom\n", encoding="utf-8")

        config = AdrConfig.load(config_path=config_file)
        assert config.template == "custom"
        assert config.status_values == DEFAULT_STATUS_VALUES  # default

    def test_load_empty_file(self, temp_dir: Path) -> None:
        """Test loading empty config file."""
        config_file = temp_dir / "empty.yaml"
        config_file.write_text("", encoding="utf-8")

        config = AdrConfig.load(config_path=config_file)
        assert config.template == DEFAULT_TEMPLATE
        assert config.status_values == DEFAULT_STATUS_VALUES

    def test_load_invalid_yaml(self, temp_dir: Path) -> None:
        """Test loading invalid YAML returns defaults."""
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        config = AdrConfig.load(config_path=config_file)
        assert config.template == DEFAULT_TEMPLATE

    def test_load_no_args_returns_defaults(self) -> None:
        """Test loading with no arguments returns defaults."""
        config = AdrConfig.load()
        assert config.template == DEFAULT_TEMPLATE
        assert config.status_values == DEFAULT_STATUS_VALUES
