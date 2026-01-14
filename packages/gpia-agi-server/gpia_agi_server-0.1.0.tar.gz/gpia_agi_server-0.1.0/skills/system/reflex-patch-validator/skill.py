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


class ReflexPatchValidatorSkill(Skill):
    """Validate reflex patch proposals before deployment."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/reflex-patch-validator",
            name="Reflex Patch Validator",
            description="Simulates reflex patches before deployment.",
            category=SkillCategory.SYSTEM,
            level=SkillLevel.INTERMEDIATE,
            tags=["reflex", "validation", "safety"],
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        patch = input_data.get("patch") or {}

        if capability in {"simulate_shadow_run", "validate_logic_idempotency"}:
            if not patch:
                return SkillResult(
                    success=False,
                    output=None,
                    error="missing_patch",
                    skill_id=self.metadata().id,
                )
            corrector = ReflexCorrector()
            allowed = corrector.validate_patch(patch)
            status = "simulated" if allowed else "rejected"
            return SkillResult(
                success=allowed,
                output={
                    "status": status,
                    "validation_status": patch.get("validation_status"),
                    "patch": patch,
                },
                skill_id=self.metadata().id,
            )

        if capability == "check_regulatory_compliance":
            return SkillResult(
                success=True,
                output={
                    "status": "ok",
                    "notes": "No explicit compliance rules configured.",
                    "patch": patch,
                },
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="unsupported_capability",
            skill_id=self.metadata().id,
        )


__all__ = ["ReflexPatchValidatorSkill"]
