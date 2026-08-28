"""
test_ingestion.py — run all 3 demo files through the ingestion pipeline.

Usage (from project root, with venv active):
    python scripts/test_ingestion.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from ingestion import ingest_document


def preview(text: str, max_chars: int = 250) -> str:
    """Show the start of extracted text without flooding the terminal."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def main() -> None:
    demo_files = [
        "physician_note.txt",
        "discharge_summary.pdf",
        "lab_report.png",
    ]

    print("=== Phase 1: Ingestion test ===\n")

    for name in demo_files:
        file_path = config.DEMO_DIR / name
        print(f"--- {name} ---")

        try:
            doc = ingest_document(file_path)
            print(f"  source_type : {doc.source_type}")
            print(f"  page_count  : {doc.page_count}")
            print(f"  text length : {len(doc.text)} characters")
            print(f"  preview     : {preview(doc.text)!r}")
            print("  status      : OK\n")
        except Exception as exc:
            print(f"  status      : FAILED — {exc}\n")
            sys.exit(1)

    print("All demo files ingested successfully.")


if __name__ == "__main__":
    main()
