"""Reflex patch synthesis and validation for Meta-Cognitive Mirror."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


class ReflexCorrector:
    """Converts weakness signals into reflex patch proposals."""

    def __init__(self, reflexes_dir: str = "reflexes/"):
        self.reflexes_dir = Path(reflexes_dir)
        self.meta_dir = Path("memory/meta_state_v1")
        self.patch_log = self.meta_dir / "patch_registry.jsonl"
        self.self_model_path = self.meta_dir / "self_model.json"
        self.schema_path = Path("memory/schemas/reflex_patch_v1.json")
        self._ensure_paths()

    def _ensure_paths(self) -> None:
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        if not self.self_model_path.exists():
            self._write_self_model({
                "version": 1.0,
                "self_perception": {"strengths": [], "weaknesses": []},
                "correction_state": {"active_patches": [], "last_updated": time.time()},
            })

    def _write_self_model(self, model: Dict[str, Any]) -> None:
        self.self_model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    def _load_self_model(self) -> Dict[str, Any]:
        try:
            return json.loads(self.self_model_path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "version": 1.0,
                "self_perception": {"strengths": [], "weaknesses": []},
                "correction_state": {"active_patches": [], "last_updated": time.time()},
            }

    def _log_patch(self, patch: Dict[str, Any]) -> None:
        with self.patch_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(patch, ensure_ascii=True) + "\n")

    def _validate_patch_schema(self, patch: Dict[str, Any]) -> bool:
        """Minimal schema validation against reflex_patch_v1.json."""
        if not isinstance(patch, dict):
            return False
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        required = schema.get("required", [])
        for key in required:
            if key not in patch:
                return False
        if not isinstance(patch.get("justification_bundle"), dict):
            return False
        if not isinstance(patch.get("diff"), dict):
            return False
        bundle = patch.get("justification_bundle", {})
        for key in ["historical_failure_rate", "average_delta", "observed_bias"]:
            if key not in bundle:
                return False
        if "validation_status" in patch:
            allowed = schema.get("properties", {}).get("validation_status", {}).get("enum")
            if allowed and patch["validation_status"] not in allowed:
                return False
        return True

    def _register_patch(self, patch: Dict[str, Any]) -> None:
        model = self._load_self_model()
        correction_state = model.setdefault("correction_state", {})
        active = correction_state.setdefault("active_patches", [])
        active.append({
            "patch_id": patch.get("patch_id"),
            "target_reflex_id": patch.get("target_reflex_id"),
            "status": patch.get("validation_status", "PENDING"),
            "ts": patch.get("ts"),
        })
        correction_state["last_updated"] = time.time()
        self._write_self_model(model)

    def propose_correction(self, weakness: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synthesizes a patch proposal based on a weakness entry."""
        skill_id = weakness.get("skill") or weakness.get("skill_id") or "unknown"
        delta = float(weakness.get("delta", weakness.get("delta_avg", 0.0)))
        if delta < 0.3:
            return None

        patch = {
            "patch_id": str(uuid.uuid4()),
            "target_reflex_id": f"reflex_{str(skill_id).replace('/', '_')}",
            "justification_bundle": {
                "historical_failure_rate": float(weakness.get("failure_rate", delta)),
                "average_delta": delta,
                "observed_bias": weakness.get("observed_bias", "Execution/Inference Mismatch"),
            },
            "diff": {
                "priority_adjustment": 1,
                "updated_policy_rules": [
                    "Require double-check on high-delta outputs."
                ],
            },
            "validation_status": "PENDING",
            "ts": time.time(),
        }

        if not self._validate_patch_schema(patch):
            return None

        self._log_patch(patch)
        self._register_patch(patch)
        return patch

    def validate_patch(self, patch: Dict[str, Any]) -> bool:
        """Simulated validation for a proposed patch."""
        if not self._validate_patch_schema(patch):
            return False
        target = str(patch.get("target_reflex_id", "")).lower()
        if "l4" in target or "safety" in target:
            patch["validation_status"] = "REJECTED"
            self._log_patch(patch)
            return False

        patch["validation_status"] = "SIMULATED"
        self._log_patch(patch)
        return True


if __name__ == "__main__":
    corrector = ReflexCorrector()
    model = corrector._load_self_model()
    weaknesses = model.get("self_perception", {}).get("weaknesses", [])
    for weakness in weaknesses:
        patch = corrector.propose_correction(weakness)
        if patch:
            corrector.validate_patch(patch)
