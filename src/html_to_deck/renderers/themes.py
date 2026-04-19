"""Built-in CSS themes for the standalone HTML deck viewer."""

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

CSS_DEFAULT: Final[str] = """
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
.slide-figure {
  margin: 0.75rem 0 0;
  border-radius: 0.75rem;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(0,0,0,0.2);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  max-height: min(48vh, 620px);
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
.audit-badge {
  font-size: .8rem;
  color: var(--muted);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-left: auto;
  color: var(--muted);
  text-decoration: none;
  font-size: .8rem;
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link:hover { color: var(--text); border-color: var(--accent); }
.hint { margin: 0.35rem 0 0; font-size: 0.75rem; color: var(--muted); text-align: center; width: 100%; }
"""

CSS_PORTFOLIO: Final[str] = """
:root {
  color-scheme: light dark;
  --page-bg: #faf9f7;
  --text: oklch(0.22 0.006 56);
  --muted: oklch(0.45 0.02 56);
  --accent: oklch(0.45 0.2 294);
  --accent-hover: oklch(0.52 0.18 294);
  --panel: oklch(0.98 0.005 60);
  --border: rgba(0, 0, 0, 0.12);
  --figure-bg: #e9e6e2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --page-bg: #1b1411;
    --text: oklch(0.92 0.005 60);
    --muted: oklch(0.72 0.02 60);
    --accent: #f59e0b;
    --accent-hover: #fbbf24;
    --panel: #1a0f0c;
    --border: rgba(255, 255, 255, 0.12);
    --figure-bg: var(--panel);
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background-color: var(--page-bg);
  color: var(--text);
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
  background: var(--panel);
  border: 1px solid var(--border);
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
  color: var(--text);
}
.slide p { margin: 0; color: var(--muted); font-size: clamp(1rem, 2.2vw, 1.25rem); line-height: 1.55; }
.slide ul {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--muted);
  font-size: clamp(1rem, 2.2vw, 1.35rem);
  line-height: 1.5;
}
.slide li + li { margin-top: .4rem; }
.slide-notes { margin-top: .8rem; font-size: .9rem; color: var(--muted); opacity: .9; }
.slide-meta { margin-top: .5rem; font-size: .78rem; color: var(--muted); opacity: .85; }
.slide-meta code { color: var(--text); }
.slide-figure {
  margin: 0.75rem 0 0;
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  background: var(--figure-bg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1rem, 2.5vw, 1.25rem);
  max-height: min(52vh, 660px);
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
.controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .75rem;
  padding: .75rem 1rem 1rem;
  border-top: 1px solid var(--border);
  background: color-mix(in oklch, var(--page-bg), transparent 0%);
}
button {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text);
  padding: .45rem .85rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}
button:hover { background: color-mix(in oklch, var(--panel), var(--text) 6%); }
button:disabled { opacity: 0.4; cursor: default; }
.progress {
  height: 8px;
  background: color-mix(in oklch, var(--text), transparent 88%);
  border-radius: 999px;
  overflow: hidden;
  flex: 1;
  min-width: 120px;
}
.progress > div {
  height: 100%;
  width: 0%;
  background: var(--accent);
  border-radius: 999px;
  transition: width 300ms ease-out;
}
.meta { font-size: .85rem; color: var(--muted); min-width: 5rem; text-align: right; font-variant-numeric: tabular-nums; }
.audit-badge {
  font-size: .8rem;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-left: auto;
  color: var(--muted);
  text-decoration: none;
  font-size: .8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: .28rem .55rem;
}
.source-link:hover { color: var(--text); border-color: var(--accent); }
.hint {
  flex-basis: 100%;
  margin: 0;
  font-size: 0.7rem;
  color: var(--muted);
  text-align: center;
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
