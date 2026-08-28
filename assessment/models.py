"""Models for deterministic clinical assessment output."""

from pydantic import BaseModel


class AssessmentResult(BaseModel):
    """
    One workflow-oriented flag from the rules engine.

    Does NOT prescribe treatment — only suggests review/follow-up actions.
    """

    finding: str
    severity: str
    evidence: str
    knowledge_source: str
    recommended_action: str
    canonical_name: str | None = None
    confidence: float | None = None
