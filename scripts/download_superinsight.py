"""
download_superinsight.py — fetch Superinsight Medical Chronology Benchmark cases.

Downloads synthetic source documents and golden.json reference files from
Hugging Face into data/evaluation/external/.

Source dataset (Apache 2.0):
  https://huggingface.co/datasets/Superinsight/medical-chronology-benchmark

Usage:
    python scripts/download_superinsight.py
    python scripts/download_superinsight.py --cases golden_a golden_b
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = PROJECT_ROOT / "data" / "evaluation" / "external"

HF_BASE = (
    "https://huggingface.co/datasets/Superinsight/"
    "medical-chronology-benchmark/resolve/main/golden"
)

CASE_OUTPUT_NAMES = {
    "golden_a": ("golden_a_dde.txt", "golden_a_golden.json"),
    "golden_b": ("golden_b_clinical_note.txt", "golden_b_golden.json"),
}


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  -> {dest.name}")
    urllib.request.urlretrieve(url, dest)


def download_case(case_id: str) -> None:
    if case_id not in CASE_OUTPUT_NAMES:
        raise ValueError(f"Unknown case: {case_id}. Choose from {list(CASE_OUTPUT_NAMES)}")

    txt_name, json_name = CASE_OUTPUT_NAMES[case_id]
    case_url = f"{HF_BASE}/{case_id}"

    download_file(f"{case_url}/synthetic_source.txt", EXTERNAL_DIR / txt_name)
    download_file(f"{case_url}/golden.json", EXTERNAL_DIR / json_name)


def create_eval_excerpts() -> None:
    """
    Build smaller eval files that fit Groq token limits.

    Full Superinsight documents are kept for reference; evaluation uses excerpts
    that still contain every field listed in ground_truth.json.
    """
    a_full = (EXTERNAL_DIR / "golden_a_dde.txt").read_text(encoding="utf-8")
    a_excerpt = a_full[:4200].rstrip()
    a_excerpt += "\n\n[... truncated for POC evaluation — see golden_a_dde.txt ...]\n"
    (EXTERNAL_DIR / "golden_a_eval.txt").write_text(a_excerpt, encoding="utf-8")
    print(f"  -> golden_a_eval.txt ({len(a_excerpt)} chars)")

    b_full = (EXTERNAL_DIR / "golden_b_clinical_note.txt").read_text(encoding="utf-8")
    end = b_full.find("**CONSENT FOR TREATMENT**")
    b_excerpt = b_full[:end].rstrip() + "\n\n"
    progress_marker = "The patient, a 39-year-old female"
    progress_idx = b_full.find(progress_marker)
    if progress_idx >= 0:
        b_excerpt += b_full[progress_idx : progress_idx + 120].rstrip() + "\n"
    (EXTERNAL_DIR / "golden_b_eval.txt").write_text(b_excerpt, encoding="utf-8")
    print(f"  -> golden_b_eval.txt ({len(b_excerpt)} chars)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Superinsight benchmark files.")
    parser.add_argument(
        "--cases",
        nargs="+",
        default=["golden_a", "golden_b"],
        help="Which golden cases to download (default: golden_a golden_b)",
    )
    args = parser.parse_args()

    print("=== Superinsight benchmark download ===\n")
    print(f"Destination: {EXTERNAL_DIR}\n")

    for case_id in args.cases:
        print(f"Downloading {case_id}...")
        try:
            download_case(case_id)
        except Exception as exc:
            print(f"FAILED {case_id}: {exc}", file=sys.stderr)
            sys.exit(1)

    print("\nCreating evaluation excerpts...")
    create_eval_excerpts()

    print("\nDone. Ground-truth mappings live in data/evaluation/ground_truth.json")
    print("Run evaluation: python scripts/evaluate_extraction.py -v")


if __name__ == "__main__":
    main()
