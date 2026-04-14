# html_to_deck architecture scaffold

The repository is split into stage-oriented packages under `src/html_to_deck/`:

1. `ingest` → HTML loading and normalization.
2. `extract` → semantic block extraction.
3. `narrative` → deck-type/storyline inference.
4. `schema` → canonical typed intermediate representation.
5. `layout` → layout pattern selection by slide intent.
6. `design` → visual hierarchy and emphasis rules.
7. `renderers` → target-specific output adapters.
8. `audit` → coherence and quality checks.
9. `pipeline` → orchestration and stage wiring.
10. `io` → output/snapshot serialization.

## Dependency boundary

Renderers are isolated and consume only canonical schema models. They should not
import `extract` or `narrative` internals directly. This is enforced by
`tests/test_renderer_boundaries.py`.
