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

# --- Paths (easy to reuse in other files) ---
DEMO_DIR = BASE_DIR / "data" / "demo"
EVAL_DIR = BASE_DIR / "data" / "evaluation"

# --- Groq LLM (used starting Phase 2; safe to leave empty in Phase 0) ---
# Groq uses an OpenAI-compatible API, so Phase 2 will use the `openai` Python
# package with GROQ_BASE_URL — no OpenAI account needed.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# --- Tesseract (Windows often needs the full path) ---
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

# --- Confidence (Phase 3) ---
# Fields below this score may need human review (used in Phase 6+)
CONFIDENCE_REVIEW_THRESHOLD = float(os.getenv("CONFIDENCE_REVIEW_THRESHOLD", "0.6"))
