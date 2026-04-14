"""Canonical deck specification models.

These dataclasses represent the canonical in-memory deck structure used as
input to renderer targets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class SlideSpec:
    """A canonical slide specification."""

    id: str
    title: str
    blocks: list[dict[str, Any]] = field(default_factory=list)
    notes: str | None = None


@dataclass(slots=True)
class DeckSpec:
    """A canonical deck specification."""

    version: str
    title: str
    slides: list[SlideSpec] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-Python representation for serialization."""
        return asdict(self)
