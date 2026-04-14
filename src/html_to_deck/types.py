"""Shared types and stage contracts used across package boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from .audit import AuditReport


class SourceKind(str, Enum):
    """Explicit source kinds accepted by ingestion."""

    FILE = "file"
    HTML_STRING = "html_string"
    URL = "url"


@dataclass(frozen=True)
class PipelineInput:
    """Normalized pipeline input from CLI or API caller."""

    source: str | Path
    source_kind: SourceKind = SourceKind.FILE


@dataclass(frozen=True)
class PipelineOutput:
    """Pipeline result metadata."""

    output_path: Path
    audit_report: AuditReport


class SupportsRender(Protocol):
    """Renderer boundary protocol.

    Renderers should only consume canonical schema models.
    """

    def render(self, deck: "DeckDocument", audit_report: AuditReport | None = None) -> str:
        """Return target-specific serialized output."""


# Imported at bottom to avoid circular import at runtime/type checking.
from .schema.ir import DeckDocument
