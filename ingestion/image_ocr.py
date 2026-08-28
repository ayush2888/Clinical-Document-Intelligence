"""Extract text from images using Tesseract OCR."""

from pathlib import Path

import pytesseract
from PIL import Image

import config
from ingestion.exceptions import EmptyDocumentError, OcrFailureError
from ingestion.models import NormalizedDocument

# On Windows, Tesseract is often not on PATH — config tells us where it lives.
if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def parse_image_file(file_path: Path) -> NormalizedDocument:
    """Run OCR on an image file and return extracted text."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise OcrFailureError(
            f"OCR failed for '{file_path.name}': {exc}. "
            "Is Tesseract installed? Set TESSERACT_CMD in .env if needed."
        ) from exc

    if not text:
        raise EmptyDocumentError(
            f"OCR returned no text for image: {file_path.name}"
        )

    return NormalizedDocument(
        source_type="image",
        filename=file_path.name,
        page_count=1,
        text=text,
        metadata={"parser": "tesseract", "ocr_engine": "tesseract"},
    )
