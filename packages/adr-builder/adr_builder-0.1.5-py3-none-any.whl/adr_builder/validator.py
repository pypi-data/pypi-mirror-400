from __future__ import annotations

import re
from pathlib import Path

from .config import AdrConfig
from .models import CriteriaModel

REQUIRED_FIELDS = ["title", "status"]

# Simple URL pattern for validation
URL_PATTERN = re.compile(
    r"^https?://"  # http:// or https://
    r"[a-zA-Z0-9]"  # starts with alphanumeric
    r"[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]*$"  # valid URL chars
)

# ISO date pattern (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_criteria(
    criteria: CriteriaModel,
    config: AdrConfig | None = None,
    project_root: Path | None = None,
) -> list[str]:
    """
    Validate ADR criteria for completeness and consistency.

    Args:
        criteria: The criteria model to validate
        config: Optional config instance. If None, will attempt to load from project_root.
        project_root: Optional project root for loading config

    Returns:
        List of error messages (empty if valid)
    """
    errors: list[str] = []

    # Load config if not provided
    if config is None:
        config = AdrConfig.load(project_root=project_root)

    # Required fields presence
    for field_name in REQUIRED_FIELDS:
        value = getattr(criteria, field_name)
        if value in (None, "", []):
            errors.append(f"Missing required field: {field_name}")

    # Validate title is not too short
    if criteria.title and len(criteria.title.strip()) < 3:
        errors.append("Title must be at least 3 characters long")

    # Status validation using config
    if criteria.status and not config.is_valid_status(criteria.status):
        allowed = ", ".join(sorted(config.status_values))
        errors.append(f"Invalid status '{criteria.status}'. Allowed: {allowed}")

    # Date format validation
    if criteria.date and not DATE_PATTERN.match(criteria.date):
        errors.append(f"Invalid date format '{criteria.date}'. Expected: YYYY-MM-DD")

    # Encourage rationale if decision exists
    if criteria.decision and not (criteria.decision.rationale or "").strip():
        errors.append("Decision rationale should not be empty when a decision is provided.")

    # Validate options
    if criteria.options is not None:
        if len(criteria.options) < 1:
            errors.append("If 'options' is provided, it should include at least one option.")
        else:
            # Check for duplicate option names
            option_names: set[str] = set()
            for opt in criteria.options:
                name_lower = opt.name.lower().strip()
                if name_lower in option_names:
                    errors.append(f"Duplicate option name: '{opt.name}'")
                option_names.add(name_lower)

            # Validate score range if provided
            for opt in criteria.options:
                if opt.score is not None and (opt.score < 0 or opt.score > 10):
                    errors.append(f"Option '{opt.name}' score must be between 0 and 10")

    # Validate references URLs
    if criteria.references and criteria.references.links:
        for link in criteria.references.links:
            # Only validate if it looks like a URL (starts with http)
            if link.startswith("http") and not URL_PATTERN.match(link):
                errors.append(f"Invalid URL format: '{link}'")

    # Validate decision chosen matches an option if options are provided
    if criteria.decision and criteria.options:
        option_names = {opt.name.lower().strip() for opt in criteria.options}
        chosen_lower = criteria.decision.chosen.lower().strip()
        if chosen_lower not in option_names:
            errors.append(
                f"Decision chosen '{criteria.decision.chosen}' does not match any provided option"
            )

    return errors
