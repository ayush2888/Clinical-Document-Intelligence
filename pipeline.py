"""
pipeline.py — wire Phase 1 through Phase 7 in one call.

Used by the test script now and by Streamlit in Phase 8.
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path

from assessment import assess
from assessment.models import AssessmentResult
from extraction import (
    add_confidence_scores,
    extract_clinical_data,
    normalize_terminology,
)
from extraction.schemas import ClinicalExtraction
from generation import generate_summary
from generation.schemas import ClinicalSummary
from ingestion import ingest_document
from ingestion.models import NormalizedDocument
from knowledge import get_knowledge_retriever
from knowledge.models import RetrievedKnowledge


@dataclass
class AnalysisResult:
    """Everything produced by analyzing one document."""

    document: NormalizedDocument
    extraction: ClinicalExtraction
    knowledge: list[RetrievedKnowledge]
    assessments: list[AssessmentResult]
    summary: ClinicalSummary


def analyze_document(file_path: str | Path) -> AnalysisResult:
    """Run the full Phase 1–7 pipeline on one file path."""
    document = ingest_document(file_path)

    extraction = extract_clinical_data(document)
    extraction = add_confidence_scores(extraction, document)
    extraction = normalize_terminology(extraction)

    retriever = get_knowledge_retriever()
    knowledge = retriever.retrieve_for_extraction(extraction)
    assessments = assess(extraction, knowledge)
    summary = generate_summary(extraction, knowledge, assessments)

    return AnalysisResult(
        document=document,
        extraction=extraction,
        knowledge=knowledge,
        assessments=assessments,
        summary=summary,
    )


def analyze_uploaded_file(content: bytes, filename: str) -> AnalysisResult:
    """Save an uploaded file temporarily, run the pipeline, then clean up."""
    suffix = Path(filename).suffix or ".txt"
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)
        return analyze_document(temp_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
