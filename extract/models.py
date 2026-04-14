from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceBlock:
    """A normalized semantic block extracted from source content."""

    block_type: str
    text: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
