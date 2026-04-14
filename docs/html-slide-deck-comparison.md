# Comparison: `html-to-deck` vs `sprknsprocore/html-slide-deck`

Date: 2026-04-14

## Quick verdict

Your current repository is **stronger on transformation pipeline rigor** (structured stages, contracts, tests, audits), while `sprknsprocore/html-slide-deck` is **stronger on immediate in-browser presentation UX** (CSS shell + slide controller + keyboard/touch navigation).

If the benchmark is “HTML in, live slideshow viewer out,” your project is likely **~60–70% of the way there** in user-facing runtime experience, and ahead in pipeline architecture quality.

## What `sprknsprocore/html-slide-deck` appears to provide

From its public README/repo page:

- A static shell with:
  - `deck-shell.css` for theme/layout/typography
  - `deck-shell.js` for slide navigation/progress/keyboard/touch
  - `TEMPLATE.html` starter
- A Node build script (`deck-build.js`) to compile `deck.json` into `index.html`.
- “No build step” operation for the shell itself and simple GitHub Pages publishing guidance.

## Where your repo is stronger today

- Explicit multi-stage architecture (`ingest` → `extract` → `narrative` → `mapping` → `layout` → `design` → `audit` → `renderer_json`).
- Deterministic output and test/snapshot discipline.
- Clear quality checks and auditable pipeline output.
- Python CLI/pipeline orchestration that can be extended to many render targets.

## Where your repo appears behind that benchmark

- No direct browser slide runtime (no equivalent visible to `deck-shell.js` + `deck-shell.css`).
- Output target is JSON-oriented; not yet a ready-to-present HTML viewer shell.
- Current mapping/design defaults are intentionally simple (`hero`/`two-column`, single theme).

## Practical gap to close (ordered)

1. Add a first-class HTML runtime renderer target (`renderer_html`) that emits an `index.html` deck.
2. Add a lightweight slide controller JS (left/right keys, touch, progress bar, URL hash deep-link).
3. Add a baseline deck shell CSS (theme tokens + responsive typography + speaker/readability defaults).
4. Map your existing slide intents/layout hints into CSS classes so pipeline semantics affect runtime presentation.
5. Keep your existing audit stage and add presentation-focused checks (contrast, text density, title length in ems).

## Bottom line

- **Pipeline maturity:** yours is likely higher.
- **Presentation runtime polish:** `sprknsprocore/html-slide-deck` likely higher right now.
- **Overall closeness for “live slide deck viewer”:** moderate; main missing piece is the runtime shell/controller layer, not the upstream conversion logic.
