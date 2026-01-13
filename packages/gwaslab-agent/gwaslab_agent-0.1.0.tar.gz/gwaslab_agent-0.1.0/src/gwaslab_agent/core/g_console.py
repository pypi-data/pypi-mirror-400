from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme
from rich.text import Text

GWASLAB_BLUE = "#74BAD3"
GWASLAB_CODE = "#AA2839"
GWASLAB_DARK = "#597FBD"
GWASLAB_BLACK = "#000000"
GWASLAB_GREY = "#DDDDDD"

gwaslab_theme = Theme({
    # --- Headings ---
    "markdown.h1": f"bold {GWASLAB_DARK}",
    "markdown.h2": f"bold {GWASLAB_DARK}",
    "markdown.h3": f"bold {GWASLAB_DARK}",

    # --- Body text ---
    "markdown.paragraph": GWASLAB_BLACK,
    "markdown.emph": f"italic {GWASLAB_BLACK}",
    "markdown.strong": f"bold {GWASLAB_BLACK}",

    # --- Inline code ---
    "markdown.code": f"{GWASLAB_CODE} on {GWASLAB_GREY}",

    # --- Links ---
    "markdown.link": f"bold {GWASLAB_BLUE} underline",

    # --- Blockquotes ---
    "markdown.block_quote": f"italic {GWASLAB_BLUE}",

    "rule.line": f"{GWASLAB_BLUE}",
    "rule.text": f"{GWASLAB_BLUE}"
})

console = Console(theme=gwaslab_theme, highlight=True)