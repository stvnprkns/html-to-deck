# Design tokens for HTML deck output

Built-in themes (`default`, `portfolio`) style the standalone viewer using **stable CSS custom properties** on `:root`. Override them from your site stylesheet, or inject a small CSS file **before** the theme with `--tokens-css` (CLI) or `tokens_css=` (Python) so your portfolio variables map into the deck.

## Canonical `--deck-*` variables

| Token | Role |
| --- | --- |
| `--deck-bg` | Page / shell background |
| `--deck-text` | Primary text |
| `--deck-muted` | Secondary / de-emphasized text |
| `--deck-accent` | Progress bar, focus rings, hover accents |
| `--deck-accent-2` | Second accent (default theme progress gradient) |
| `--deck-panel` | Slide card / control surfaces |
| `--deck-border` | Borders and dividers |
| `--deck-figure-bg` | Figure / image well background |

Portfolio theme also defines `--deck-accent-hover` for future button styling; default theme uses `--deck-accent-2` for the progress gradient.

## Site alias fallbacks (no mapping file required)

Themes resolve each `--deck-*` with **`var(--your-token, literal-fallback)`**. If your site already exposes common names, they apply automatically:

| Deck token | Aliases read first |
| --- | --- |
| `--deck-bg` | `--background` |
| `--deck-text` | `--foreground` |
| `--deck-muted` | `--muted-foreground` |
| `--deck-accent` | `--primary` |
| `--deck-accent-2` | `--secondary` |
| `--deck-panel` | `--panel-surface` |
| `--deck-border` | `--border-color` |
| `--deck-figure-bg` | `--figure-background` |

Portfolio dark mode additionally checks `--background-dark`, `--foreground-dark`, `--primary-dark`, etc., when `prefers-color-scheme: dark`.

## Injection order

1. **Tokens CSS** (optional) — define aliases or set `--deck-*` directly.
2. **Theme CSS** — built-in layout and typography.
3. **Extra CSS** (optional) — final overrides.

Example tokens file for a site that uses `--color-brand`:

```css
:root {
  --deck-accent: var(--color-brand, #7c3aed);
}
```

CLI:

```bash
html-to-deck --input page.html --output deck.html --theme portfolio \
  --tokens-css ./site-deck-tokens.css
```

## Embed layout

Use `--layout embed` so the deck uses `min-height` and a centered `max-width` instead of locking the shell to `100vh`, which behaves better inside a portfolio article layout.
