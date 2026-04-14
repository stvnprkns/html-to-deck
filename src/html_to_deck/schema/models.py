from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import StrEnum
import json
from typing import Any


class DeckType(StrEnum):
    """Supported presentation narrative families."""

    REPORT_SUMMARY = "report_summary"
    ARTICLE_STORY = "article_story"
    CASE_STUDY = "case_study"
    LANDING_PAGE_NARRATIVE = "landing_page_narrative"


class SlidePattern(StrEnum):
    """Supported slide-level pattern catalog."""

    HERO = "hero"
    SECTION_DIVIDER = "section_divider"
    STAT = "stat"
    QUOTE = "quote"
    TWO_COLUMN_COMPARISON = "two_column_comparison"
    CHART_WITH_TAKEAWAY = "chart_with_takeaway"
    IMAGE_WITH_CAPTION = "image_with_caption"
    TIMELINE = "timeline"
    CARDS_GRID = "cards_grid"
    CLOSING = "closing"


@dataclass(slots=True, frozen=True)
class ProvenanceRef:
    """Reference from generated artifacts back to source content blocks."""

    source_document_id: str
    source_block_id: str
    quote: str | None = None


@dataclass(slots=True, frozen=True)
class QualityMetadata:
    """Reusable quality and warning metadata attached to all stage handoffs."""

    confidence: float = 1.0
    warnings: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class ContentBlock:
    """Normalized source block extracted from input material."""

    block_id: str
    block_type: str
    text: str
    order_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class SourceDocument:
    """Source material for deck generation."""

    document_id: str
    title: str
    deck_type: DeckType
    blocks: tuple[ContentBlock, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class NarrativeArc:
    """Structured story arc derived from source material."""

    arc_id: str
    title: str
    thesis: str
    key_points: tuple[str, ...]
    source_refs: tuple[ProvenanceRef, ...]
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class SlideIntent:
    """High-level intent for an upcoming slide."""

    intent_id: str
    arc_id: str
    sequence_index: int
    objective: str
    pattern: SlidePattern
    source_refs: tuple[ProvenanceRef, ...]
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class WarningFlag:
    """Warning emitted while building the deck spec."""

    warning_id: str
    code: str
    message: str
    severity: str
    source_refs: tuple[ProvenanceRef, ...] = ()


@dataclass(slots=True, frozen=True)
class AuditReport:
    """Audit and quality report for the deck output."""

    audit_id: str
    summary: str
    score: float
    warnings: tuple[WarningFlag, ...] = ()
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class LayoutPattern:
    """Resolved layout details for a slide pattern."""

    layout_id: str
    pattern: SlidePattern
    slots: tuple[str, ...]
    guidance: str
    source_refs: tuple[ProvenanceRef, ...] = ()
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class SlideSpec:
    """Final instruction set for one slide."""

    slide_id: str
    sequence_index: int
    title: str
    intent_id: str
    pattern: SlidePattern
    layout: LayoutPattern
    body: tuple[str, ...]
    source_refs: tuple[ProvenanceRef, ...]
    quality: QualityMetadata = field(default_factory=QualityMetadata)


@dataclass(slots=True, frozen=True)
class DeckSpec:
    """Final deck output specification."""

    deck_id: str
    title: str
    deck_type: DeckType
    slides: tuple[SlideSpec, ...]
    source_document_id: str
    source_refs: tuple[ProvenanceRef, ...]
    audit: AuditReport
    quality: QualityMetadata = field(default_factory=QualityMetadata)


def _normalize_for_json(value: Any) -> Any:
    """Recursively normalize schemas into deterministic JSON-safe types."""

    if isinstance(value, StrEnum):
        return value.value

    if is_dataclass(value):
        return _normalize_for_json(asdict(value))

    if isinstance(value, dict):
        return {k: _normalize_for_json(value[k]) for k in sorted(value)}

    if isinstance(value, (list, tuple)):
        normalized = [_normalize_for_json(item) for item in value]
        if normalized and all(isinstance(item, dict) for item in normalized):
            id_keys = [next((k for k in item if k.endswith("_id")), None) for item in normalized]
            if all(id_keys):
                return sorted(
                    normalized,
                    key=lambda item: tuple(str(item[k]) for k in sorted(k for k in item if k.endswith("_id"))),
                )
        return normalized

    return value


def to_ordered_dict(model: Any) -> dict[str, Any]:
    """Convert a model to a deterministic dictionary for snapshot testing."""

    normalized = _normalize_for_json(model)
    if not isinstance(normalized, dict):
        raise TypeError("to_ordered_dict expects a dataclass model producing a mapping")
    return normalized


def to_json(model: Any, *, indent: int = 2) -> str:
    """Serialize schema models with deterministic key ordering."""

    return json.dumps(to_ordered_dict(model), indent=indent, sort_keys=True, ensure_ascii=False)
