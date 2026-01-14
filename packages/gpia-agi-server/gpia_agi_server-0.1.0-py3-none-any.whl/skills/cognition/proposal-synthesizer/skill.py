from __future__ import annotations

from typing import Any, Dict

from core.reflex_corrector import ReflexCorrector
from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class ProposalSynthesizerSkill(Skill):
    """Generate reflex patch proposals from weakness signals."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="cognition/proposal-synthesizer",
            name="Proposal Synthesizer",
            description="Translates alignment deltas into reflex patch proposals.",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["mirror", "proposals", "reflex"],
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        weakness = input_data.get("weakness") or {}
        delta_log = input_data.get("delta_log") or []

        if capability == "extract_error_signature":
            signature = self._build_signature(weakness, delta_log)
            return SkillResult(
                success=True,
                output={"status": "ok", "signature": signature},
                skill_id=self.metadata().id,
            )

        if capability == "map_failure_to_logic_branch":
            mapping = self._map_to_reflex(weakness)
            return SkillResult(
                success=True,
                output={"status": "ok", "mapping": mapping},
                skill_id=self.metadata().id,
            )

        if capability == "draft_reflex_edit_v1":
            corrector = ReflexCorrector()
            patch = corrector.propose_correction(weakness)
            if not patch:
                return SkillResult(
                    success=False,
                    output={"status": "skipped"},
                    error="delta_below_threshold",
                    skill_id=self.metadata().id,
                )
            return SkillResult(
                success=True,
                output={"status": "proposed", "patch": patch},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="unsupported_capability",
            skill_id=self.metadata().id,
        )

    def _build_signature(self, weakness: Dict[str, Any], delta_log: list) -> str:
        skill_id = weakness.get("skill") or weakness.get("skill_id") or "unknown"
        delta = weakness.get("delta", weakness.get("delta_avg", "n/a"))
        return f"skill={skill_id};delta={delta};events={len(delta_log)}"

    def _map_to_reflex(self, weakness: Dict[str, Any]) -> str:
        skill_id = weakness.get("skill") or weakness.get("skill_id") or "unknown"
        return f"reflex_{str(skill_id).replace('/', '_')}"


__all__ = ["ProposalSynthesizerSkill"]
