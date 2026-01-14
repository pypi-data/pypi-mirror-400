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


class EnterpriseWorkflowsSkill(Skill):
    """Encode internal workflows into repeatable steps."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/workflows",
            name="Enterprise Workflows",
            description="Encode internal operational workflows into repeatable steps",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "workflow", "operations"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["define", "execute"]},
                "process": {"type": "string"},
                "steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        process = input_data.get("process", "")
        steps: List[str] = input_data.get("steps", [])

        if capability == "define":
            output_steps = [
                f"Define goal for {process}",
                "Identify stakeholders",
                "List required inputs",
                "Define success criteria",
            ]
            return SkillResult(success=True, output={"steps": output_steps}, skill_id=self.metadata().id)

        if capability == "execute":
            output_steps = steps or [
                "Gather inputs",
                "Run checklist",
                "Validate outputs",
                "Record outcome",
            ]
            return SkillResult(success=True, output={"steps": output_steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseWorkflowsSkill"]
