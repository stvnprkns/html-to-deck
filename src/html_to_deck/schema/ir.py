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
class SlideImage:
    """Raster figure extracted from source HTML (standalone deck viewer)."""

    src: str
    alt: str = ""
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class Slide:
    intent: SlideIntent
    title: str
    bullets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    figures: tuple[SlideImage, ...] = ()


@dataclass(frozen=True)
class DeckDocument:
    slides: list[Slide]
    deck_type: str
    source_href: str | None = None
    layouts: dict[int, str] = field(default_factory=dict)
    audit_issues: list[str] = field(default_factory=list)
