"""Canonical typed models shared across downstream stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SlideIntent(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    SUMMARY = "summary"


@dataclass(frozen=True)
class Slide:
    intent: SlideIntent
    title: str
    bullets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DeckDocument:
    slides: list[Slide]
    deck_type: str
