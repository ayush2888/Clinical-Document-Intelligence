"""Read plain .txt files directly from disk."""

from pathlib import Path

from ingestion.exceptions import EmptyDocumentError
from ingestion.models import NormalizedDocument


def parse_text_file(file_path: Path) -> NormalizedDocument:
    """Read a text file and wrap it in a NormalizedDocument."""
    text = file_path.read_text(encoding="utf-8").strip()

    if not text:
        raise EmptyDocumentError(f"Text file is empty: {file_path.name}")

    return NormalizedDocument(
        source_type="txt",
        filename=file_path.name,
        page_count=None,
        text=text,
        metadata={"encoding": "utf-8"},
    )
