"""Pipeline orchestrator with inspectable artifacts and structured stage errors."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

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


class PipelineError(Exception):
    """Base exception for pipeline execution failures."""

    def __init__(self, message: str, *, stage: str, fatal: bool = True) -> None:
        super().__init__(message)
        self.stage = stage
        self.fatal = fatal


class ParseFailureError(PipelineError):
    pass


class WeakContentError(PipelineError):
    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(message, stage=stage, fatal=False)


class UnsupportedStructureError(PipelineError):
    pass


class RenderFailureError(PipelineError):
    pass


@dataclass(slots=True)
class WarningMessage:
    stage: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


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

        ingest = self._run_stage("ingest", ingest_input, lambda payload: self.ingest_stage.run(payload), report)
        if ingest is None:
            return result
        result.ingest = ingest

        extract_input = self._contract("ExtractInput", ingest=ingest)
        extract = self._run_stage("extract", extract_input, lambda payload: self.extract_stage.run(payload), report)
        if extract is None:
            return result
        result.extract = extract

        narrative_input = self._contract("NarrativeInput", extracted=extract)
        narrative = self._run_stage("narrative", narrative_input, lambda payload: self.narrative_stage.run(payload), report)
        if narrative is None:
            return result
        result.narrative = narrative

        mapped_input = self._contract("MapToSlidesInput", narrative=narrative)
        mapped = self._run_stage("map_to_slides", mapped_input, lambda payload: self.map_to_slides_stage.run(payload), report)
        if mapped is None:
            return result
        result.mapped = mapped

        layout_input = self._contract("LayoutInput", mapped=mapped)
        layout = self._run_stage("layout", layout_input, lambda payload: self.layout_stage.run(payload), report)
        if layout is None:
            return result
        result.layout = layout

        design_input = self._contract("DesignInput", layout=layout)
        design = self._run_stage("design", design_input, lambda payload: self.design_stage.run(payload), report)
        if design is None:
            return result
        result.design = design

        render_input = self._contract("RenderInput", design=design)
        render = self._run_stage("render", render_input, lambda payload: self.render_stage.run(payload), report)
        if render is None:
            return result
        result.render = render

        audit_input = self._contract("AuditInput", render=render, design=design)
        audit = self._run_stage("audit", audit_input, lambda payload: self.audit_stage.run(payload), report)
        result.audit = audit

        if audit is not None:
            for warning in getattr(audit, "warnings", []):
                self._record_warning(report, "audit", WarningMessage(stage="audit", code="audit.warning", message=warning))

        return result

    def _run_stage(
        self,
        stage_name: str,
        stage_input: Any,
        runner: Callable[[Any], Any],
        report: PipelineReport,
    ) -> Any | None:
        artifact = StageArtifact(stage=stage_name, input_data=stage_input)
        report.artifacts[stage_name] = artifact
        try:
            output = runner(stage_input)
            artifact.output_data = output
            return output
        except PipelineError as exc:
            report.errors.append(exc)
            artifact.errors.append(str(exc))
            if not exc.fatal:
                self._record_warning(
                    report,
                    stage_name,
                    WarningMessage(stage=stage_name, code=exc.__class__.__name__, message=str(exc)),
                )
            return None
        except Exception as exc:  # pragma: no cover
            wrapped = PipelineError(str(exc), stage=stage_name, fatal=True)
            report.errors.append(wrapped)
            artifact.errors.append(str(exc))
            return None

    def _record_warning(self, report: PipelineReport, stage_name: str, warning: WarningMessage) -> None:
        report.warnings.append(warning)
        report.artifacts[stage_name].warnings.append(warning)

    def _contract(self, model_name: str, **kwargs: Any) -> Any:
        """Instantiate schema model when available; otherwise preserve named payload."""
        spec = importlib.util.find_spec("html_to_deck.schema.models")
        if spec is None:
            return kwargs
        module = importlib.import_module("html_to_deck.schema.models")
        model = getattr(module, model_name, None)
        if model is None:
            return kwargs
        return model(**kwargs)
