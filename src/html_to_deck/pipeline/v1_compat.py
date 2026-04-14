"""Legacy v1 pipeline implementation hosted in canonical ``html_to_deck`` package.

This module preserves the deterministic fixture-oriented behavior used by existing
snapshot tests while the newer orchestrated runtime evolves in parallel.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from typing import Any


@dataclass
class HtmlDocument:
    fixture_id: str
    path: str
    html: str


class _SimpleHtmlExtractor(HTMLParser):
    """Minimal HTML extractor for deterministic fixtures/snapshots."""

    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.in_h2 = False
        self.current_tag: str | None = None

        self.title = ""
        self.h1 = ""
        self.h2s: list[str] = []
        self.paragraphs: list[str] = []
        self.bullets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.current_tag = tag
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "h2":
            self.in_h2 = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "h2":
            self.in_h2 = False
        self.current_tag = None

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self.in_title:
            self.title = text
        elif self.in_h1 and not self.h1:
            self.h1 = text
        elif self.in_h2:
            self.h2s.append(text)
        elif self.current_tag == "p":
            self.paragraphs.append(text)
        elif self.current_tag == "li":
            self.bullets.append(text)


def ingest_html(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    return {
        "stage": "ingest",
        "document": HtmlDocument(
            fixture_id=path.stem,
            path=str(path),
            html=path.read_text(encoding="utf-8"),
        ),
    }


def extract_content(ingested: dict[str, Any]) -> dict[str, Any]:
    doc: HtmlDocument = ingested["document"]
    parser = _SimpleHtmlExtractor()
    parser.feed(doc.html)
    structured = {
        "diagrams": re.findall(r'data-diagram(?:-type)?="([^"]+)"', doc.html, flags=re.IGNORECASE),
        "tables": re.findall(r"<table(?:\\s|>)", doc.html, flags=re.IGNORECASE),
        "stats": re.findall(r'data-stat(?:-value)?="([^"]+)"', doc.html, flags=re.IGNORECASE),
    }

    extracted = {
        "stage": "extract",
        "fixture_id": doc.fixture_id,
        "meta": {
            "title": parser.title,
            "primary_heading": parser.h1,
            "section_headings": parser.h2s,
        },
        "content": {
            "paragraphs": parser.paragraphs,
            "bullets": parser.bullets,
            "structured": structured,
        },
    }
    return extracted


def build_narrative(extracted: dict[str, Any]) -> dict[str, Any]:
    headings = extracted["meta"]["section_headings"]
    beats = []
    for idx, heading in enumerate(headings, start=1):
        beats.append({"id": f"beat-{idx}", "label": heading, "intent": "inform"})

    return {
        "stage": "narrative",
        "fixture_id": extracted["fixture_id"],
        "story": {
            "title": extracted["meta"]["primary_heading"] or extracted["meta"]["title"],
            "summary": extracted["content"]["paragraphs"][0] if extracted["content"]["paragraphs"] else "",
            "beats": beats,
            "structured": extracted["content"].get("structured", {}),
        },
    }


def map_to_slides(narrative: dict[str, Any]) -> dict[str, Any]:
    story = narrative["story"]
    slides = [
        {
            "id": "slide-1",
            "kind": "title",
            "pattern": "hero",
            "title": story["title"],
            "body": story["summary"],
        }
    ]
    index = 2
    structured = story.get("structured", {})
    visual_patterns = (
        ("diagrams", "MERMAID_DIAGRAM", "diagram"),
        ("tables", "TABLE_FROM_DATA", "table"),
        ("stats", "CHART_FROM_SERIES", "stat"),
    )
    for key, pattern, label in visual_patterns:
        entries = structured.get(key, [])
        if entries:
            slides.append(
                {
                    "id": f"slide-{index}",
                    "kind": "content",
                    "pattern": pattern,
                    "title": f"{label.title()} View",
                    "body": f"Code-rendered {label} slide from structured metadata.",
                }
            )
            index += 1

    for beat in story["beats"]:
        slides.append(
            {
                "id": f"slide-{index}",
                "kind": "content",
                "pattern": "two_column_comparison",
                "title": beat["label"],
                "body": f"Narrative intent: {beat['intent']}",
            }
        )
        index += 1

    return {"stage": "mapping", "fixture_id": narrative["fixture_id"], "slides": slides}


def apply_layout(mapping: dict[str, Any]) -> dict[str, Any]:
    out = []
    for slide in mapping["slides"]:
        pattern = slide.get("pattern")
        if pattern == "MERMAID_DIAGRAM":
            layout = "code-mermaid"
        elif pattern == "TABLE_FROM_DATA":
            layout = "code-table"
        elif pattern == "CHART_FROM_SERIES":
            layout = "code-chart"
        else:
            layout = "hero" if slide["kind"] == "title" else "two-column"
        out.append({**slide, "layout": layout})
    return {"stage": "layout", "fixture_id": mapping["fixture_id"], "slides": out}


def apply_design(layouted: dict[str, Any]) -> dict[str, Any]:
    themed = [{**slide, "theme": "v1-light"} for slide in layouted["slides"]]
    return {"stage": "design", "fixture_id": layouted["fixture_id"], "slides": themed}


def audit_deck(designed: dict[str, Any]) -> dict[str, Any]:
    issues = []
    for slide in designed["slides"]:
        if len(slide.get("title", "")) > 90:
            issues.append({"slide_id": slide["id"], "severity": "warning", "rule": "title-length"})
        if not slide.get("body"):
            issues.append({"slide_id": slide["id"], "severity": "warning", "rule": "empty-body"})
        metadata = slide.get("body_metadata", {})
        block_type = str(metadata.get("block_type", "")).lower()
        visual_intent = str(metadata.get("visual_intent", "")).lower()
        diagram_source = str(metadata.get("diagram_source", "")).lower()
        is_diagram_intent = visual_intent == "diagram" or bool(metadata.get("diagram_intent"))
        uses_image_like_block = block_type in {
            "image",
            "image_with_caption",
            "figure",
            "diagram_image",
            "screenshot",
        }
        has_explicit_exception = bool(metadata.get("diagram_exception"))
        is_code_spec_diagram = diagram_source in {"code_spec", "code-spec", "dsl"}
        if is_diagram_intent and uses_image_like_block and not has_explicit_exception and not is_code_spec_diagram:
            issues.append(
                {
                    "slide_id": slide["id"],
                    "severity": "error",
                    "rule": "diagram_should_be_code",
                    "message": (
                        "Diagram intent should use a code spec; set body_metadata.diagram_exception=true "
                        "for explicit waivers."
                    ),
                }
            )

    return {
        "stage": "audit",
        "fixture_id": designed["fixture_id"],
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }


def render_json(designed: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "deck_version": "v1",
        "fixture_id": designed["fixture_id"],
        "slides": designed["slides"],
        "audit": audit,
    }


def run_pipeline(path: str | Path) -> dict[str, Any]:
    ingested = ingest_html(path)
    extracted = extract_content(ingested)
    narrative = build_narrative(extracted)
    mapped = map_to_slides(narrative)
    layouted = apply_layout(mapped)
    designed = apply_design(layouted)
    audit = audit_deck(designed)
    rendered = render_json(designed, audit)

    return {
        "canonical_ir": {
            "extracted": extracted,
            "narrative": narrative,
            "mapping": mapped,
            "layout": layouted,
            "design": designed,
        },
        "audit": audit,
        "deck_json": rendered,
    }


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


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
