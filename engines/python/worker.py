#!/usr/bin/env python3
import sys
import os
import json
import importlib.util
import concurrent.futures

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    sys.stdout.flush = sys.stdout.write

current_dir = os.path.dirname(os.path.abspath(__file__))
engines_path = os.path.join(current_dir, "engines.py")
spec = importlib.util.spec_from_file_location("engines_python", engines_path)
eng_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eng_mod)
ENGINES = eng_mod.ENGINES

if len(sys.argv) > 1:
    requested = sys.argv[1].split(",")
else:
    requested = list(ENGINES.keys())

sys.stderr.write(f"✅ {len(requested)} engine(s) ready: {', '.join(requested)}\n")

def render_with_engine(name: str, tpl: str) -> tuple[str, str]:
    fn = ENGINES.get(name)
    if not fn:
        return name, f"❌ Unknown engine: {name}"
    try:
        return name, fn(tpl)
    except Exception as e:
        return name, f"❌ {e}"

for line in sys.stdin:
    tpl = line.rstrip("\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(render_with_engine, name, tpl): name for name in requested}
        results = {name: future.result()[1] for future, name in zip(futures.keys(), requested)}

    sys.stdout.write(json.dumps(results, ensure_ascii=False) + "\n")
    sys.stdout.write("__END__\n")
    sys.stdout.flush()
