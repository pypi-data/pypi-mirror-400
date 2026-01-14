"""Reflex Engine (System 1) - deterministic host-level control primitives."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml


@dataclass
class ReflexModule:
    """Loaded reflex module metadata."""
    reflex_id: str
    path: Path
    priority: int
    layer: str
    version: str
    entry: Callable[..., Dict[str, Any]]
    policy: Optional[Dict[str, Any]]
    schema: Optional[Dict[str, Any]]


class ReflexEngine:
    """Deterministic pre-boot reflex execution chain."""

    DEFAULT_TIMEOUT_SECONDS = 0.05

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.registry_path = self.root_dir / "reflexes" / "registry.yaml"
        self.modules: List[ReflexModule] = []
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.audit_log = self.root_dir / "core" / "reflex_audit.log"
        self._load_registry_manifest()

    def _load_registry_manifest(self) -> None:
        """Load reflex registry and prepare execution chain."""
        if not self.registry_path.exists():
            return

        registry = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        reflexes = registry.get("reflexes", [])
        modules: List[ReflexModule] = []

        for entry in reflexes:
            if not entry or not entry.get("enabled", True):
                continue
            module_path = self.root_dir / entry["path"]
            manifest_path = module_path / "manifest.yaml"
            if not manifest_path.exists():
                continue

            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            version_tag = entry.get("version_tag")
            if version_tag and str(manifest.get("version")) != str(version_tag):
                continue

            entry_point = manifest.get("entry_point", "execute.py:run")
            module_file, func_name = entry_point.split(":", 1)
            module_file_path = module_path / module_file
            if not module_file_path.exists():
                continue

            runner = self._load_module_function(module_file_path, func_name)
            if runner is None:
                continue

            policy = self._load_optional_json(module_path / "policy.json")
            schema = self._load_optional_json(module_path / "schema.json")

            modules.append(ReflexModule(
                reflex_id=manifest.get("id", entry["id"]),
                path=module_path,
                priority=int(entry.get("priority", 100)),
                layer=str(entry.get("layer", "L3")),
                version=str(manifest.get("version", "0.0.0")),
                entry=runner,
                policy=policy,
                schema=schema,
            ))

        self.modules = self._build_execution_chain(modules)

    def _load_module_function(self, module_path: Path, func_name: str) -> Optional[Callable[..., Dict[str, Any]]]:
        """Load a module function from disk without package imports."""
        spec = importlib.util.spec_from_file_location(f"reflex_{module_path.stem}", module_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runner = getattr(module, func_name, None)
        if not callable(runner):
            return None
        return runner

    def _load_optional_json(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON config if present."""
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_execution_chain(self, modules: List[ReflexModule]) -> List[ReflexModule]:
        """Sort modules by layer and priority."""
        layer_rank = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
        return sorted(
            modules,
            key=lambda mod: (layer_rank.get(mod.layer, 3), mod.priority),
        )

    def _enforce_timeout(self, start: float, budget: float) -> bool:
        """Return True if within timeout budget."""
        return (time.perf_counter() - start) <= budget

    def _log_audit(self, payload: Dict[str, Any]) -> None:
        """Append audit entry."""
        try:
            self.audit_log.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        except OSError:
            return

    def _hash_input(self, task: str, context: Dict[str, Any]) -> str:
        """Compute deterministic hash of task and context."""
        normalized = json.dumps({"task": task, "context": context}, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reflex chain and return the first non-PASS action."""
        task = payload.get("task", "")
        context = payload.get("context", {}) or {}
        level = payload.get("level", "AUTO")
        flags = payload.get("flags", {}) or {}

        start = time.perf_counter()
        runtime = {
            "cache": self.cache,
            "input_hash": self._hash_input(task, context),
            "start_time": start,
            "budget": self.DEFAULT_TIMEOUT_SECONDS,
        }

        decision = {"action": "PASS", "payload": {}, "audit": {"level": level, "decision": "pass"}}

        for module in self.modules:
            if not self._enforce_timeout(start, self.DEFAULT_TIMEOUT_SECONDS):
                decision = {
                    "action": "PASS",
                    "payload": {"reason": "timeout"},
                    "audit": {"level": level, "decision": "timeout"},
                }
                break

            result = module.entry(
                task=task,
                context=context,
                level=level,
                flags=flags,
                runtime=runtime,
                manifest={
                    "id": module.reflex_id,
                    "version": module.version,
                    "layer": module.layer,
                },
                policy=module.policy or {},
                schema=module.schema or {},
            ) or {}

            action = str(result.get("action", "PASS")).upper()
            payload = result.get("payload", {}) if isinstance(result.get("payload"), dict) else {}
            audit = result.get("audit", {"level": level, "decision": "pass"})
            context_delta = result.get("context_delta", {})

            if context_delta:
                context.update(context_delta)

            decision = {"action": action, "payload": payload, "audit": audit, "context_delta": context_delta}
            runtime["last_decision"] = decision

            if action == "PASS":
                continue

            break

        decision["context"] = context
        decision["elapsed_ms"] = int((time.perf_counter() - start) * 1000)
        self._log_audit({
            "input_hash": runtime.get("input_hash"),
            "decision": decision.get("action"),
            "audit": decision.get("audit"),
            "elapsed_ms": decision.get("elapsed_ms"),
        })
        return decision
