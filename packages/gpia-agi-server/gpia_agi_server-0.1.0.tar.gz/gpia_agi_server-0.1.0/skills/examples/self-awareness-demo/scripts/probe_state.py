from __future__ import annotations

from typing import Any, Dict


def build_snapshot(signal: Dict[str, Any] | None) -> Dict[str, Any]:
    """Build a lightweight stability snapshot from input signals."""
    signal = signal or {}

    uptime_s = int(signal.get("uptime_s", 0))
    load = float(signal.get("load", 0.0))
    errors = int(signal.get("errors", 0))

    stable = errors == 0 and load < 0.8

    return {
        "uptime_s": uptime_s,
        "load": load,
        "errors": errors,
        "stable": stable,
    }
