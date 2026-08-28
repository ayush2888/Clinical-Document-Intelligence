"""
llm_client.py — one place to create the Groq LLM client (Phase 2+).

Groq exposes an OpenAI-compatible HTTP API. We reuse the official `openai`
Python package but point it at Groq's server instead of OpenAI's.

Usage (later in extraction/):
    from llm_client import get_llm_client
    client = get_llm_client()
    response = client.chat.completions.create(model=..., messages=[...])
"""

from openai import OpenAI

import config


def get_llm_client() -> OpenAI:
    """Return a client configured for Groq."""
    if not config.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file "
            "(see .env.example)."
        )

    return OpenAI(
        api_key=config.GROQ_API_KEY,
        base_url=config.GROQ_BASE_URL,
    )
