"""Pipeline orchestrator with inspectable artifacts and structured errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from html_to_deck.pipeline.interfaces import (
    AuditStage,
    DesignStage,
    ExtractStage,
    IngestStage,
    LayoutStage,
    MapToSlidesStage,
    NarrativeStage,
    RenderStage,
)
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
    WarningMessage,
)


class PipelineError(Exception):
    """Base exception for pipeline execution problems."""

    def __init__(self, message: str, *, stage: str, fatal: bool = True) -> None:
        super().__init__(message)
        self.stage = stage
        self.fatal = fatal


class ParseFailureError(PipelineError):
    """Raised when source content cannot be parsed/normalized."""


class WeakContentError(PipelineError):
    """Raised when content quality is low but potentially recoverable."""


class UnsupportedStructureError(PipelineError):
    """Raised when source structure cannot be represented downstream."""


class RenderFailureError(PipelineError):
    """Raised when deck rendering fails."""


@dataclass(slots=True)
class StageArtifact:
    stage: str
    input_data: Any
    output_data: Any | None = None
    warnings: list[WarningMessage] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PipelineReport:
    artifacts: dict[str, StageArtifact] = field(default_factory=dict)
    warnings: list[WarningMessage] = field(default_factory=list)
    errors: list[PipelineError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(error.fatal for error in self.errors)


@dataclass(slots=True)
class OrchestrationResult:
    report: PipelineReport
    ingest: IngestOutput | None = None
    extract: ExtractOutput | None = None
    narrative: NarrativeOutput | None = None
    mapped: MapToSlidesOutput | None = None
    layout: LayoutOutput | None = None
    design: DesignOutput | None = None
    render: RenderOutput | None = None
    audit: AuditOutput | None = None


@dataclass(slots=True)
class PipelineOrchestrator:
    ingest_stage: IngestStage
    extract_stage: ExtractStage
    narrative_stage: NarrativeStage
    map_to_slides_stage: MapToSlidesStage
    layout_stage: LayoutStage
    design_stage: DesignStage
    render_stage: RenderStage
    audit_stage: AuditStage

    def run(self, ingest_input: IngestInput) -> OrchestrationResult:
        report = PipelineReport()
        result = OrchestrationResult(report=report)

        ingest_output = self._run_stage(
            stage_name="ingest",
            report=report,
            input_data=ingest_input,
            fn=lambda payload: self.ingest_stage.run(payload),
        )
        if ingest_output is None:
            return result
        result.ingest = ingest_output

        extract_output = self._run_stage(
            stage_name="extract",
            report=report,
            input_data=ExtractInput(ingest=ingest_output),
            fn=lambda payload: self.extract_stage.run(payload),
        )
        if extract_output is None:
            return result
        result.extract = extract_output

        narrative_output = self._run_stage(
            stage_name="narrative",
            report=report,
            input_data=NarrativeInput(extracted=extract_output),
            fn=lambda payload: self.narrative_stage.run(payload),
        )
        if narrative_output is None:
            return result
        result.narrative = narrative_output

        mapped_output = self._run_stage(
            stage_name="map_to_slides",
            report=report,
            input_data=MapToSlidesInput(narrative=narrative_output),
            fn=lambda payload: self.map_to_slides_stage.run(payload),
        )
        if mapped_output is None:
            return result
        result.mapped = mapped_output

        layout_output = self._run_stage(
            stage_name="layout",
            report=report,
            input_data=LayoutInput(mapped=mapped_output),
            fn=lambda payload: self.layout_stage.run(payload),
        )
        if layout_output is None:
            return result
        result.layout = layout_output

        design_output = self._run_stage(
            stage_name="design",
            report=report,
            input_data=DesignInput(layout=layout_output),
            fn=lambda payload: self.design_stage.run(payload),
        )
        if design_output is None:
            return result
        result.design = design_output

        render_output = self._run_stage(
            stage_name="render",
            report=report,
            input_data=RenderInput(design=design_output),
            fn=lambda payload: self.render_stage.run(payload),
        )
        if render_output is None:
            return result
        result.render = render_output

        audit_output = self._run_stage(
            stage_name="audit",
            report=report,
            input_data=AuditInput(render=render_output, design=design_output),
            fn=lambda payload: self.audit_stage.run(payload),
        )
        result.audit = audit_output

        if audit_output is not None:
            for warning in audit_output.warnings:
                self._record_warning(
                    report=report,
                    stage_name="audit",
                    warning=WarningMessage(
                        stage="audit",
                        code="audit.warning",
                        message=warning,
                    ),
                )

        return result

    def _run_stage(self, stage_name: str, report: PipelineReport, input_data: Any, fn: Any) -> Any | None:
        artifact = StageArtifact(stage=stage_name, input_data=input_data)
        report.artifacts[stage_name] = artifact

        try:
            output = fn(input_data)
        except WeakContentError as exc:
            report.errors.append(exc)
            warning = WarningMessage(stage=stage_name, code="weak_content", message=str(exc))
            self._record_warning(report=report, stage_name=stage_name, warning=warning)
            artifact.errors.append(str(exc))
            return None
        except PipelineError as exc:
            report.errors.append(exc)
            artifact.errors.append(str(exc))
            if not exc.fatal:
                warning = WarningMessage(stage=stage_name, code="non_fatal", message=str(exc))
                self._record_warning(report=report, stage_name=stage_name, warning=warning)
                return None
            return None
        except Exception as exc:  # pragma: no cover - defensive wrapper
            wrapped = PipelineError(str(exc), stage=stage_name, fatal=True)
            report.errors.append(wrapped)
            artifact.errors.append(str(exc))
            return None

        artifact.output_data = output
        return output

    def _record_warning(self, report: PipelineReport, stage_name: str, warning: WarningMessage) -> None:
        report.warnings.append(warning)
        report.artifacts[stage_name].warnings.append(warning)
