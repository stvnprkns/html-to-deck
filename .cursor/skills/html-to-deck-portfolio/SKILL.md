---
name: html-to-deck-portfolio
description: Generate portfolio-ready slide decks from HTML using html-to-deck (themes, design tokens, embed layout).
---

# html-to-deck portfolio skill

Use this when the user wants a **slide deck** from their **HTML content** for a personal site or case study.

## Install and run

- Prefer `pip install .` from the repo root (or an installed wheel), then run `html-to-deck` (console script) or `python -m html_to_deck.cli`.
- Do not rely on `PYTHONPATH=src` once the package is installed.

Typical command for a public portfolio page:

```bash
html-to-deck --input case-study.html --output public/deck.html \
  --theme portfolio --layout embed \
  --tokens-css ./deck-tokens.css \
  --no-audit-badge --no-source-link \
  --audit-output none
```

## Source HTML

Follow `docs/authoring-decks.md`: one `<h1>`, section `<h2>`s, focused `<p>` and `<ul><li>`, meaningful `<img alt>` for figures.

## Design tokens

- Read `docs/design-tokens.md` for the `--deck-*` contract and site aliases (`--primary`, `--background`, etc.).
- Put site-specific mappings in a small file and pass `--tokens-css` so it loads **before** the theme.
- Use `--extra-css` only for last-mile overrides after the theme.

## Python API

For generators or static site scripts:

```python
from html_to_deck import convert

convert(
    "source.html",
    "out/deck.html",
    theme="portfolio",
    layout="embed",
    tokens_css=Path("deck-tokens.css").read_text(encoding="utf-8"),
    show_audit_badge=False,
    show_source_link=False,
)
```

## Quality checks

- Run `pytest` after pipeline or renderer changes.
- Use CLI audit output (`summary` or `json`) while authoring; hide the badge in production HTML with `--no-audit-badge`.

## URL ingestion

Fetching remote HTML requires `HTML_TO_DECK_ENABLE_URL_INGEST=1` (see `src/html_to_deck/ingest/loader.py`). Default file-based flows do not need this.
