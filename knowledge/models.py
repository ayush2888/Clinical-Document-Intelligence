"""Pydantic models for the local clinical knowledge layer."""

from pydantic import BaseModel


class KnowledgeDocument(BaseModel):
    """One versioned guidance document stored as JSON in knowledge/sources/."""

    topic: str
    canonical_name: str
    source: str
    version: str
    interpretation: str
    url: str | None = None


class RetrievedKnowledge(BaseModel):
    """Knowledge passage retrieved for one extracted observation."""

    topic: str
    canonical_name: str
    source: str
    version: str
    interpretation: str
    url: str | None = None
    observed_value: str | None = None
    observed_unit: str | None = None
