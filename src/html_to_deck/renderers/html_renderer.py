"""HTML runtime renderer: canonical schema to a live slide deck viewer."""

from __future__ import annotations

import json
from html import escape

from ..audit import AuditReport
from ..schema.ir import DeckDocument, SlideImage
from .themes import font_links_for_theme, normalize_theme_id, theme_css


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
    prev.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    location.hash = 'slide-' + (index + 1);
  };

  const go = (nextIndex) => { index = clamp(nextIndex); render(); };

  prev.addEventListener('click', () => go(index - 1));
  next.addEventListener('click', () => go(index + 1));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown') {
      event.preventDefault();
      go(index + 1);
    }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
      event.preventDefault();
      go(index - 1);
    }
    if (event.key === ' ' || event.key === 'Spacebar') {
      event.preventDefault();
      go(index + 1);
    }
    if (event.key === 'Home') go(0);
    if (event.key === 'End') go(slides.length - 1);
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

    def __init__(self, *, theme: str = "default", extra_css: str | None = None) -> None:
        self._theme = normalize_theme_id(theme)
        self._extra_css = (extra_css or "").strip()

    def render(self, deck: DeckDocument, audit_report: AuditReport | None = None) -> str:
        slide_markup = "\n".join(
            self._render_slide(idx, slide.title, slide.bullets, slide.figures, slide.metadata)
            for idx, slide in enumerate(deck.slides, start=1)
        )
        title = escape(deck.slides[0].title if deck.slides else "Generated Deck")
        source_link_markup = self._render_source_link(deck.source_href)
        audit_markup = self._render_audit_summary(audit_report)

        if audit_report is not None:
            audit_payload = escape(json.dumps(audit_report.to_dict(), sort_keys=True))
        else:
            audit_payload = escape(
                json.dumps({"issue_count": len(deck.audit_issues), "issues": deck.audit_issues}, sort_keys=True)
            )

        base_css = theme_css(self._theme)
        font_links = font_links_for_theme(self._theme)
        extra_style = f"\n{self._extra_css}\n" if self._extra_css else ""

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  {font_links}
  <style>
{base_css}
{extra_style}
  </style>
</head>
<body>
  <main class="deck" data-deck-type="{escape(deck.deck_type)}" data-theme="{escape(self._theme)}">
    <section class="slides">{slide_markup}</section>
    <footer class="controls">
      <button type="button" data-prev aria-label="Previous slide">◀ Prev</button>
      <div class="progress" aria-hidden="true"><div data-progress></div></div>
      <button type="button" data-next aria-label="Next slide">Next ▶</button>
      {source_link_markup}
      {audit_markup}
      <div class="meta" data-counter>0 / 0</div>
      <p class="hint">Arrow keys or space · swipe</p>
    </footer>
  </main>
  <script type="application/json" id="deck-audit">{audit_payload}</script>
  <script>{_BASE_JS}</script>
</body>
</html>
"""

    @staticmethod
    def _render_figures(figures: tuple[SlideImage, ...]) -> str:
        parts: list[str] = []
        for fig in figures:
            safe_src = escape(fig.src, quote=True)
            safe_alt = escape(fig.alt, quote=True)
            dims = ""
            if fig.width is not None:
                dims += f' width="{fig.width}"'
            if fig.height is not None:
                dims += f' height="{fig.height}"'
            parts.append(
                f'<figure class="slide-figure"><img src="{safe_src}" alt="{safe_alt}"{dims} loading="lazy" decoding="async" /></figure>'
            )
        return "\n".join(parts)

    @staticmethod
    def _render_slide(
        index: int,
        title: str,
        bullets: list[str],
        figures: tuple[SlideImage, ...],
        metadata: dict[str, object] | None = None,
    ) -> str:
        if bullets:
            items = "\n".join(f"<li>{escape(bullet)}</li>" for bullet in bullets)
            list_markup = f"<ul>{items}</ul>"
        else:
            list_markup = ""

        if not list_markup and not figures:
            list_markup = "<ul><li>No bullet content extracted.</li></ul>"

        figures_markup = HtmlDeckRenderer._render_figures(figures)
        data_layout = (metadata or {}).get("layout")
        layout_attr = f' data-layout="{escape(str(data_layout), quote=True)}"' if data_layout else ""
        return (
            f'<article class="slide" id="slide-{index}"{layout_attr}>'
            f'<section class="slide-inner"><h1>{escape(title)}</h1>{list_markup}{figures_markup}</section>'
            "</article>"
        )

    @staticmethod
    def _render_audit_summary(audit_report: AuditReport | None) -> str:
        if audit_report is None:
            return ""
        return f'<div class="audit-badge" data-audit-summary>{escape(audit_report.summary_line)}</div>'

    @staticmethod
    def _render_source_link(source_href: str | None) -> str:
        if not source_href:
            return ""
        safe_href = escape(source_href, quote=True)
        return (
            f'<a class="source-link" data-source-link href="{safe_href}" target="_blank" rel="noopener noreferrer">'
            '<span aria-hidden="true">🔗</span><span>Source</span></a>'
        )
