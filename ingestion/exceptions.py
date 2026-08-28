"""Custom errors for document ingestion — easy to catch and explain."""


class IngestionError(Exception):
    """Base error for anything that goes wrong while reading a file."""


class UnsupportedFileTypeError(IngestionError):
    """File extension is not TXT, PDF, or image."""


class EmptyDocumentError(IngestionError):
    """File opened fine but no text could be extracted."""


class UnreadablePdfError(IngestionError):
    """PDF is corrupt or cannot be opened."""


class OcrFailureError(IngestionError):
    """Tesseract OCR failed (missing install, bad image, etc.)."""
