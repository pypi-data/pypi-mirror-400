import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def run_ollama(model, prompt, timeout):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "").strip())
    return (result.stdout or "").strip()


def check_task(response, task):
    expects = task.get("expected_contains", [])
    regexes = task.get("expected_regex", [])
    ok = True
    text = response.lower()
    for item in expects:
        if item.lower() not in text:
            ok = False
    for pattern in regexes:
        if not re.search(pattern, response, re.IGNORECASE):
            ok = False
    return ok


def load_tasks(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("tasks", [])


def main():
    parser = argparse.ArgumentParser(description="Run cross-domain generalization checks")
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--runner", choices=["none", "ollama"], default="none")
    parser.add_argument("--model", default="qwen3:latest")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--output", default="runs/generalization_report.json")
    args = parser.parse_args()

    tasks = load_tasks(args.tasks)
    results = []
    domain_totals = defaultdict(lambda: {"pass": 0, "total": 0})

    for task in tasks:
        domain = task.get("domain", "unknown")
        domain_totals[domain]["total"] += 1
        record = {"id": task.get("id"), "domain": domain, "prompt": task.get("prompt")}
        if args.runner == "none":
            record.update({"status": "skipped", "reason": "runner=none"})
        else:
            try:
                response = run_ollama(args.model, task.get("prompt", ""), args.timeout)
                passed = check_task(response, task)
                record.update({"status": "pass" if passed else "fail", "response": response[:500]})
                if passed:
                    domain_totals[domain]["pass"] += 1
            except Exception as exc:
                record.update({"status": "error", "error": str(exc)[:200]})
        results.append(record)

    summary = {
        "total": len(results),
        "domains": {
            key: {"pass": val["pass"], "total": val["total"]}
            for key, val in domain_totals.items()
        },
    }

    report = {"summary": summary, "results": results}
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
