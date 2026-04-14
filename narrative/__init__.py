"""Narrative inference package."""

from .infer import infer_deck_narrative
from .models import DeckNarrative, SlideIntent

__all__ = ["infer_deck_narrative", "DeckNarrative", "SlideIntent"]
