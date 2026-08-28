"""Errors during summary generation (LLM #2)."""


class GenerationError(Exception):
    """Base error for summary generation failures."""


class LlmSummaryError(GenerationError):
    """Groq returned empty or unusable summary content."""


class SummaryValidationError(GenerationError):
    """Summary JSON did not match the expected schema."""
