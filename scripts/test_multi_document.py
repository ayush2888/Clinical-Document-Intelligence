"""
test_multi_document.py — Phase 9 end-to-end on patient_001 demo folder.

Usage:
    python scripts/create_demo_files.py
    python scripts/test_multi_document.py
    python scripts/test_multi_document.py data/demo/patient_001
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from generation import POC_DISCLAIMER
from merge import PatientConflictError
from pipeline import analyze_patient_documents


SUPPORTED_SUFFIXES = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}


def collect_documents(folder: Path) -> list[Path]:
    files = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        raise FileNotFoundError(f"No supported documents found in {folder}")
    return files


def print_merge_overview(result) -> None:
    print("\n--- Source documents ---")
    for name in result.source_filenames:
        print(f"  - {name}")

    print("\n--- Merged extraction counts ---")
    extraction = result.extraction
    print(f"  Diagnoses: {len(extraction.diagnoses)}")
    print(f"  Medications: {len(extraction.medications)}")
    print(f"  Labs: {len(extraction.laboratory_results)}")
    print(f"  Vitals: {len(extraction.vital_signs)}")

    print("\n--- Lab provenance ---")
    for lab in extraction.laboratory_results:
        source = lab.source_document or "unknown"
        print(f"  {lab.test_name}: {lab.value} (from {source}, conf={lab.confidence})")

    print("\n--- Assessment flags ---")
    for item in result.assessments:
        print(f"  [{item.severity}] {item.finding} -> {item.recommended_action}")

    print("\n--- Patient summary ---")
    print(f"  {result.summary.patient_summary}")
    print(f"\n  Next step: {result.summary.recommended_next_step}")
    print(f"\n  {POC_DISCLAIMER}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:
        folder = config.PATIENT_DEMO_DIR

    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        print("Run: python scripts/create_demo_files.py")
        sys.exit(1)

    files = collect_documents(folder)
    patient_id = folder.name if folder.name.startswith("patient_") else None

    print("=== Phase 9: Multi-document patient merge ===\n")
    print(f"Folder: {folder}")
    print(f"Patient ID: {patient_id or '(not set)'}")
    print(f"Files: {len(files)}\n")

    try:
        result = analyze_patient_documents(files, patient_id=patient_id)
    except PatientConflictError as exc:
        print(f"Merge blocked — patient conflict: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"Pipeline FAILED: {exc}")
        sys.exit(1)

    print("Steps: OK (per-doc ingest/extract -> merge -> knowledge -> assessment -> summary)")
    print_merge_overview(result)

    print("\n--- Merged extraction JSON (sample) ---")
    print(json.dumps(json.loads(result.extraction.model_dump_json()), indent=2)[:2000])
    print("  ... (truncated)")


if __name__ == "__main__":
    main()
