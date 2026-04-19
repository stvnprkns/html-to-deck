# html-to-deck

Okay so: you wrote a page in HTML. Good. Now you also want a **deck**—arrow keys, swipey slides, the whole thing—without hand-copying everything into Keynote at midnight. That’s basically what this is.

Under the hood it’s a **small, stubborn pipeline**: HTML in → structured stages out → either **JSON** (for whatever you’re building) or a **self-contained HTML viewer** you can drop on a portfolio or static host. Deterministic, tested, not pretending to be a browser engine. (We’re not running your React bundle. Sorry.)

---

## Get it running

Python **3.11+**, from the repo root:

```bash
pip install .
```

You get the `html_to_deck` package plus a CLI named **`html-to-deck`**. If your shell can’t find it, no drama—use `python3 -m html_to_deck.cli` instead.

---

## The “make it look like my site” path

If you’re shipping this next to your actual work, you probably care about three things: **structure**, **tokens**, **not looking like a devtool**.

1. **Structure** — One `<h1>`, real `<h2>` sections, short `<p>` chunks, lists that mean something, `<img>` when you care about the visual. [Authoring guide](docs/authoring-decks.md) goes deep; tl;dr don’t paste a novel and expect magic.

2. **Tokens** — We expose a little **`--deck-*`** contract so your CSS can line up with the viewer. Aliases like `--primary` / `--background` work too. [Design tokens](docs/design-tokens.md) is the cheat sheet.

3. **Polish** — Embed layout, hide the audit badge and source pill when you’re not debugging.

```bash
html-to-deck --input case-study.html --output public/deck.html \
  --theme portfolio --layout embed \
  --tokens-css ./deck-tokens.css \
  --no-audit-badge --no-source-link \
  --audit-output none
```

Quick decoder ring:

- **`--layout embed`** — Doesn’t hijack the whole viewport like it owns the place. Nicer inside a long portfolio page.
- **`--tokens-css`** — Loaded *before* the theme so your variables can feed `--deck-*`.
- **`--extra-css`** — Loaded *after* the theme when you need to win a specificity fight.
- **`--no-audit-badge` / `--no-source-link`** — For when strangers visit and don’t need your linter cosplay.

### From Python

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

There’s also `render_html_string(...)` if you already have a `DeckDocument` and just want HTML in a string. Fancy.

### Cursor friends

There’s a skill at **`.cursor/skills/html-to-deck-portfolio/SKILL.md`** so your agent stops improvising and actually uses the flags. You’re welcome.

---

## How the sausage gets made

Still a pipeline. Still boring to read. Still useful when you’re debugging.

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

---

## CLI you’ll actually run

Version check (trust issues):

```bash
html-to-deck --version
```

**Legacy v1 JSON** straight to stdout (snapshot-era workflow):

```bash
PYTHONPATH=src python3 -m html_to_deck_v1 fixtures/html/report-summary.html
```

**HTML deck** with keys + touch:

```bash
html-to-deck --input fixtures/html/report-summary.html --output out/deck.html --format html
```

Living out of the git tree without `pip install`? Same thing, more typing:

```bash
PYTHONPATH=src python3 -m html_to_deck.cli --input fixtures/html/report-summary.html --output out/deck.html --format html
```

Stdout prints the output path, then an audit summary unless you tell it not to.

### Themes

- **`default`** — Midnight vibes. Good for “I’m in the zone and also possibly a submarine.”
- **`portfolio`** — Warmer, serif headlines, respects `prefers-color-scheme`. Good for “this is on my website and humans will see it.”

```bash
html-to-deck --input fixtures/html/report-summary.html --output out/deck.html --format html --theme portfolio
```

Extra CSS after the theme:

```bash
html-to-deck --input page.html --output out/deck.html --format html --theme portfolio --extra-css ./overrides.css
```

---

## Tests (yes you should)

```bash
pip install -e ".[dev]"
python3 -m pytest -q
```

Or, if you’re living dangerously with `PYTHONPATH` only:

```bash
PYTHONPATH=src python3 -m pytest -q
```

---

## Fixtures & snapshots

HTML fixtures live in `fixtures/html/*.html`. Rough checklist:

- a `<title>`
- one real `<h1>`
- at least one `<h2>` section
- `<p>` / `<li>` with actual thoughts in them

When you change pipeline output and the snapshots need love:

1. Do the thing you’re doing.
2. Regenerate:

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

3. Run pytest again and stare at the diff until it makes sense.

---

## What we’re trying to be good at

- **Same input → same output** (boring in a good way).
- **Stages with contracts** so tests know what “correct” means.
- **Snapshots** so nobody accidentally ships a silent regression.
- **stdlib HTML parsing**—small dependency footprint, no “download half of npm to read a `<p>` tag.”

---

## What we’re *not* pretending to be

- A full browser layout engine. CSS grid on your blog does not magically become slide geometry here.
- A semantic free-for-all. Headings, paragraphs, lists, images—that’s the deal.
- A giant audit product. The checks are a baseline, not your VP of Compliance.
- Markdown images as first-class slide figures in the HTML viewer—use real `<img>` if you need the picture to show up.
- URL fetch unless you flip **`HTML_TO_DECK_ENABLE_URL_INGEST=1`** (see `src/html_to_deck/ingest/loader.py`). Default is local files; less “surprise I called the internet.”

---

That’s the gist. Ship something weird and beautiful.
