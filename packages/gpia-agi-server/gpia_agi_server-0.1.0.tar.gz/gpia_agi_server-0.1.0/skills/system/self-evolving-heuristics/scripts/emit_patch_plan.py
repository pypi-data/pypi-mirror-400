#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict


def _load_bottlenecks(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_replacement(key: str, value: Any) -> str:
    return f"heuristics_registry.get_value(\"{key}\", default={value})"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="runs/heuristics_bottlenecks.json")
    parser.add_argument("--output", default="runs/heuristics_patch_plan.md")
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = _load_bottlenecks(input_path)
    items = payload.get("items", [])
    counts = payload.get("counts_by_kind", {})

    lines = []
    lines.append("# Heuristic Patch Plan")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append(f"Input: {input_path}")
    lines.append("")
    lines.append(f"Total candidates: {len(items)}")
    if counts:
        lines.append("Counts by kind:")
        for kind, count in sorted(counts.items()):
            lines.append(f"- {kind}: {count}")
    lines.append("")
    lines.append("## Candidates")

    for item in items:
        file_path = item.get("file")
        line = item.get("line")
        snippet = item.get("snippet") or ""
        key = item.get("heuristic_key")
        value = item.get("value")
        kind = item.get("kind")

        lines.append("")
        lines.append(f"### {file_path}:{line}")
        lines.append(f"Kind: {kind}")
        if snippet:
            lines.append(f"Snippet: `{snippet}`")
        if key:
            lines.append(f"Key: `{key}`")
        if key is not None:
            replacement = _format_replacement(key, value)
            lines.append("Suggested replacement:")
            lines.append(f"`{replacement}`")
        lines.append("Add an observation hook after execution:")
        lines.append(f"`heuristics_registry.observe(\"{key}\", observed_value)`")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote patch plan: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

