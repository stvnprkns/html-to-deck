from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SlideIntent:
    communication_job: str
    section: str
    supporting_block_ids: list[int]
    overload_score: float = 0.0


@dataclass(frozen=True)
class DeckNarrative:
    deck_type: str
    confidence: float
    sections: list[str]
    intents: list[SlideIntent] = field(default_factory=list)
