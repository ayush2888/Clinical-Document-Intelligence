"""
test_extraction.py — Phase 1 + Phase 2 end-to-end on one file.

Usage:
    python scripts/test_extraction.py
    python scripts/test_extraction.py data/demo/physician_note.txt
    python scripts/test_extraction.py data/demo/discharge_summary.pdf
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from extraction import extract_clinical_data, extraction_to_dict
from ingestion import ingest_document


def main() -> None:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = config.DEMO_DIR / "physician_note.txt"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("=== Phase 2: Extraction test ===\n")
    print(f"File: {file_path.name}\n")

    # Step 1 — Phase 1: file → plain text
    print("Step 1: Ingesting document...")
    document = ingest_document(file_path)
    print(f"  Extracted {len(document.text)} characters of text.\n")

    # Step 2 — Phase 2: plain text → structured JSON via Groq
    print("Step 2: Calling Groq for structured extraction...")
    try:
        result = extract_clinical_data(document)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        sys.exit(1)

    data = extraction_to_dict(result)

    print("  OK\n")
    print("--- Structured output (JSON) ---")
    print(json.dumps(data, indent=2))

    # Quick human-readable summary
    print("\n--- Quick summary ---")
    if result.patient:
        p = result.patient
        print(f"  Patient: {p.name or '—'} | Age: {p.age or '—'} | Sex: {p.sex or '—'}")
    print(f"  Diagnoses: {len(result.diagnoses)}")
    print(f"  Medications: {len(result.medications)}")
    print(f"  Lab results: {len(result.laboratory_results)}")
    print(f"  Important findings: {len(result.important_findings)}")

    if result.laboratory_results:
        lab = result.laboratory_results[0]
        print(f"\n  Sample lab: {lab.test_name} = {lab.value} {lab.unit or ''}")
        print(f"  Evidence: {lab.evidence!r}")


if __name__ == "__main__":
    main()
