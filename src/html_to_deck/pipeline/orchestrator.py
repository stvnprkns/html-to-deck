"""Pipeline orchestration from ingest through render and write."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..audit import run_quality_checks
from ..design import apply_design_rules
from ..extract import extract_blocks
from ..ingest import load_html, normalize_snapshot
from ..io import write_output
from ..layout import choose_layout_patterns
from ..narrative import infer_storyline
from ..renderers import HtmlDeckRenderer, JsonDeckRenderer
from ..schema.ir import DeckDocument, Slide, SlideIntent
from ..types import PipelineInput, PipelineOutput, SupportsRender


@dataclass
class HtmlToDeckPipeline:
    renderer: SupportsRender

    @classmethod
    def default(cls) -> "HtmlToDeckPipeline":
        return cls(renderer=JsonDeckRenderer())

    @classmethod
    def from_output_path(cls, output_path: Path) -> "HtmlToDeckPipeline":
        if output_path.suffix.lower() in {".html", ".htm"}:
            return cls(renderer=HtmlDeckRenderer())
        return cls(renderer=JsonDeckRenderer())

    def run(self, pipeline_input: PipelineInput, output_path: Path) -> PipelineOutput:
        html = load_html(pipeline_input.source, is_file=pipeline_input.is_file)
        source_href = self._resolve_source_href(pipeline_input)
        snapshot = normalize_snapshot(html)
        blocks = extract_blocks(snapshot)
        storyline = infer_storyline(blocks)

        slides = [
            Slide(
                intent=SlideIntent.CONTENT,
                title="Generated Slide",
                bullets=[block.text for block in blocks],
            )
        ] if blocks else []

        deck = DeckDocument(slides=slides, deck_type=storyline.deck_type, source_href=source_href)
        layouts = choose_layout_patterns(deck)
        designed = apply_design_rules(deck, layouts)
        audit_report = run_quality_checks(designed)
        rendered = self.renderer.render(designed, audit_report=audit_report)
        final_path = write_output(rendered, output_path)
        return PipelineOutput(output_path=final_path, audit_report=audit_report)

    @staticmethod
    def _resolve_source_href(pipeline_input: PipelineInput) -> str | None:
        if pipeline_input.is_file:
            return Path(pipeline_input.source).resolve().as_uri()
        source = str(pipeline_input.source).strip()
        if source.startswith(("http://", "https://")):
            return source
        return None
