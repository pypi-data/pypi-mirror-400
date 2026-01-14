from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "memory" / "agent_state_v1"
TELEMETRY_LOG = LEDGER_DIR / "telemetry.jsonl"

try:
    from . import heuristics_registry

    HEURISTICS_AVAILABLE = True
except Exception:
    heuristics_registry = None
    HEURISTICS_AVAILABLE = False

@dataclass
class TelemetrySnapshot:
    timestamp: int
    cpu_percent: Optional[float]
    ram_total_mb: Optional[int]
    ram_used_mb: Optional[int]
    vram_total_mb: Optional[int]
    vram_used_mb: Optional[int]
    net_bytes_sent: Optional[int]
    net_bytes_recv: Optional[int]

    @property
    def vram_util(self) -> Optional[float]:
        if self.vram_total_mb and self.vram_used_mb is not None:
            return self.vram_used_mb / max(self.vram_total_mb, 1)
        return None

    @property
    def ram_util(self) -> Optional[float]:
        if self.ram_total_mb and self.ram_used_mb is not None:
            return self.ram_used_mb / max(self.ram_total_mb, 1)
        return None


@dataclass
class BudgetDecision:
    ok: bool
    status: str
    reasons: Tuple[str, ...]
    requires_model_shed: bool


MODEL_SHED_ORDER = [
    "gpia-gpt-oss:20b",
    "gpia-deepseek-r1:latest",
    "gpia-qwen3:latest",
    "gpia-codegemma:latest",
]


def _run_powershell(command: str, timeout: int = 5) -> Optional[str]:
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return None
        return (result.stdout or "").strip()
    except Exception:
        return None


def _get_memory_stats_mb() -> Tuple[Optional[int], Optional[int]]:
    try:
        import psutil  # type: ignore

        vm = psutil.virtual_memory()
        return int(vm.total / (1024 * 1024)), int(vm.used / (1024 * 1024))
    except Exception:
        pass

    system = platform.system().lower()
    if system == "windows":
        output = _run_powershell(
            "Get-CimInstance Win32_OperatingSystem | "
            "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"
        )
        if not output:
            return None, None
        try:
            data = json.loads(output)
            total_kb = int(data.get("TotalVisibleMemorySize", 0))
            free_kb = int(data.get("FreePhysicalMemory", 0))
            return total_kb // 1024, max((total_kb - free_kb) // 1024, 0)
        except Exception:
            return None, None

    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_pages = os.sysconf("SC_PHYS_PAGES")
        avail_pages = os.sysconf("SC_AVPHYS_PAGES")
        total_mb = int((page_size * total_pages) / (1024 * 1024))
        used_mb = total_mb - int((page_size * avail_pages) / (1024 * 1024))
        return total_mb, used_mb
    except Exception:
        return None, None


def _get_vram_stats_mb() -> Tuple[Optional[int], Optional[int]]:
    if shutil.which("nvidia-smi") is None:
        return None, None
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
            return None, None
        line = (result.stdout or "").strip().splitlines()[0]
        total_mb, used_mb = [int(x.strip()) for x in line.split(",")[:2]]
        return total_mb, used_mb
    except Exception:
        return None, None


def _get_cpu_percent() -> Optional[float]:
    try:
        import psutil  # type: ignore

        return float(psutil.cpu_percent(interval=0.1))
    except Exception:
        return None


def _get_network_bytes() -> Tuple[Optional[int], Optional[int]]:
    try:
        import psutil  # type: ignore

        counters = psutil.net_io_counters()
        return int(counters.bytes_sent), int(counters.bytes_recv)
    except Exception:
        return None, None


def sample_telemetry() -> TelemetrySnapshot:
    ram_total, ram_used = _get_memory_stats_mb()
    vram_total, vram_used = _get_vram_stats_mb()
    cpu = _get_cpu_percent()
    net_sent, net_recv = _get_network_bytes()
    return TelemetrySnapshot(
        timestamp=int(time.time()),
        cpu_percent=cpu,
        ram_total_mb=ram_total,
        ram_used_mb=ram_used,
        vram_total_mb=vram_total,
        vram_used_mb=vram_used,
        net_bytes_sent=net_sent,
        net_bytes_recv=net_recv,
    )


def log_telemetry(snapshot: TelemetrySnapshot) -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with TELEMETRY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot.__dict__) + "\n")


