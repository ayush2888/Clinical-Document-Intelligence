"""Extract text from PDF files using PyMuPDF (fitz)."""

from pathlib import Path

import pymupdf

from ingestion.exceptions import EmptyDocumentError, UnreadablePdfError
from ingestion.models import NormalizedDocument


def parse_pdf_file(file_path: Path) -> NormalizedDocument:
    """Read a PDF page by page and keep page numbers in the text."""
    try:
        doc = pymupdf.open(file_path)
    except Exception as exc:
        raise UnreadablePdfError(
            f"Cannot open PDF '{file_path.name}': {exc}"
        ) from exc

    page_count = len(doc)
    page_chunks: list[str] = []

    for page_number in range(page_count):
        page = doc[page_number]
        page_text = page.get_text().strip()
        if page_text:
            page_chunks.append(f"[Page {page_number + 1}]\n{page_text}")

    doc.close()

    full_text = "\n\n".join(page_chunks).strip()
    if not full_text:
        raise EmptyDocumentError(
            f"PDF '{file_path.name}' has no extractable text. "
            "It may be a scanned document (OCR fallback can be added later)."
        )

    return NormalizedDocument(
        source_type="pdf",
        filename=file_path.name,
        page_count=page_count,
        text=full_text,
        metadata={"parser": "pymupdf"},
    )
