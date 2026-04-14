"""Architectural tests enforcing renderer dependency boundaries."""

from __future__ import annotations

import ast
from pathlib import Path


RENDERERS_DIR = Path(__file__).resolve().parents[1] / "src" / "html_to_deck" / "renderers"
FORBIDDEN_IMPORT_SUBSTRINGS = (
    "html_to_deck.extract",
    "html_to_deck.narrative",
    "..extract",
    "..narrative",
)


def test_renderers_do_not_import_extract_or_narrative() -> None:
    for py_file in RENDERERS_DIR.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert FORBIDDEN_IMPORT_SUBSTRINGS[0] not in alias.name
                    assert FORBIDDEN_IMPORT_SUBSTRINGS[1] not in alias.name
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level:
                    module = "." * node.level + module
                assert FORBIDDEN_IMPORT_SUBSTRINGS[0] not in module
                assert FORBIDDEN_IMPORT_SUBSTRINGS[1] not in module
                assert FORBIDDEN_IMPORT_SUBSTRINGS[2] not in module
                assert FORBIDDEN_IMPORT_SUBSTRINGS[3] not in module
