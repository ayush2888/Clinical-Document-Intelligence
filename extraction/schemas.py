"""
schemas.py — the structured JSON shape we ask Groq to fill.

Every list item includes evidence (from Groq) and confidence (from Python Phase 3).
Phase 4 adds canonical_name / display_name (from terminology normalizer).
"""

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    name: str | None = None
    age: int | None = None
    sex: str | None = None


class Diagnosis(BaseModel):
    name: str
    canonical_name: str | None = None
    display_name: str | None = None
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class Medication(BaseModel):
    name: str
    canonical_name: str | None = None
    display_name: str | None = None
    dose: str | None = None
    frequency: str | None = None
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class Allergy(BaseModel):
    substance: str
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class Symptom(BaseModel):
    name: str
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class VitalSign(BaseModel):
    name: str
    canonical_name: str | None = None
    display_name: str | None = None
    value: str
    unit: str | None = None
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class LabResult(BaseModel):
    test_name: str
    canonical_name: str | None = None
    display_name: str | None = None
    value: str
    unit: str | None = None
    reference_range_if_present: str | None = None
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class Procedure(BaseModel):
    name: str
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class ImportantFinding(BaseModel):
    finding: str
    evidence: str
    confidence: float | None = None
    source_document: str | None = None


class ClinicalExtraction(BaseModel):
    """Top-level object returned by LLM #1 and validated by Pydantic."""

    patient: PatientInfo | None = None
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    allergies: list[Allergy] = Field(default_factory=list)
    symptoms: list[Symptom] = Field(default_factory=list)
    vital_signs: list[VitalSign] = Field(default_factory=list)
    laboratory_results: list[LabResult] = Field(default_factory=list)
    procedures: list[Procedure] = Field(default_factory=list)
    important_findings: list[ImportantFinding] = Field(default_factory=list)
