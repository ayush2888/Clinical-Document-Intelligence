"""
retriever.py — fetch relevant clinical guidance for extracted observations.

Uses local JSON files in knowledge/sources/ (no vector DB, no external API).
Matches on canonical_name from Phase 4 terminology normalization.
"""

import json
from pathlib import Path

import config
from extraction.schemas import ClinicalExtraction
from knowledge.models import KnowledgeDocument, RetrievedKnowledge

SOURCES_DIR = config.BASE_DIR / "knowledge" / "sources"

UNAVAILABLE_MESSAGE = (
    "Clinical interpretation unavailable from configured knowledge sources; "
    "clinician review required."
)


class KnowledgeRetriever:
    """
    Simple lookup: canonical concept id → local guidance JSON.

    Like a small library shelf — one booklet per lab/vital topic.
    """

    def __init__(self, sources_dir: Path = SOURCES_DIR) -> None:
        self._sources_dir = sources_dir
        self._documents: dict[str, KnowledgeDocument] = {}
        self._load_sources()

    def _load_sources(self) -> None:
        for path in self._sources_dir.glob("*.json"):
            raw = json.loads(path.read_text(encoding="utf-8"))
            doc = KnowledgeDocument.model_validate(raw)
            self._documents[doc.canonical_name] = doc

    def retrieve(self, canonical_name: str) -> RetrievedKnowledge | None:
        """Return guidance for one canonical concept, or None if not in KB."""
        doc = self._documents.get(canonical_name)
        if doc is None:
            return None
        return RetrievedKnowledge(
            topic=doc.topic,
            canonical_name=doc.canonical_name,
            source=doc.source,
            version=doc.version,
            interpretation=doc.interpretation,
            url=doc.url,
        )

    def retrieve_or_unavailable(self, canonical_name: str) -> RetrievedKnowledge:
        """Return guidance or a fixed unavailable message (never invent text)."""
        found = self.retrieve(canonical_name)
        if found is not None:
            return found
        return RetrievedKnowledge(
            topic=canonical_name,
            canonical_name=canonical_name,
            source="Configured knowledge sources",
            version="n/a",
            interpretation=UNAVAILABLE_MESSAGE,
            url=None,
        )

    def retrieve_for_extraction(
        self, extraction: ClinicalExtraction
    ) -> list[RetrievedKnowledge]:
        """
        Find knowledge for labs and vitals that have a canonical_name.

        Skips duplicates. Attaches observed value/unit when available.
        """
        results: list[RetrievedKnowledge] = []
        seen: set[str] = set()

        for lab in extraction.laboratory_results:
            if not lab.canonical_name or lab.canonical_name in seen:
                continue
            seen.add(lab.canonical_name)
            item = self.retrieve_or_unavailable(lab.canonical_name)
            item = item.model_copy(
                update={
                    "observed_value": lab.value,
                    "observed_unit": lab.unit,
                }
            )
            results.append(item)

        for vital in extraction.vital_signs:
            if not vital.canonical_name or vital.canonical_name in seen:
                continue
            seen.add(vital.canonical_name)
            item = self.retrieve_or_unavailable(vital.canonical_name)
            item = item.model_copy(
                update={
                    "observed_value": vital.value,
                    "observed_unit": vital.unit,
                }
            )
            results.append(item)

        return results


def get_knowledge_retriever() -> KnowledgeRetriever:
    """Shared retriever for the app."""
    return KnowledgeRetriever()
