# html-to-deck v1

This repository provides a deterministic **v1 HTML → deck JSON** reference pipeline, fixtures, and snapshot-driven test coverage. It also ships a **standalone HTML slide viewer** suitable for portfolio sites.

## Install

From the repository root (Python 3.11+):

```bash
pip install .
```

This installs the `html_to_deck` package and the **`html-to-deck`** command-line tool (ensure your user script directory is on `PATH`, or invoke `python3 -m html_to_deck.cli`).

## Portfolio quickstart

1. Structure your source HTML as described in **[docs/authoring-decks.md](docs/authoring-decks.md)** (one `<h1>`, section `<h2>`s, focused paragraphs and lists, `<img>` for figures).
2. Map your site’s design tokens (optional): see **[docs/design-tokens.md](docs/design-tokens.md)** for the `--deck-*` contract and built-in aliases such as `--primary` / `--background`.
3. Generate a deck for embedding in a page or static host:

```bash
html-to-deck --input case-study.html --output public/deck.html \
  --theme portfolio --layout embed \
  --tokens-css ./deck-tokens.css \
  --no-audit-badge --no-source-link \
  --audit-output none
```

- **`--layout embed`** — centered `max-width`, `min-height` instead of locking the shell to `100vh` (better inside an article layout).
- **`--tokens-css`** — CSS injected **before** the theme (map site variables to `--deck-*`).
- **`--extra-css`** — overrides injected **after** the theme.
- **`--no-audit-badge` / `--no-source-link`** — cleaner public-facing HTML.

### Python API

```python
from pathlib import Path
from html_to_deck import convert

convert(
    Path("case-study.html"),
    Path("public/deck.html"),
    theme="portfolio",
    layout="embed",
    tokens_css=Path("deck-tokens.css").read_text(encoding="utf-8"),
    show_audit_badge=False,
    show_source_link=False,
)
```

`render_html_string(...)` renders a `DeckDocument` to HTML without writing a file.

### Cursor skill

For agent-assisted authoring and CLI usage, see **`.cursor/skills/html-to-deck-portfolio/SKILL.md`**.

## Architecture

```text
[ingest] -> HtmlDocument
    contract: { fixture_id, path, html }

[extract] -> canonical content IR
    contract: {
      meta: { title, primary_heading, section_headings[] },
      content: { paragraphs[], bullets[] }
    }

[narrative] -> story IR
    contract: {
      story: { title, summary, beats[{id,label,intent}] }
    }

[mapping] -> slide plan
    contract: {
      slides[{id,kind,title,body}]
    }

[layout] -> spatial hints
    contract: {
      slides[{...,layout}]
    }

[design] -> themed slides
    contract: {
      slides[{...,theme}]
    }

[audit] -> quality report
    contract: {
      ok, issue_count, issues[{slide_id,severity,rule}]
    }

[renderer_json] -> final deck spec
    contract: {
      deck_version, fixture_id, slides[], audit
    }
```

## CLI usage

Print version:

```bash
html-to-deck --version
```

Run the legacy v1 JSON pipeline (fixture snapshot style):

```bash
PYTHONPATH=src python3 -m html_to_deck_v1 fixtures/html/report-summary.html
```

The command prints the final JSON deck spec.

Generate an interactive HTML deck viewer (keyboard + touch navigation):

```bash
html-to-deck --input fixtures/html/report-summary.html --output out/deck.html --format html
```

Or without installing (development tree):

```bash
PYTHONPATH=src python3 -m html_to_deck.cli --input fixtures/html/report-summary.html --output out/deck.html --format html
```

The CLI prints the written output path on stdout (for example `out/deck.html`), then prints the audit summary by default.

### HTML viewer themes

- **`default`** — Dark “midnight” viewer (default when `--theme` is omitted).
- **`portfolio`** — Warm light shell, `prefers-color-scheme` dark palette, Instrument Serif + Inter (see `src/html_to_deck/renderers/themes.py`).

```bash
html-to-deck --input fixtures/html/report-summary.html --output out/deck.html --format html --theme portfolio
```

Append your own CSS after the theme (HTML output only):

```bash
html-to-deck --input page.html --output out/deck.html --format html --theme portfolio --extra-css ./overrides.css
```

### Authoring narrative source

See **[docs/authoring-decks.md](docs/authoring-decks.md)** for how to structure HTML or markdown so slides stay focused and presentation-native.

### Python version

Use Python 3.11+ for `html_to_deck.cli` and packaged installs.

## Running tests

```bash
pip install -e ".[dev]"
python3 -m pytest -q
```

During development without an editable install:

```bash
PYTHONPATH=src python3 -m pytest -q
```

## Fixture format and snapshot workflow

### Fixture format

Put fixture pages under `fixtures/html/*.html`.

Guidelines:
- include one `<title>`
- include one primary `<h1>`
- include one or more `<h2>` sections
- include narrative text in `<p>` and optional bullet points in `<li>`

### Snapshot update workflow

1. Make fixture or pipeline changes.
2. Regenerate snapshots:

   ```bash
   PYTHONPATH=src python3 - <<'PY'
   import json
   from pathlib import Path
   from html_to_deck_v1.pipeline import run_pipeline

   root = Path('.')
   fixtures = sorted((root/'fixtures'/'html').glob('*.html'))
   out = root/'tests'/'snapshots'
   out.mkdir(parents=True, exist_ok=True)

   canonical = {p.stem: run_pipeline(p)['canonical_ir'] for p in fixtures}
   deck = {p.stem: run_pipeline(p)['deck_json'] for p in fixtures}
   audit = {p.stem: run_pipeline(p)['audit'] for p in fixtures}

   (out/'canonical_ir.json').write_text(json.dumps(canonical, indent=2, sort_keys=True) + '\n')
   (out/'deck_json.json').write_text(json.dumps(deck, indent=2, sort_keys=True) + '\n')
   (out/'audit_report.json').write_text(json.dumps(audit, indent=2, sort_keys=True) + '\n')
   PY
   ```

3. Run tests and ensure e2e snapshot assertions pass.

## v1 design principles

- **Deterministic outputs**: identical HTML input yields identical stage artifacts.
- **Explicit contracts per stage**: tests assert field presence and core semantics.
- **Snapshot confidence**: e2e snapshots guard canonical IR, rendered deck JSON, and audit output.
- **Small-footprint parser**: standard-library HTML parser only, optimized for reliable fixtures.

## Known limitations (v1)

- Not a full browser-grade HTML model (no CSS/DOM layout evaluation).
- Semantics are intentionally simple (headings + paragraphs + list items + HTML images).
- Audit rule set is minimal and intended as a baseline.
- Markdown image references are flagged as warnings, not rendered as slides; use HTML `<img>` for figures in the standalone viewer.
- Fetching remote HTML requires `HTML_TO_DECK_ENABLE_URL_INGEST=1` (see `src/html_to_deck/ingest/loader.py`).
