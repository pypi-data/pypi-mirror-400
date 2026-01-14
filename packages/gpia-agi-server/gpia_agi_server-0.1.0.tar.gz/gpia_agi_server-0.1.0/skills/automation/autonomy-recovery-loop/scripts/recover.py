import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_PLAN = Path(__file__).parent.parent / "assets" / "recovery_plan.json"


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, (result.stdout or "") + (result.stderr or "")
    except Exception as exc:
        return False, str(exc)


def check_ollama():
    return run_cmd(["ollama", "list"], timeout=10)


def start_ollama():
    try:
        if os.name == "nt":
            flags = 0
            if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            if hasattr(subprocess, "DETACHED_PROCESS"):
                flags |= subprocess.DETACHED_PROCESS
            subprocess.Popen(["ollama", "serve"], creationflags=flags)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "started"
    except Exception as exc:
        return False, str(exc)


def run_benchmark(sections, extra_args):
    cmd = [sys.executable, "gpia_benchmark_suite.py"]
    if sections:
        cmd += ["--sections", sections]
    if extra_args:
        cmd += extra_args
    return run_cmd(cmd, timeout=300)


def main():
    parser = argparse.ArgumentParser(description="Recover from failed runs")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--auto-start", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", default="runs/recovery_report.json")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    steps = plan.get("steps", [])

    report = {"plan": str(plan_path), "steps": []}
    state = {"ollama_ok": None}

    for step in steps:
        kind = step.get("kind")
        entry = {"kind": kind, "status": "skipped"}
        if kind == "check_ollama":
            ok, output = check_ollama()
            state["ollama_ok"] = ok
            entry.update({"status": "ok" if ok else "fail", "detail": output.strip()[:300]})
        elif kind == "start_ollama":
            if not state.get("ollama_ok") and args.auto_start:
                if args.dry_run:
                    entry.update({"status": "dry_run"})
                else:
                    ok, detail = start_ollama()
                    time.sleep(2)
                    recheck, _ = check_ollama()
                    state["ollama_ok"] = recheck
                    entry.update({"status": "ok" if ok else "fail", "detail": detail, "recheck": recheck})
        elif kind == "run_benchmark":
            sections = step.get("sections", "")
            extra_args = step.get("args", [])
            if args.dry_run:
                entry.update({"status": "dry_run", "sections": sections, "args": extra_args})
            else:
                ok, output = run_benchmark(sections, extra_args)
                entry.update({"status": "ok" if ok else "fail", "sections": sections, "detail": output.strip()[:300]})
        report["steps"].append(entry)

    out_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
