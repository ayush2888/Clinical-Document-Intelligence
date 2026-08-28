"""
assessor.py — Phase 6 deterministic rules engine.

Inputs:  validated extraction + retrieved knowledge
Outputs: workflow flags (review, follow-up) — never prescriptions
"""

import re

import config
from assessment.models import AssessmentResult
from extraction.schemas import ClinicalExtraction, LabResult, VitalSign
from knowledge.models import RetrievedKnowledge
from knowledge.retriever import UNAVAILABLE_MESSAGE

ACTION_PRIORITIZE = "prioritize_clinician_review"
ACTION_REVIEW = "requires_additional_review"
ACTION_FOLLOWUP = "routine_follow_up"
ACTION_NONE = "no_immediate_flag_detected"


def _parse_number(value: str) -> float | None:
    """Pull the first number from a string like '9.2' or '186 mg/dL'."""
    match = re.search(r"(\d+\.?\d*)", value.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _parse_blood_pressure(value: str) -> tuple[float | None, float | None]:
    """Parse '148/92' into systolic and diastolic."""
    match = re.search(r"(\d+\.?\d*)\s*/\s*(\d+\.?\d*)", value)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def _parse_reference_range(ref: str | None) -> tuple[float | None, float | None]:
    """Parse '0.6-1.2' or '0.6–1.2' into low and high."""
    if not ref:
        return None, None
    match = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", ref)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def _knowledge_lookup(
    knowledge: list[RetrievedKnowledge],
) -> dict[str, RetrievedKnowledge]:
    return {item.canonical_name: item for item in knowledge}


def _source_label(item: RetrievedKnowledge | None) -> str:
    if item is None:
        return "No knowledge source"
    if UNAVAILABLE_MESSAGE in item.interpretation:
        return "Configured knowledge sources (unavailable for topic)"
    return f"{item.source} ({item.version})"


def _add_result(
    results: list[AssessmentResult],
    *,
    finding: str,
    severity: str,
    evidence: str,
    knowledge_source: str,
    recommended_action: str,
    canonical_name: str | None = None,
    confidence: float | None = None,
) -> None:
    results.append(
        AssessmentResult(
            finding=finding,
            severity=severity,
            evidence=evidence,
            knowledge_source=knowledge_source,
            recommended_action=recommended_action,
            canonical_name=canonical_name,
            confidence=confidence,
        )
    )


def _check_low_confidence(
    results: list[AssessmentResult],
    label: str,
    evidence: str,
    confidence: float | None,
    canonical_name: str | None,
) -> None:
    if confidence is not None and confidence < config.CONFIDENCE_REVIEW_THRESHOLD:
        _add_result(
            results,
            finding=f"Low extraction confidence for {label}",
            severity="medium",
            evidence=evidence,
            knowledge_source="Extraction confidence rules",
            recommended_action=ACTION_REVIEW,
            canonical_name=canonical_name,
            confidence=confidence,
        )


def _assess_lab(
    lab: LabResult,
    know: RetrievedKnowledge | None,
    results: list[AssessmentResult],
) -> None:
    canonical = lab.canonical_name
    numeric = _parse_number(lab.value)
    source = _source_label(know)

    _check_low_confidence(
        results, lab.test_name, lab.evidence, lab.confidence, canonical
    )

    if numeric is None or not canonical:
        return

    if canonical == "hba1c" and numeric >= config.HBA1C_REVIEW_THRESHOLD:
        _add_result(
            results,
            finding=f"HbA1c elevated at {lab.value}{lab.unit or ''}".strip(),
            severity="high",
            evidence=lab.evidence,
            knowledge_source=source,
            recommended_action=ACTION_REVIEW,
            canonical_name=canonical,
            confidence=lab.confidence,
        )

    if canonical == "fasting_glucose" and numeric >= config.GLUCOSE_REVIEW_THRESHOLD:
        _add_result(
            results,
            finding=f"Fasting glucose elevated at {lab.value}{lab.unit or ''}".strip(),
            severity="high",
            evidence=lab.evidence,
            knowledge_source=source,
            recommended_action=ACTION_REVIEW,
            canonical_name=canonical,
            confidence=lab.confidence,
        )

    if canonical == "creatinine":
        low, high = _parse_reference_range(lab.reference_range_if_present)
        if high is not None and numeric > high:
            _add_result(
                results,
                finding=f"Creatinine above reference at {lab.value}{lab.unit or ''}".strip(),
                severity="medium",
                evidence=lab.evidence,
                knowledge_source=source,
                recommended_action=ACTION_FOLLOWUP,
                canonical_name=canonical,
                confidence=lab.confidence,
            )

    if canonical == "hemoglobin":
        low, high = _parse_reference_range(lab.reference_range_if_present)
        if low is not None and numeric < low:
            _add_result(
                results,
                finding=f"Hemoglobin below reference at {lab.value}{lab.unit or ''}".strip(),
                severity="medium",
                evidence=lab.evidence,
                knowledge_source=source,
                recommended_action=ACTION_FOLLOWUP,
                canonical_name=canonical,
                confidence=lab.confidence,
            )


def _assess_vital(
    vital: VitalSign,
    know: RetrievedKnowledge | None,
    results: list[AssessmentResult],
) -> None:
    canonical = vital.canonical_name
    source = _source_label(know)

    _check_low_confidence(
        results, vital.name, vital.evidence, vital.confidence, canonical
    )

    if canonical != "blood_pressure":
        return

    systolic, diastolic = _parse_blood_pressure(vital.value)
    if systolic is None or diastolic is None:
        return

    if (
        systolic >= config.BP_URGENT_SYSTOLIC
        or diastolic >= config.BP_URGENT_DIASTOLIC
    ):
        _add_result(
            results,
            finding=f"Blood pressure critically elevated at {vital.value} {vital.unit or ''}".strip(),
            severity="critical",
            evidence=vital.evidence,
            knowledge_source=source,
            recommended_action=ACTION_PRIORITIZE,
            canonical_name=canonical,
            confidence=vital.confidence,
        )
    elif (
        systolic >= config.BP_ELEVATED_SYSTOLIC
        or diastolic >= config.BP_ELEVATED_DIASTOLIC
    ):
        _add_result(
            results,
            finding=f"Blood pressure above target at {vital.value} {vital.unit or ''}".strip(),
            severity="medium",
            evidence=vital.evidence,
            knowledge_source=source,
            recommended_action=ACTION_REVIEW,
            canonical_name=canonical,
            confidence=vital.confidence,
        )


def assess(
    extraction: ClinicalExtraction,
    knowledge: list[RetrievedKnowledge],
) -> list[AssessmentResult]:
    """
    Run transparent threshold rules on extracted labs and vitals.

    Returns workflow flags for clinician/administrative review.
    """
    results: list[AssessmentResult] = []
    know_map = _knowledge_lookup(knowledge)

    for lab in extraction.laboratory_results:
        know = know_map.get(lab.canonical_name) if lab.canonical_name else None
        _assess_lab(lab, know, results)

    for vital in extraction.vital_signs:
        know = know_map.get(vital.canonical_name) if vital.canonical_name else None
        _assess_vital(vital, know, results)

    if not results:
        _add_result(
            results,
            finding="No immediate clinical workflow flags detected",
            severity="low",
            evidence="No configured thresholds were exceeded.",
            knowledge_source="Assessment rules (config.py)",
            recommended_action=ACTION_NONE,
        )

    return results
