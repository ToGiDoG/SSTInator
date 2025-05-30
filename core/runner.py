# core/runner.py

import sys
import json
import os
import atexit
import readline
import concurrent.futures
from pathlib import Path
from typing import List, Optional, Dict, Set

from rich.console import Console

from core.discriminator import interactive_discriminate
from core.interface import start_worker, run_worker
from core.utils import make_result_table

# History file for user input
HISTORY_FILE = os.path.expanduser("~/.ssti_playground_history")

# Load command history if available
try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass

# Save command history at exit
atexit.register(readline.write_history_file, HISTORY_FILE)

# Enable autocomplete with TAB
readline.parse_and_bind("tab: complete")

console = Console()

def load_json(path: Path) -> dict:
    if not path.is_file():
        console.print(f"[red]❌ File not found: {path}[/red]")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ JSON error in {path}: {e}[/red]")
        sys.exit(1)

def run(
    engines_arg: Optional[str],
    lang_arg: Optional[str],
    do_discriminate: bool
):
    # 1) Determine target languages
    langs: List[str] = (
        [l.strip().lower() for l in lang_arg.split(",")]
        if lang_arg else ["node", "php", "ruby", "python", "java"]
    )

    # 2) Parse requested engines (-e)
    engines_arg_list = [e.strip().lower() for e in engines_arg.split(",")] if engines_arg else None

    loaded_engines: Dict[str, List[str]] = {}

    def load_lang_engines(lang: str) -> tuple[str, List[str]]:
        start_worker(lang)
        engines_to_request = engines_arg_list if engines_arg_list else None
        info = run_worker(lang, "", engines=engines_to_request) or {}
        return lang, sorted(info.keys())

    # 3) Load engines in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(load_lang_engines, lang): lang for lang in langs}
        for future in concurrent.futures.as_completed(futures):
            lang, engines = future.result()
            loaded_engines[lang] = engines

    # 4) Load and merge all payload databases
    all_dbs: Dict[str, dict] = {}
    for lang in langs:
        path = Path(f"payloads/payloads_{lang}.json")
        db = load_json(path)
        for engine, data in db.items():
            all_dbs[engine.lower()] = {
                "payloads": data.get("payloads", {}),
                "exploit": data.get("exploit"),
                "__lang": lang
            }

    # 5) Add engines without payloads JSON
    for lang, engines in loaded_engines.items():
        for eng in engines:
            if eng not in all_dbs:
                all_dbs[eng] = {"payloads": {}, "exploit": None, "__lang": lang}

    # 6) Build initial engine list
    initial: Set[str] = set()
    for lang in langs:
        if engines_arg_list:
            initial.update([e for e in loaded_engines[lang] if e in engines_arg_list])
        else:
            initial.update(loaded_engines[lang])

    # 7) Run discrimination if requested
    if do_discriminate:
        final: Set[str] = interactive_discriminate(
            db=all_dbs,
            engines=initial,
            field="payloads"
        )
        if not final:
            console.print("[red]❌ No matching engine after discrimination.[/red]")
            sys.exit(1)
        console.print(f"\n✅ After discrimination: [green]{', '.join(sorted(final))}[/green]\n")
        selected = final
    else:
        selected = initial

    # 8) Show exploits if requested
    if engines_arg or do_discriminate:
        console.print("\n🔓 Available exploits:\n")
        for eng in sorted(selected):
            exp = all_dbs[eng].get("exploit")
            if exp:
                if isinstance(exp, dict):
                    console.print(f"- {eng}:", markup=False)
                    for k, v in exp.items():
                        console.print(f"    • {k} → {v}", markup=False)
                else:
                    console.print(f"- [cyan]{eng}[/cyan]: {exp}")
            else:
                console.print(f"- [cyan]{eng}[/cyan]: [yellow]No PoC available[/yellow]")

    # 9) Group selected engines by language
    engines_for_lang = {lang: [] for lang in langs}
    for engine in selected:
        lang = all_dbs[engine]["__lang"]
        engines_for_lang[lang].append(engine)

    console.print("\n[bold]Type ‘exit’ to quit.[/bold]\n")

    # 10) Interactive REPL loop
    while True:
        console.print()
        cmd = input("🧪 Template > ").strip()
        console.print()

        if cmd.lower() == "exit":
            break

        if cmd in ("?", "help"):
            console.print("""\
[bold]Available commands:[/bold]

 help / ?         → Show this help message
 ?engines         → List active engines
 ?payloads        → Show all payloads and exploits
 <template>       → Send a template to all engines
 exit             → Exit the program\
""")
            continue

        if cmd == "?engines":
            console.print("[bold]Active engines:[/bold]\n")
            for eng in sorted(selected):
                console.print(f" • {eng}", markup=False)
            continue

        if cmd == "?payloads":
            console.print("[bold]All payloads and exploits:[/bold]\n")
            for idx, eng in enumerate(sorted(selected)):
                if idx > 0:
                    console.rule("", style="dim")
                console.print(f"[cyan]{eng}[/cyan]:\n")
                for p in all_dbs[eng]["payloads"].keys():
                    console.print(f"  • {p}", markup=False)
                exp = all_dbs[eng].get("exploit")
                if exp:
                    console.print("\n  [yellow]Exploit:[/yellow]\n")
                    if isinstance(exp, dict):
                        for k, v in exp.items():
                            console.print(f"    – {k} → {v}", markup=False)
                    else:
                        console.print(f"    – {exp}", markup=False)
                console.print()
            continue

        # Send template to selected engines
        for lang in langs:
            engines = engines_for_lang.get(lang, [])
            if not engines:
                continue
            result = run_worker(lang, cmd, engines)
            if result:
                console.print(make_result_table(lang, result))
