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


class EnterpriseInternalToolsSkill(Skill):
    """Internal tooling usage guidance."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/internal-tools",
            name="Enterprise Internal Tools",
            description="Document internal tool usage patterns and escalation paths",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "internal", "tooling"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["guide", "escalate"]},
                "tool": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        tool = input_data.get("tool", "internal tool")

        if capability == "guide":
            steps = [
                f"Authenticate to {tool}",
                "Select required workflow",
                "Execute steps with audit logging",
                "Record results",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "escalate":
            steps = [
                "Capture error context",
                "Notify on-call owner",
                "Provide reproduction steps",
                "Document workaround",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseInternalToolsSkill"]
