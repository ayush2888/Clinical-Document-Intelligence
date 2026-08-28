"""
loinc_service.py — optional stub for external LOINC lookup (not used in POC demo).

The rest of the app uses TerminologyResolver (local JSON map).
This interface shows how you could plug in LOINC later without rewriting extraction.
"""


class LoincService:
    """Placeholder for future LOINC API integration."""

    def lookup(self, test_name: str) -> str | None:
        """
        Return a LOINC code for a lab test name, or None if unavailable.

        POC: always returns None — local terminology map is enough for demo.
        """
        return None
