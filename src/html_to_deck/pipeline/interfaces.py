"""Stage interfaces and typed contracts for the html-to-deck pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from html_to_deck.schema.models import (
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
else:
    AuditInput = Any
    AuditOutput = Any
    DesignInput = Any
    DesignOutput = Any
    ExtractInput = Any
    ExtractOutput = Any
    IngestInput = Any
    IngestOutput = Any
    LayoutInput = Any
    LayoutOutput = Any
    MapToSlidesInput = Any
    MapToSlidesOutput = Any
    NarrativeInput = Any
    NarrativeOutput = Any
    RenderInput = Any
    RenderOutput = Any


class IngestStage(Protocol):
    def run(self, data: IngestInput) -> IngestOutput: ...


class ExtractStage(Protocol):
    def run(self, data: ExtractInput) -> ExtractOutput: ...


class NarrativeStage(Protocol):
    def run(self, data: NarrativeInput) -> NarrativeOutput: ...


class MapToSlidesStage(Protocol):
    def run(self, data: MapToSlidesInput) -> MapToSlidesOutput: ...


class LayoutStage(Protocol):
    def run(self, data: LayoutInput) -> LayoutOutput: ...


class DesignStage(Protocol):
    def run(self, data: DesignInput) -> DesignOutput: ...


class RenderStage(Protocol):
    def run(self, data: RenderInput) -> RenderOutput: ...


class AuditStage(Protocol):
    def run(self, data: AuditInput) -> AuditOutput: ...
