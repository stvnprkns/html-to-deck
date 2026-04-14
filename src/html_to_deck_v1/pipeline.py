"""Compatibility shim for legacy ``html_to_deck_v1`` imports.

Authoritative stage logic now lives under ``html_to_deck.pipeline.v1_compat``.
"""

from html_to_deck.pipeline.v1_compat import (
    HtmlDocument,
    apply_design,
    apply_layout,
    audit_deck,
    build_narrative,
    extract_content,
    ingest_html,
    map_to_slides,
    render_json,
    run_pipeline,
    stable_json,
)

__all__ = [
    "HtmlDocument",
    "ingest_html",
    "extract_content",
    "build_narrative",
    "map_to_slides",
    "apply_layout",
    "apply_design",
    "audit_deck",
    "render_json",
    "run_pipeline",
    "stable_json",
]
