"""
llm_extractor.py — LLM #1: plain text → validated ClinicalExtraction.

Flow:
  NormalizedDocument  →  Groq API  →  JSON  →  Pydantic check
"""

import json

from pydantic import ValidationError as PydanticValidationError

import config
from extraction.exceptions import ExtractionError, LlmResponseError, ValidationError
from extraction.prompts import SYSTEM_PROMPT, USER_PROMPT
from extraction.schemas import ClinicalExtraction
from ingestion.models import NormalizedDocument
from llm_client import get_llm_client


def _schema_hint() -> str:
    """Short schema summary for the prompt (not the full JSON Schema blob)."""
    return """
{
  "patient": {"name": str|null, "age": int|null, "sex": str|null},
  "diagnoses": [{"name": str, "evidence": str}],
  "medications": [{"name": str, "dose": str|null, "frequency": str|null, "evidence": str}],
  "allergies": [{"substance": str, "evidence": str}],
  "symptoms": [{"name": str, "evidence": str}],
  "vital_signs": [{"name": str, "value": str, "unit": str|null, "evidence": str}],
  "laboratory_results": [{"test_name": str, "value": str, "unit": str|null,
                            "reference_range_if_present": str|null, "evidence": str}],
  "procedures": [{"name": str, "evidence": str}],
  "important_findings": [{"finding": str, "evidence": str}]
}
""".strip()


def extract_clinical_data(document: NormalizedDocument) -> ClinicalExtraction:
    """
    Send document text to Groq and return validated structured data.

    Args:
        document: Output from Phase 1 ingestion (must contain .text).

    Returns:
        ClinicalExtraction validated by Pydantic.
    """
    if not document.text.strip():
        raise ExtractionError("Cannot extract from an empty document.")

    client = get_llm_client()

    system_message = SYSTEM_PROMPT.format(schema_hint=_schema_hint())
    user_message = USER_PROMPT.format(
        filename=document.filename,
        source_type=document.source_type,
        document_text=document.text,
    )

    try:
        response = client.chat.completions.create(
            model=config.get_groq_model(),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    except Exception as exc:
        raise ExtractionError(f"Groq API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise LlmResponseError("Groq returned an empty response.")

    try:
        return ClinicalExtraction.model_validate_json(raw_content)
    except PydanticValidationError as exc:
        raise ValidationError(
            f"LLM JSON did not match schema: {exc}"
        ) from exc


def extraction_to_dict(extraction: ClinicalExtraction) -> dict:
    """Convert extraction to a plain dict (handy for printing/saving)."""
    return json.loads(extraction.model_dump_json(exclude_none=False))
