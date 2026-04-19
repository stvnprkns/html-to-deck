# Authoring source content for html-to-deck

This guide complements the deterministic pipeline: it describes **how to write or edit source HTML (or markdown fixtures)** so the generated deck stays readable, honest, and presentation-native—rather than a scroll-order dump of a webpage.

## Core idea

A web page invites exploration. A slide directs attention to **one takeaway**. Do not mirror weak page structure when a stronger narrative arc exists.

## Before you write HTML

1. **Intent** — Classify the deck: pitch, case study, report readout, launch, training, etc. Who is the audience and what must they believe or do at the end?
2. **Spine** — Thesis → supporting moves → proof → implication / next step. Cut anything that does not serve that spine.
3. **Slide roles** (conceptual) — Cover, tension, big idea, proof, comparison, section divider, summary, CTA. Each slide answers: *What single thing should the viewer remember?* If two answers, split the source into two sections.

## Source HTML that maps well

The v1 extractor focuses on **title**, **headings**, **paragraphs**, **list items**, and **`<img>`** (with `src`, `alt`, and optional `width` / `height` for stable layout in the HTML viewer).

- One **`<h1>`** for the deck title; use **`<h2>`** for major sections that should become content slides.
- Keep **`<p>`** units focused; prefer several short paragraphs over one wall of text.
- Use **`<ul><li>`** for discrete bullets the mapper can lift verbatim.
- Put **screenshots in context**: same section as the claim they support, with meaningful **alt** text.
- **Do not** rely on layout tables, deep `div` trees, or embedded widgets—the parser ignores them.

## Anti-patterns

- Pasting an entire article into one section and expecting a good deck.
- Using headings only for styling (skips narrative hierarchy).
- Generic slide titles that duplicate the site nav (“Overview”, “Features”) instead of an assertion.
- Images with no `alt` or intrinsic dimensions when you care about layout in the standalone viewer.

## Markdown fixtures

Richer markdown (tables, fenced diagram specs, merged lists) is supported for **non-HTML** snapshots. External markdown images are recorded as **warnings** with audit metadata (not rendered as figures); use **HTML `<img>`** if you need raster slides in the HTML viewer.

## After generation

Use the **audit summary** in CLI output and the JSON `audit` object to catch overloaded slides, missing evidence metadata on claims (when you attach structured claims later), and diagram-as-image warnings from the quality rules.

For presentation-heavy work beyond v1’s mapping (hooks, metric tiles, custom layouts), treat html-to-deck as the **structured first pass** and hand-edit downstream—or build a richer mapper in your own fork.
