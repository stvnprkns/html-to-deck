"""Pipeline orchestration from ingest through render and write."""

from __future__ import annotations

from dataclasses import dataclass, replace
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

MAX_WORDS_PER_SLIDE = 45
MAX_BULLETS_PER_SLIDE = 6


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

        slides = _build_slides_from_blocks(blocks, storyline.deck_type)
        deck = DeckDocument(slides=slides, deck_type=storyline.deck_type, source_href=source_href)
        layouts = choose_layout_patterns(deck)
        deck_with_layouts = replace(
            deck,
            slides=[replace(slide, layout=layouts.get(index)) for index, slide in enumerate(deck.slides)],
        )
        designed = apply_design_rules(deck_with_layouts, layouts)
        issues = run_quality_checks(designed)
        audited = replace(designed, audit_issues=issues)
        rendered = self.renderer.render(audited)
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


def _build_slides_from_blocks(blocks: list, deck_type: str) -> list[Slide]:
    if not blocks:
        return []

    title = next((block.text for block in blocks if block.kind in {"title", "heading"}), "Generated Slide")
    bullets = [block.text for block in blocks if block.kind in {"paragraph", "bullet", "section_heading"}]

    slides: list[Slide] = [Slide(intent=SlideIntent.TITLE, title=title, bullets=bullets[:1])]
    remaining = bullets[1:]

    for chunk in _chunk_bullets_for_clarity(remaining):
        slides.append(
            Slide(
                intent=SlideIntent.CONTENT,
                title="Key Points",
                bullets=chunk,
            )
        )

    if deck_type in {"report_summary", "case_study", "landing_page_narrative", "article_story"}:
        slides.append(Slide(intent=SlideIntent.SUMMARY, title="Summary", bullets=[f"Deck type: {deck_type}"]))

    return slides


def _chunk_bullets_for_clarity(bullets: list[str]) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    current_words = 0

    for bullet in bullets:
        word_count = len(bullet.split())
        if current and (len(current) >= MAX_BULLETS_PER_SLIDE or current_words + word_count > MAX_WORDS_PER_SLIDE):
            chunks.append(current)
            current = []
            current_words = 0

        current.append(bullet)
        current_words += word_count

    if current:
        chunks.append(current)

    return chunks
