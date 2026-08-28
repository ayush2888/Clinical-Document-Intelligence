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
    api_key = config.get_groq_api_key()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Local: add to .env. "
            "Streamlit Cloud: Settings → Secrets (TOML format). "
            "See .env.example and docs/STREAMLIT_DEPLOY.md."
        )

    return OpenAI(
        api_key=api_key,
        base_url=config.get_groq_base_url(),
    )
