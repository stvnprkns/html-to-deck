from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from .models import SourceBlock


@dataclass(frozen=True)
class ExtractorRule:
    block_type: str
    pattern: re.Pattern[str]
    confidence: float


EXTRACTOR_RULES: tuple[ExtractorRule, ...] = (
    ExtractorRule("heading", re.compile(r"^(#{1,6})\s+(.+)$"), 0.98),
    ExtractorRule("quote", re.compile(r"^>\s+(.+)$"), 0.95),
    ExtractorRule("unordered_list", re.compile(r"^\s*[-*+]\s+(.+)$"), 0.92),
    ExtractorRule("ordered_list", re.compile(r"^\s*\d+[.)]\s+(.+)$"), 0.92),
    ExtractorRule("image", re.compile(r"!\[(.*?)\]\((.*?)\)"), 0.96),
    ExtractorRule("key_stat", re.compile(r"^(.*?)(\d[\d,.]*\s?[%$xX]?)\s*$"), 0.75),
)

TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")


def _normalize_source(source: str | dict) -> list[str]:
    if isinstance(source, str):
        return [line.rstrip() for line in source.splitlines()]
    if isinstance(source, dict):
        text = source.get("text", "")
        if isinstance(text, str):
            return [line.rstrip() for line in text.splitlines()]
    raise TypeError("source must be str or dict with a text field")


def _extract_table_block(lines: list[str], index: int) -> tuple[SourceBlock | None, int]:
    if index + 1 >= len(lines):
        return None, index
    first, second = lines[index], lines[index + 1]
    if not TABLE_ROW_RE.match(first) or not re.match(r"^\|?\s*[-:]+", second):
        return None, index

    rows = [first]
    j = index + 2
    while j < len(lines) and TABLE_ROW_RE.match(lines[j]):
        rows.append(lines[j])
        j += 1

    parsed_rows = []
    for row in rows:
        parsed_rows.append([cell.strip() for cell in row.strip("|").split("|")])

    block = SourceBlock(
        block_type="table",
        text="\n".join(rows),
        confidence=0.94,
        metadata={"rows": parsed_rows, "columns": len(parsed_rows[0]) if parsed_rows else 0},
    )
    return block, j - 1


def extract_blocks(source: str | dict) -> list[SourceBlock]:
    """Extract semantic blocks from source markdown-like content."""

    lines = _normalize_source(source)
    blocks: list[SourceBlock] = []
    paragraph_buffer: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_buffer:
            return
        text = " ".join(segment.strip() for segment in paragraph_buffer).strip()
        if text:
            blocks.append(SourceBlock(block_type="paragraph", text=text, confidence=0.9))
        paragraph_buffer.clear()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            flush_paragraph()
            i += 1
            continue

        table_block, table_end = _extract_table_block(lines, i)
        if table_block:
            flush_paragraph()
            blocks.append(table_block)
            i = table_end + 1
            continue

        matched = False
        for rule in EXTRACTOR_RULES:
            hit = rule.pattern.match(line)
            if not hit:
                continue

            flush_paragraph()
            metadata: dict[str, str | int] = {}
            text = line

            if rule.block_type == "heading":
                metadata["level"] = len(hit.group(1))
                text = hit.group(2)
            elif rule.block_type in {"unordered_list", "ordered_list", "quote"}:
                text = hit.group(1)
            elif rule.block_type == "image":
                text = hit.group(1) or "Image"
                metadata["src"] = hit.group(2)
            elif rule.block_type == "key_stat":
                metric_name, metric_value = hit.group(1).strip(), hit.group(2).strip()
                if metric_name and any(token in metric_name.lower() for token in ("growth", "revenue", "users", "cost", "margin", "rate")):
                    metadata["metric"] = metric_name
                    metadata["value"] = metric_value
                else:
                    paragraph_buffer.append(line)
                    matched = True
                    break

            blocks.append(
                SourceBlock(
                    block_type="list" if "list" in rule.block_type else rule.block_type,
                    text=text,
                    confidence=rule.confidence,
                    metadata=metadata,
                )
            )
            matched = True
            break

        if not matched:
            paragraph_buffer.append(line)

        i += 1

    flush_paragraph()
    return _merge_contiguous_lists(blocks)


def _merge_contiguous_lists(blocks: Iterable[SourceBlock]) -> list[SourceBlock]:
    merged: list[SourceBlock] = []
    list_items: list[str] = []

    for block in blocks:
        if block.block_type == "list":
            list_items.append(block.text)
            continue

        if list_items:
            merged.append(
                SourceBlock(
                    block_type="list",
                    text="\n".join(list_items),
                    confidence=0.93,
                    metadata={"items": list_items.copy(), "count": len(list_items)},
                )
            )
            list_items.clear()

        merged.append(block)

    if list_items:
        merged.append(
            SourceBlock(
                block_type="list",
                text="\n".join(list_items),
                confidence=0.93,
                metadata={"items": list_items.copy(), "count": len(list_items)},
            )
        )

    return merged
