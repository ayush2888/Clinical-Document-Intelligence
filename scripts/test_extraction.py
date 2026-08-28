"""
test_extraction.py — Phase 1–6 end-to-end on one file.

Usage:
    python scripts/test_extraction.py
    python scripts/test_extraction.py data/demo/physician_note.txt
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from assessment import assess
from extraction import (
    CONFIDENCE_DISCLAIMER,
    add_confidence_scores,
    extract_clinical_data,
    extraction_to_dict,
    normalize_terminology,
)
from ingestion import ingest_document
from knowledge import get_knowledge_retriever


def print_assessment_results(assessments) -> None:
    print("\n--- Assessment / workflow flags ---")
    for item in assessments:
        print(f"\n  Finding: {item.finding}")
        print(f"  Severity: {item.severity}")
        print(f"  Action: {item.recommended_action}")
        print(f"  Knowledge source: {item.knowledge_source}")
        print(f"  Evidence: {item.evidence!r}")


def print_knowledge_context(knowledge_items) -> None:
    print("\n--- Retrieved knowledge ---")
    for item in knowledge_items:
        value = ""
        if item.observed_value:
            unit = f" {item.observed_unit}" if item.observed_unit else ""
            value = f" [{item.observed_value}{unit}]"
        print(f"  {item.topic}{value}: {item.source}")


def main() -> None:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = config.DEMO_DIR / "physician_note.txt"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("=== Phase 2–6: Full pipeline through assessment ===\n")
    print(f"File: {file_path.name}\n")

    document = ingest_document(file_path)
    print(f"Step 1: Ingested ({document.source_type})\n")

    try:
        result = extract_clinical_data(document)
    except Exception as exc:
        print(f"Step 2 FAILED: {exc}")
        sys.exit(1)
    print("Step 2: Extraction OK\n")

    result = add_confidence_scores(result, document)
    print("Step 3: Confidence OK\n")

    result = normalize_terminology(result)
    print("Step 4: Terminology OK\n")

    retriever = get_knowledge_retriever()
    knowledge = retriever.retrieve_for_extraction(result)
    print(f"Step 5: Knowledge OK ({len(knowledge)} items)\n")

    assessments = assess(result, knowledge)
    print(f"Step 6: Assessment OK ({len(assessments)} flag(s))\n")

    print("--- Extraction JSON (abbreviated summary) ---")
    summary = extraction_to_dict(result)
    print(json.dumps(summary, indent=2))

    print_knowledge_context(knowledge)
    print_assessment_results(assessments)

    print(f"\n  Note: {CONFIDENCE_DISCLAIMER}")
    print("  Assessment outputs are workflow suggestions for human review — not medical advice.")


if __name__ == "__main__":
    main()
