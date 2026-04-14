"""Typed audit contracts for canonical pipeline quality checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class AuditWarning:
    slide_id: str
    check: str
    severity: Severity
    confidence: float
    actionable: str


@dataclass(frozen=True)
class AuditReport:
    warnings: list[AuditWarning]

    @property
    def has_blockers(self) -> bool:
        return any(w.severity in {"high", "critical"} for w in self.warnings)

    @property
    def counts_by_severity(self) -> dict[Severity, int]:
        counts: dict[Severity, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for warning in self.warnings:
            counts[warning.severity] += 1
        return counts


    @property
    def summary_line(self) -> str:
        status = "BLOCKERS" if self.has_blockers else "OK"
        counts = self.counts_by_severity
        return (
            f"audit={status} warning_count={len(self.warnings)} "
            f"critical={counts['critical']} high={counts['high']} "
            f"medium={counts['medium']} low={counts['low']}"
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "has_blockers": self.has_blockers,
            "counts_by_severity": self.counts_by_severity,
            "warning_count": len(self.warnings),
            "warnings": [asdict(warning) for warning in self.warnings],
        }
