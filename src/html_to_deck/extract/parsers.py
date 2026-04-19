"""Parsing helpers for extraction stage."""

from __future__ import annotations

from html.parser import HTMLParser
import re

from .blocks import ContentBlock


def _attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {k.lower(): (v if v is not None else "") for k, v in attrs}


def _parse_dim(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


class SemanticHtmlParser(HTMLParser):
    """Capture ordered semantic text blocks from HTML."""

    _TEXT_TAGS = {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[ContentBlock] = []
        self._tag_stack: list[str] = []
        self._buffer: list[str] = []
        self._order = -1

    def _append_block(self, block_type: str, text: str, metadata: dict[str, object] | None = None) -> None:
        self._order += 1
        self.blocks.append(
            ContentBlock(
                block_id=f"block-{self._order:04d}",
                block_type=block_type,
                text=text,
                order_index=self._order,
                metadata=dict(metadata or {}),
            )
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered == "img":
            ad = _attrs_dict(attrs)
            src = ad.get("src", "").strip()
            if src:
                alt = ad.get("alt", "").strip()
                self._append_block(
                    "image",
                    alt or "(image)",
                    {
                        "src": src,
                        "alt": alt,
                        "width": _parse_dim(ad.get("width")),
                        "height": _parse_dim(ad.get("height")),
                    },
                )
            return
        self._tag_stack.append(lowered)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "img":
            return

        text = " ".join(part.strip() for part in self._buffer if part.strip()).strip()

        kind_map = {
            "title": "title",
            "h1": "heading",
            "h2": "heading",
            "h3": "heading",
            "h4": "heading",
            "h5": "heading",
            "h6": "heading",
            "p": "paragraph",
            "li": "list_item",
        }

        if lowered in kind_map and text:
            self._append_block(kind_map[lowered], text)

        if lowered in self._TEXT_TAGS:
            self._buffer = []

        if self._tag_stack and self._tag_stack[-1] == lowered:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._tag_stack:
            return
        active = self._tag_stack[-1]
        if active in self._TEXT_TAGS:
            self._buffer.append(data)


_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")
_LIST_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
_ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_IMAGE_LINE_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>.*?)\)$")


def extract_markdown_like(snapshot: str) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    order = -1

    def append(block_type: str, text: str, metadata: dict[str, object] | None = None) -> None:
        nonlocal order
        order += 1
        blocks.append(
            ContentBlock(
                block_id=f"block-{order:04d}",
                block_type=block_type,
                text=text,
                order_index=order,
                metadata=dict(metadata or {}),
            )
        )

    for raw_line in snapshot.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_hit = _HEADING_RE.match(line)
        if heading_hit:
            append("heading", heading_hit.group(1).strip())
            continue

        list_hit = _LIST_RE.match(line) or _ORDERED_LIST_RE.match(line)
        if list_hit:
            append("list_item", list_hit.group(1).strip())
            continue

        image_hit = _IMAGE_LINE_RE.fullmatch(line)
        if image_hit:
            src = image_hit.group("src").strip()
            alt = image_hit.group("alt").strip()
            append(
                "image",
                alt or "(image)",
                {"src": src, "alt": alt, "width": None, "height": None},
            )
            continue

        append("paragraph", line)

    return blocks


def extract_semantic_blocks(snapshot: str) -> list[ContentBlock]:
    text = snapshot.strip()
    if "<" in text and ">" in text:
        parser = SemanticHtmlParser()
        parser.feed(snapshot)
        parser.close()
        if parser.blocks:
            return parser.blocks

    return extract_markdown_like(snapshot)
