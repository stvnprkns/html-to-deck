from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class SlideClaim:
    text: str
    has_evidence: bool = False
    provenance: str | None = None


@dataclass(frozen=True)
class SlideSpec:
    id: str
    title: str
    takeaway: str
    communication_job: str
    text_blocks: list[str]
    pattern_signature: str
    claims: list[SlideClaim]


@dataclass(frozen=True)
class DeckSpec:
    slides: list[SlideSpec]


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

    def to_dict(self) -> dict:
        return {
            "has_blockers": self.has_blockers,
            "warnings": [asdict(w) for w in self.warnings],
        }
