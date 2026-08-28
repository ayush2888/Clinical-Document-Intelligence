"""
router.py — picks the right parser based on file type.

Like a hospital reception desk:
  .txt  → text_parser
  .pdf  → pdf_parser
  .png/.jpg → image_ocr
"""

from pathlib import Path

from ingestion.exceptions import UnsupportedFileTypeError
from ingestion.image_ocr import parse_image_file
from ingestion.models import NormalizedDocument
from ingestion.pdf_parser import parse_pdf_file
from ingestion.text_parser import parse_text_file

# Map file extension → internal source type
SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".txt": "txt",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}


def ingest_document(file_path: str | Path) -> NormalizedDocument:
    """
    Main entry point for Phase 1.

    Give it a file path → get back a NormalizedDocument with plain text.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()
    source_type = SUPPORTED_EXTENSIONS.get(extension)

    if source_type is None:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}'. Supported: {supported}"
        )

    if source_type == "txt":
        return parse_text_file(path)
    if source_type == "pdf":
        return parse_pdf_file(path)
    return parse_image_file(path)
