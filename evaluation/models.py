"""Pydantic models for Phase 10 extraction evaluation."""

from pydantic import BaseModel, Field


class ExpectedPatientField(BaseModel):
    value: str | int | None = None
    match: str = "equals"  # equals | contains | normalized_contains


class ExpectedListItem(BaseModel):
    """One entity we expect the extractor to find."""

    canonical_name: str | None = None
    name: str | None = None
    value: str | None = None
    value_contains: str | None = None
    dose_contains: str | None = None
    name_contains: str | None = None


class ExpectedExtraction(BaseModel):
    patient: dict[str, ExpectedPatientField] = Field(default_factory=dict)
    diagnoses: list[ExpectedListItem] = Field(default_factory=list)
    medications: list[ExpectedListItem] = Field(default_factory=list)
    laboratory_results: list[ExpectedListItem] = Field(default_factory=list)
    vital_signs: list[ExpectedListItem] = Field(default_factory=list)
    symptoms: list[ExpectedListItem] = Field(default_factory=list)
    allergies: list[ExpectedListItem] = Field(default_factory=list)


class EvaluationCase(BaseModel):
    id: str
    document: str
    notes: str | None = None
    expected: ExpectedExtraction


class GroundTruthFile(BaseModel):
    version: str = "1.0"
    description: str = ""
    cases: list[EvaluationCase] = Field(default_factory=list)
