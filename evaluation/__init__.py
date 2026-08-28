# Evaluation: compare LLM extraction against ground truth (Phase 10)

from evaluation.comparator import EvaluationReport, FieldResult, evaluate_case, merge_reports
from evaluation.models import EvaluationCase, GroundTruthFile

__all__ = [
    "EvaluationCase",
    "EvaluationReport",
    "FieldResult",
    "GroundTruthFile",
    "evaluate_case",
    "merge_reports",
]
