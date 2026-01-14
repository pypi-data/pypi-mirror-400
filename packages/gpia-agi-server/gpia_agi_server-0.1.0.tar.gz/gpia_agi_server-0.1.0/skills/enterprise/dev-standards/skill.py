from __future__ import annotations

from typing import Any, Dict, List

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class EnterpriseDevStandardsSkill(Skill):
    """Apply internal development standards and workflow checks."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/dev-standards",
            name="Enterprise Dev Standards",
            description="Apply internal code standards and workflow expectations",
            category=SkillCategory.CODE,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "standards", "developer"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["checklist", "review"]},
                "scope": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"items": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        scope = input_data.get("scope", "repo")

        if capability == "checklist":
            items = [
                f"Confirm lint/type checks for {scope}",
                "Verify tests updated",
                "Check security considerations",
                "Document behavior changes",
            ]
            return SkillResult(success=True, output={"items": items}, skill_id=self.metadata().id)

        if capability == "review":
            items = [
                "Scan for regressions",
                "Confirm error handling",
                "Validate performance impact",
                "Ensure config changes documented",
            ]
            return SkillResult(success=True, output={"items": items}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseDevStandardsSkill"]
