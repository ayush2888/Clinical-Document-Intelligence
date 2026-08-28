"""
schemas.py — the structured JSON shape we ask Groq to fill.

Every list item (diagnosis, lab, medication, etc.) includes an
evidence field: a short quote copied from the source document.
"""

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    name: str | None = None
    age: int | None = None
    sex: str | None = None


class Diagnosis(BaseModel):
    name: str
    evidence: str


class Medication(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None
    evidence: str


class Allergy(BaseModel):
    substance: str
    evidence: str


class Symptom(BaseModel):
    name: str
    evidence: str


class VitalSign(BaseModel):
    name: str
    value: str
    unit: str | None = None
    evidence: str


class LabResult(BaseModel):
    test_name: str
    value: str
    unit: str | None = None
    reference_range_if_present: str | None = None
    evidence: str


class Procedure(BaseModel):
    name: str
    evidence: str


class ImportantFinding(BaseModel):
    finding: str
    evidence: str


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
