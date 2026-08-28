"""
merger.py — Phase 9 deterministic merge of per-document extractions.

Each document is processed independently through Phases 1–4 first.
This module consolidates validated fields into one patient-level view.
"""

import re

from extraction.schemas import (
    Allergy,
    ClinicalExtraction,
    Diagnosis,
    ImportantFinding,
    LabResult,
    Medication,
    PatientInfo,
    Procedure,
    Symptom,
    VitalSign,
)
from merge.exceptions import PatientConflictError


def _normalize_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().lower()
    cleaned = re.sub(r"^(patient|name)\s*:\s*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or None


def _dedupe_key(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value.strip().lower())


def _pick_better(current, candidate, score_fn):
    """Keep the item with the higher confidence score."""
    if current is None:
        return candidate
    return candidate if score_fn(candidate) > score_fn(current) else current


def _confidence(item) -> float:
    return item.confidence if item.confidence is not None else 0.0


def validate_patient_consistency(
    extractions: list[ClinicalExtraction],
    source_documents: list[str],
) -> PatientInfo | None:
    """
    Ensure all documents refer to the same patient.

    Raises PatientConflictError when extracted names clearly disagree.
    """
    names: set[str] = set()
    merged = PatientInfo()
    conflicts: list[str] = []

    for extraction, source in zip(extractions, source_documents, strict=True):
        patient = extraction.patient
        if patient is None:
            continue

        normalized = _normalize_name(patient.name)
        if normalized:
            names.add(normalized)

        if merged.name is None and patient.name:
            merged.name = patient.name
        elif (
            merged.name
            and patient.name
            and _normalize_name(merged.name) != _normalize_name(patient.name)
        ):
            conflicts.append(
                f"{source}: {patient.name!r} conflicts with {merged.name!r}"
            )

        if merged.age is None and patient.age is not None:
            merged.age = patient.age
        elif (
            merged.age is not None
            and patient.age is not None
            and merged.age != patient.age
        ):
            conflicts.append(
                f"{source}: age {patient.age} conflicts with {merged.age}"
            )

        if merged.sex is None and patient.sex:
            merged.sex = patient.sex
        elif (
            merged.sex
            and patient.sex
            and _dedupe_key(merged.sex) != _dedupe_key(patient.sex)
        ):
            conflicts.append(
                f"{source}: sex {patient.sex!r} conflicts with {merged.sex!r}"
            )

    if len(names) > 1:
        conflict_list = ", ".join(sorted(names))
        raise PatientConflictError(
            "Cannot merge documents for different patients. "
            f"Extracted names: {conflict_list}."
        )

    if conflicts:
        raise PatientConflictError(
            "Patient demographics conflict across documents: "
            + "; ".join(conflicts)
        )

    if merged.name or merged.age or merged.sex:
        return merged
    return None


def _merge_diagnoses(items: list[tuple[Diagnosis, str]]) -> list[Diagnosis]:
    merged: dict[str, Diagnosis] = {}
    for item, source in items:
        key = item.canonical_name or _dedupe_key(item.name) or item.name
        tagged = item.model_copy(update={"source_document": source})
        if key not in merged:
            merged[key] = tagged
            continue
        merged[key] = _pick_better(merged[key], tagged, _confidence)
    return list(merged.values())


def _merge_medications(items: list[tuple[Medication, str]]) -> list[Medication]:
    merged: dict[str, Medication] = {}
    for item, source in items:
        key = item.canonical_name or _dedupe_key(item.name) or item.name
        tagged = item.model_copy(update={"source_document": source})
        if key not in merged:
            merged[key] = tagged
            continue
        merged[key] = _pick_better(merged[key], tagged, _confidence)
    return list(merged.values())


def _merge_labs(items: list[tuple[LabResult, str]]) -> list[LabResult]:
    merged: dict[str, LabResult] = {}
    for item, source in items:
        key = item.canonical_name or _dedupe_key(item.test_name) or item.test_name
        tagged = item.model_copy(update={"source_document": source})
        if key not in merged:
            merged[key] = tagged
            continue
        merged[key] = _pick_better(merged[key], tagged, _confidence)
    return list(merged.values())


def _merge_vitals(items: list[tuple[VitalSign, str]]) -> list[VitalSign]:
    merged: dict[str, VitalSign] = {}
    for item, source in items:
        key = item.canonical_name or _dedupe_key(item.name) or item.name
        tagged = item.model_copy(update={"source_document": source})
        if key not in merged:
            merged[key] = tagged
            continue
        merged[key] = _pick_better(merged[key], tagged, _confidence)
    return list(merged.values())


def _merge_simple_named(items: list[tuple], name_attr: str) -> list:
    merged: dict[str, T] = {}
    for item, source in items:
        label = getattr(item, name_attr)
        key = _dedupe_key(label) or label
        tagged = item.model_copy(update={"source_document": source})
        if key not in merged:
            merged[key] = tagged
            continue
        merged[key] = _pick_better(merged[key], tagged, _confidence)
    return list(merged.values())


def merge_extractions(
    extractions: list[ClinicalExtraction],
    source_documents: list[str],
) -> ClinicalExtraction:
    """
    Merge validated extractions into one patient-level ClinicalExtraction.

    Dedupes by canonical_name (or normalized label). Keeps highest-confidence
    duplicate and records source_document provenance on every item.
    """
    if len(extractions) != len(source_documents):
        raise ValueError("extractions and source_documents must align")

    if not extractions:
        return ClinicalExtraction()

    patient = validate_patient_consistency(extractions, source_documents)

    diagnoses: list[tuple[Diagnosis, str]] = []
    medications: list[tuple[Medication, str]] = []
    allergies: list[tuple[Allergy, str]] = []
    symptoms: list[tuple[Symptom, str]] = []
    vitals: list[tuple[VitalSign, str]] = []
    labs: list[tuple[LabResult, str]] = []
    procedures: list[tuple[Procedure, str]] = []
    findings: list[tuple[ImportantFinding, str]] = []

    for extraction, source in zip(extractions, source_documents, strict=True):
        diagnoses.extend((item, source) for item in extraction.diagnoses)
        medications.extend((item, source) for item in extraction.medications)
        allergies.extend((item, source) for item in extraction.allergies)
        symptoms.extend((item, source) for item in extraction.symptoms)
        vitals.extend((item, source) for item in extraction.vital_signs)
        labs.extend((item, source) for item in extraction.laboratory_results)
        procedures.extend((item, source) for item in extraction.procedures)
        findings.extend((item, source) for item in extraction.important_findings)

    return ClinicalExtraction(
        patient=patient,
        diagnoses=_merge_diagnoses(diagnoses),
        medications=_merge_medications(medications),
        allergies=_merge_simple_named(allergies, "substance"),
        symptoms=_merge_simple_named(symptoms, "name"),
        vital_signs=_merge_vitals(vitals),
        laboratory_results=_merge_labs(labs),
        procedures=_merge_simple_named(procedures, "name"),
        important_findings=_merge_simple_named(findings, "finding"),
    )
