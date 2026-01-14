from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ContextModel(BaseModel):
    background: Optional[str] = None
    constraints: Optional[List[str]] = None
    drivers: Optional[List[str]] = None


class OptionModel(BaseModel):
    name: str
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    score: Optional[float] = None
    description: Optional[str] = None


class DecisionModel(BaseModel):
    chosen: str
    rationale: Optional[str] = None


class ConsequencesModel(BaseModel):
    positive: Optional[List[str]] = None
    negative: Optional[List[str]] = None


class ReferencesModel(BaseModel):
    links: Optional[List[str]] = None
    related_adrs: Optional[List[str]] = Field(default=None, description="ADR numbers or filenames")
    extra: Optional[Dict[str, Any]] = None


# HLD/LLD specific models


class RationaleItemModel(BaseModel):
    """Detailed rationale item for HLD/LLD templates."""

    name: Optional[str] = None
    description: str


class ComponentModel(BaseModel):
    """Component definition for LLD templates."""

    name: str
    responsibilities: Optional[Union[str, List[str]]] = None
    services: Optional[Union[str, List[str]]] = None
    diagram: Optional[str] = None


class OperationsModel(BaseModel):
    """Operational configuration for LLD templates."""

    regions: Optional[Union[str, List[str]]] = None
    networking: Optional[Union[str, List[str]]] = None
    scaling: Optional[Union[str, List[str]]] = None
    monitoring: Optional[Union[str, List[str]]] = None
    backup: Optional[Union[str, List[str]]] = None


class SecurityModel(BaseModel):
    """Security considerations for LLD templates."""

    threat_model: Optional[str] = None
    secrets: Optional[str] = None
    compliance: Optional[Union[str, List[str]]] = None
    review: Optional[str] = None


class RolloutModel(BaseModel):
    """Rollout and rollback plan for LLD templates."""

    strategy: Optional[str] = None
    rollback: Optional[str] = None
    feature_flags: Optional[Union[str, List[str]]] = None


class CriteriaModel(BaseModel):
    title: str
    status: str = Field(default="Proposed")
    authors: Optional[List[str]] = None
    date: Optional[str] = None  # ISO date string; if None, will be filled with today
    tags: Optional[List[str]] = None
    context: Optional[ContextModel] = None
    options: Optional[List[OptionModel]] = None
    decision: Optional[DecisionModel] = None
    consequences: Optional[ConsequencesModel] = None
    references: Optional[ReferencesModel] = None

    # HLD-specific fields
    adr_number: Optional[str] = Field(default=None, description="ADR identifier (e.g., ADR-20260106-01)")
    reviewers: Optional[List[str]] = Field(default=None, description="List of reviewers")
    stakeholders: Optional[List[str]] = Field(default=None, description="List of stakeholders (HLD)")
    assumptions: Optional[List[str]] = Field(default=None, description="Key assumptions (HLD)")
    rationale: Optional[Union[List[str], List[RationaleItemModel]]] = Field(
        default=None, description="Detailed rationale points"
    )
    alternatives: Optional[List[OptionModel]] = Field(
        default=None, description="Alternative approaches considered (HLD)"
    )
    next_steps: Optional[List[str]] = Field(default=None, description="Next steps after ADR approval")

    # LLD-specific fields
    parent_adr: Optional[str] = Field(default=None, description="Parent HLD ADR reference (LLD)")
    components: Optional[List[ComponentModel]] = Field(
        default=None, description="Component designs (LLD)"
    )
    operations: Optional[OperationsModel] = Field(
        default=None, description="Operational configuration (LLD)"
    )
    security: Optional[SecurityModel] = Field(default=None, description="Security considerations (LLD)")
    testing: Optional[List[str]] = Field(default=None, description="Testing and validation requirements (LLD)")
    rollout: Optional[RolloutModel] = Field(default=None, description="Rollout and rollback plan (LLD)")
    dependencies: Optional[List[str]] = Field(default=None, description="Dependencies (LLD)")
