#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _default_registry_path() -> Path:
    env_path = os.getenv("HEURISTICS_REGISTRY_PATH")
    if env_path:
        return Path(env_path)

    start = Path(__file__).resolve()
    for parent in [start] + list(start.parents):
        candidate = parent / "memory" / "agent_state_v1" / "heuristics.json"
        if candidate.exists():
            return candidate
    return start.parents[2] / "memory" / "agent_state_v1" / "heuristics.json"


def _infer_bounds(value: float) -> Tuple[float, float]:
    if 0 <= value <= 1:
        return 0.0, 1.0
    if value > 1:
        upper = max(value * 4, value + 1)
        return 0.0, float(upper)
    lower = min(value * 4, value - 1)
    return float(lower), 0.0


def _load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "entries": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_registry(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def get_value(key: str, default: Optional[float] = None, registry_path: Optional[Path] = None) -> Optional[float]:
    path = registry_path or _default_registry_path()
    data = _load_registry(path)
    entry = data.get("entries", {}).get(key)
    if not entry:
        return default
    return entry.get("value", default)


def observe(
    key: str,
    observed_value: float,
    registry_path: Optional[Path] = None,
    alpha: Optional[float] = None,
) -> None:
    if not _is_numeric(observed_value):
        return

    path = registry_path or _default_registry_path()
    data = _load_registry(path)
    entries = data.setdefault("entries", {})

    entry = entries.get(key)
    if not entry:
        min_value, max_value = _infer_bounds(float(observed_value))
        entry = {
            "value": float(observed_value),
            "min": min_value,
            "max": max_value,
            "alpha": float(alpha) if alpha is not None else 0.1,
            "count": 0,
        }
        entries[key] = entry

    if alpha is not None:
        entry["alpha"] = float(alpha)

    current = float(entry.get("value", observed_value))
    lr = float(entry.get("alpha", 0.1))
    updated = (1.0 - lr) * current + lr * float(observed_value)

    min_value = entry.get("min")
    max_value = entry.get("max")
    if min_value is not None:
        updated = max(float(min_value), updated)
    if max_value is not None:
        updated = min(float(max_value), updated)

    entry["value"] = updated
    entry["count"] = int(entry.get("count", 0)) + 1
    entry["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    _save_registry(path, data)


def record_outcome(
    key: str,
    reward: float,
    registry_path: Optional[Path] = None,
) -> None:
    if not _is_numeric(reward):
        return

    path = registry_path or _default_registry_path()
    data = _load_registry(path)
    entries = data.setdefault("entries", {})
    entry = entries.get(key)
    if not entry:
        entry = {"value": 0.0, "min": -1.0, "max": 1.0, "alpha": 0.1, "count": 0}
        entries[key] = entry

    entry["last_reward"] = float(reward)
    entry["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_registry(path, data)


def set_bounds(
    key: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    registry_path: Optional[Path] = None,
) -> None:
    if min_value is None and max_value is None:
        return

    path = registry_path or _default_registry_path()
    data = _load_registry(path)
    entries = data.setdefault("entries", {})
    entry = entries.get(key)

    if not entry:
        seed_value = min_value if min_value is not None else 0.0
        min_bound, max_bound = _infer_bounds(float(seed_value))
        entry = {
            "value": float(seed_value),
            "min": min_bound,
            "max": max_bound,
            "alpha": 0.1,
            "count": 0,
        }
        entries[key] = entry

    if min_value is not None:
        entry["min"] = float(min_value)
        entry["value"] = max(float(entry.get("value", min_value)), float(min_value))
    if max_value is not None:
        entry["max"] = float(max_value)
        entry["value"] = min(float(entry.get("value", max_value)), float(max_value))

    entry["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_registry(path, data)


__all__ = ["get_value", "observe", "record_outcome", "set_bounds"]