def _percent(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(value * 100, 2)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


LIMIT_BOUNDS = {
    "vram": (0.5, 0.98),
    "cpu": (0.5, 0.99),
    "ram": (0.5, 0.99),
}


def _limit_bounds(metric: str) -> Tuple[float, float]:
    return LIMIT_BOUNDS.get(metric, (0.5, 0.99))


def _resolve_limit(key: str, default_limit: float, metric: str) -> float:
    if not HEURISTICS_AVAILABLE:
        return default_limit
    stored = heuristics_registry.get_value(key, default=default_limit)
    if stored is None:
        stored = default_limit
    low, high = _limit_bounds(metric)
    effective = max(float(stored), default_limit)
    return _clamp(effective, low, high)


def _derive_limit(
    observed_util: Optional[float],
    default_limit: float,
    buffer_ratio: float,
    metric: str,
) -> float:
    if observed_util is None:
        return default_limit
    low, high = _limit_bounds(metric)
    target = max(default_limit, observed_util + buffer_ratio)
    return _clamp(target, low, high)


def _cpu_util(cpu_percent: Optional[float]) -> Optional[float]:
    if cpu_percent is None:
        return None
    return _clamp(cpu_percent / 100.0, 0.0, 1.0)


def evaluate_budget(snapshot: TelemetrySnapshot) -> BudgetDecision:
    vram_limit = _resolve_limit("telemetry.vram_limit", float(os.getenv("GPIA_VRAM_LIMIT", "0.85")), "vram")
    cpu_limit = _resolve_limit("telemetry.cpu_limit", float(os.getenv("GPIA_CPU_LIMIT", "0.90")), "cpu")
    ram_limit = _resolve_limit("telemetry.ram_limit", float(os.getenv("GPIA_RAM_LIMIT", "0.90")), "ram")

    reasons = []
    requires_shed = False

    if snapshot.vram_util is not None and snapshot.vram_util >= vram_limit:
        reasons.append(f"vram_util={snapshot.vram_util:.2f} >= {vram_limit:.2f}")
        requires_shed = True
    if snapshot.cpu_percent is not None and snapshot.cpu_percent >= cpu_limit * 100:
        reasons.append(f"cpu_percent={snapshot.cpu_percent:.1f} >= {cpu_limit*100:.1f}")
    if snapshot.ram_util is not None and snapshot.ram_util >= ram_limit:
        reasons.append(f"ram_util={snapshot.ram_util:.2f} >= {ram_limit:.2f}")

    if reasons:
        status = "warning" if not requires_shed else "critical"
        return BudgetDecision(False, status, tuple(reasons), requires_shed)
    return BudgetDecision(True, "ok", tuple(), False)


def recommend_model_shed(current_model: str) -> str:
    if not current_model:
        return current_model
    normalized = current_model.lower()
    for idx, model in enumerate(MODEL_SHED_ORDER):
        if model in normalized:
            return MODEL_SHED_ORDER[min(idx + 1, len(MODEL_SHED_ORDER) - 1)]
    return MODEL_SHED_ORDER[-1]


def telemetry_gate(current_model: str) -> Dict[str, object]:
    snapshot = sample_telemetry()
    log_telemetry(snapshot)
    decision = evaluate_budget(snapshot)
    if HEURISTICS_AVAILABLE:
        vram_default = float(os.getenv("GPIA_VRAM_LIMIT", "0.85"))
        cpu_default = float(os.getenv("GPIA_CPU_LIMIT", "0.90"))
        ram_default = float(os.getenv("GPIA_RAM_LIMIT", "0.90"))
        vram_buffer = float(os.getenv("GPIA_VRAM_BUFFER", "0.10"))
        cpu_buffer = float(os.getenv("GPIA_CPU_BUFFER", "0.05"))
        ram_buffer = float(os.getenv("GPIA_RAM_BUFFER", "0.05"))

        cpu_util = _cpu_util(snapshot.cpu_percent)
        vram_limit = _derive_limit(snapshot.vram_util, vram_default, vram_buffer, "vram")
        cpu_limit = _derive_limit(cpu_util, cpu_default, cpu_buffer, "cpu")
        ram_limit = _derive_limit(snapshot.ram_util, ram_default, ram_buffer, "ram")

        vram_low, vram_high = _limit_bounds("vram")
        cpu_low, cpu_high = _limit_bounds("cpu")
        ram_low, ram_high = _limit_bounds("ram")

        heuristics_registry.set_bounds("telemetry.vram_limit", min_value=vram_default, max_value=vram_high)
        heuristics_registry.set_bounds("telemetry.cpu_limit", min_value=cpu_default, max_value=cpu_high)
        heuristics_registry.set_bounds("telemetry.ram_limit", min_value=ram_default, max_value=ram_high)

        if snapshot.vram_util is not None:
            heuristics_registry.observe("telemetry.vram_limit", vram_limit)
        if cpu_util is not None:
            heuristics_registry.observe("telemetry.cpu_limit", cpu_limit)
        if snapshot.ram_util is not None:
            heuristics_registry.observe("telemetry.ram_limit", ram_limit)

    resources = {
        "vram_usage_pct": _percent(snapshot.vram_util),
        "cpu_load_pct": round(snapshot.cpu_percent, 2) if snapshot.cpu_percent is not None else None,
        "ram_usage_pct": _percent(snapshot.ram_util),
        "vram_used_mb": snapshot.vram_used_mb,
        "vram_total_mb": snapshot.vram_total_mb,
        "ram_used_mb": snapshot.ram_used_mb,
        "ram_total_mb": snapshot.ram_total_mb,
    }

    if decision.ok:
        return {"status": "ok", "reason": "budget_ok", "resources": resources}
    if decision.requires_model_shed:
        return {
            "status": "shed",
            "reason": "; ".join(decision.reasons),
            "model": recommend_model_shed(current_model),
            "resources": resources,
        }
    return {"status": "warning", "reason": "; ".join(decision.reasons), "resources": resources}
