import argparse
import json
import subprocess
from pathlib import Path


def list_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    if result.returncode != 0:
        return []
    lines = (result.stdout or "").strip().splitlines()
    if len(lines) <= 1:
        return []
    models = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0].strip())
    return models


def pick(preferences, available):
    for name in preferences:
        if name in available:
            return name
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend an Ollama model and tuning preset")
    parser.add_argument("--task", default="reasoning")
    parser.add_argument("--presets", default=str(Path(__file__).parent.parent / "references" / "presets.json"))
    parser.add_argument("--output")
    args = parser.parse_args()

    presets = json.loads(Path(args.presets).read_text(encoding="utf-8"))
    available = list_models()

    tasks = presets.get("tasks", {})
    params = presets.get("params", {})

    preferences = tasks.get(args.task, tasks.get("reasoning", []))
    recommended = pick(preferences, available)
    backup = pick(preferences[1:], available) if preferences else None

    if not recommended:
        recommended = available[0] if available else None
    if not backup:
        backup = available[1] if available and len(available) > 1 else None

    output = {
        "task": args.task,
        "available": available,
        "recommended": recommended,
        "backup": backup,
        "params": params.get(args.task, params.get("reasoning", {})),
    }

    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
