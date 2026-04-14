from __future__ import annotations

from extract.models import SourceBlock
from pipeline.map_to_slides import map_to_slide_intents

from .infer import infer_deck_narrative
from .models import SlideIntent


def infer_slide_intents(blocks: list[SourceBlock]) -> list[SlideIntent]:
    """Infer deck narrative and map content into slide intents."""

    narrative = infer_deck_narrative(blocks)
    return map_to_slide_intents(blocks, narrative)
