"""Built-in CSS themes for the standalone HTML deck viewer.

Stable customization surface: ``--deck-*`` variables (see docs/design-tokens.md).
Optional site aliases are read via ``var(--primary, ...)`` etc. in the theme root block.
"""

from __future__ import annotations

from typing import Final

THEME_DEFAULT: Final[str] = "default"
THEME_PORTFOLIO: Final[str] = "portfolio"

VALID_THEMES: Final[tuple[str, ...]] = (THEME_DEFAULT, THEME_PORTFOLIO)

# Google Fonts used by the portfolio-inspired preset (matches steveperkins.dev pairing).
PORTFOLIO_FONT_LINKS: Final[str] = """
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:ital,opsz,wght@0,14..32,400..700;1,14..32,400..700&display=swap" rel="stylesheet" />
"""

# Default (midnight): internal rules consume --deck-* only. Root maps from optional site tokens.
CSS_DEFAULT: Final[str] = """
:root {
  --deck-bg: var(--background, #0b1020);
  --deck-panel: var(--panel-surface, #121937);
  --deck-text: var(--foreground, #edf2ff);
  --deck-muted: var(--muted-foreground, #a9b5d6);
  --deck-accent: var(--primary, #7aa2ff);
  --deck-accent-2: var(--secondary, #66e3c4);
  --deck-border: var(--border-color, rgba(255, 255, 255, 0.15));
  --deck-figure-bg: var(--figure-background, rgba(0, 0, 0, 0.2));
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background: radial-gradient(circle at 20% 10%, #1f2b58 0%, var(--deck-bg) 45%);
  color: var(--deck-text);
}
.deck {
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
}
.deck.deck--embed {
  height: auto;
  min-height: min(100vh, 52rem);
  max-width: 72rem;
  margin-inline: auto;
}
.slides {
  position: relative;
  overflow: hidden;
  min-height: 12rem;
}
.deck--embed .slides {
  min-height: min(70vh, 40rem);
}
.slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transform: translateX(30px);
  transition: opacity 240ms ease, transform 240ms ease;
  padding: clamp(1rem, 3vw, 2.5rem);
}
@media (prefers-reduced-motion: reduce) {
  .slide {
    transition: opacity 120ms ease;
    transform: none;
  }
  .slide.is-active { transform: none; }
}
.slide.is-active {
  opacity: 1;
  transform: translateX(0);
}
.slide-inner {
  background: linear-gradient(165deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
  border: 1px solid var(--deck-border);
  border-radius: 18px;
  height: 100%;
  padding: clamp(1rem, 4vw, 3rem);
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 1rem;
}
.slide h1 { margin: 0; font-size: clamp(1.5rem, 4vw, 3rem); letter-spacing: -0.02em; color: var(--deck-text); }
.slide p { margin: 0; color: var(--deck-muted); font-size: clamp(1rem, 2.3vw, 1.35rem); line-height: 1.45; }
.slide ul { margin: 0; padding-left: 1.25rem; color: var(--deck-muted); font-size: clamp(1rem, 2.3vw, 1.6rem); line-height: 1.45; }
.slide li + li { margin-top: .45rem; }
.slide-notes { margin-top: .8rem; font-size: .9rem; color: var(--deck-muted); opacity: .9; }
.slide-meta { margin-top: .5rem; font-size: .78rem; color: var(--deck-muted); opacity: .85; }
.slide-meta code { color: var(--deck-text); }
.slide-figure {
  margin: 0.75rem 0 0;
  border-radius: 0.75rem;
  border: 1px solid var(--deck-border);
  background: var(--deck-figure-bg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  max-height: min(48vh, 620px);
}
.deck--embed .slide-figure {
  max-height: min(40vh, 520px);
}
.slide-figure img {
  max-width: 100%;
  max-height: min(44vh, 560px);
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center top;
  vertical-align: middle;
}
.deck--embed .slide-figure img {
  max-height: min(36vh, 480px);
}
.controls {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .75rem 1rem 1rem;
}
button {
  appearance: none;
  border: 1px solid var(--deck-border);
  background: var(--deck-panel);
  color: var(--deck-text);
  padding: .45rem .75rem;
  border-radius: 10px;
  cursor: pointer;
}
button:hover { border-color: var(--deck-accent); }
button:focus-visible {
  outline: 2px solid var(--deck-accent);
  outline-offset: 2px;
}
.progress {
  height: 8px;
  background: color-mix(in srgb, var(--deck-text) 18%, transparent);
  border-radius: 999px;
  overflow: hidden;
  flex: 1;
}
.progress > div {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--deck-accent), var(--deck-accent-2));
}
.meta { font-size: .9rem; color: var(--deck-muted); min-width: 5rem; text-align: right; }
.audit-badge {
  font-size: .8rem;
  color: var(--deck-muted);
  border: 1px solid var(--deck-border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-left: auto;
  color: var(--deck-muted);
  text-decoration: none;
  font-size: .8rem;
  border: 1px solid var(--deck-border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link:hover { color: var(--deck-text); border-color: var(--deck-accent); }
.hint { margin: 0.35rem 0 0; font-size: 0.75rem; color: var(--deck-muted); text-align: center; width: 100%; }
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
"""

