#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, Tuple


def _is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _infer_bounds(value: float) -> Tuple[float, float]:
    if 0 <= value <= 1:
        return 0.0, 1.0
    if value > 1:
        upper = max(value * 4, value + 1)
        return 0.0, float(upper)
    lower = min(value * 4, value - 1)
    return float(lower), 0.0


def _load_bottlenecks(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="runs/heuristics_bottlenecks.json")
    parser.add_argument("--output", default="memory/agent_state_v1/heuristics.json")
    parser.add_argument("--alpha", type=float, default=0.1)
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = _load_bottlenecks(input_path)
    items = payload.get("items", [])

    entries: Dict[str, Dict[str, Any]] = {}
    for item in items:
        key = item.get("heuristic_key")
        value = item.get("value")
        if not key or not _is_numeric(value):
            continue
        min_value, max_value = _infer_bounds(float(value))
        entries[key] = {
            "value": float(value),
            "min": min_value,
            "max": max_value,
            "alpha": float(args.alpha),
            "count": 0,
            "source": f"{item.get('file')}:{item.get('line')}",
            "kind": item.get("kind"),
        }

    registry = {
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entries": entries,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    print(f"Wrote heuristic registry: {output_path} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

