# html-to-deck v1

This repository provides a deterministic **v1 HTML → deck JSON** reference pipeline, fixtures, and snapshot-driven test coverage.

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

Run pipeline for a single HTML input:

```bash
PYTHONPATH=src python -m html_to_deck_v1 fixtures/html/report-summary.html
```

The command prints the final JSON deck spec.

Generate an interactive HTML deck viewer (keyboard + touch navigation):

```bash
PYTHONPATH=src python -m html_to_deck.cli --input fixtures/html/report-summary.html --output out/deck.html --format html
```

The CLI prints the written output path on stdout (for example `out/deck.html`), then prints the audit summary by default.

### Python version

Use Python 3.11+ when running the new `html_to_deck.cli` entrypoint locally.
Older interpreters (for example 3.9) may fail on enum features used by the v1 CLI/tooling.

## Running tests

```bash
PYTHONPATH=src pytest -q
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
   PYTHONPATH=src python - <<'PY'
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
- Semantics are intentionally simple (headings + paragraphs + bullets).
- Audit rule set is minimal and intended as a baseline.
- No image extraction or rich media mapping in v1.
