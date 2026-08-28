"""Output schema for LLM #2 — human-readable summary card."""

from pydantic import BaseModel, Field

from generation.disclaimer import POC_DISCLAIMER


class ClinicalSummary(BaseModel):
    """Summary card shown to clinical/administrative users."""

    patient_summary: str
    key_findings: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommended_next_step: str
    disclaimer: str = POC_DISCLAIMER
    evidence_highlights: list[str] = Field(default_factory=list)
    knowledge_citations: list[str] = Field(default_factory=list)
