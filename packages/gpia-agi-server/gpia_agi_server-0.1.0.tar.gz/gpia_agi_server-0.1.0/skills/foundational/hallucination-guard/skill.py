from __future__ import annotations

from typing import Any, Dict

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class HallucinationGuardSkill(Skill):
    """Constrain outputs to valid identifiers."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/hallucination-guard",
            name="Hallucination Guard",
            description="Constrain decoding to valid document identifiers",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["retrieval", "safety", "constraints"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["constrain", "verify"]},
                "allowed": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        if capability == "constrain":
            steps = [
                "Build prefix tree from allowed IDs",
                "Limit decoder transitions to valid prefixes",
                "Reject out-of-vocabulary tokens",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "verify":
            steps = [
                "Check output IDs against allowed list",
                "Flag unknown identifiers",
                "Return only verified IDs",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["HallucinationGuardSkill"]
