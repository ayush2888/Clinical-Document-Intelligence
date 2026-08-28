# Extraction: LLM + Pydantic schemas (Phase 2+)

from extraction.confidence import (
    CONFIDENCE_DISCLAIMER,
    add_confidence_scores,
    score_field,
)
from extraction.llm_extractor import extract_clinical_data, extraction_to_dict
from extraction.normalizer import normalize_terminology
from extraction.schemas import ClinicalExtraction

__all__ = [
    "ClinicalExtraction",
    "CONFIDENCE_DISCLAIMER",
    "add_confidence_scores",
    "extract_clinical_data",
    "extraction_to_dict",
    "normalize_terminology",
    "score_field",
]
