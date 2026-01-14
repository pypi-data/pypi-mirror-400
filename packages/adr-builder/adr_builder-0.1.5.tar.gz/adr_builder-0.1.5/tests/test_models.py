"""Tests for data models."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from adr_builder.models import (
    CriteriaModel,
    ContextModel,
    OptionModel,
    DecisionModel,
    ConsequencesModel,
    ReferencesModel,
)


class TestCriteriaModel:
    """Tests for the CriteriaModel."""

    def test_minimal_valid(self) -> None:
        """Test creating a model with only required fields."""
        model = CriteriaModel(title="Test ADR")
        assert model.title == "Test ADR"
        assert model.status == "Proposed"  # default

    def test_full_model(self, full_criteria: CriteriaModel) -> None:
        """Test creating a fully populated model."""
        assert full_criteria.title == "Database Selection"
        assert full_criteria.status == "Accepted"
        assert full_criteria.authors == ["John Doe", "Jane Smith"]
        assert len(full_criteria.options or []) == 2

    def test_title_required(self) -> None:
        """Test that title is required."""
        with pytest.raises(ValidationError):
            CriteriaModel()  # type: ignore[call-arg]

    def test_status_default(self) -> None:
        """Test that status defaults to Proposed."""
        model = CriteriaModel(title="Test")
        assert model.status == "Proposed"

    def test_model_dump(self, minimal_criteria: CriteriaModel) -> None:
        """Test that model_dump returns expected structure."""
        data = minimal_criteria.model_dump()
        assert data["title"] == "Test ADR"
        assert data["status"] == "Proposed"
        assert data["authors"] is None


class TestOptionModel:
    """Tests for the OptionModel."""

    def test_minimal(self) -> None:
        """Test option with only name."""
        opt = OptionModel(name="Option A")
        assert opt.name == "Option A"
        assert opt.pros is None
        assert opt.score is None

    def test_with_score(self) -> None:
        """Test option with score."""
        opt = OptionModel(name="Option A", score=8.5)
        assert opt.score == 8.5

    def test_full_option(self) -> None:
        """Test fully populated option."""
        opt = OptionModel(
            name="PostgreSQL",
            pros=["Fast", "Reliable"],
            cons=["Complex"],
            risks=["Learning curve"],
            score=9.0,
        )
        assert len(opt.pros or []) == 2
        assert len(opt.cons or []) == 1


class TestDecisionModel:
    """Tests for the DecisionModel."""

    def test_minimal(self) -> None:
        """Test decision with only chosen field."""
        dec = DecisionModel(chosen="Option A")
        assert dec.chosen == "Option A"
        assert dec.rationale is None

    def test_with_rationale(self) -> None:
        """Test decision with rationale."""
        dec = DecisionModel(chosen="Option A", rationale="Best fit")
        assert dec.rationale == "Best fit"


class TestContextModel:
    """Tests for the ContextModel."""

    def test_empty(self) -> None:
        """Test empty context."""
        ctx = ContextModel()
        assert ctx.background is None
        assert ctx.constraints is None

    def test_full(self) -> None:
        """Test fully populated context."""
        ctx = ContextModel(
            background="We need to decide...",
            constraints=["Budget limited", "Time constraint"],
            drivers=["Performance", "Cost"],
        )
        assert len(ctx.constraints or []) == 2
        assert len(ctx.drivers or []) == 2


class TestConsequencesModel:
    """Tests for the ConsequencesModel."""

    def test_empty(self) -> None:
        """Test empty consequences."""
        cons = ConsequencesModel()
        assert cons.positive is None
        assert cons.negative is None

    def test_with_values(self) -> None:
        """Test consequences with values."""
        cons = ConsequencesModel(
            positive=["Faster development"],
            negative=["Learning curve"],
        )
        assert len(cons.positive or []) == 1
        assert len(cons.negative or []) == 1


class TestReferencesModel:
    """Tests for the ReferencesModel."""

    def test_empty(self) -> None:
        """Test empty references."""
        refs = ReferencesModel()
        assert refs.links is None
        assert refs.related_adrs is None

    def test_with_links(self) -> None:
        """Test references with links."""
        refs = ReferencesModel(
            links=["https://example.com", "https://docs.example.com"],
            related_adrs=["001", "002"],
        )
        assert len(refs.links or []) == 2
        assert len(refs.related_adrs or []) == 2
