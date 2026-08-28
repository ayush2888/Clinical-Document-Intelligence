# Merge: multi-document patient consolidation (Phase 9)

from merge.exceptions import MergeError, PatientConflictError
from merge.merger import merge_extractions, validate_patient_consistency

__all__ = [
    "MergeError",
    "PatientConflictError",
    "merge_extractions",
    "validate_patient_consistency",
]
