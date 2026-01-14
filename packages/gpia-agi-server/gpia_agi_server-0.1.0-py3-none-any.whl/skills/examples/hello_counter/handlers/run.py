from __future__ import annotations

from typing import Dict, Any


def main(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Add increment to base and return result.

    Deterministic, side-effect free. Validates required keys minimally; full
    validation is expected to be handled by the loader via JSON Schema.
    """
    base = float(payload.get("base", 0))
    inc = float(payload.get("increment", 0))
    return {"result": base + inc}

