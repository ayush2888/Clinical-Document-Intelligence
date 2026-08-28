"""
create_demo_files.py — builds sample PDF and PNG for the demo folder.

Run once after installing dependencies:
    python scripts/create_demo_files.py

Why a script?
- Easier than checking large binary files into git
- You can re-run anytime to recreate the samples
"""

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

# Go up one level from scripts/ to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"


def create_discharge_pdf() -> Path:
    """Create a simple text-based PDF discharge summary."""
    output = DEMO_DIR / "discharge_summary.pdf"

    doc = fitz.open()
    page = doc.new_page()

    lines = [
        "SYNTHETIC DISCHARGE SUMMARY — NOT REAL PHI",
        "",
        "Patient: John Demo | Age: 65 | Sex: Male",
        "Admission: 2026-08-01  Discharge: 2026-08-05",
        "",
        "Primary diagnosis: Acute exacerbation of COPD",
        "Secondary: Type 2 diabetes mellitus",
        "",
        "Hospital course:",
        "Patient admitted with shortness of breath and wheezing.",
        "Treated with bronchodilators and short course of prednisone.",
        "Glucose monitored; HbA1c on admission: 8.4%.",
        "",
        "Discharge medications:",
        "- Albuterol inhaler 2 puffs every 4-6 hours PRN",
        "- Tiotropium 18 mcg daily",
        "- Metformin 500 mg twice daily",
        "",
        "Follow-up: Pulmonology in 2 weeks. Primary care in 1 week.",
        "",
        "Attending: Dr. B. Jones, MD (synthetic)",
    ]

    # Simple text placement — top-left, line by line
    y = 50
    for line in lines:
        page.insert_text((50, y), line, fontsize=11)
        y += 18

    doc.save(output)
    doc.close()
    return output


def create_lab_png() -> Path:
    """Create a simple lab report image (for OCR testing in Phase 1)."""
    output = DEMO_DIR / "lab_report.png"

    width, height = 700, 500
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Default font works everywhere; no custom font file needed
    font = ImageFont.load_default()

    lines = [
        "SYNTHETIC LAB REPORT — NOT REAL PHI",
        "Patient: Maria Sample | DOB: 1968-03-12",
        "Collection date: 2026-08-10",
        "",
        "Test                  Result    Reference",
        "------------------------------------------------",
        "HbA1c                 9.2 %     4.0 - 5.6",
        "Fasting Glucose       186 mg/dL 70 - 99",
        "Creatinine            1.4 mg/dL 0.6 - 1.2",
        "Hemoglobin            11.8 g/dL 12.0 - 15.5",
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


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    pdf_path = create_discharge_pdf()
    png_path = create_lab_png()

    print("Demo files created:")
    print(f"  - {pdf_path.name}")
    print(f"  - {png_path.name}")
    print(f"  - physician_note.txt (already in folder)")


if __name__ == "__main__":
    main()
