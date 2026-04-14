"""Shared types and stage contracts used across package boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class PipelineInput:
    """Normalized pipeline input from CLI or API caller."""

    source: str | Path
    is_file: bool = True


@dataclass(frozen=True)
class PipelineOutput:
    """Pipeline result metadata."""

    output_path: Path


class SupportsRender(Protocol):
    """Renderer boundary protocol.

    Renderers should only consume canonical schema models.
    """

    def render(self, deck: "DeckDocument") -> str:
        """Return target-specific serialized output."""


# Imported at bottom to avoid circular import at runtime/type checking.
from .schema.models import DeckDocument
