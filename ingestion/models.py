"""
models.py — the standard shape every parser returns.

No matter if the input is TXT, PDF, or image, the rest of the app
always receives a NormalizedDocument with plain text inside.
"""

from typing import Any
import uuid

from pydantic import BaseModel, Field


class NormalizedDocument(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str  # "txt", "pdf", or "image"
    filename: str
    page_count: int | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
