"""
normalizer.py — Phase 4: add canonical_name to extracted clinical terms.

Keeps the original extracted name unchanged (audit trail).
Adds canonical_name + display_name when a known alias matches.
"""

from extraction.schemas import ClinicalExtraction
from knowledge.terminology import TerminologyResolver, get_terminology_resolver


def _apply_match(term: str, resolver: TerminologyResolver) -> dict:
    """Return fields to merge when a term resolves, else empty dict."""
    match = resolver.resolve(term)
    if match is None:
        return {}
    return {
        "canonical_name": match.canonical_name,
        "display_name": match.display_name,
    }


def normalize_terminology(
    extraction: ClinicalExtraction,
    resolver: TerminologyResolver | None = None,
) -> ClinicalExtraction:
    """
    Map known aliases to canonical clinical concepts.

    Does not change name/test_name — only adds canonical fields.
    """
    if resolver is None:
        resolver = get_terminology_resolver()

    diagnoses = [
        d.model_copy(update=_apply_match(d.name, resolver)) for d in extraction.diagnoses
    ]
    medications = [
        m.model_copy(update=_apply_match(m.name, resolver))
        for m in extraction.medications
    ]
    vital_signs = [
        v.model_copy(update=_apply_match(v.name, resolver))
        for v in extraction.vital_signs
    ]
    laboratory_results = [
        lab.model_copy(update=_apply_match(lab.test_name, resolver))
        for lab in extraction.laboratory_results
    ]

    return extraction.model_copy(
        update={
            "diagnoses": diagnoses,
            "medications": medications,
            "vital_signs": vital_signs,
            "laboratory_results": laboratory_results,
        }
    )
