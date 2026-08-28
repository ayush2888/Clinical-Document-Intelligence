"""
summary_generator.py — LLM #2: validated data → human-readable summary.

LLM #2 never sees raw document text — only the validated bundle from Phases 2–6.
"""

import json

from pydantic import ValidationError as PydanticValidationError

import config
from assessment.models import AssessmentResult
from extraction.schemas import ClinicalExtraction
from generation.disclaimer import POC_DISCLAIMER
from generation.exceptions import GenerationError, LlmSummaryError, SummaryValidationError
from generation.prompts import SYSTEM_PROMPT, USER_PROMPT
from generation.schemas import ClinicalSummary
from knowledge.models import RetrievedKnowledge
from llm_client import get_llm_client


def _schema_hint() -> str:
    return """
{
  "patient_summary": "string (2-4 sentences)",
  "key_findings": ["string", "..."],
  "risk_flags": ["string", "..."],
  "recommended_next_step": "string",
  "evidence_highlights": ["string", "..."],
  "knowledge_citations": ["string", "..."]
}
""".strip()


def build_summary_input(
    extraction: ClinicalExtraction,
    knowledge: list[RetrievedKnowledge],
    assessments: list[AssessmentResult],
) -> dict:
    """
    Bundle validated inputs for LLM #2.

    No raw document text — only structured outputs from earlier phases.
    """
    low_confidence: list[str] = []

    for lab in extraction.laboratory_results:
        if lab.confidence is not None and lab.confidence < config.CONFIDENCE_REVIEW_THRESHOLD:
            low_confidence.append(
                f"{lab.test_name}: confidence {lab.confidence} — {lab.evidence}"
            )

    for vital in extraction.vital_signs:
        if vital.confidence is not None and vital.confidence < config.CONFIDENCE_REVIEW_THRESHOLD:
            low_confidence.append(
                f"{vital.name}: confidence {vital.confidence} — {vital.evidence}"
            )

    return {
        "structured_extraction": json.loads(extraction.model_dump_json()),
        "assessment_flags": [
            json.loads(item.model_dump_json()) for item in assessments
        ],
        "knowledge_context": [
            json.loads(item.model_dump_json()) for item in knowledge
        ],
        "low_confidence_fields": low_confidence,
    }


def generate_summary(
    extraction: ClinicalExtraction,
    knowledge: list[RetrievedKnowledge],
    assessments: list[AssessmentResult],
) -> ClinicalSummary:
    """
    Call Groq to produce a grounded clinical summary card.

    The disclaimer is always forced to the fixed POC text after validation.
    """
    input_bundle = build_summary_input(extraction, knowledge, assessments)
    input_json = json.dumps(input_bundle, indent=2)

    client = get_llm_client()
    system_message = SYSTEM_PROMPT.format(schema_hint=_schema_hint())
    user_message = USER_PROMPT.format(input_json=input_json)

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    except Exception as exc:
        raise GenerationError(f"Groq summary call failed: {exc}") from exc

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise LlmSummaryError("Groq returned an empty summary response.")

    try:
        summary = ClinicalSummary.model_validate_json(raw_content)
    except PydanticValidationError as exc:
        raise SummaryValidationError(
            f"Summary JSON did not match schema: {exc}"
        ) from exc

    # Always use the fixed disclaimer — do not trust the LLM for legal/POC text.
    return summary.model_copy(update={"disclaimer": POC_DISCLAIMER})
