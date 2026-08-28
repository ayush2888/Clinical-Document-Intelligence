"""
terminology.py — map clinical aliases to one canonical concept name.

Example:
  "T2DM"  →  canonical: type_2_diabetes_mellitus
  "Type 2 diabetes"  →  same canonical name

This is deterministic Python — no LLM call.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

import config

TERMINOLOGY_MAP_PATH = config.BASE_DIR / "knowledge" / "terminology_map.json"


@dataclass(frozen=True)
class TerminologyMatch:
    """Result when a term matches a known concept."""

    canonical_name: str
    display_name: str


def _normalize_term(text: str) -> str:
    """Prepare text for lookup: lowercase, trim, simplify punctuation."""
    cleaned = text.lower().strip()
    cleaned = re.sub(r"[^\w\s/%.-]", " ", cleaned)
    return " ".join(cleaned.split())


class TerminologyResolver:
    """
    Look up clinical terms using a local JSON alias map + in-memory cache.

    Think of it as a phone book:
      many nicknames (aliases) → one official entry (canonical concept)
    """

    def __init__(self, map_path: Path = TERMINOLOGY_MAP_PATH) -> None:
        self._map_path = map_path
        self._alias_to_concept: dict[str, TerminologyMatch] = {}
        self._cache: dict[str, TerminologyMatch | None] = {}
        self._load_map()

    def _lookup_key(self, key: str) -> TerminologyMatch | None:
        """Try exact key, then longest alias contained inside the key."""
        if not key:
            return None

        if key in self._alias_to_concept:
            return self._alias_to_concept[key]

        best_match: TerminologyMatch | None = None
        best_len = 0
        for alias, match in self._alias_to_concept.items():
            if alias in key and len(alias) > best_len:
                best_len = len(alias)
                best_match = match
        return best_match

    def resolve(self, term: str) -> TerminologyMatch | None:
        """Return canonical concept for a term, or None if unknown."""
        if not term or not term.strip():
            return None

        if term in self._cache:
            return self._cache[term]

        key = _normalize_term(term)
        match = self._lookup_key(key)

        # Handle notes in parentheses, e.g. "Type 2 diabetes (diagnosed 2019)"
        if match is None:
            stripped = re.sub(r"\([^)]*\)", "", term)
            match = self._lookup_key(_normalize_term(stripped))

        self._cache[term] = match
        return match

    def _load_map(self) -> None:
        raw = json.loads(self._map_path.read_text(encoding="utf-8"))
        concepts = raw.get("concepts", {})

        for canonical_name, info in concepts.items():
            display_name = info["display_name"]
            match = TerminologyMatch(
                canonical_name=canonical_name,
                display_name=display_name,
            )
            all_names = [display_name, canonical_name.replace("_", " ")]
            all_names.extend(info.get("aliases", []))

            for name in all_names:
                key = _normalize_term(name)
                if key:
                    self._alias_to_concept[key] = match


def get_terminology_resolver() -> TerminologyResolver:
    """Shared resolver instance for the app."""
    return TerminologyResolver()
