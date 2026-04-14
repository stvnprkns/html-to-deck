"""Canonical typed models shared across downstream stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SlideIntent(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    SUMMARY = "summary"


@dataclass(frozen=True)
class Slide:
    intent: SlideIntent
    title: str
    bullets: list[str] = field(default_factory=list)
    body: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    layout_hint: str | None = None
    pattern: str | None = None


@dataclass(frozen=True)
class DeckDocument:
    slides: list[Slide]
    deck_type: str
    source_href: str | None = None
