"""Tests for validation logic."""
from __future__ import annotations

from pathlib import Path

import pytest

from adr_builder.config import AdrConfig
from adr_builder.models import CriteriaModel, OptionModel, DecisionModel, ReferencesModel
from adr_builder.validator import validate_criteria


class TestValidateCriteria:
    """Tests for the validate_criteria function."""

    def test_valid_minimal(self, minimal_criteria: CriteriaModel) -> None:
        """Test validation passes for minimal valid criteria."""
        errors = validate_criteria(minimal_criteria)
        assert errors == []

    def test_valid_full(self, full_criteria: CriteriaModel) -> None:
        """Test validation passes for fully populated criteria."""
        errors = validate_criteria(full_criteria)
        assert errors == []

    def test_missing_title(self) -> None:
        """Test validation fails when title is empty."""
        criteria = CriteriaModel(title="", status="Proposed")
        errors = validate_criteria(criteria)
        assert any("title" in e.lower() for e in errors)

    def test_invalid_status(self) -> None:
        """Test validation fails for invalid status."""
        criteria = CriteriaModel(title="Test", status="Invalid")
        errors = validate_criteria(criteria)
        assert any("status" in e.lower() for e in errors)

    def test_custom_status_values(self) -> None:
        """Test validation with custom status values from config."""
        config = AdrConfig(status_values=["Draft", "Final"])
        criteria = CriteriaModel(title="Test", status="Draft")
        errors = validate_criteria(criteria, config=config)
        assert errors == []

        # Original status should now be invalid
        criteria2 = CriteriaModel(title="Test", status="Proposed")
        errors2 = validate_criteria(criteria2, config=config)
        assert any("status" in e.lower() for e in errors2)

    def test_title_too_short(self) -> None:
        """Test validation fails for very short title."""
        criteria = CriteriaModel(title="AB", status="Proposed")
        errors = validate_criteria(criteria)
        assert any("3 characters" in e for e in errors)

    def test_invalid_date_format(self) -> None:
        """Test validation fails for invalid date format."""
        criteria = CriteriaModel(title="Test", status="Proposed", date="01-15-2024")
        errors = validate_criteria(criteria)
        assert any("date format" in e.lower() for e in errors)

    def test_valid_date_format(self) -> None:
        """Test validation passes for valid date format."""
        criteria = CriteriaModel(title="Test", status="Proposed", date="2024-01-15")
        errors = validate_criteria(criteria)
        assert errors == []

    def test_decision_without_rationale(self) -> None:
        """Test warning when decision has no rationale."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            decision=DecisionModel(chosen="Option A"),
        )
        errors = validate_criteria(criteria)
        assert any("rationale" in e.lower() for e in errors)

    def test_decision_with_rationale(self) -> None:
        """Test no warning when decision has rationale."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            decision=DecisionModel(chosen="Option A", rationale="Good choice"),
        )
        errors = validate_criteria(criteria)
        assert not any("rationale" in e.lower() for e in errors)

    def test_empty_options_list(self) -> None:
        """Test validation fails for empty options list."""
        criteria = CriteriaModel(title="Test", status="Proposed", options=[])
        errors = validate_criteria(criteria)
        assert any("option" in e.lower() for e in errors)

    def test_duplicate_option_names(self) -> None:
        """Test validation fails for duplicate option names."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[
                OptionModel(name="Option A"),
                OptionModel(name="Option A"),  # duplicate
            ],
        )
        errors = validate_criteria(criteria)
        assert any("duplicate" in e.lower() for e in errors)

    def test_duplicate_option_names_case_insensitive(self) -> None:
        """Test duplicate detection is case-insensitive."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[
                OptionModel(name="Option A"),
                OptionModel(name="option a"),  # duplicate (different case)
            ],
        )
        errors = validate_criteria(criteria)
        assert any("duplicate" in e.lower() for e in errors)

    def test_score_out_of_range(self) -> None:
        """Test validation fails for score out of range."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[OptionModel(name="Option A", score=15.0)],
        )
        errors = validate_criteria(criteria)
        assert any("score" in e.lower() and "0" in e and "10" in e for e in errors)

    def test_score_in_range(self) -> None:
        """Test validation passes for score in valid range."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[OptionModel(name="Option A", score=8.5)],
        )
        errors = validate_criteria(criteria)
        assert not any("score" in e.lower() for e in errors)

    def test_decision_not_matching_options(self) -> None:
        """Test validation fails when decision doesn't match any option."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[
                OptionModel(name="Option A"),
                OptionModel(name="Option B"),
            ],
            decision=DecisionModel(chosen="Option C", rationale="Best"),
        )
        errors = validate_criteria(criteria)
        assert any("does not match" in e.lower() for e in errors)

    def test_decision_matching_options(self) -> None:
        """Test validation passes when decision matches an option."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            options=[
                OptionModel(name="Option A"),
                OptionModel(name="Option B"),
            ],
            decision=DecisionModel(chosen="Option A", rationale="Best fit"),
        )
        errors = validate_criteria(criteria)
        assert not any("does not match" in e.lower() for e in errors)

    def test_invalid_url_format(self) -> None:
        """Test validation warns for invalid URL format."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            references=ReferencesModel(links=["http://invalid url with spaces"]),
        )
        errors = validate_criteria(criteria)
        assert any("url" in e.lower() for e in errors)

    def test_valid_url_format(self) -> None:
        """Test validation passes for valid URLs."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            references=ReferencesModel(links=["https://example.com/path?query=1"]),
        )
        errors = validate_criteria(criteria)
        assert not any("url" in e.lower() for e in errors)

    def test_non_url_links_allowed(self) -> None:
        """Test that non-URL references are allowed (e.g., ADR numbers)."""
        criteria = CriteriaModel(
            title="Test",
            status="Proposed",
            references=ReferencesModel(links=["ADR-001", "See internal docs"]),
        )
        errors = validate_criteria(criteria)
        assert not any("url" in e.lower() for e in errors)
