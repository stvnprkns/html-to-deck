"""Explicit stage transformations used by the orchestrator."""

from __future__ import annotations

from collections import defaultdict

from ..extract.blocks import ContentBlock
from ..narrative.inference import Storyline
from ..schema.ir import DeckDocument, Slide, SlideIntent


def map_to_slides(blocks: list[ContentBlock], storyline: Storyline, source_href: str | None) -> DeckDocument:
    """Map extracted blocks + storyline into explicit, intent-driven slides."""

    if not blocks:
        return DeckDocument(slides=[], deck_type=storyline.deck_type, source_href=source_href)

    title = _resolve_title(blocks)
    sections = _group_sections(blocks)

    slides: list[Slide] = [
        Slide(
            intent=SlideIntent.TITLE,
            title=title,
            bullets=[storyline.narrative_arc],
            metadata={"stage": "map", "section": "cover"},
        )
    ]

    for idx, (section_title, lines) in enumerate(sections, start=1):
        bullets = [line for line in lines if line]
        if not bullets:
            continue
        slides.append(
            Slide(
                intent=SlideIntent.CONTENT,
                title=section_title or f"Section {idx}",
                bullets=bullets,
                metadata={"stage": "map", "section": section_title or f"Section {idx}"},
            )
        )

    if len(slides) > 2:
        summary_points = _unique_points([bullet for slide in slides[1:] for bullet in slide.bullets], limit=3)
        slides.append(
            Slide(
                intent=SlideIntent.SUMMARY,
                title="Summary",
                bullets=summary_points,
                metadata={"stage": "map", "section": "summary"},
            )
        )

    return DeckDocument(slides=slides, deck_type=storyline.deck_type, source_href=source_href)


def layout_stage(deck: DeckDocument, layouts: dict[int, str]) -> DeckDocument:
    """Persist layout decisions into the canonical deck model."""

    return DeckDocument(
        slides=deck.slides,
        deck_type=deck.deck_type,
        source_href=deck.source_href,
        layouts=layouts,
        audit_issues=deck.audit_issues,
    )


def design_stage(deck: DeckDocument) -> DeckDocument:
    """Apply layout-aware design metadata onto each slide."""

    themed_slides: list[Slide] = []
    for index, slide in enumerate(deck.slides):
        layout = deck.layouts.get(index, slide.intent.value)
        metadata = dict(slide.metadata)
        metadata.update(
            {
                "layout": layout,
                "theme": "v2-dark",
                "stage": "design",
            }
        )
        themed_slides.append(
            Slide(intent=slide.intent, title=slide.title, bullets=slide.bullets, metadata=metadata)
        )

    return DeckDocument(
        slides=themed_slides,
        deck_type=deck.deck_type,
        source_href=deck.source_href,
        layouts=deck.layouts,
        audit_issues=deck.audit_issues,
    )


def _resolve_title(blocks: list[ContentBlock]) -> str:
    for block in blocks:
        if block.kind in {"title", "heading"} and block.text:
            return block.text
    return "Untitled Deck"


def _group_sections(blocks: list[ContentBlock]) -> list[tuple[str, list[str]]]:
    sections: dict[str, list[str]] = defaultdict(list)
    current_section = "Overview"

    for block in blocks:
        if block.kind == "title":
            continue
        if block.kind == "heading":
            current_section = block.text
            continue
        sections[current_section].append(block.text)

    return [(name, lines) for name, lines in sections.items() if lines]


def _unique_points(points: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for point in points:
        normalized = point.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
        if len(ordered) >= limit:
            break
    return ordered
