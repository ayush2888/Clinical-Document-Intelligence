"""
verify_setup.py — quick check that Phase 0 is working.

Run from project root:
    python scripts/verify_setup.py
"""

import sys
from pathlib import Path

# Allow imports from project root (so we can use config.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_imports() -> None:
    """Try importing each library we will use in the project."""
    print("Checking Python packages...")
    import dotenv  # noqa: F401
    import pydantic  # noqa: F401
    import fitz  # noqa: F401
    import pytesseract  # noqa: F401
    import streamlit  # noqa: F401
    print("  OK — all packages import successfully")


def check_config() -> None:
    """Load config.py and print key paths."""
    import config

    print("\nChecking config.py...")
    print(f"  Project root : {config.BASE_DIR}")
    print(f"  Demo folder  : {config.DEMO_DIR}")
    print(f"  Groq model   : {config.get_groq_model()}")
    print(f"  Groq base URL: {config.get_groq_base_url()}")
    if config.get_groq_api_key():
        print("  Groq API key : set (hidden)")
    else:
        print("  Groq API key : not set yet (fine for Phase 0)")


def check_demo_files() -> None:
    """Make sure the three demo files exist."""
    demo = PROJECT_ROOT / "data" / "demo"
    expected = ["physician_note.txt", "discharge_summary.pdf", "lab_report.png"]

    print("\nChecking demo files...")
    missing = [name for name in expected if not (demo / name).exists()]
    if missing:
        print(f"  Missing: {', '.join(missing)}")
        print("  Run: python scripts/create_demo_files.py")
        sys.exit(1)
    print("  OK — all 3 demo files present")


def main() -> None:
    print("=== Phase 0 setup check ===\n")
    check_imports()
    check_config()
    check_demo_files()
    print("\nPhase 0 looks good. Ready for Phase 1 (ingestion).")


if __name__ == "__main__":
    main()
