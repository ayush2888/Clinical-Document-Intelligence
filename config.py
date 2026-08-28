"""
config.py — reads settings from the .env file.

Think of this like a reception desk checklist:
- Where is the project folder?  → BASE_DIR
- Where are demo files?         → DEMO_DIR
- API key for Groq (later)      → GROQ_API_KEY
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# Folder that contains this config.py file (= project root)
BASE_DIR = Path(__file__).resolve().parent

# Load variables from .env (if the file exists)
load_dotenv(BASE_DIR / ".env")


def _setting(name: str, default: str = "") -> str:
    """Read from Streamlit secrets (cloud) or environment (.env local)."""
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


# --- Paths (easy to reuse in other files) ---
DEMO_DIR = BASE_DIR / "data" / "demo"
PATIENT_DEMO_DIR = DEMO_DIR / "patient_001"
EVAL_DIR = BASE_DIR / "data" / "evaluation"
SUPERINSIGHT_DIR = EVAL_DIR / "external"

# --- Groq LLM (used starting Phase 2; safe to leave empty in Phase 0) ---
# Groq uses an OpenAI-compatible API, so Phase 2 will use the `openai` Python
# package with GROQ_BASE_URL — no OpenAI account needed.
GROQ_API_KEY = _setting("GROQ_API_KEY", "")
GROQ_BASE_URL = _setting("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = _setting("GROQ_MODEL", "openai/gpt-oss-20b")

# --- Tesseract (Windows often needs the full path) ---
TESSERACT_CMD = _setting("TESSERACT_CMD", "")

# --- Confidence (Phase 3) ---
# Fields below this score may need human review (used in Phase 6+)
CONFIDENCE_REVIEW_THRESHOLD = float(os.getenv("CONFIDENCE_REVIEW_THRESHOLD", "0.6"))

# --- Assessment thresholds (Phase 6) — transparent rules in assessor.py ---
HBA1C_REVIEW_THRESHOLD = float(os.getenv("HBA1C_REVIEW_THRESHOLD", "9.0"))
GLUCOSE_REVIEW_THRESHOLD = float(os.getenv("GLUCOSE_REVIEW_THRESHOLD", "126"))
BP_URGENT_SYSTOLIC = float(os.getenv("BP_URGENT_SYSTOLIC", "180"))
BP_URGENT_DIASTOLIC = float(os.getenv("BP_URGENT_DIASTOLIC", "120"))
BP_ELEVATED_SYSTOLIC = float(os.getenv("BP_ELEVATED_SYSTOLIC", "140"))
BP_ELEVATED_DIASTOLIC = float(os.getenv("BP_ELEVATED_DIASTOLIC", "90"))
