from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from core.dense_logic.decoder import verify_intent_integrity
from core.resonant_kernel.interface import TemporalFormalismContract
from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class DenseStateLogicSkill(Skill):
    """Dense-State Logic v1 resonator and verifier."""

    def __init__(self) -> None:
        self.contract = TemporalFormalismContract()

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/dense-state-logic",
            name="Dense-State Logic",
            description="Resonant state mapping, stability checks, and intent integrity verification.",
            category=SkillCategory.SYSTEM,
            level=SkillLevel.EXPERT,
            tags=["resonance", "state", "formalism"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["resonate", "verify", "spectrum"]},
                "tokens": {"type": "array", "items": {"type": "integer"}},
                "text": {"type": "string"},
                "max_tokens": {"type": "integer"},
                "telemetry": {
                    "type": "object",
                    "properties": {
                        "cpu": {"type": "number"},
                        "vram": {"type": "number"},
                    },
                },
                "state": {"type": "array"},
                "state_dim": {"type": "integer"},
                "resonance_threshold": {"type": "number"},
                "phase_mod": {"type": "integer"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "resonance_score": {"type": "number"},
                "is_stable": {"type": "boolean"},
                "vector_hash": {"type": "string"},
                "drift": {"type": "number"},
                "spectrum": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        self._configure_contract(input_data)

        if capability == "resonate":
            return self._resonate(input_data)
        if capability == "verify":
            return self._verify(input_data)
        if capability == "spectrum":
            return self._spectrum()

        return SkillResult(
            success=False,
            output=None,
            error=f"Unknown capability: {capability}",
            skill_id=self.metadata().id,
        )

    def _configure_contract(self, input_data: Dict[str, Any]) -> None:
        state_dim = input_data.get("state_dim")
        threshold = input_data.get("resonance_threshold")
        phase_mod = input_data.get("phase_mod")

        if state_dim or threshold or phase_mod:
            self.contract = TemporalFormalismContract(
                state_dim=state_dim or self.contract.state_dim,
                resonance_threshold=threshold or self.contract.resonance_threshold,
                phase_mod=phase_mod or self.contract.phase_mod,
            )

    def _build_tokens(self, input_data: Dict[str, Any]) -> List[int]:
        tokens = input_data.get("tokens") or []
        if tokens:
            return [int(t) for t in tokens]

        text = input_data.get("text", "")
        max_tokens = int(input_data.get("max_tokens") or 256)
        return self.contract.tokens_from_text(text, max_tokens=max_tokens)

    def _resonate(self, input_data: Dict[str, Any]) -> SkillResult:
        tokens = self._build_tokens(input_data)
        telemetry = input_data.get("telemetry") or {}
        env_bias = self.contract.observe_telemetry(
            telemetry.get("cpu"),
            telemetry.get("vram"),
        )
        result = self.contract.evolve_state(tokens, env_bias)
        return SkillResult(
            success=True,
            output={
                "status": "RESONANCE_LOCKED" if result.get("is_stable") else "FLICKER_STATE",
                "resonance_score": result.get("resonance_score"),
                "is_stable": result.get("is_stable"),
                "vector_hash": result.get("vector_hash"),
            },
            skill_id=self.metadata().id,
        )

    def _verify(self, input_data: Dict[str, Any]) -> SkillResult:
        tokens = self._build_tokens(input_data)
        state = self._parse_state(input_data.get("state"))
        if state is None:
            state = self.contract.current_state
        drift = verify_intent_integrity(tokens, state, phase_mod=self.contract.phase_mod)
        return SkillResult(
            success=True,
            output={
                "status": "VERIFIED" if drift <= 0.05 else "DRIFTED",
                "drift": drift,
            },
            skill_id=self.metadata().id,
        )

    def _spectrum(self) -> SkillResult:
        spectrum = self.contract.export_spectrum()
        return SkillResult(
            success=True,
            output={
                "status": "SPECTRUM",
                "spectrum": spectrum,
            },
            skill_id=self.metadata().id,
        )

    def _parse_state(self, raw: Any) -> Optional[np.ndarray]:
        if raw is None:
            return None
        if isinstance(raw, np.ndarray):
            return raw
        if isinstance(raw, list):
            if not raw:
                return None
            if isinstance(raw[0], (int, float)):
                return np.asarray(raw, dtype=np.float64).astype(np.complex128)
            if isinstance(raw[0], (list, tuple)) and len(raw[0]) == 2:
                values = [complex(pair[0], pair[1]) for pair in raw]
                return np.asarray(values, dtype=np.complex128)
        return None


__all__ = ["DenseStateLogicSkill"]
