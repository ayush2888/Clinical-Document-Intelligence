"""
test_extraction.py — Phase 1–5 end-to-end on one file.

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
from extraction import (
    CONFIDENCE_DISCLAIMER,
    add_confidence_scores,
    extract_clinical_data,
    extraction_to_dict,
    normalize_terminology,
)
from ingestion import ingest_document
from knowledge import get_knowledge_retriever


def print_lab_with_confidence(result) -> None:
    if not result.laboratory_results:
        return

    print("\n--- Lab results (confidence + canonical) ---")
    for lab in result.laboratory_results:
        unit = f" {lab.unit}" if lab.unit else ""
        print(f"\n  {lab.test_name} -> {lab.canonical_name or '(no match)'}")
        print(f"  Value: {lab.value}{unit} | Confidence: {lab.confidence}")


def print_terminology_summary(result) -> None:
    print("\n--- Terminology normalization ---")
    for dx in result.diagnoses:
        print(f"  Diagnosis: {dx.name!r} -> {dx.canonical_name or '(no match)'}")
    for lab in result.laboratory_results:
        print(f"  Lab: {lab.test_name!r} -> {lab.canonical_name or '(no match)'}")


def print_knowledge_context(knowledge_items) -> None:
    print("\n--- Retrieved knowledge ---")
    if not knowledge_items:
        print("  (no canonical labs/vitals to look up)")
        return

    for item in knowledge_items:
        value = ""
        if item.observed_value:
            unit = f" {item.observed_unit}" if item.observed_unit else ""
            value = f" [observed: {item.observed_value}{unit}]"
        print(f"\n  Topic: {item.topic}{value}")
        print(f"  Source: {item.source} ({item.version})")
        print(f"  Context: {item.interpretation}")
        if item.url:
            print(f"  URL: {item.url}")


def main() -> None:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = config.DEMO_DIR / "physician_note.txt"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("=== Phase 2–5: Extract through knowledge retrieval ===\n")
    print(f"File: {file_path.name}\n")

    print("Step 1: Ingesting document...")
    document = ingest_document(file_path)
    print(f"  OK ({document.source_type}, {len(document.text)} chars)\n")

    print("Step 2: Groq structured extraction...")
    try:
        result = extract_clinical_data(document)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        sys.exit(1)
    print("  OK\n")

    print("Step 3: Confidence scores...")
    result = add_confidence_scores(result, document)
    print("  OK\n")

    print("Step 4: Terminology normalization...")
    result = normalize_terminology(result)
    print("  OK\n")

    print("Step 5: Knowledge retrieval...")
    retriever = get_knowledge_retriever()
    knowledge = retriever.retrieve_for_extraction(result)
    print(f"  OK ({len(knowledge)} knowledge item(s))\n")

    print("--- Structured extraction (JSON) ---")
    print(json.dumps(extraction_to_dict(result), indent=2))

    print_terminology_summary(result)
    print_lab_with_confidence(result)
    print_knowledge_context(knowledge)

    print(f"\n  Note: {CONFIDENCE_DISCLAIMER}")
    print("  Knowledge passages are POC decision-support references only.")


if __name__ == "__main__":
    main()
