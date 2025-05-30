# core/utils.py

import json
from pathlib import Path
from typing import List, Optional, Set, Tuple

from rich.console import Console
from rich.table import Table

console = Console()

def truncate_text(text: str, max_lines: int = 10) -> str:
    """
    Truncate the given text to a maximum number of lines.
    Adds '...' if the text was truncated.
    """
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines] + ["..."])

# Centralized style settings per language
LANG_STYLES = {
    "node": {
        "title_style": "bold yellow",
        "border_style": "yellow",
        "col1_style": "yellow",
        "col2_style": "white"
    },
    "php": {
        "title_style": "bold magenta",
        "border_style": "magenta",
        "col1_style": "magenta",
        "col2_style": "green"
    },
    "ruby": {
        "title_style": "bold dark_red",
        "border_style": "dark_red",
        "col1_style": "dark_red",
        "col2_style": "white"
    },
    "python": {
        "title_style": "bold blue",
        "border_style": "blue",
        "col1_style": "blue",
        "col2_style": "white"
    },
    "java": {
        "title_style": "bold green",
        "border_style": "green",
        "col1_style": "green",
        "col2_style": "white"
    },
}

# Default fallback style
DEFAULT_STYLE = {
    "title_style": "bold",
    "border_style": None,
    "col1_style": "cyan",
    "col2_style": "white"
}

def make_result_table(lang: str, result: dict, max_lines: int = 10) -> Table:
    """
    Build a Rich table for the results of a specific language engine.
    Applies color styles based on the language.
    """
    style = LANG_STYLES.get(lang, DEFAULT_STYLE)

    table = Table(
        title=f"Results ({lang.upper()})",
        title_style=style["title_style"],
        border_style=style["border_style"],
        show_lines=True
    )
    table.add_column("Engine", style=style["col1_style"], no_wrap=True)
    table.add_column("Output", style=style["col2_style"])

    for engine, output in sorted(result.items()):
        # Serialize JSON output if needed
        text = json.dumps(output, ensure_ascii=False) if isinstance(output, (dict, list)) else str(output)
        truncated = truncate_text(text, max_lines)
        cell = f"[red]{truncated}[/red]" if "❌" in truncated else f"[green]{truncated}[/green]"
        table.add_row(engine.upper(), cell)

    return table

def gather_engines(langs: Optional[str]) -> Set[Tuple[str, str]]:
    """
    Load all engines from `payloads_<lang>.json` files.
    Returns a set of (engine, language) pairs.
    """
    langs_list: List[str] = [l.strip().lower() for l in langs.split(",")] if langs else ["node", "php"]
    seen = set()

    for lang in langs_list:
        path = Path(f"payloads/payloads_{lang}.json")
        if not path.is_file():
            console.print(f"[yellow]⚠️  File not found: {path} (skipped)[/yellow]")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ JSON error in {path}: {e}[/red]")
            continue
        for engine in data.keys():
            seen.add((engine, lang))
    return seen

def list_engines(langs: Optional[str]) -> None:
    """
    Print a styled table of available engines per language.
    """
    entries = gather_engines(langs)
    # Print in this preferred order
    for lang in ["node", "php", "ruby", "python", "java"]:
        group = sorted(e for e, l in entries if l == lang)
        if not group:
            continue
        style = LANG_STYLES.get(lang, DEFAULT_STYLE)
        table = Table(
            title=f"Engines ({lang.upper()})",
            title_style=style["title_style"],
            border_style=style["border_style"],
            show_lines=True
        )
        table.add_column("ENGINE", style=style["col1_style"], no_wrap=True)
        for eng in group:
            table.add_row(eng)
        console.print(table)
