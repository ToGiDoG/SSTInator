import subprocess
import json
from rich.console import Console

console = Console()
workers = {}

def start_worker(lang: str, engines=None):
    """
    Launch a persistent worker for the given language (`lang`),
    wait for its readiness message ("✅ ... engine(s) ready")
    before returning.
    """
    if lang in workers:
        return

    # 1) Determine the command to run
    if lang == "node":
        cmd = ["node", "engines/node/worker.js"]
    elif lang == "php":
        cmd = ["php", "engines/php/worker.php"]
    elif lang == "ruby":
        cmd = ["ruby", "engines/ruby/worker.rb"]
    elif lang == "python":
        cmd = ["python3", "engines/python/worker.py"]
    elif lang == "java":
        cmd = ["java", "-jar", "engines/java/target/java-worker-1.0-all.jar"]
    elif lang == "go":
        cmd = ["./engines/go/worker"]
    else:
        raise ValueError(f"Unsupported language: {lang}")

    if engines:
        cmd.append(",".join(engines))

    # 2) Start the subprocess
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    workers[lang] = proc

    # 3) Wait until the worker is ready
    while True:
        line = proc.stderr.readline()
        if not line:
            raise RuntimeError(f"Worker for {lang} exited prematurely")
        console.print(f"[grey]{line.strip()}[/grey]")
        if line.strip().startswith("✅"):
            break


def run_worker(lang: str, template: str, engines=None):
    """
    Sends a `template` to the already-started worker for `lang`
    and returns the parsed JSON result.
    """
    if lang not in workers:
        raise RuntimeError(f"Worker for {lang} is not running")

    proc = workers[lang]
    proc.stdin.write(template + "\n")
    proc.stdin.flush()

    # Read stdout until "__END__" delimiter
    lines = []
    while True:
        line = proc.stdout.readline()
        if not line or line.strip() == "__END__":
            break
        lines.append(line)

    # Extract and parse the JSON output
    try:
        candidate = next(l for l in reversed(lines) if l.strip().startswith("{"))
        result = json.loads(candidate)
        if engines:
            result = {k: v for k, v in result.items() if k in engines}
        return result

    except Exception as e:
        console.print(f"[red]❌ {lang.upper()} JSON parse error:[/red] {e}")
        console.print(f"[yellow]⛔ {lang.upper()} full output:[/yellow]\n" + "".join(lines))
        return {}
