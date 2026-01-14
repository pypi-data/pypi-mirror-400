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


def get_disk_free_mb():
    try:
        import shutil
        usage = shutil.disk_usage(Path.cwd())
        return int(usage.free / (1024 * 1024))
    except Exception:
        return None


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


def load_defaults(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data


def main():
    parser = argparse.ArgumentParser(description="Calibrate guardrail thresholds")
    parser.add_argument("--duration", type=int, default=20)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--defaults", default=str(Path(__file__).parent.parent / "references" / "guardrail_defaults.json"))
    parser.add_argument("--output", default="runs/guardrail_recommendations.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    defaults = load_defaults(args.defaults)
    mem = get_memory_stats_mb()
    vram = get_vram_stats_mb()
    disk_free_mb = get_disk_free_mb()

    samples = []
    start = time.time()
    while time.time() - start < args.duration:
        bps = get_disk_write_bps()
        if bps is not None:
            samples.append(bps)
        time.sleep(args.interval)

    if samples:
        samples_sorted = sorted(samples)
        p95 = samples_sorted[int(0.95 * (len(samples_sorted) - 1))]
        max_disk_write_bps = int(p95 * 1.5)
    else:
        max_disk_write_bps = int(defaults.get("max_disk_write_mbps_default", 50) * 1024 * 1024)

    total_ram = mem.get("total_mb") or 0
    total_vram = vram.get("total_mb") or 0
    try:
        import shutil
        total_disk_mb = int(shutil.disk_usage(Path.cwd()).total / (1024 * 1024))
    except Exception:
        total_disk_mb = 0

    min_free_ram_mb = max(int(total_ram * defaults.get("min_free_ram_ratio", 0.25)), defaults.get("min_free_ram_mb", 4096))
    min_free_vram_mb = max(int(total_vram * defaults.get("min_free_vram_ratio", 0.2)), defaults.get("min_free_vram_mb", 2048))
    min_free_disk_mb = max(int(total_disk_mb * defaults.get("min_free_disk_ratio", 0.05)), defaults.get("min_free_disk_mb", 102400))

    output = {
        "memory": mem,
        "vram": vram,
        "disk_free_mb": disk_free_mb,
        "samples": {"disk_write_bps": samples},
        "recommended": {
            "GPIA_MIN_FREE_RAM_MB": min_free_ram_mb,
            "GPIA_MIN_FREE_VRAM_MB": min_free_vram_mb,
            "GPIA_MIN_FREE_DISK_MB": min_free_disk_mb,
            "GPIA_MAX_DISK_WRITE_BPS": max_disk_write_bps,
        },
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    if args.apply:
        env_lines = [
            f"GPIA_MIN_FREE_RAM_MB={min_free_ram_mb}",
            f"GPIA_MIN_FREE_VRAM_MB={min_free_vram_mb}",
            f"GPIA_MIN_FREE_DISK_MB={min_free_disk_mb}",
            f"GPIA_MAX_DISK_WRITE_BPS={max_disk_write_bps}",
        ]
        Path(".env.guardrails").write_text("\n".join(env_lines) + "\n", encoding="utf-8")

    print(json.dumps(output["recommended"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
