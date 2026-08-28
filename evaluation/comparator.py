"""
comparator.py — compare extracted JSON against ground truth.

Each expected entity counts as one evaluated field (or one field group for patient scalars).
"""

import re
from dataclasses import dataclass, field

from evaluation.models import EvaluationCase, ExpectedListItem, ExpectedPatientField
from extraction.schemas import ClinicalExtraction


@dataclass
class FieldResult:
    case_id: str
    field_path: str
    status: str  # correct | incorrect | missing
    expected: str | None = None
    actual: str | None = None


@dataclass
class EvaluationReport:
    documents_evaluated: int = 0
    fields_evaluated: int = 0
    correct: int = 0
    incorrect: int = 0
    missing: int = 0
    details: list[FieldResult] = field(default_factory=list)

    def add(self, result: FieldResult) -> None:
        self.details.append(result)
        self.fields_evaluated += 1
        if result.status == "correct":
            self.correct += 1
        elif result.status == "incorrect":
            self.incorrect += 1
        elif result.status == "missing":
            self.missing += 1


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().lower())


def _first_number(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"(\d+\.?\d*)", value.replace(",", ""))
    return match.group(1) if match else None


def _match_patient_field(
    expected: ExpectedPatientField,
    actual: str | int | None,
) -> bool:
    if expected.value is None:
        return actual is not None

    expected_str = str(expected.value)
    actual_str = "" if actual is None else str(actual)

    if expected.match == "contains":
        return _normalize_text(expected_str) in _normalize_text(actual_str)
    if expected.match == "normalized_contains":
        return _normalize_text(expected_str) in _normalize_text(actual_str)

    if isinstance(expected.value, int):
        try:
            return int(_first_number(actual_str) or -1) == expected.value
        except ValueError:
            return False

    return _normalize_text(expected_str) == _normalize_text(actual_str)


def _item_key(item: ExpectedListItem) -> str:
    return item.canonical_name or item.name or item.name_contains or "unknown"


def _find_list_item(items, expected: ExpectedListItem):
    """Return the best matching extracted item, or None."""
    for item in items:
        if expected.canonical_name and getattr(item, "canonical_name", None) == expected.canonical_name:
            return item
        if expected.name and _normalize_text(getattr(item, "name", None)) == _normalize_text(expected.name):
            return item
        if expected.name_contains:
            label = getattr(item, "name", None) or getattr(item, "substance", None) or getattr(item, "test_name", None)
            if label and _normalize_text(expected.name_contains) in _normalize_text(label):
                return item
    return None


def _check_list_item(item, expected: ExpectedListItem) -> bool:
    if expected.value is not None:
        actual_value = getattr(item, "value", None)
        return _first_number(str(actual_value)) == _first_number(str(expected.value))

    if expected.value_contains:
        actual_value = getattr(item, "value", None) or ""
        return _normalize_text(expected.value_contains) in _normalize_text(str(actual_value))

    if expected.dose_contains:
        dose = getattr(item, "dose", None) or ""
        return _normalize_text(expected.dose_contains) in _normalize_text(str(dose))

    return True


def _evaluate_patient(
    case_id: str,
    expected: dict[str, ExpectedPatientField],
    extraction: ClinicalExtraction,
    report: EvaluationReport,
) -> None:
    patient = extraction.patient
    for field_name, spec in expected.items():
        path = f"patient.{field_name}"
        actual = None if patient is None else getattr(patient, field_name, None)

        if actual is None:
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="missing",
                    expected=str(spec.value),
                    actual=None,
                )
            )
            continue

        if _match_patient_field(spec, actual):
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="correct",
                    expected=str(spec.value),
                    actual=str(actual),
                )
            )
        else:
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="incorrect",
                    expected=str(spec.value),
                    actual=str(actual),
                )
            )


def _evaluate_list_section(
    case_id: str,
    section: str,
    expected_items: list[ExpectedListItem],
    actual_items,
    report: EvaluationReport,
) -> None:
    for expected in expected_items:
        key = _item_key(expected)
        path = f"{section}.{key}"
        match = _find_list_item(actual_items, expected)

        if match is None:
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="missing",
                    expected=_expected_label(expected),
                    actual=None,
                )
            )
            continue

        if _check_list_item(match, expected):
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="correct",
                    expected=_expected_label(expected),
                    actual=_actual_label(match),
                )
            )
        else:
            report.add(
                FieldResult(
                    case_id=case_id,
                    field_path=path,
                    status="incorrect",
                    expected=_expected_label(expected),
                    actual=_actual_label(match),
                )
            )


def _expected_label(expected: ExpectedListItem) -> str:
    parts = []
    if expected.canonical_name:
        parts.append(expected.canonical_name)
    if expected.name:
        parts.append(expected.name)
    if expected.name_contains:
        parts.append(f"name~{expected.name_contains}")
    if expected.value:
        parts.append(f"value={expected.value}")
    if expected.value_contains:
        parts.append(f"value~{expected.value_contains}")
    if expected.dose_contains:
        parts.append(f"dose~{expected.dose_contains}")
    return " | ".join(parts) or "entity"


def _actual_label(item) -> str:
    name = (
        getattr(item, "name", None)
        or getattr(item, "test_name", None)
        or getattr(item, "substance", None)
        or "?"
    )
    value = getattr(item, "value", None)
    dose = getattr(item, "dose", None)
    chunks = [str(name)]
    if value is not None:
        chunks.append(f"value={value}")
    if dose is not None:
        chunks.append(f"dose={dose}")
    return " | ".join(chunks)


def evaluate_case(case: EvaluationCase, extraction: ClinicalExtraction) -> EvaluationReport:
    """Compare one extraction against one ground-truth case."""
    report = EvaluationReport(documents_evaluated=1)

    expected = case.expected
    _evaluate_patient(case.id, expected.patient, extraction, report)
    _evaluate_list_section(case.id, "diagnoses", expected.diagnoses, extraction.diagnoses, report)
    _evaluate_list_section(case.id, "medications", expected.medications, extraction.medications, report)
    _evaluate_list_section(
        case.id, "laboratory_results", expected.laboratory_results, extraction.laboratory_results, report
    )
    _evaluate_list_section(case.id, "vital_signs", expected.vital_signs, extraction.vital_signs, report)
    _evaluate_list_section(case.id, "symptoms", expected.symptoms, extraction.symptoms, report)
    _evaluate_list_section(case.id, "allergies", expected.allergies, extraction.allergies, report)

    return report


def merge_reports(reports: list[EvaluationReport]) -> EvaluationReport:
    """Combine per-document reports into one summary."""
    combined = EvaluationReport(documents_evaluated=len(reports))
    for item in reports:
        for detail in item.details:
            combined.add(detail)
    return combined
