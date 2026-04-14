"""Typed schema models for html-to-deck stage handoffs."""

from .models import (
    AuditReport,
    ContentBlock,
    DeckSpec,
    DeckType,
    LayoutPattern,
    NarrativeArc,
    ProvenanceRef,
    QualityMetadata,
    SlideIntent,
    SlidePattern,
    SlideSpec,
    SourceDocument,
    WarningFlag,
    to_json,
    to_ordered_dict,
)

__all__ = [
    "AuditReport",
    "ContentBlock",
    "DeckSpec",
    "DeckType",
    "LayoutPattern",
    "NarrativeArc",
    "ProvenanceRef",
    "QualityMetadata",
    "SlideIntent",
    "SlidePattern",
    "SlideSpec",
    "SourceDocument",
    "WarningFlag",
    "to_json",
    "to_ordered_dict",
]
