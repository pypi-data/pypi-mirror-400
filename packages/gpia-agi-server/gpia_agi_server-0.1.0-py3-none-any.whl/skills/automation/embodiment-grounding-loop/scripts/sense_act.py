import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_ps(command, timeout=5):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return None
        return (result.stdout or "").strip()
    except Exception:
        return None


def sensor_cpu_mem():
    output = run_ps(
        "Get-CimInstance Win32_OperatingSystem | "
        "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"
    )
    if not output:
        return None
    try:
        data = json.loads(output)
        return data
    except Exception:
        return None


def sensor_disk():
    try:
        import shutil
        usage = shutil.disk_usage(Path.cwd())
        return {"total": usage.total, "free": usage.free}
    except Exception:
        return None


def sensor_gpu():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None


def sensor_processes():
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        lines = (result.stdout or "").splitlines()[:6]
        return lines
    result = subprocess.run(["ps", "-eo", "pid,comm"], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return (result.stdout or "").splitlines()[:6]


def action_list_dir(path):
    return [p.name for p in Path(path).iterdir()][:20]


def action_read_file_head(path, lines):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return "\n".join(text.splitlines()[:lines])


def action_ping_http(url):
    if not url.startswith("http://localhost") and not url.startswith("http://127.0.0.1"):
        return "blocked"
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=5) as resp:
            return {"status": resp.status, "length": resp.length}
    except Exception as exc:
        return str(exc)


def main():
    parser = argparse.ArgumentParser(description="Run a safe sensor/actuator loop")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output", default="runs/embodiment_loop.json")
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    sensors = plan.get("sensors", [])
    actions = plan.get("actions", [])

    results = {"sensors": {}, "actions": []}

    for sensor in sensors:
        if sensor == "cpu_mem":
            results["sensors"][sensor] = sensor_cpu_mem()
        elif sensor == "disk":
            results["sensors"][sensor] = sensor_disk()
        elif sensor == "gpu":
            results["sensors"][sensor] = sensor_gpu()
        elif sensor == "processes":
            results["sensors"][sensor] = sensor_processes()

    for action in actions:
        kind = action.get("type")
        entry = {"type": kind, "status": "skipped"}
        try:
            if kind == "list_dir":
                entry.update({"status": "ok", "result": action_list_dir(action.get("path", "."))})
            elif kind == "read_file_head":
                entry.update({"status": "ok", "result": action_read_file_head(action.get("path"), int(action.get("lines", 5)))})
            elif kind == "ping_http":
                entry.update({"status": "ok", "result": action_ping_http(action.get("url", ""))})
        except Exception as exc:
            entry.update({"status": "error", "error": str(exc)})
        results["actions"].append(entry)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
