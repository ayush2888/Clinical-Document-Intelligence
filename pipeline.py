"""
pipeline.py — wire Phase 1 through Phase 9 in one call.

Single document: analyze_document()
Multi document:  analyze_patient_documents()
"""

import tempfile
from dataclasses import dataclass, field
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
from merge import merge_extractions


@dataclass
class AnalysisResult:
    """Everything produced by analyzing one document."""

    document: NormalizedDocument
    extraction: ClinicalExtraction
    knowledge: list[RetrievedKnowledge]
    assessments: list[AssessmentResult]
    summary: ClinicalSummary


@dataclass
class PatientAnalysisResult:
    """Merged view after processing multiple documents for one patient."""

    patient_id: str | None
    documents: list[NormalizedDocument]
    extractions: list[ClinicalExtraction]
    extraction: ClinicalExtraction
    knowledge: list[RetrievedKnowledge]
    assessments: list[AssessmentResult]
    summary: ClinicalSummary
    source_filenames: list[str] = field(default_factory=list)


def _tag_extraction_source(
    extraction: ClinicalExtraction,
    source_document: str,
) -> ClinicalExtraction:
    """Attach provenance to every extracted list item."""

    def tag_items(items):
        return [item.model_copy(update={"source_document": source_document}) for item in items]

    return extraction.model_copy(
        update={
            "diagnoses": tag_items(extraction.diagnoses),
            "medications": tag_items(extraction.medications),
            "allergies": tag_items(extraction.allergies),
            "symptoms": tag_items(extraction.symptoms),
            "vital_signs": tag_items(extraction.vital_signs),
            "laboratory_results": tag_items(extraction.laboratory_results),
            "procedures": tag_items(extraction.procedures),
            "important_findings": tag_items(extraction.important_findings),
        }
    )


def extract_from_document(document: NormalizedDocument) -> ClinicalExtraction:
    """Phases 2–4: structured extraction with confidence and terminology."""
    extraction = extract_clinical_data(document)
    extraction = add_confidence_scores(extraction, document)
    extraction = normalize_terminology(extraction)
    return _tag_extraction_source(extraction, document.filename)


def finalize_analysis(
    document: NormalizedDocument,
    extraction: ClinicalExtraction,
) -> AnalysisResult:
    """Phases 5–7: knowledge, assessment, and summary on one extraction."""
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


def analyze_document(file_path: str | Path) -> AnalysisResult:
    """Run the full Phase 1–7 pipeline on one file path."""
    document = ingest_document(file_path)
    extraction = extract_from_document(document)
    return finalize_analysis(document, extraction)


def analyze_patient_documents(
    file_paths: list[str | Path],
    patient_id: str | None = None,
) -> PatientAnalysisResult:
    """
    Phase 9: process each file through Phases 1–4, merge, then Phases 5–7.

    Raises PatientConflictError if extracted patient identities disagree.
    """
    if not file_paths:
        raise ValueError("At least one document path is required.")

    documents: list[NormalizedDocument] = []
    extractions: list[ClinicalExtraction] = []
    source_filenames: list[str] = []

    for file_path in file_paths:
        path = Path(file_path)
        document = ingest_document(path)
        extraction = extract_from_document(document)
        documents.append(document)
        extractions.append(extraction)
        source_filenames.append(document.filename)

    merged = merge_extractions(extractions, source_filenames)

    retriever = get_knowledge_retriever()
    knowledge = retriever.retrieve_for_extraction(merged)
    assessments = assess(merged, knowledge)
    summary = generate_summary(merged, knowledge, assessments)

    return PatientAnalysisResult(
        patient_id=patient_id,
        documents=documents,
        extractions=extractions,
        extraction=merged,
        knowledge=knowledge,
        assessments=assessments,
        summary=summary,
        source_filenames=source_filenames,
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


def analyze_uploaded_files(
    uploads: list[tuple[bytes, str]],
    patient_id: str | None = None,
) -> PatientAnalysisResult:
    """Save multiple uploads temporarily, merge, then clean up."""
    temp_paths: list[Path] = []

    try:
        for content, filename in uploads:
            suffix = Path(filename).suffix or ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                temp_paths.append(Path(tmp.name))
        return analyze_patient_documents(temp_paths, patient_id=patient_id)
    finally:
        for path in temp_paths:
            path.unlink(missing_ok=True)
