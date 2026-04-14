"""HTML runtime renderer: canonical schema to a live slide deck viewer."""

from __future__ import annotations

import json
from html import escape

from ..schema.ir import DeckDocument, Slide

_BASE_CSS = """
:root {
  --bg: #0b1020;
  --panel: #121937;
  --text: #edf2ff;
  --muted: #a9b5d6;
  --accent: #7aa2ff;
  --accent-2: #66e3c4;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background: radial-gradient(circle at 20% 10%, #1f2b58 0%, var(--bg) 45%);
  color: var(--text);
}
.deck {
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
}
.slides {
  position: relative;
  overflow: hidden;
}
.slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transform: translateX(30px);
  transition: opacity 240ms ease, transform 240ms ease;
  padding: clamp(1rem, 3vw, 2.5rem);
}
.slide.is-active {
  opacity: 1;
  transform: translateX(0);
}
.slide-inner {
  background: linear-gradient(165deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 18px;
  height: 100%;
  padding: clamp(1rem, 4vw, 3rem);
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 1rem;
}
.slide h1 { margin: 0; font-size: clamp(1.5rem, 4vw, 3rem); letter-spacing: -0.02em; }
.slide p { margin: 0; color: var(--muted); font-size: clamp(1rem, 2.3vw, 1.35rem); line-height: 1.45; }
.slide ul { margin: 0; padding-left: 1.25rem; color: var(--muted); font-size: clamp(1rem, 2.3vw, 1.6rem); line-height: 1.45; }
.slide li + li { margin-top: .45rem; }
.slide-notes { margin-top: .8rem; font-size: .9rem; color: var(--muted); opacity: .9; }
.slide-meta { margin-top: .5rem; font-size: .78rem; color: var(--muted); opacity: .85; }
.slide-meta code { color: var(--text); }
.controls {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .75rem 1rem 1rem;
}
button {
  appearance: none;
  border: 1px solid rgba(255,255,255,.18);
  background: var(--panel);
  color: var(--text);
  padding: .45rem .75rem;
  border-radius: 10px;
  cursor: pointer;
}
button:hover { border-color: var(--accent); }
.progress {
  height: 8px;
  background: rgba(255,255,255,0.15);
  border-radius: 999px;
  overflow: hidden;
  flex: 1;
}
.progress > div {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
.meta { font-size: .9rem; color: var(--muted); min-width: 5rem; text-align: right; }
.source-link {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-left: auto;
  color: var(--muted);
  text-decoration: none;
  font-size: .8rem;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link:hover { color: var(--text); border-color: var(--accent); }
"""

_BASE_JS = """
(function () {
  const slides = Array.from(document.querySelectorAll('.slide'));
  const progress = document.querySelector('[data-progress]');
  const counter = document.querySelector('[data-counter]');
  const prev = document.querySelector('[data-prev]');
  const next = document.querySelector('[data-next]');

  if (!slides.length) return;

  const clamp = (n) => Math.max(0, Math.min(n, slides.length - 1));
  const fromHash = () => {
    const val = Number((location.hash || '').replace('#slide-', ''));
    return Number.isInteger(val) && val > 0 ? val - 1 : 0;
  };

  let index = clamp(fromHash());

  const render = () => {
    slides.forEach((el, i) => el.classList.toggle('is-active', i === index));
    const pct = ((index + 1) / slides.length) * 100;
    progress.style.width = pct + '%';
    counter.textContent = (index + 1) + ' / ' + slides.length;
    location.hash = 'slide-' + (index + 1);
  };

  const go = (nextIndex) => { index = clamp(nextIndex); render(); };

  prev.addEventListener('click', () => go(index - 1));
  next.addEventListener('click', () => go(index + 1));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') go(index + 1);
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') go(index - 1);
  });

  let touchStartX = null;
  document.addEventListener('touchstart', (event) => {
    touchStartX = event.changedTouches[0].clientX;
  }, { passive: true });

  document.addEventListener('touchend', (event) => {
    if (touchStartX === null) return;
    const delta = event.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 40) go(index + (delta < 0 ? 1 : -1));
    touchStartX = null;
  }, { passive: true });

  window.addEventListener('hashchange', () => go(fromHash()));
  render();
})();
"""


class HtmlDeckRenderer:
    """Render a DeckDocument into a standalone interactive HTML slideshow."""

    def render(self, deck: DeckDocument) -> str:
        slide_markup = "\n".join(self._render_slide(idx, slide) for idx, slide in enumerate(deck.slides, start=1))
        title = escape(deck.slides[0].title if deck.slides else "Generated Deck")
        source_link_markup = self._render_source_link(deck.source_href)

        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <style>{_BASE_CSS}</style>
</head>
<body>
  <main class=\"deck\" data-deck-type=\"{escape(deck.deck_type)}\">
    <section class=\"slides\">{slide_markup}</section>
    <footer class=\"controls\">
      <button type=\"button\" data-prev aria-label=\"Previous slide\">◀ Prev</button>
      <button type=\"button\" data-next aria-label=\"Next slide\">Next ▶</button>
      <div class=\"progress\" aria-hidden=\"true\"><div data-progress></div></div>
      {source_link_markup}
      <div class=\"meta\" data-counter>0 / 0</div>
    </footer>
  </main>
  <script>{_BASE_JS}</script>
</body>
</html>
"""

    @staticmethod
    def _render_slide(index: int, slide: Slide) -> str:
        items = "\n".join(f"<li>{escape(bullet)}</li>" for bullet in slide.bullets) if slide.bullets else "<li>No bullet content extracted.</li>"
        body_markup = f"<p>{escape(slide.body)}</p>" if slide.body else ""
        notes_markup = f"<aside class=\"slide-notes\">Notes: {escape(slide.notes)}</aside>" if slide.notes else ""
        evidence_markup = (
            "<p class=\"slide-meta\"><strong>Evidence:</strong> "
            + ", ".join(escape(item) for item in slide.evidence)
            + "</p>"
        ) if slide.evidence else ""
        source_refs_markup = (
            "<p class=\"slide-meta\"><strong>Source refs:</strong> "
            + ", ".join(escape(ref) for ref in slide.source_refs)
            + "</p>"
        ) if slide.source_refs else ""
        metadata_markup = (
            f"<p class=\"slide-meta\"><strong>Metadata:</strong> <code>{escape(json.dumps(slide.metadata, sort_keys=True))}</code></p>"
            if slide.metadata else ""
        )

        meta_items: list[str] = []
        if slide.layout_hint:
            meta_items.append(f"layout={escape(slide.layout_hint)}")
        if slide.pattern:
            meta_items.append(f"pattern={escape(slide.pattern)}")
        meta_markup = f"<p class=\"slide-meta\"><code>{' | '.join(meta_items)}</code></p>" if meta_items else ""

        return (
            f"<article class=\"slide\" id=\"slide-{index}\">"
            f"<section class=\"slide-inner\"><h1>{escape(slide.title)}</h1>{body_markup}<ul>{items}</ul>{notes_markup}{evidence_markup}{source_refs_markup}{metadata_markup}{meta_markup}</section>"
            "</article>"
        )

    @staticmethod
    def _render_source_link(source_href: str | None) -> str:
        if not source_href:
            return ""
        safe_href = escape(source_href, quote=True)
        return (
            f"<a class=\"source-link\" data-source-link href=\"{safe_href}\" target=\"_blank\" rel=\"noopener noreferrer\">"
            "<span aria-hidden=\"true\">🔗</span><span>Source</span></a>"
        )
