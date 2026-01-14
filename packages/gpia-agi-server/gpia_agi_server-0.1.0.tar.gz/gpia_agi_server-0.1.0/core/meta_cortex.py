"""Meta-Cognitive Mirror (System 5) - introspection and proposal loop."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from skills.base import SkillContext
from skills.registry import get_registry


class MetaCortex:
    """Observes thought packets and proposes reflex improvements."""

    def __init__(self, root_dir: Path, state_dir: Optional[Path] = None):
        self.root_dir = Path(root_dir)
        self.state_dir = state_dir or (self.root_dir / "memory" / "meta_state_v1")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.self_model_path = self.state_dir / "self_model.json"
        self.alignment_log = self.state_dir / "alignment_tracker.log"
        self.thought_log = self.state_dir / "thought_packets.jsonl"
        self.registry = get_registry()
        self.context = SkillContext(agent_role="meta_cortex")
        self._ensure_self_model()

    def _ensure_self_model(self) -> None:
        if not self.self_model_path.exists():
            self.self_model_path.write_text(
                json.dumps({
                    "version": 1.0,
                    "self_perception": {"strengths": [], "weaknesses": []},
                    "correction_state": {"active_patches": [], "last_updated": time.time()},
                }, indent=2),
                encoding="utf-8",
            )

    def observe_thought(self, packet: Dict[str, Any], outcome: Dict[str, Any]) -> float:
        """Compute delta between intent and outcome, update self model, and propose fixes."""
        intent = float(packet.get("confidence_score", 0.5))
        reality = float(outcome.get("success_score", 0.5))
        delta = abs(intent - reality)

        self._log_thought(packet, outcome, delta)

        if delta > 0.3:
            weakness = self._update_self_model(packet.get("origin_skill", "unknown"), delta, reality < intent)
            if weakness:
                patch = self._propose_patch(weakness)
                if patch:
                    self._validate_patch(patch)

        return delta

    def _log_thought(self, packet: Dict[str, Any], outcome: Dict[str, Any], delta: float) -> None:
        entry = {
            "ts": time.time(),
            "thought_id": packet.get("thought_id"),
            "origin_skill": packet.get("origin_skill"),
            "confidence_score": packet.get("confidence_score"),
            "success_score": outcome.get("success_score"),
            "delta": delta,
        }
        try:
            with self.thought_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
        except OSError:
            pass

    def _update_self_model(self, skill_id: str, delta: float, overestimated: bool) -> Optional[Dict[str, Any]]:
        try:
            model = json.loads(self.self_model_path.read_text(encoding="utf-8"))
        except Exception:
            model = {
                "version": 1.0,
                "self_perception": {"strengths": [], "weaknesses": []},
                "correction_state": {"active_patches": [], "last_updated": time.time()},
            }

        entry = {"skill": skill_id, "delta": delta, "ts": time.time()}
        target = model.setdefault("self_perception", {}).setdefault("weaknesses" if overestimated else "strengths", [])
        target.append(entry)
        model.setdefault("correction_state", {}).setdefault("last_updated", time.time())

        try:
            self.self_model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
        except OSError:
            return None

        if overestimated:
            self._log_alignment_conflict(entry, delta)
            return entry
        return None

    def _log_alignment_conflict(self, entry: Dict[str, Any], delta: float) -> None:
        payload = {
            "ts": time.time(),
            "thought_id": entry.get("ts"),
            "delta": delta,
            "volition": entry.get("delta"),
            "outcome": "overestimated",
        }
        try:
            with self.alignment_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        except OSError:
            pass

    def _propose_patch(self, weakness: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        skill = self.registry.get_skill("cognition/proposal-synthesizer")
        if not skill:
            return None
        result = skill.execute(
            {"capability": "draft_reflex_edit_v1", "weakness": weakness},
            self.context,
        )
        if not result.success:
            return None
        return (result.output or {}).get("patch")

    def _validate_patch(self, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        skill = self.registry.get_skill("system/reflex-patch-validator")
        if not skill:
            return None
        result = skill.execute(
            {"capability": "simulate_shadow_run", "patch": patch},
            self.context,
        )
        if not result.success:
            return None
        return result.output


__all__ = ["MetaCortex"]
