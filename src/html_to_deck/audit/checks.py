"""Audit deck coherence and quality constraints."""

from __future__ import annotations

from ..schema.ir import DeckDocument


def run_quality_checks(deck: DeckDocument) -> list[str]:
    issues: list[str] = []
    if not deck.slides:
        issues.append("Deck has no slides")
    issues.extend(_check_diagram_should_be_code(deck))
    return issues


def _check_diagram_should_be_code(deck: DeckDocument) -> list[str]:
    """Warn when diagram intent is delivered as an image block without exception."""

    issues: list[str] = []
    for index, slide in enumerate(deck.slides, start=1):
        block_type = str(slide.metadata.get("block_type", "")).lower()
        visual_intent = str(slide.metadata.get("visual_intent", "")).lower()
        diagram_source = str(slide.metadata.get("diagram_source", "")).lower()
        has_exception = bool(slide.metadata.get("diagram_exception"))

        is_diagram_intent = visual_intent == "diagram" or bool(slide.metadata.get("diagram_intent"))
        uses_image_like_block = block_type in {"image", "image_with_caption", "figure", "diagram_image", "screenshot"}
        is_code_spec_diagram = diagram_source in {"code_spec", "code-spec", "dsl"}

        if is_diagram_intent and uses_image_like_block and not is_code_spec_diagram and not has_exception:
            issues.append(
                "[high] diagram_should_be_code on "
                f"slide-{index}: Diagram intent uses image-like block without explicit exception."
            )
    return issues