CSS_PORTFOLIO: Final[str] = """
:root {
  color-scheme: light dark;
  --deck-bg: var(--background, #faf9f7);
  --deck-text: var(--foreground, oklch(0.22 0.006 56));
  --deck-muted: var(--muted-foreground, oklch(0.45 0.02 56));
  --deck-accent: var(--primary, oklch(0.45 0.2 294));
  --deck-accent-hover: var(--primary-hover, oklch(0.52 0.18 294));
  --deck-panel: var(--panel-surface, oklch(0.98 0.005 60));
  --deck-border: var(--border-color, rgba(0, 0, 0, 0.12));
  --deck-figure-bg: var(--figure-background, #e9e6e2);
  --deck-accent-2: var(--secondary, var(--deck-accent));
}
@media (prefers-color-scheme: dark) {
  :root {
    --deck-bg: var(--background-dark, #1b1411);
    --deck-text: var(--foreground-dark, oklch(0.92 0.005 60));
    --deck-muted: var(--muted-foreground-dark, oklch(0.72 0.02 60));
    --deck-accent: var(--primary-dark, #f59e0b);
    --deck-accent-hover: var(--primary-hover-dark, #fbbf24);
    --deck-panel: var(--panel-surface-dark, #1a0f0c);
    --deck-border: var(--border-color-dark, rgba(255, 255, 255, 0.12));
    --deck-figure-bg: var(--figure-background-dark, var(--deck-panel));
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background-color: var(--deck-bg);
  color: var(--deck-text);
  position: relative;
}
body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.4;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(120, 119, 198, 0.25), transparent),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(255, 210, 180, 0.12), transparent);
}
@media (prefers-color-scheme: dark) {
  body::before { opacity: 1; }
}
.deck {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
}
.deck.deck--embed {
  height: auto;
  min-height: min(100vh, 52rem);
  max-width: 72rem;
  margin-inline: auto;
}
.slides {
  position: relative;
  overflow: hidden;
  min-height: 12rem;
}
.deck--embed .slides {
  min-height: min(70vh, 40rem);
}
.slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transform: translateX(30px);
  transition: opacity 240ms ease, transform 240ms ease;
  padding: clamp(1rem, 3vw, 2.5rem);
}
@media (prefers-reduced-motion: reduce) {
  .slide {
    transition: opacity 120ms ease;
    transform: none;
  }
  .slide.is-active { transform: none; }
}
.slide.is-active {
  opacity: 1;
  transform: translateX(0);
}
.slide-inner {
  background: var(--deck-panel);
  border: 1px solid var(--deck-border);
  border-radius: 1rem;
  height: 100%;
  padding: clamp(1rem, 4vw, 3rem);
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 1rem;
  overflow-y: auto;
}
.slide h1 {
  margin: 0;
  font-family: "Instrument Serif", ui-serif, Georgia, serif;
  font-weight: 400;
  font-size: clamp(1.75rem, 4.2vw, 3rem);
  line-height: 1.18;
  text-wrap: balance;
  letter-spacing: 0;
  color: var(--deck-text);
}
.slide p { margin: 0; color: var(--deck-muted); font-size: clamp(1rem, 2.2vw, 1.25rem); line-height: 1.55; }
.slide ul {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--deck-muted);
  font-size: clamp(1rem, 2.2vw, 1.35rem);
  line-height: 1.5;
}
.slide li + li { margin-top: .4rem; }
.slide-notes { margin-top: .8rem; font-size: .9rem; color: var(--deck-muted); opacity: .9; }
.slide-meta { margin-top: .5rem; font-size: .78rem; color: var(--deck-muted); opacity: .85; }
.slide-meta code { color: var(--deck-text); }
.slide-figure {
  margin: 0.75rem 0 0;
  border-radius: 0.75rem;
  border: 1px solid var(--deck-border);
  background: var(--deck-figure-bg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1rem, 2.5vw, 1.25rem);
  max-height: min(52vh, 660px);
}
.deck--embed .slide-figure {
  max-height: min(42vh, 540px);
}
.slide-figure img {
  max-width: 100%;
  max-height: min(48vh, 600px);
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center top;
  vertical-align: middle;
}
.deck--embed .slide-figure img {
  max-height: min(38vh, 500px);
}
.controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .75rem;
  padding: .75rem 1rem 1rem;
  border-top: 1px solid var(--deck-border);
  background: color-mix(in oklch, var(--deck-bg), transparent 0%);
}
button {
  appearance: none;
  border: 1px solid var(--deck-border);
  background: var(--deck-panel);
  color: var(--deck-text);
  padding: .45rem .85rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}
button:hover { background: color-mix(in oklch, var(--deck-panel), var(--deck-text) 6%); }
button:focus-visible {
  outline: 2px solid var(--deck-accent);
  outline-offset: 2px;
}
button:disabled { opacity: 0.4; cursor: default; }
.progress {
  height: 8px;
  background: color-mix(in oklch, var(--deck-text), transparent 88%);
  border-radius: 999px;
  overflow: hidden;
  flex: 1;
  min-width: 120px;
}
.progress > div {
  height: 100%;
  width: 0%;
  background: var(--deck-accent);
  border-radius: 999px;
  transition: width 300ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  .progress > div { transition: none; }
}
.meta { font-size: .85rem; color: var(--deck-muted); min-width: 5rem; text-align: right; font-variant-numeric: tabular-nums; }
.audit-badge {
  font-size: .8rem;
  color: var(--deck-muted);
  border: 1px solid var(--deck-border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-left: auto;
  color: var(--deck-muted);
  text-decoration: none;
  font-size: .8rem;
  border: 1px solid var(--deck-border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link:hover { color: var(--deck-text); border-color: var(--deck-accent); }
.hint {
  flex-basis: 100%;
  margin: 0;
  font-size: 0.7rem;
  color: var(--deck-muted);
  text-align: center;
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
"""


def theme_css(theme_id: str) -> str:
    if theme_id == THEME_PORTFOLIO:
        return CSS_PORTFOLIO
    return CSS_DEFAULT


def font_links_for_theme(theme_id: str) -> str:
    if theme_id == THEME_PORTFOLIO:
        return PORTFOLIO_FONT_LINKS.strip()
    return ""


def normalize_theme_id(raw: str) -> str:
    lowered = (raw or "").strip().lower()
    if lowered == THEME_PORTFOLIO:
        return THEME_PORTFOLIO
    return THEME_DEFAULT
