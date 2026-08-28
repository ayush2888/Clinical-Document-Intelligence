"""
confidence.py — score how well each extracted field matches the source document.

Important: this is an AI EXTRACTION confidence estimate.
It is NOT clinical certainty or a medical probability.
"""

import re
from difflib import SequenceMatcher

from extraction.schemas import ClinicalExtraction
from ingestion.models import NormalizedDocument

# Shown in tests and later in the Streamlit UI
CONFIDENCE_DISCLAIMER = (
    "Confidence is an AI extraction estimate based on evidence matching "
    "the source document. It is NOT clinical certainty."
)

# Words/patterns that often mean OCR noise in our demo corpus
_GARBLED_HINTS = (" mail", "gidl", " mgid", "hate 9", "notreal", "labreport")


def _normalize(text: str) -> str:
    """Lowercase and collapse extra spaces for fair comparison."""
    return " ".join(text.lower().split())


def _looks_garbled(text: str) -> bool:
    """True when text looks like noisy OCR output."""
    lower = text.lower()
    if any(hint in lower for hint in _GARBLED_HINTS):
        return True
    # Many smashed-together words (no spaces in long chunk)
    if re.search(r"[a-z]{15,}", lower):
        return True
    return False


def _value_in_document(value: str | None, document_text: str) -> bool:
    """Check if an extracted value appears in the document."""
    if not value or not value.strip():
        return False
    return value.strip() in document_text


def score_field(
    evidence: str,
    document_text: str,
    source_type: str,
    primary_value: str | None = None,
) -> float:
    """
    Return a 0.0–1.0 confidence score for one extracted field.

    Base idea: compare the evidence quote to Phase 1 document text.
    """
    if not evidence or not evidence.strip():
        return 0.0

    evidence = evidence.strip()
    score: float

    # Rule 1 — exact evidence quote found in document
    if evidence in document_text:
        score = 0.98
    # Rule 2 — same text after normalizing case/spaces
    elif _normalize(evidence) in _normalize(document_text):
        score = 0.88
    # Rule 3 — fuzzy overlap between evidence and document
    else:
        ratio = SequenceMatcher(
            None, _normalize(evidence), _normalize(document_text)
        ).ratio()
        if ratio >= 0.45:
            score = 0.55 + (ratio * 0.25)
        elif _value_in_document(primary_value, document_text):
            score = 0.68
        else:
            score = 0.32

    # Boost slightly when the main value (e.g. "9.2") is in the document
    if primary_value and _value_in_document(primary_value, document_text):
        score = max(score, 0.70 if score < 0.75 else score)

    # Rule 4 — penalize garbled OCR text
    if _looks_garbled(evidence) or _looks_garbled(document_text):
        score -= 0.15

    # Rule 5 — image/OCR sources are less trusted overall
    if source_type == "image":
        score = min(score, 0.85)
        if _looks_garbled(evidence):
            score = min(score, 0.65)
        if primary_value and not _value_in_document(primary_value, document_text):
            score = min(score, 0.50)

    return round(max(0.0, min(1.0, score)), 2)


def add_confidence_scores(
    extraction: ClinicalExtraction,
    document: NormalizedDocument,
) -> ClinicalExtraction:
    """
    Add confidence scores to every evidence-based field.

    Returns a new ClinicalExtraction (does not mutate the original).
    """
    doc_text = document.text
    source_type = document.source_type

    def score_list(items, value_getter):
        scored = []
        for item in items:
            primary = value_getter(item)
            conf = score_field(item.evidence, doc_text, source_type, primary)
            scored.append(item.model_copy(update={"confidence": conf}))
        return scored

    return extraction.model_copy(
        update={
            "diagnoses": score_list(extraction.diagnoses, lambda x: x.name),
            "medications": score_list(extraction.medications, lambda x: x.name),
            "allergies": score_list(extraction.allergies, lambda x: x.substance),
            "symptoms": score_list(extraction.symptoms, lambda x: x.name),
            "vital_signs": score_list(extraction.vital_signs, lambda x: x.value),
            "laboratory_results": score_list(
                extraction.laboratory_results, lambda x: x.value
            ),
            "procedures": score_list(extraction.procedures, lambda x: x.name),
            "important_findings": score_list(
                extraction.important_findings, lambda x: x.finding
            ),
        }
    )


def low_confidence_items(
    extraction: ClinicalExtraction, threshold: float = 0.6
) -> list[str]:
    """Return human-readable labels for fields below the threshold."""
    flagged: list[str] = []

    def check(label: str, items) -> None:
        for item in items:
            if item.confidence is not None and item.confidence < threshold:
                flagged.append(f"{label}: {item.confidence}")

    check("diagnosis", extraction.diagnoses)
    check("medication", extraction.medications)
    check("lab", extraction.laboratory_results)
    check("vital", extraction.vital_signs)

    return flagged
