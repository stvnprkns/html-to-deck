"""Extract headings, paragraphs, lists, stats, quotes, images, and tables."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class ContentBlock:
    kind: str
    text: str


class _SemanticHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[ContentBlock] = []
        self._tag_stack: list[str] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag.lower())
        if tag.lower() == "li":
            self._buffer = []

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

        if lowered in {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}:
            self._buffer = []

        if self._tag_stack and self._tag_stack[-1] == lowered:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._tag_stack:
            return
        active = self._tag_stack[-1]
        if active in {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}:
            self._buffer.append(data)


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Extract semantic blocks from an HTML snapshot."""
    if not snapshot:
        return []

    parser = _SemanticHtmlParser()
    parser.feed(snapshot)
    parser.close()
    return parser.blocks
