"""Explicit stage transformations used by the orchestrator."""

from __future__ import annotations

from ..extract.blocks import ContentBlock
from ..narrative.inference import Storyline
from ..schema.ir import DeckDocument, Slide, SlideImage, SlideIntent

SectionItem = str | SlideImage


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

    for idx, (section_title, items) in enumerate(sections, start=1):
        bullets = [x for x in items if isinstance(x, str)]
        figures = tuple(x for x in items if isinstance(x, SlideImage))
        if not bullets and not figures:
            continue
        slides.append(
            Slide(
                intent=SlideIntent.CONTENT,
                title=section_title or f"Section {idx}",
                bullets=bullets,
                figures=figures,
                metadata={"stage": "map", "section": section_title or f"Section {idx}"},
            )
        )

    if len(slides) > 2:
        summary_points = _unique_points(
            [bullet for slide in slides[1:] for bullet in slide.bullets],
            limit=3,
        )
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
            Slide(
                intent=slide.intent,
                title=slide.title,
                bullets=slide.bullets,
                figures=slide.figures,
                metadata=metadata,
            )
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
        if block.block_type in {"title", "heading"} and block.text:
            return block.text
    return "Untitled Deck"


def _group_sections(blocks: list[ContentBlock]) -> list[tuple[str, list[SectionItem]]]:
    """Preserve in-section order of paragraphs and images."""

    section_order: list[str] = []
    content: dict[str, list[SectionItem]] = {}
    current_section = "Overview"

    def touch(name: str) -> None:
        if name not in content:
            content[name] = []
            section_order.append(name)

    touch(current_section)

    for block in blocks:
        bt = block.block_type
        if bt == "title":
            continue
        if bt == "heading":
            current_section = block.text
            touch(current_section)
            continue
        if bt == "image":
            src = str(block.metadata.get("src", "")).strip()
            if not src:
                continue
            w = block.metadata.get("width")
            h = block.metadata.get("height")
            fig = SlideImage(
                src=src,
                alt=str(block.metadata.get("alt", "")),
                width=w if isinstance(w, int) else None,
                height=h if isinstance(h, int) else None,
            )
            touch(current_section)
            content[current_section].append(fig)
            continue

        text = block.text.strip()
        if not text:
            continue
        touch(current_section)
        content[current_section].append(text)

    return [(name, content[name]) for name in section_order if content[name]]


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
