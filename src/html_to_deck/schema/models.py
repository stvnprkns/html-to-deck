"""Schema models for each html-to-deck pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class IngestInput:
    """Raw source payload for ingestion."""

    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IngestOutput:
    """Normalized document and metadata from ingest stage."""

    normalized_html: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractInput:
    ingest: IngestOutput


@dataclass(slots=True)
class ExtractOutput:
    """Structured content units extracted from normalized HTML."""

    blocks: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NarrativeInput:
    extracted: ExtractOutput


@dataclass(slots=True)
class NarrativeOutput:
    """Story-level representation produced from extracted blocks."""

    sections: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""


@dataclass(slots=True)
class MapToSlidesInput:
    narrative: NarrativeOutput


@dataclass(slots=True)
class MapToSlidesOutput:
    """Slide candidates before concrete layout and design."""

    slides: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class LayoutInput:
    mapped: MapToSlidesOutput


@dataclass(slots=True)
class LayoutOutput:
    """Placed slide content with spatial layout hints."""

    laid_out_slides: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class DesignInput:
    layout: LayoutOutput


@dataclass(slots=True)
class DesignOutput:
    """Visual styling and theme material for each slide."""

    designed_slides: list[dict[str, Any]] = field(default_factory=list)
    theme: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RenderInput:
    design: DesignOutput


@dataclass(slots=True)
class RenderOutput:
    """Binary/text render outputs and references to generated assets."""

    deck_bytes: bytes | None = None
    output_path: str | None = None
    assets: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AuditInput:
    render: RenderOutput
    design: DesignOutput


@dataclass(slots=True)
class AuditOutput:
    """Quality checks and post-render validations."""

    quality_score: float | None = None
    checks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WarningMessage:
    """Structured warning information from any stage."""

    stage: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
