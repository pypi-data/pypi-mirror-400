from __future__ import annotations

import time
from typing import Any, Dict, Optional

from . import identity_checker, telemetry_observer


def run(current_model: Optional[str] = None) -> Dict[str, Any]:
    """Run mandatory sovereignty checks before planning."""
    identity_summary = identity_checker.run_self_consistency()
    if identity_summary.get("refuse", 0) > 0:
        return {
            "status": "blocked",
            "reason": "identity_refusal",
            "identity_summary": identity_summary,
            "timestamp": int(time.time()),
        }

    telemetry = telemetry_observer.telemetry_gate(current_model or "")
    result: Dict[str, Any] = {
        "status": telemetry.get("status", "ok"),
        "reason": telemetry.get("reason", ""),
        "identity_summary": identity_summary,
        "resources": telemetry.get("resources", {}),
        "timestamp": int(time.time()),
    }

    if telemetry.get("status") == "shed":
        model_hint = telemetry.get("model")
        result["model_hint"] = model_hint
        result["context_note"] = (
            f"Resource pressure detected; use lighter model {model_hint}."
            if model_hint
            else "Resource pressure detected; use a lighter model."
        )
    elif telemetry.get("status") == "warning":
        result["context_note"] = f"Resource pressure warning: {telemetry.get('reason', '')}".strip()

    return result
