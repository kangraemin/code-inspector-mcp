from __future__ import annotations

from code_inspector.models import Issue

SEVERITY_WEIGHTS: dict[str, float] = {
    "error": 0.3,
    "warning": 0.1,
    "info": 0.05,
}


def calculate_score(
    issues: list[Issue],
    total_files: int,
    severity_weights: dict[str, float] | None = None,
) -> float:
    if not issues:
        return 10.0

    weights = severity_weights or SEVERITY_WEIGHTS
    raw_deduction = sum(weights.get(i.severity, 0.0) for i in issues)
    normalized = raw_deduction * (10 / max(total_files, 1))
    return round(max(0.0, 10.0 - min(normalized, 10.0)), 2)
