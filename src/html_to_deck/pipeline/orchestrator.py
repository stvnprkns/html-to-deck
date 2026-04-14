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
from ..schema.ir import DeckDocument
from ..types import PipelineInput, PipelineOutput, SupportsRender
from .stages import layout_stage, map_to_slides


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

        mapped_deck = map_to_slides(blocks, storyline, source_href=source_href)
        layouts = choose_layout_patterns(mapped_deck)
        layouted_deck = layout_stage(mapped_deck, layouts)
        designed_deck = apply_design_rules(layouted_deck, layouted_deck.layouts)

        issues = run_quality_checks(designed_deck)
        audited_deck = DeckDocument(
            slides=designed_deck.slides,
            deck_type=designed_deck.deck_type,
            source_href=designed_deck.source_href,
            layouts=designed_deck.layouts,
            audit_issues=issues,
        )

        rendered = self.renderer.render(audited_deck)
        final_path = write_output(rendered, output_path)
        return PipelineOutput(output_path=final_path)

    @staticmethod
    def _resolve_source_href(pipeline_input: PipelineInput) -> str | None:
        if pipeline_input.is_file:
            return Path(pipeline_input.source).resolve().as_uri()
        source = str(pipeline_input.source).strip()
        if source.startswith(("http://", "https://")):
            return source
        return None
