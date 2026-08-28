"""
create_demo_files.py — builds sample PDF and PNG for the demo folders.

Run once after installing dependencies:
    python scripts/create_demo_files.py

Creates:
  data/demo/                  — mixed single-file demos (3 patients)
  data/demo/patient_001/      — multi-document case (same patient)
"""

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"
PATIENT_DEMO_DIR = DEMO_DIR / "patient_001"

PATIENT_NAME = "Jane Doe"
PATIENT_AGE = "58"
PATIENT_SEX = "Female"


def create_discharge_pdf(output: Path, patient_line: str) -> Path:
    """Create a simple text-based PDF discharge summary."""
    doc = fitz.open()
    page = doc.new_page()

    lines = [
        "SYNTHETIC DISCHARGE SUMMARY — NOT REAL PHI",
        "",
        patient_line,
        "Admission: 2026-08-01  Discharge: 2026-08-03",
        "",
        "Primary diagnosis: Type 2 diabetes mellitus — poor glycemic control",
        "Secondary: Hypertension",
        "",
        "Hospital course:",
        "Patient admitted for hyperglycemia and medication review.",
        "Blood glucose monitored; endocrinology consulted.",
        "HbA1c on admission: 9.2%.",
        "",
        "Discharge medications:",
        "- Metformin 500 mg twice daily",
        "- Lisinopril 10 mg once daily",
        "",
        "Follow-up: Primary care in 1 week. Endocrinology in 2 weeks.",
        "",
        "Attending: Dr. B. Jones, MD (synthetic)",
    ]

    y = 50
    for line in lines:
        page.insert_text((50, y), line, fontsize=11)
        y += 18

    doc.save(output)
    doc.close()
    return output


def create_lab_png(output: Path, patient_line: str) -> Path:
    """Create a simple lab report image (for OCR testing)."""
    width, height = 700, 500
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    lines = [
        "SYNTHETIC LAB REPORT — NOT REAL PHI",
        patient_line,
        "Collection date: 2026-08-10",
        "",
        "Test                  Result    Reference",
        "------------------------------------------------",
        "HbA1c                 9.2 %     4.0 - 5.6",
        "Fasting Glucose       186 mg/dL 70 - 99",
        "Creatinine            1.1 mg/dL 0.6 - 1.2",
        "Hemoglobin            12.4 g/dL 12.0 - 15.5",
        "",
        "Note: Elevated HbA1c and glucose.",
        "Lab director: Demo Lab Inc. (synthetic)",
    ]

    y = 30
    for line in lines:
        draw.text((30, y), line, fill="black", font=font)
        y += 28

    image.save(output)
    return output


def create_physician_note(output: Path) -> Path:
    content = f"""SYNTHETIC PATIENT NOTE — NOT REAL PHI
=====================================

Patient: {PATIENT_NAME} (demo case)
Age: {PATIENT_AGE} | Sex: {PATIENT_SEX}
Date: 2026-08-15

Chief complaint: Increased thirst and fatigue for 3 weeks.

History:
- Type 2 diabetes mellitus (diagnosed 2019)
- Hypertension
- No known drug allergies

Medications:
- Metformin 500 mg twice daily
- Lisinopril 10 mg once daily

Vitals today:
- Blood pressure: 148/92 mmHg
- Heart rate: 78 bpm

Recent labs (referenced from external lab report):
- HbA1c: 9.2%
- Fasting glucose: 186 mg/dL
- Creatinine: 1.1 mg/dL (reference 0.6–1.2)

Assessment:
Poor glycemic control. Blood pressure above target.

Plan:
- Reinforce diet and exercise counseling
- Consider endocrinology referral
- Repeat HbA1c in 3 months
- Clinician to review medication adjustment

Signed: Dr. A. Smith, MD (synthetic)
"""
    output.write_text(content, encoding="utf-8")
    return output


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    PATIENT_DEMO_DIR.mkdir(parents=True, exist_ok=True)

    patient_line = f"Patient: {PATIENT_NAME} | Age: {PATIENT_AGE} | Sex: {PATIENT_SEX}"

    # Original mixed demos (different synthetic patients per file)
    mixed_pdf = create_discharge_pdf(
        DEMO_DIR / "discharge_summary.pdf",
        "Patient: John Demo | Age: 65 | Sex: Male",
    )
    mixed_png = create_lab_png(
        DEMO_DIR / "lab_report.png",
        "Patient: Maria Sample | DOB: 1968-03-12",
    )

    # Multi-document case — same patient across all three files
    note_path = create_physician_note(PATIENT_DEMO_DIR / "physician_note.txt")
    patient_pdf = create_discharge_pdf(
        PATIENT_DEMO_DIR / "discharge_summary.pdf",
        patient_line,
    )
    patient_png = create_lab_png(
        PATIENT_DEMO_DIR / "lab_report.png",
        patient_line,
    )

    print("Demo files created:")
    print(f"  Single-file demos ({DEMO_DIR.name}/):")
    print(f"    - physician_note.txt")
    print(f"    - {mixed_pdf.name}")
    print(f"    - {mixed_png.name}")
    print(f"  Multi-document case ({PATIENT_DEMO_DIR.name}/):")
    print(f"    - {note_path.name}")
    print(f"    - {patient_pdf.name}")
    print(f"    - {patient_png.name}")


if __name__ == "__main__":
    main()
