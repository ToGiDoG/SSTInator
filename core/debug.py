#!/usr/bin/env python3
"""
debug.py

This script verifies that each payload defined in your payloads_<lang>.json
only triggers (i.e. produces the expected output) on the engines it's assigned to,
and not on others. It checks both true positives and false positives.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.table import Table

from core.interface import start_worker, run_worker

console = Console()

def load_payloads(path: Path) -> Dict[str, Dict]:
    if not path.is_file():
        console.print(f"[red]❌ File not found: {path}[/red]")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ JSON error in {path}: {e}[/red]")
        sys.exit(1)

def validate_language(lang: str):
    """Cross-validate payloads for a given language."""
    path = Path(f"payloads_{lang}.json")
    db = load_payloads(path)
    engines = [e.lower() for e in db.keys()]
    console.print(f"\n[bold underline]Cross-validation ({lang.upper()})[/bold underline]")

    # Start persistent worker
    start_worker(lang, engines)

    # Build a mapping from payloads to engines and expected output
    payload_map = {}
    for engine, info in db.items():
        for payload, expected in info.get("payloads", {}).items():
            payload_map.setdefault(payload, {})[engine.lower()] = str(expected)

    total_ok = 0
    total_tests = 0
    false_negatives = []
    false_positives = []

    for payload, expected_map in payload_map.items():
        results = run_worker(lang, payload, engines)
        for engine in engines:
            actual = str(results.get(engine, "")).strip()
            if engine in expected_map:
                # Should match expected
                total_tests += 1
                if actual == expected_map[engine]:
                    total_ok += 1
                else:
                    false_negatives.append((payload, engine, expected_map[engine], actual))
            else:
                # Should NOT match any expected values
                if actual in expected_map.values():
                    false_positives.append((payload, engine, actual))

    # Report
    console.print(f"  • Success: [green]{total_ok}[/green] out of [bold]{total_tests}[/bold] expected checks")
    
    if false_negatives:
        console.print(f"  • False Negatives (expected match failed): [red]{len(false_negatives)}[/red]")
        table = Table("Payload", "Engine", "Expected", "Actual", show_lines=True)
        for p, e, expected, actual in false_negatives:
            table.add_row(p, e, expected, actual)
        console.print(table)

    if false_positives:
        console.print(f"  • False Positives (unexpected match): [red]{len(false_positives)}[/red]")
        table = Table("Payload", "Engine", "Unexpected Value", show_lines=True)
        for p, e, val in false_positives:
            table.add_row(p, e, val)
        console.print(table)

    if not false_negatives and not false_positives:
        console.print("[green]✔ All payloads are unique and correctly scoped[/green]")

def main():
    # Languages to validate (can be adjusted)
    langs = ["node", "php", "ruby", "python", "java"]
    for lang in langs:
        validate_language(lang)

if __name__ == "__main__":
    main()
