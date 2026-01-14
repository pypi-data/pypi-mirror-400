from __future__ import annotations

from typing import Any, Dict, List, Optional

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
