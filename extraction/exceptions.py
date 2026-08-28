"""Errors that can happen during LLM extraction."""


class ExtractionError(Exception):
    """Base error for extraction failures."""


class LlmResponseError(ExtractionError):
    """Groq returned empty or unusable content."""


class ValidationError(ExtractionError):
    """LLM JSON did not match our Pydantic schema."""
