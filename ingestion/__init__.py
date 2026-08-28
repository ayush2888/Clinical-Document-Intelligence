# Ingestion: read PDF / image / text files (Phase 1)

from ingestion.models import NormalizedDocument
from ingestion.router import ingest_document

__all__ = ["NormalizedDocument", "ingest_document"]
