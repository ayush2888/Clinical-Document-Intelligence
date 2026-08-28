"""
evaluate_extraction.py — Phase 10: compare LLM extraction vs ground truth.

Runs live extraction (Groq required) and reports honest field-level metrics.
Does NOT fabricate performance numbers.

Usage:
    python scripts/evaluate_extraction.py
    python scripts/evaluate_extraction.py data/evaluation/ground_truth.json
    python scripts/evaluate_extraction.py --report-json data/evaluation/last_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from evaluation import GroundTruthFile, evaluate_case, merge_reports
from ingestion import ingest_document
from pipeline import extract_from_document


DEFAULT_GROUND_TRUTH = config.EVAL_DIR / "ground_truth.json"


def load_ground_truth(path: Path) -> GroundTruthFile:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return GroundTruthFile.model_validate(raw)


def resolve_document_path(case_document: str, ground_truth_path: Path) -> Path:
    doc_path = Path(case_document)
    if doc_path.is_absolute():
        return doc_path
    return (ground_truth_path.parent / doc_path).resolve()


def print_report(report, verbose: bool = False) -> None:
    print("\n=== Extraction evaluation summary ===")
    print(f"Documents evaluated: {report.documents_evaluated}")
    print(f"Fields evaluated:    {report.fields_evaluated}")
    print(f"Correct:             {report.correct}")
    print(f"Incorrect:           {report.incorrect}")
    print(f"Missing:             {report.missing}")

    if report.fields_evaluated:
        accuracy = report.correct / report.fields_evaluated * 100
        print(f"Field accuracy:      {accuracy:.1f}%")

    if verbose:
        print("\n--- Field details ---")
        for item in report.details:
            marker = {"correct": "OK", "incorrect": "WRONG", "missing": "MISSING"}[item.status]
            print(f"  [{marker}] {item.case_id} :: {item.field_path}")
            print(f"         expected: {item.expected}")
            print(f"         actual:   {item.actual}")
    else:
        failures = [d for d in report.details if d.status != "correct"]
        if failures:
            print("\n--- Non-matching fields ---")
            for item in failures:
                print(
                    f"  [{item.status.upper()}] {item.field_path} "
                    f"(expected: {item.expected!r}, actual: {item.actual!r})"
                )
        else:
            print("\nAll evaluated fields matched ground truth.")


def save_report_json(report, output_path: Path) -> None:
    payload = {
        "documents_evaluated": report.documents_evaluated,
        "fields_evaluated": report.fields_evaluated,
        "correct": report.correct,
        "incorrect": report.incorrect,
        "missing": report.missing,
        "details": [asdict(item) for item in report.details],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {output_path}")


def run_evaluation(
    ground_truth_path: Path,
    verbose: bool = False,
) -> tuple:
    gt = load_ground_truth(ground_truth_path)
    reports = []

    print("=== Phase 10: Extraction evaluation ===\n")
    print(f"Ground truth: {ground_truth_path}")
    print(f"Cases: {len(gt.cases)}\n")

    for case in gt.cases:
        doc_path = resolve_document_path(case.document, ground_truth_path)
        if not doc_path.exists():
            print(f"SKIP {case.id}: document not found at {doc_path}")
            continue

        print(f"Evaluating {case.id}")
        print(f"  Document: {doc_path.name}")
        if case.notes:
            print(f"  Notes: {case.notes}")

        document = ingest_document(doc_path)
        extraction = extract_from_document(document)
        case_report = evaluate_case(case, extraction)
        reports.append(case_report)

        if verbose:
            print(f"  -> {case_report.correct}/{case_report.fields_evaluated} fields correct")

    if not reports:
        print("\nNo cases evaluated.")
        sys.exit(1)

    combined = merge_reports(reports)
    return combined, gt


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate LLM extraction against ground truth.")
    parser.add_argument(
        "ground_truth",
        nargs="?",
        default=str(DEFAULT_GROUND_TRUTH),
        help="Path to ground_truth.json",
    )
    parser.add_argument(
        "--report-json",
        metavar="PATH",
        help="Optional path to save JSON metrics report",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print every evaluated field",
    )
    args = parser.parse_args()

    ground_truth_path = Path(args.ground_truth)
    if not ground_truth_path.exists():
        print(f"Ground truth file not found: {ground_truth_path}")
        sys.exit(1)

    try:
        report, gt = run_evaluation(ground_truth_path, verbose=args.verbose)
    except Exception as exc:
        print(f"Evaluation FAILED: {exc}")
        sys.exit(1)

    print_report(report, verbose=args.verbose)

    if args.report_json:
        save_report_json(report, Path(args.report_json))

    print(f"\n{gt.description}")


if __name__ == "__main__":
    main()
