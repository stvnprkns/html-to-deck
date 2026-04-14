"""Extract semantic blocks from HTML snapshots or markdown-like content."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re


@dataclass(frozen=True)
class ContentBlock:
    kind: str
    text: str


class _SemanticHtmlParser(HTMLParser):
    """Capture ordered semantic text blocks from HTML."""

    _SUPPORTED_TAGS = {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[ContentBlock] = []
        self._tag_stack: list[str] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        self._tag_stack.append(tag.lower())

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
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
            self.blocks.append(ContentBlock(kind=kind_map[lowered], text=text))

        if lowered in self._SUPPORTED_TAGS:
            self._buffer = []

        if self._tag_stack and self._tag_stack[-1] == lowered:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._tag_stack:
            return
        active = self._tag_stack[-1]
        if active in self._SUPPORTED_TAGS:
            self._buffer.append(data)


_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")
_LIST_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
_ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_IMAGE_LINE_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>.*?)\)$")


def _extract_markdown_like(snapshot: str) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    for raw_line in snapshot.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_hit = _HEADING_RE.match(line)
        if heading_hit:
            blocks.append(ContentBlock(kind="heading", text=heading_hit.group(1).strip()))
            continue

        list_hit = _LIST_RE.match(line) or _ORDERED_LIST_RE.match(line)
        if list_hit:
            blocks.append(ContentBlock(kind="list_item", text=list_hit.group(1).strip()))
            continue

        image_hit = _IMAGE_LINE_RE.fullmatch(line)
        if image_hit:
            blocks.append(ContentBlock(kind="warning", text=f"External image ignored: {image_hit.group('src')}"))
            continue

        blocks.append(ContentBlock(kind="paragraph", text=line))

    return blocks


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Extract semantic blocks from an HTML snapshot or markdown-like fallback."""

    if not snapshot:
        return []

    text = snapshot.strip()
    if "<" in text and ">" in text:
        parser = _SemanticHtmlParser()
        parser.feed(snapshot)
        parser.close()
        if parser.blocks:
            return parser.blocks

    return _extract_markdown_like(snapshot)
