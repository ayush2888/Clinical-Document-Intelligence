"""Errors during multi-document patient merge."""


class MergeError(Exception):
    """Base error for merge failures."""


class PatientConflictError(MergeError):
    """Extracted patient identities conflict — merge blocked."""
