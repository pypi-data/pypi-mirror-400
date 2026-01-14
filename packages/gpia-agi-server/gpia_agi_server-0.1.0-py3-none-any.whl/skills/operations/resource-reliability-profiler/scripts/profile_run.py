import argparse
import json
import subprocess
import time
from pathlib import Path


def run_ps(command, timeout=5):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return None
        return (result.stdout or "").strip()
    except Exception:
        return None


def get_memory_stats_mb():
    output = run_ps(
        "Get-CimInstance Win32_OperatingSystem | "
        "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"
    )
    if not output:
        return {"total_mb": None, "free_mb": None}
    try:
        data = json.loads(output)
        total_kb = int(data.get("TotalVisibleMemorySize", 0))
        free_kb = int(data.get("FreePhysicalMemory", 0))
        return {"total_mb": total_kb // 1024, "free_mb": free_kb // 1024}
    except Exception:
        return {"total_mb": None, "free_mb": None}


def get_disk_write_bps():
    output = run_ps(
        "$val = (Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | "
        "Where-Object { $_.Name -eq '_Total' } | "
        "Select-Object -ExpandProperty DiskWriteBytesPerSec); "
        "if (-not $val) { "
        "$val = (Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | "
        "Select-Object -First 1 -ExpandProperty DiskWriteBytesPerSec) }; "
        "$val"
    )
    if not output:
        return None
    try:
        return int(float(output.strip().splitlines()[-1]))
    except Exception:
        return None


def get_vram_stats_mb():
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return {"total_mb": None, "free_mb": None}
        line = (result.stdout or "").strip().splitlines()[0]
        total_mb, used_mb = [int(x.strip()) for x in line.split(",")[:2]]
        return {"total_mb": total_mb, "free_mb": max(total_mb - used_mb, 0)}
    except Exception:
        return {"total_mb": None, "free_mb": None}


def main():
    parser = argparse.ArgumentParser(description="Run a command under resource budgets")
    parser.add_argument("--budget", required=True)
    parser.add_argument("--output", default="runs/profile_report.json")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise SystemExit("No command provided. Use -- <command>")

    budget = json.loads(Path(args.budget).read_text(encoding="utf-8"))
    max_duration = float(budget.get("max_duration_sec", 120))
    max_disk_write_bps = float(budget.get("max_disk_write_mbps", 50)) * 1024 * 1024
    min_free_ram_mb = float(budget.get("min_free_ram_mb", 4096))
    min_free_vram_mb = float(budget.get("min_free_vram_mb", 2048))
    interval = float(budget.get("sample_interval_sec", 1.0))

    proc = subprocess.Popen(args.command)
    start = time.time()
    samples = []
    violated = None

    while proc.poll() is None:
        elapsed = time.time() - start
        mem = get_memory_stats_mb()
        vram = get_vram_stats_mb()
        disk_bps = get_disk_write_bps()
        samples.append({
            "elapsed": elapsed,
            "mem": mem,
            "vram": vram,
            "disk_write_bps": disk_bps,
        })

        if elapsed > max_duration:
            violated = "max_duration_sec"
            break
        if mem.get("free_mb") is not None and mem["free_mb"] < min_free_ram_mb:
            violated = "min_free_ram_mb"
            break
        if vram.get("free_mb") is not None and vram["free_mb"] < min_free_vram_mb:
            violated = "min_free_vram_mb"
            break
        if disk_bps is not None and disk_bps > max_disk_write_bps:
            violated = "max_disk_write_mbps"
            break

        time.sleep(interval)

    if violated:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    report = {
        "command": args.command,
        "violated": violated,
        "returncode": proc.poll(),
        "samples": samples[-10:],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
