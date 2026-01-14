from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_STATUS_VALUES = ["Proposed", "Accepted", "Superseded", "Rejected"]
DEFAULT_TEMPLATE = "madr"

# Built-in template names (for documentation/validation)
BUILTIN_TEMPLATE_NAMES = ["madr", "hld", "lld"]


@dataclass
class AdrConfig:
    """Configuration for ADR Builder."""
    template: str = DEFAULT_TEMPLATE
    status_values: list[str] = field(default_factory=lambda: DEFAULT_STATUS_VALUES.copy())

    @classmethod
    def load(cls, config_path: Path | None = None, project_root: Path | None = None) -> AdrConfig:
        """
        Load configuration from file.

        Args:
            config_path: Direct path to config file
            project_root: Project root directory (will look for .adr/adr.config.yaml)

        Returns:
            AdrConfig instance with loaded or default values
        """
        if config_path is None and project_root is not None:
            config_path = project_root / ".adr" / "adr.config.yaml"

        if config_path is None or not config_path.exists():
            return cls()

        try:
            text = config_path.read_text(encoding="utf-8")
            data = yaml.safe_load(text) or {}
            return cls(
                template=data.get("template", DEFAULT_TEMPLATE),
                status_values=data.get("status_values", DEFAULT_STATUS_VALUES.copy()),
            )
        except Exception:
            # Fall back to defaults on any error
            return cls()

    def is_valid_status(self, status: str) -> bool:
        """Check if a status value is valid according to config."""
        return status in self.status_values
