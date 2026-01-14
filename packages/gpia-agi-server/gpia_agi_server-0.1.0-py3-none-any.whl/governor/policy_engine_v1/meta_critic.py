"""Cognitive Governor v1 meta-critic for risk-weighted gating."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


IMPACT_SCORES = {
    "LOW": 2,
    "MEDIUM": 5,
    "HIGH": 8,
    "CRITICAL": 10,
}


@dataclass
class GovernorDecision:
    decision: str
    control_ratio: float
    risk_score: int
    reason: str
    step_results: List[Dict[str, Any]]


class MetaCritic:
    """Risk-weighted governor that decides when to require human approval."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.policy_dir = self.root_dir / "governor" / "policy_engine_v1"
        self.profile = self._load_json(self.policy_dir / "risk_profile.json")
        self.telemetry_path = self.policy_dir / "telemetry.log"

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _log(self, message: str, payload: Optional[Dict[str, Any]] = None) -> None:
        self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "message": message,
            "payload": payload or {},
        }
        try:
            with self.telemetry_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
        except OSError:
            return

    def compute_control_ratio(self, metrics: Dict[str, Any]) -> float:
        uncertainty = float(metrics.get("uncertainty", 0.2))
        recursion_depth = float(metrics.get("recursion_depth", 0.0))
        semantic_drift = float(metrics.get("semantic_drift", 0.0))
        cost_velocity = float(metrics.get("cost_velocity", 0.0))

        ratio = 1.0
        ratio -= min(max(uncertainty, 0.0), 1.0) * 0.45
        ratio -= min(recursion_depth / 5.0, 1.0) * 0.2
        ratio -= min(max(semantic_drift, 0.0), 1.0) * 0.2
        ratio -= min(max(cost_velocity, 0.0), 1.0) * 0.15
        return max(0.0, min(1.0, ratio))

    def _infer_impact(self, instruction: str) -> str:
        lowered = instruction.lower()
        destructive = ["delete", "remove", "wipe", "format", "rm -rf", "drop table"]
        if any(token in lowered for token in destructive):
            return "CRITICAL"
        high = ["move", "rename", "overwrite", "truncate"]
        if any(token in lowered for token in high):
            return "HIGH"
        medium = ["write", "create", "update", "append"]
        if any(token in lowered for token in medium):
            return "MEDIUM"
        return "LOW"

    def _infer_reversibility(self, impact: str) -> int:
        if impact == "CRITICAL":
            return 1
        if impact == "HIGH":
            return 3
        if impact == "MEDIUM":
            return 6
        return 9

    def assess_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        instruction = step.get("instruction") or step.get("operation") or ""
        predicted_impact = step.get("predicted_impact") or self._infer_impact(instruction)
        reversibility_score = int(step.get("reversibility_score") or self._infer_reversibility(predicted_impact))
        justification = step.get("safety_justification") or ""

        risk_score = IMPACT_SCORES.get(str(predicted_impact).upper(), 5)
        return {
            "step_id": step.get("id") or step.get("step_id") or "unknown",
            "instruction": instruction,
            "predicted_impact": str(predicted_impact).upper(),
            "reversibility_score": reversibility_score,
            "safety_justification": justification,
            "risk_score": risk_score,
        }

    def evaluate_plan(self, plan: Dict[str, Any], metrics: Dict[str, Any]) -> GovernorDecision:
        dag = plan.get("dag") if isinstance(plan, dict) else []
        step_results = [self.assess_step(step) for step in (dag or [])]

        risk_score = max([step["risk_score"] for step in step_results], default=0)
        control_ratio = self.compute_control_ratio(metrics)

        forbidden = set(self.profile.get("forbidden_impact_levels", []))
        min_reversibility = int(self.profile.get("min_reversibility_score", 4))
        max_risk = int(self.profile.get("max_risk_score", 8))
        floor = float(self.profile.get("control_ratio_floor", 0.3))

        blocked = False
        reason = "Plan within policy"
        for step in step_results:
            if step["predicted_impact"] in forbidden:
                blocked = True
                reason = f"Impact {step['predicted_impact']} is forbidden"
                break
            if step["reversibility_score"] < min_reversibility:
                blocked = True
                reason = "Reversibility score below policy threshold"
                break

        if control_ratio < floor:
            blocked = True
            reason = "Control ratio below policy floor"

        if risk_score >= max_risk:
            blocked = True
            reason = "Risk score exceeds policy limit"

        decision = "HIB" if blocked else "ALLOW"
        self._log("plan_audit", {"decision": decision, "risk_score": risk_score, "control_ratio": control_ratio})
        return GovernorDecision(
            decision=decision,
            control_ratio=control_ratio,
            risk_score=risk_score,
            reason=reason,
            step_results=step_results,
        )

    def evaluate_action(self, action: Dict[str, Any], metrics: Dict[str, Any]) -> GovernorDecision:
        pseudo_step = {
            "id": action.get("action_id") or action.get("type"),
            "instruction": action.get("summary") or action.get("instruction") or action.get("type", ""),
            "predicted_impact": action.get("predicted_impact"),
            "reversibility_score": action.get("reversibility_score"),
            "safety_justification": action.get("safety_justification"),
        }
        step_result = self.assess_step(pseudo_step)
        return self.evaluate_plan({"dag": [step_result]}, metrics)

    def build_intervention_manifest(
        self,
        proposed_action: str,
        decision: GovernorDecision,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        manifest = {
            "status": "PROMPT_HUMAN_APPROVAL",
            "proposed_action": proposed_action,
            "risk_score": decision.risk_score,
            "moral_compass_failure": decision.reason,
            "agent_state": {
                "uncertainty": float(metrics.get("uncertainty", 0.0)),
                "recursion_depth": float(metrics.get("recursion_depth", 0.0)),
                "semantic_drift": float(metrics.get("semantic_drift", 0.0)),
                "cost_velocity": float(metrics.get("cost_velocity", 0.0)),
                "control_ratio": decision.control_ratio,
            },
            "timestamp": time.time(),
        }
        self._log("hib_manifest", manifest)
        return manifest

