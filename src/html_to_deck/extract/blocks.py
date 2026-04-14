"""Extraction stage public API."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from ..schema.models import ContentBlock as SchemaContentBlock

ContentBlock = SchemaContentBlock

TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
TABLE_DIVIDER_CELL_RE = re.compile(r"^:?-{3,}:?$")
FENCED_BLOCK_START_RE = re.compile(r"^```(?P<language>[a-zA-Z0-9_-]+)?\s*$")
IMAGE_LINE_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>.*?)\)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
UNORDERED_LIST_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")

DIAGRAM_LANGUAGES = {"mermaid", "graphviz", "dot", "plantuml", "pikchr"}
DIAGRAM_PREFIXES = ("graph ", "flowchart ", "sequencediagram", "classdiagram", "statediagram")

CONFIDENCE_BY_TYPE: dict[str, float] = {
    "heading": 0.98,
    "paragraph": 0.90,
    "list": 0.93,
    "table": 0.94,
    "diagram_spec": 0.97,
    "warning": 0.91,
}


@dataclass(slots=True)
class _PendingBlock:
    block_type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.9


def _build_block(block_type: str, text: str, order_index: int, *, metadata: dict[str, Any] | None = None) -> ContentBlock:
    final_metadata = dict(metadata or {})
    final_metadata["confidence_score"] = CONFIDENCE_BY_TYPE[block_type]
    return ContentBlock(
        block_id=f"block-{order_index:04d}",
        block_type=block_type,
        text=text,
        order_index=order_index,
        metadata=final_metadata,
    )


def _extract_table_block(lines: list[str], index: int) -> tuple[_PendingBlock | None, int]:
    if index + 1 >= len(lines):
        return None, index

    first, second = lines[index], lines[index + 1]
    if not TABLE_ROW_RE.match(first):
        return None, index

    divider_cells = [cell.strip() for cell in second.strip("|").split("|")]
    if not divider_cells or not all(TABLE_DIVIDER_CELL_RE.match(cell) for cell in divider_cells):
        return None, index

    rows = [first]
    j = index + 2
    while j < len(lines) and TABLE_ROW_RE.match(lines[j]):
        rows.append(lines[j])
        j += 1

    if not rows:
        return None, index

    parsed_rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    column_count = len(parsed_rows[0]) if parsed_rows else 0
    if column_count == 0 or any(len(row) != column_count for row in parsed_rows):
        return None, index

    return (
        _PendingBlock(
            block_type="table",
            text="\n".join(rows),
            metadata={"rows": parsed_rows, "columns": column_count},
            confidence=CONFIDENCE_BY_TYPE["table"],
        ),
        j - 1,
    )


def _extract_fenced_diagram_block(lines: list[str], index: int) -> tuple[_PendingBlock | None, int]:
    match = FENCED_BLOCK_START_RE.match(lines[index].strip())
    if not match:
        return None, index

    language = (match.group("language") or "").lower()
    content: list[str] = []
    j = index + 1
    while j < len(lines):
        if lines[j].strip() == "```":
            break
        content.append(lines[j])
        j += 1

    if j >= len(lines) or lines[j].strip() != "```":
        return None, index

    normalized = "\n".join(content).strip()
    leading = normalized.lower()
    is_diagram = language in DIAGRAM_LANGUAGES or leading.startswith(DIAGRAM_PREFIXES)
    if not is_diagram:
        return None, index

    return (
        _PendingBlock(
            block_type="diagram_spec",
            text=normalized,
            metadata={"diagram_language": language or "unknown", "source_format": "fenced_code"},
            confidence=CONFIDENCE_BY_TYPE["diagram_spec"],
        ),
        j,
    )


def _merge_contiguous_lists(blocks: list[_PendingBlock]) -> list[_PendingBlock]:
    merged: list[_PendingBlock] = []
    run_items: list[str] = []

    def flush() -> None:
        if not run_items:
            return
        merged.append(
            _PendingBlock(
                block_type="list",
                text="\n".join(run_items),
                metadata={"items": run_items.copy(), "count": len(run_items)},
                confidence=CONFIDENCE_BY_TYPE["list"],
            )
        )
        run_items.clear()

    for block in blocks:
        if block.block_type == "list":
            run_items.append(block.text)
            continue
        flush()
        merged.append(block)

    flush()
    return merged


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Extract semantic blocks from HTML or markdown-like snapshots."""

    if not snapshot:
        return []

    from .parsers import extract_semantic_blocks

    return extract_semantic_blocks(snapshot)
