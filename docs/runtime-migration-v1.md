# Runtime Canonicalization: `html_to_deck` vs `html_to_deck_v1`

## Decision

As of April 14, 2026, the **authoritative runtime tree is `src/html_to_deck/*`**.

`src/html_to_deck_v1/*` is now a **legacy compatibility shim** for external imports that
still reference the old package path.

## What changed

- The fixture-oriented v1 stage functions (`ingest_html`, `extract_content`,
  `build_narrative`, `map_to_slides`, `apply_layout`, `apply_design`,
  `audit_deck`, `render_json`, `run_pipeline`) are now implemented in:
  - `src/html_to_deck/pipeline/v1_compat.py`
- `src/html_to_deck_v1/pipeline.py` now forwards imports only, and should not
  contain independent runtime logic.
- CLI and public API in `src/html_to_deck` continue to route through the
  canonical `html_to_deck` package path.

## Migration guidance

- Prefer imports from `html_to_deck` paths in all new code and tests.
- Existing consumers can keep `html_to_deck_v1.pipeline` imports temporarily;
  behavior is preserved via shim forwarding.
- Do not add new stage logic to both `src/html_to_deck` and
  `src/html_to_deck_v1`.

## Enforcement

A CI guard test (`tests/test_runtime_path_guard.py`) ensures
`src/html_to_deck_v1/pipeline.py` remains a thin shim and blocks reintroducing
split runtime implementations.
