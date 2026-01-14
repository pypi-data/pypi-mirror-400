import json
import os
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


def _env_bool(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


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


def _get_memory_stats_mb() -> Dict[str, Optional[int]]:
    try:
        import psutil  # type: ignore

        vm = psutil.virtual_memory()
        return {
            "total_mb": int(vm.total / (1024 * 1024)),
            "free_mb": int(vm.available / (1024 * 1024)),
        }
    except Exception:
        pass

    system = platform.system().lower()
    if system == "windows":
        output = _run_powershell(
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

    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_pages = os.sysconf("SC_PHYS_PAGES")
        avail_pages = os.sysconf("SC_AVPHYS_PAGES")
        total_mb = int((page_size * total_pages) / (1024 * 1024))
        free_mb = int((page_size * avail_pages) / (1024 * 1024))
        return {"total_mb": total_mb, "free_mb": free_mb}
    except Exception:
        return {"total_mb": None, "free_mb": None}


def _get_vram_stats_mb() -> Dict[str, Optional[int]]:
    if shutil.which("nvidia-smi") is None:
        return {"total_mb": None, "free_mb": None}
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


_RESOURCE_CACHE: Dict[str, Any] = {"timestamp": 0.0, "data": None}


def _get_resource_snapshot(ttl_seconds: int) -> Dict[str, Optional[int]]:
    now = time.time()
    cached = _RESOURCE_CACHE.get("data")
    if cached and (now - _RESOURCE_CACHE.get("timestamp", 0) < ttl_seconds):
        return cached

    mem = _get_memory_stats_mb()
    vram = _get_vram_stats_mb()
    snapshot = {
        "ram_total_mb": mem.get("total_mb"),
        "ram_free_mb": mem.get("free_mb"),
        "vram_total_mb": vram.get("total_mb"),
        "vram_free_mb": vram.get("free_mb"),
        "timestamp": int(now),
    }
    _RESOURCE_CACHE["timestamp"] = now
    _RESOURCE_CACHE["data"] = snapshot
    return snapshot


def _estimate_prompt_tokens(prompt: str) -> int:
    if not prompt:
        return 0
    return max(1, int(len(prompt) / 4))


def _model_factor(model_id: Optional[str]) -> float:
    if not model_id:
        return 1.0
    model_id = model_id.lower()
    if "gpt-oss" in model_id or "20b" in model_id:
        return 0.6
    if "deepseek" in model_id:
        return 0.8
    if "qwen" in model_id:
        return 0.9
    if "llava" in model_id:
        return 0.8
    return 1.0


@dataclass
class BudgetSettings:
    enabled: bool
    profile: str
    min_tokens: int
    max_tokens: int
    allow_upscale: bool
    prompt_ratio: float
    tokens_per_gb_ram: int
    tokens_per_gb_vram: int
    reserve_ram_mb: int
    reserve_vram_mb: int
    resource_ttl: int
    log_decisions: bool
    profile_factors: Dict[str, float]

    @classmethod
    def from_env(cls) -> "BudgetSettings":
        return cls(
            enabled=_env_bool("GPIA_DYNAMIC_BUDGET", "1"),
            profile=os.getenv("GPIA_BUDGET_PROFILE", "balanced"),
            min_tokens=_env_int("GPIA_BUDGET_MIN_TOKENS", 128),
            max_tokens=_env_int("GPIA_BUDGET_MAX_TOKENS", 4096),
            allow_upscale=_env_bool("GPIA_BUDGET_ALLOW_UPSCALE", "0"),
            prompt_ratio=_env_float("GPIA_BUDGET_PROMPT_RATIO", 1.2),
            tokens_per_gb_ram=_env_int("GPIA_BUDGET_TOKENS_PER_GB_RAM", 256),
            tokens_per_gb_vram=_env_int("GPIA_BUDGET_TOKENS_PER_GB_VRAM", 384),
            reserve_ram_mb=_env_int("GPIA_BUDGET_RESERVE_RAM_MB", 2048),
            reserve_vram_mb=_env_int("GPIA_BUDGET_RESERVE_VRAM_MB", 1024),
            resource_ttl=_env_int("GPIA_BUDGET_RESOURCE_TTL", 20),
            log_decisions=_env_bool("GPIA_BUDGET_LOG", "0"),
            profile_factors={
                "safe": 0.6,
                "fast": 0.8,
                "balanced": 1.0,
                "quality": 1.25,
            },
        )


def compute_budget(
    prompt: str,
    requested_tokens: int,
    model_id: Optional[str] = None,
    profile: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    settings = BudgetSettings.from_env()
    requested_tokens = max(1, int(requested_tokens or settings.min_tokens))
    if not settings.enabled:
        return requested_tokens, {
            "reason": "disabled",
            "requested_tokens": requested_tokens,
        }

    profile = profile or settings.profile
    profile_factor = settings.profile_factors.get(profile, 1.0)
    prompt_tokens = _estimate_prompt_tokens(prompt)
    prompt_cap = max(settings.min_tokens, int(prompt_tokens * settings.prompt_ratio))

    snapshot = _get_resource_snapshot(settings.resource_ttl)
    model_factor = _model_factor(model_id)
    tokens_per_gb_ram = int(settings.tokens_per_gb_ram * model_factor)
    tokens_per_gb_vram = int(settings.tokens_per_gb_vram * model_factor)

    resource_caps = []
    ram_mb = snapshot.get("ram_free_mb") or snapshot.get("ram_total_mb")
    if ram_mb:
        usable_ram_mb = max(int(ram_mb) - settings.reserve_ram_mb, 0)
        resource_caps.append(int((usable_ram_mb / 1024.0) * tokens_per_gb_ram))

    vram_mb = snapshot.get("vram_free_mb") or snapshot.get("vram_total_mb")
    if vram_mb:
        usable_vram_mb = max(int(vram_mb) - settings.reserve_vram_mb, 0)
        resource_caps.append(int((usable_vram_mb / 1024.0) * tokens_per_gb_vram))

    resource_cap = min(resource_caps) if resource_caps else None
    adjusted = int(requested_tokens * profile_factor)

    caps = [adjusted, prompt_cap]
    if resource_cap is not None:
        caps.append(resource_cap)
    if settings.max_tokens > 0:
        caps.append(settings.max_tokens)
    if not settings.allow_upscale:
        caps.append(requested_tokens)

    effective = max(settings.min_tokens, min(caps))

    details = {
        "profile": profile,
        "profile_factor": profile_factor,
        "requested_tokens": requested_tokens,
        "adjusted_tokens": adjusted,
        "prompt_tokens": prompt_tokens,
        "prompt_cap": prompt_cap,
        "resource_cap": resource_cap,
        "min_tokens": settings.min_tokens,
        "max_tokens": settings.max_tokens,
        "allow_upscale": settings.allow_upscale,
        "model_factor": model_factor,
        "resource_snapshot": snapshot,
    }
    return effective, details


def apply_dynamic_budget(
    prompt: str,
    requested_tokens: int,
    model_id: Optional[str] = None,
    profile: Optional[str] = None,
) -> int:
    effective, details = compute_budget(
        prompt,
        requested_tokens,
        model_id=model_id,
        profile=profile,
    )
    settings = BudgetSettings.from_env()
    if settings.log_decisions:
        print(
            "[budget] requested={requested} effective={effective} profile={profile} "
            "prompt_cap={prompt_cap} resource_cap={resource_cap}".format(
                requested=details.get("requested_tokens"),
                effective=effective,
                profile=details.get("profile"),
                prompt_cap=details.get("prompt_cap"),
                resource_cap=details.get("resource_cap"),
            )
        )
    return effective
