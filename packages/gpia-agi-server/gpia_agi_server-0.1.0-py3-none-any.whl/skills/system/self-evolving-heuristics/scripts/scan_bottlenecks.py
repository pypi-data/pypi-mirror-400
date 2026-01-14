#!/usr/bin/env python3
import argparse
import ast
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

OP_MAP = {
    ast.Gt: ">",
    ast.Lt: "<",
    ast.GtE: ">=",
    ast.LtE: "<=",
    ast.Eq: "==",
    ast.NotEq: "!=",
}

THRESHOLD_NAME_RE = re.compile(
    r"(threshold|limit|max|min|timeout|ttl|window|budget|ratio|pct|percent|retries|retry|delay|sleep)",
    re.IGNORECASE,
)

DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def _is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _expr_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _expr_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return None


def _call_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _expr_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return None


def _line_snippet(lines: List[str], lineno: Optional[int]) -> str:
    if lineno and 1 <= lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ""


def _make_key(rel_path: str, kind: str, line: Optional[int], symbol: Optional[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", rel_path.lower()).strip("_")
    sym = "value"
    if symbol:
        sym = re.sub(r"[^a-z0-9]+", "_", symbol.lower()).strip("_")
    line_part = str(line) if line else "0"
    return f"{base}.{sym}.{kind}.{line_part}"


class BottleneckVisitor(ast.NodeVisitor):
    def __init__(self, rel_path: str, lines: List[str]) -> None:
        self.rel_path = rel_path
        self.lines = lines
        self.records: List[Dict[str, Any]] = []

    def _record(
        self,
        node: ast.AST,
        kind: str,
        value: Any,
        symbol: Optional[str] = None,
        operator: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        lineno = getattr(node, "lineno", None)
        col = getattr(node, "col_offset", None)
        snippet = _line_snippet(self.lines, lineno)
        key = _make_key(self.rel_path, kind, lineno, symbol)
        record = {
            "id": f"{self.rel_path}:{lineno}:{kind}:{symbol or 'value'}",
            "file": self.rel_path,
            "line": lineno,
            "col": col,
            "kind": kind,
            "symbol": symbol,
            "operator": operator,
            "value": value,
            "snippet": snippet,
            "heuristic_key": key,
            "note": note,
        }
        self.records.append(record)

    def visit_Compare(self, node: ast.Compare) -> None:
        left = _expr_name(node.left)
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(comp, ast.Constant) and _is_numeric(comp.value):
                op_str = OP_MAP.get(type(op))
                self._record(comp, "compare_threshold", comp.value, left, op_str)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Constant) and _is_numeric(node.value.value):
            for target in node.targets:
                name = _expr_name(target)
                if name and THRESHOLD_NAME_RE.search(name):
                    self._record(node, "assign_threshold", node.value.value, name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        if name in {"sleep", "time.sleep"} and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and _is_numeric(arg.value):
                self._record(node, "sleep_seconds", arg.value, "sleep")

        if name in {"os.getenv", "getenv", "os.environ.get", "environ.get"}:
            if len(node.args) >= 2:
                default_arg = node.args[1]
                if isinstance(default_arg, ast.Constant) and _is_numeric(default_arg.value):
                    key_name = None
                    if node.args and isinstance(node.args[0], ast.Constant):
                        key_name = str(node.args[0].value)
                    self._record(node, "env_default", default_arg.value, key_name)

        self.generic_visit(node)


def _iter_python_files(root: Path, excludes: set) -> List[Path]:
    paths: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        for name in filenames:
            if name.endswith(".py"):
                paths.append(Path(dirpath) / name)
    return paths


def _scan_file(path: Path, root: Path) -> List[Dict[str, Any]]:
    rel_path = path.relative_to(root).as_posix()
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    lines = content.splitlines()
    visitor = BottleneckVisitor(rel_path, lines)
    visitor.visit(tree)
    return visitor.records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="runs/heuristics_bottlenecks.json")
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.root).resolve()
    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude)

    items: List[Dict[str, Any]] = []
    for path in _iter_python_files(root, excludes):
        items.extend(_scan_file(path, root))

    counts: Dict[str, int] = {}
    for item in items:
        kind = item.get("kind", "unknown")
        counts[kind] = counts.get(kind, 0) + 1

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(root),
        "count": len(items),
        "counts_by_kind": counts,
        "items": items,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Wrote bottleneck report: {output_path} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

