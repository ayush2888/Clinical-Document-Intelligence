# Clinical Document Intelligence Hub

**Proof-of-concept** that ingests unstructured clinical documents (text, PDF, image) and surfaces structured, decision-ready intelligence — patient summaries, workflow flags, evidence-backed extractions, and JSON export.

> **Not a clinical diagnostic system.** All outputs are decision-support for human review.

---

## Quick start

```powershell
cd clinical-document-hub
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Add your Groq API key to .env
python scripts\create_demo_files.py
streamlit run app.py
```

Open `http://localhost:8501` and upload `data/demo/physician_note.txt`.

---

## What it does

| Step | Module | Description |
|------|--------|-------------|
| 1 | `ingestion/` | Parse TXT, PDF (PyMuPDF), images (Tesseract OCR) |
| 2 | `extraction/` | Groq LLM → structured JSON (Pydantic schema) |
| 3 | `extraction/confidence.py` | Confidence scores per field |
| 4 | `extraction/normalizer.py` | Canonical terminology mapping |
| 5 | `knowledge/` | Rule-based clinical knowledge retrieval |
| 6 | `assessment/` | Deterministic workflow flags (HbA1c, BP, etc.) |
| 7 | `generation/` | Patient summary, risk flags, next step |
| 9 | `merge/` | Multi-document merge with patient conflict guard |
| 10 | `evaluation/` | Live extraction metrics vs ground truth |

---

## Demo files

| Path | Use |
|------|-----|
| `data/demo/physician_note.txt` | Best single-file demo (clean text) |
| `data/demo/discharge_summary.pdf` | PDF ingestion |
| `data/demo/lab_report.png` | OCR ingestion |
| `data/demo/patient_001/` | Multi-document case (same patient, 3 files) |

**Multi-document demo:** Sidebar → Multi-document → Patient ID `patient_001` → upload all 3 files from `patient_001/`.

---

## Example input → output

**Input** (`data/demo/physician_note.txt` excerpt):

```
Patient: Jane Doe | Age: 58 | Sex: Female
Chief complaint: Increased thirst and fatigue for 3 weeks.
Medications: Metformin 500 mg, Lisinopril 10 mg
Vitals: BP 148/92 mmHg, HR 78 bpm
Labs: HbA1c 9.2%, Fasting glucose 186 mg/dL
```

**Output** (structured extraction + summary):

- **Patient:** Jane Doe, 58, Female
- **Diagnoses:** Type 2 diabetes mellitus, Hypertension
- **Workflow flags:** Elevated HbA1c, elevated blood pressure (rule-based)
- **Summary:** Poor glycemic control; reinforce diet/exercise; consider endocrinology referral
- **Export:** Download JSON button in dashboard

---

## AI models and tools

| Tool | Role |
|------|------|
| **Groq API** (`openai/gpt-oss-20b`) | Structured clinical extraction + summary generation |
| **PyMuPDF** | PDF text extraction |
| **Tesseract** | OCR for lab report images |
| **Streamlit** | Web dashboard |
| **Pydantic** | Schema validation for all extracted data |

**Benchmark:** Evaluated against [Superinsight Medical Chronology Benchmark](https://huggingface.co/datasets/Superinsight/medical-chronology-benchmark) (synthetic, Apache 2.0). Metrics from live API calls — see `scripts/evaluate_extraction.py`.

---

## Evaluation

```powershell
.venv\Scripts\python scripts\evaluate_extraction.py -v
.venv\Scripts\python scripts\download_superinsight.py
```

Ground truth: `data/evaluation/ground_truth.json` (3 cases: internal + 2 Superinsight excerpts).

---

## Assumptions and limitations

- **Synthetic data only** — no real PHI in demo or evaluation sets
- **POC scope** — not validated for clinical deployment
- **OCR quality** depends on image clarity; noisy scans may reduce accuracy
- **Long documents** may hit Groq token limits; evaluation uses excerpts for external benchmark
- **LLM extraction** can be intermittent; evaluation script retries on JSON validation errors

---

## Project structure

```
clinical-document-hub/
├── app.py                 # Streamlit entry point
├── pipeline.py            # End-to-end orchestration
├── ingestion/             # Document parsing
├── extraction/            # LLM extraction + normalization
├── knowledge/             # Clinical knowledge base
├── assessment/            # Rule-based flags
├── generation/            # Summary generation
├── merge/                 # Multi-document patient merge
├── evaluation/            # Ground-truth comparison
├── ui/                    # Dashboard components
├── data/demo/             # Synthetic demo files
├── data/evaluation/       # Ground truth + Superinsight benchmark
└── scripts/               # Demo creation, evaluation, download
```

---

## Author

Built as a 3-day healthcare AI proof-of-concept assignment.

**Repository:** https://github.com/ayush2888/Clinical-Document-Intelligence
