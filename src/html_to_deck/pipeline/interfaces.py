"""Stage interfaces and callable contracts for html-to-deck pipeline."""

from __future__ import annotations

from typing import Protocol

from html_to_deck.schema import (
    AuditInput,
    AuditOutput,
    DesignInput,
    DesignOutput,
    ExtractInput,
    ExtractOutput,
    IngestInput,
    IngestOutput,
    LayoutInput,
    LayoutOutput,
    MapToSlidesInput,
    MapToSlidesOutput,
    NarrativeInput,
    NarrativeOutput,
    RenderInput,
    RenderOutput,
)


class IngestStage(Protocol):
    """Produces normalized HTML from source payload."""

    def run(self, data: IngestInput) -> IngestOutput: ...


class ExtractStage(Protocol):
    """Extracts semantic blocks from normalized HTML."""

    def run(self, data: ExtractInput) -> ExtractOutput: ...


class NarrativeStage(Protocol):
    """Transforms extracted blocks into a narrative structure."""

    def run(self, data: NarrativeInput) -> NarrativeOutput: ...


class MapToSlidesStage(Protocol):
    """Maps narrative sections onto candidate slides."""

    def run(self, data: MapToSlidesInput) -> MapToSlidesOutput: ...


class LayoutStage(Protocol):
    """Assigns content placements to each slide."""

    def run(self, data: LayoutInput) -> LayoutOutput: ...


class DesignStage(Protocol):
    """Applies visual theme and styling to laid out slides."""

    def run(self, data: DesignInput) -> DesignOutput: ...


class RenderStage(Protocol):
    """Renders designed slides into an exportable deck artifact."""

    def run(self, data: RenderInput) -> RenderOutput: ...


class AuditStage(Protocol):
    """Audits the rendered deck for quality and structural signals."""

    def run(self, data: AuditInput) -> AuditOutput: ...
