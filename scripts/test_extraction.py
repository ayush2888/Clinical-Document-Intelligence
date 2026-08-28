"""
test_extraction.py — Phase 1 + 2 + 3 end-to-end on one file.

Usage:
    python scripts/test_extraction.py
    python scripts/test_extraction.py data/demo/physician_note.txt
    python scripts/test_extraction.py data/demo/lab_report.png
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from extraction import (
    CONFIDENCE_DISCLAIMER,
    add_confidence_scores,
    extract_clinical_data,
    extraction_to_dict,
)
from ingestion import ingest_document


def print_lab_with_confidence(result) -> None:
    """Print lab results in the assignment example format."""
    if not result.laboratory_results:
        return

    print("\n--- Lab results with confidence ---")
    for lab in result.laboratory_results:
        unit = f" {lab.unit}" if lab.unit else ""
        print(f"\n  {lab.test_name}")
        print(f"  Value: {lab.value}{unit}")
        print(f"  Confidence: {lab.confidence}")
        print(f"  Evidence: {lab.evidence!r}")


def main() -> None:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = config.DEMO_DIR / "physician_note.txt"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("=== Phase 2 + 3: Extraction + confidence ===\n")
    print(f"File: {file_path.name}\n")

    print("Step 1: Ingesting document...")
    document = ingest_document(file_path)
    print(f"  Source type: {document.source_type}")
    print(f"  Text length: {len(document.text)} characters\n")

    print("Step 2: Groq structured extraction...")
    try:
        result = extract_clinical_data(document)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        sys.exit(1)
    print("  OK\n")

    print("Step 3: Adding confidence scores (Python rules)...")
    result = add_confidence_scores(result, document)
    print("  OK\n")

    print("--- Structured output (JSON) ---")
    print(json.dumps(extraction_to_dict(result), indent=2))

    print_lab_with_confidence(result)

    print("\n--- Quick summary ---")
    if result.patient:
        p = result.patient
        print(f"  Patient: {p.name or '—'} | Age: {p.age or '—'} | Sex: {p.sex or '—'}")
    print(f"  Diagnoses: {len(result.diagnoses)}")
    print(f"  Medications: {len(result.medications)}")
    print(f"  Lab results: {len(result.laboratory_results)}")

    low = [
        lab.test_name
        for lab in result.laboratory_results
        if lab.confidence is not None
        and lab.confidence < config.CONFIDENCE_REVIEW_THRESHOLD
    ]
    if low:
        print(f"\n  Low-confidence labs (review suggested): {', '.join(low)}")

    print(f"\n  Note: {CONFIDENCE_DISCLAIMER}")


if __name__ == "__main__":
    main()
