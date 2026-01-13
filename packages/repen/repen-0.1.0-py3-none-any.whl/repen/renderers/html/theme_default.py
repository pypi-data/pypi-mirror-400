from typing import Dict

from repen.renderers.html.datatable import CSS_DATA_TABLE
from repen.renderers.html.theme import HTMLTheme

CSS_RESET = """
*, *::before, *::after {
  box-sizing: border-box;
}

* {
  margin: 0;
}

@media (prefers-reduced-motion: no-preference) {
  html {
    interpolate-size: allow-keywords;
  }
}

body {
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
}

p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}

p {
  text-wrap: wrap;
}
h1, h2, h3, h4, h5, h6 {
  text-wrap: balance;
}

#root, #__next {
  isolation: isolate;
}
"""


class HTMLDefaultTheme(HTMLTheme):
    # Abstract methods implementation

    def variables(self) -> Dict[str, str]:
        return {
            # Base color
            "color-primary": "#2563eb",
            "color-primary-dark": "#1d4ed8",
            "color-secondary": "#64748b",
            "color-success": "#10b981",
            "color-warning": "#f59e0b",
            "color-danger": "#ef4444",
            # Text color
            "color-text": "#1f2937",
            "color-text-light": "#6b7280",
            "color-text-inverse": "#ffffff",
            # Background
            "color-bg": "#ffffff",
            "color-bg-secondary": "#f9fafb",
            "color-bg-tertiary": "#f3f4f6",
            # Border color
            "color-border": "#e5e7eb",
            "color-border-light": "#f3f4f6",
            # Spacing
            "spacing-0": "0",
            "spacing-xs": "0.25rem",
            "spacing-sm": "0.5rem",
            "spacing-md": "1rem",
            "spacing-lg": "1.5rem",
            "spacing-xl": "2rem",
            "spacing-2xl": "3rem",
            # Fonts
            "font-family-base": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "font-family-mono": "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace",
            "font-size-base": "16px",
            "line-height-base": "1.4",
            # Layout
            "layout-max-width": "800px",
        }

    def styles(self) -> str:
        return f"""
{CSS_RESET}
{CSS_DATA_TABLE}

body {{
    background-color: var(--color-bg);
    color: var(--color-text-light);
    font-family: var(--font-family-base);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
    margin: 0;
    padding: 0;
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--color-text);
}}

.layout {{
    width: 100%;
    max-width: var(--layout-max-width);
}}

.layout.vstack {{
    display: flex;
    flex-direction: column;
    gap: var(--spacing, 0);
    margin: 0 auto;
}}

.layout.vstack .item {{
    display: block;
}}

.layout.vstack .item img,
.layout.vstack .item figure > img,
.layout.vstack .item figure > svg {{
    margin: 0 auto;
}}

.bold {{
    font-weight: bold;
}}

.italic {{
    font-style: italic;
}}

.underline {{
    text-decoration: underline;
}}

.strikethrough {{
    text-decoration: line-through;
}}

.code {{
    font-family: var(--font-family-mono);
    //background: #ffeff0;
    //word-wrap: break-word;
    //box-decoration-break: clone;
    //padding: .1rem .3rem .2rem;
    //border-radius: .2rem;
}}

.metrics-group {{
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing, --spacing-md) 0.5em;
}}

.metric {{
    display: grid;
    grid-template-columns: subgrid;
    grid-column: 1 / -1;
    color: var(--color-text);
}}

.metric .label {{
    grid-column: 1;
    min-width: 150px;
    max-width: 350px;
}}

.metric .value {{
    grid-column: 2;
    display: flex;
    align-items: baseline;
    justify-content: flex-start;
    gap: 0.25rem;
    flex-wrap: wrap;
    font-weight: bold;
}}

.metric.highlight .value {{
    color: var(--color-primary);
}}

.metric.success .value {{
    color: var(--color-success);
}}

.metric.warning .value {{
    color: var(--color-warning);
}}

.metric.danger .value {{
    color: var(--color-danger);
}}
        """
