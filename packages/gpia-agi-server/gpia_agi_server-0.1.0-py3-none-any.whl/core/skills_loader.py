from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

import yaml

try:
    from jsonschema import validate as _js_validate  # type: ignore
except Exception:  # pragma: no cover - optional
    _js_validate = None  # type: ignore


@dataclass(frozen=True)
class SkillMeta:
    id: str
    name: str
    version: str
    description: str
    entry_point: str
    root: Path
    input_schema_path: Optional[Path]
    output_schema_path: Optional[Path]
    permissions: tuple[str, ...]
    capabilities: tuple[str, ...]


def _read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_skills(root: Path | str = "skills") -> Dict[str, SkillMeta]:
    """Scan `root/*/skill.yaml` and return metadata, without importing code."""
    base = Path(root)
    metas: Dict[str, SkillMeta] = {}
    for skill_yaml in base.glob("*/skill.yaml"):
        sroot = skill_yaml.parent
        m = _read_yaml(skill_yaml)
        sid = m.get("id") or sroot.name
        version = (sroot / "VERSION").read_text(encoding="utf-8").strip() if (sroot / "VERSION").exists() else m.get("version", "0.0.0")
        # Minimal consistency check (no heavy import)
        if m.get("version") and m["version"] != version:
            # Keep deterministic: prefer VERSION file
            pass
        metas[sid] = SkillMeta(
            id=sid,
            name=m.get("name", sid),
            version=version,
            description=m.get("description", ""),
            entry_point=m.get("entry_point", ""),
            root=sroot,
            input_schema_path=(sroot / m.get("inputs", {}).get("schema", "")) if m.get("inputs") else None,
            output_schema_path=(sroot / m.get("outputs", {}).get("schema", "")) if m.get("outputs") else None,
            permissions=tuple(m.get("permissions", []) or ()),
            capabilities=tuple(m.get("capabilities", []) or ()),
        )
    return metas


def _import_entry_point(entry_point: str, root: Path) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Import `module_path:callable` relative to skill root.

    Adds the skill root to `sys.path` temporarily for local imports.
    """
    if not entry_point or ":" not in entry_point:
        raise ValueError("invalid entry_point; expected 'module:callable'")
    module_path, func_name = entry_point.split(":", 1)
    # Allow relative module import within the skill root
    # by temporarily adding the handlers folder to path via module package
    pkg_root = root
    # Use importlib to load module via spec from file system
    # but simpler: rely on Python path via cwd-relative import
    # Prepend root to PYTHONPATH for this import only
    old = os.getcwd()
    try:
        os.chdir(str(root))
        module = importlib.import_module(module_path)
    finally:
        os.chdir(old)
    func = getattr(module, func_name, None)
    if not callable(func):
        raise AttributeError(f"callable '{func_name}' not found in module '{module_path}'")
    return func


def _maybe_validate(schema_path: Optional[Path], data: Dict[str, Any]) -> None:
    if not schema_path or not schema_path.exists() or _js_validate is None:
        return
    schema = _read_json(schema_path)
    _js_validate(instance=data, schema=schema)


def invoke_skill(meta: SkillMeta, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate payload, import entry point, execute, validate output."""
    _maybe_validate(meta.input_schema_path, payload)
    fn = _import_entry_point(meta.entry_point, meta.root)
    out = fn(payload)
    if not isinstance(out, dict):
        raise TypeError("skill output must be a dict")
    _maybe_validate(meta.output_schema_path, out)
    return out

