"""
test_extraction.py — Phase 1–7 end-to-end on one file.

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
from extraction import CONFIDENCE_DISCLAIMER
from generation import POC_DISCLAIMER
from pipeline import analyze_document


def print_summary_card(summary) -> None:
    print("\n--- Patient summary card ---")
    print(f"\nPatient summary:\n  {summary.patient_summary}")

    if summary.key_findings:
        print("\nKey findings:")
        for item in summary.key_findings:
            print(f"  - {item}")

    if summary.risk_flags:
        print("\nRisk flags:")
        for item in summary.risk_flags:
            print(f"  - {item}")

    print(f"\nRecommended next step:\n  {summary.recommended_next_step}")

    if summary.evidence_highlights:
        print("\nEvidence highlights:")
        for item in summary.evidence_highlights:
            print(f"  - {item!r}")

    if summary.knowledge_citations:
        print("\nKnowledge citations:")
        for item in summary.knowledge_citations:
            print(f"  - {item}")

    print(f"\nDisclaimer:\n  {summary.disclaimer}")


def print_assessment_results(assessments) -> None:
    print("\n--- Assessment flags (input to summary) ---")
    for item in assessments:
        print(f"  [{item.severity}] {item.finding} -> {item.recommended_action}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = config.DEMO_DIR / "physician_note.txt"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("=== Phase 1–7: Full pipeline through summary ===\n")
    print(f"File: {file_path.name}\n")

    try:
        result = analyze_document(file_path)
    except Exception as exc:
        print(f"Pipeline FAILED: {exc}")
        sys.exit(1)

    print("Steps 1–7: OK (ingest -> extract -> confidence -> terminology")
    print("           -> knowledge -> assessment -> summary)\n")

    print_assessment_results(result.assessments)
    print_summary_card(result.summary)

    print("\n--- Summary JSON ---")
    print(json.dumps(json.loads(result.summary.model_dump_json()), indent=2))

    print(f"\n  Note: {CONFIDENCE_DISCLAIMER}")
    print(f"  {POC_DISCLAIMER}")


if __name__ == "__main__":
    main()
