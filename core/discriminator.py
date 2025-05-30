# core/discriminator.py

from typing import Dict, Set, Optional
from rich.console import Console
from rich.table import Table

console = Console()

def get_field_entries(
    db: Dict[str, dict],
    engines: Set[str],
    field: str
) -> Dict[str, Dict[str, str]]:
    """
    Builds a mapping of payload → { engine: expected_output, … }
    from db[engine][field].
    """
    mapping: Dict[str, Dict[str, str]] = {}
    for engine in engines:
        engine_table = db.get(engine, {}).get(field, {})
        for payload, expected_output in engine_table.items():
            mapping.setdefault(payload, {})[engine] = expected_output
    return mapping

def choose_best_payload(
    payload_map: Dict[str, Dict[str, str]],
    total_engines: int
) -> Optional[str]:
    """
    Among all payloads, choose the one that minimizes the largest group
    of engines producing the same result.
    """
    best_payload = None
    smallest_max_group = total_engines

    for payload, engine_map in payload_map.items():
        result_counts: Dict[str, int] = {}
        for result in engine_map.values():
            key = "__MISSING__" if result is None else str(result)
            result_counts[key] = result_counts.get(key, 0) + 1

        missing_engines = total_engines - len(engine_map)
        if missing_engines > 0:
            result_counts["__MISSING__"] = result_counts.get("__MISSING__", 0) + missing_engines

        largest_group_size = max(result_counts.values())
        if largest_group_size < smallest_max_group:
            smallest_max_group = largest_group_size
            best_payload = payload

    return best_payload if smallest_max_group < total_engines else None

def interactive_discriminate(
    db: Dict[str, dict],
    engines: Set[str],
    field: str = "discriminators"
) -> Set[str]:
    """
    Interactive loop to narrow down matching engines using test payloads
    from db[engine][field]. Returns the final set of matching engines.
    """
    candidates = set(engines)
    console.print(f"\n[bold]Starting engine discrimination (case sensitive)[/bold]\n")

    while len(candidates) > 1:
        payload_map = get_field_entries(db, candidates, field)
        payload = choose_best_payload(payload_map, len(candidates))
        if not payload:
            break

        console.print()
        console.print(f"🔍 Discriminator payload: {payload}", markup=False)
        console.print()
        user_input = input("> ").strip()

        for engine in list(candidates):
            expected = db.get(engine, {}).get(field, {}).get(payload)
            if user_input == "":
                if expected is not None:
                    candidates.remove(engine)
            else:
                if expected is None or str(expected) != user_input:
                    candidates.remove(engine)

        if not candidates:
            console.print("[red]❌ No matching engine found![/red]")
            return set()

    return candidates
