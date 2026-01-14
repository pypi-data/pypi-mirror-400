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


class EnterpriseRecruitingSkill(Skill):
    """Recruiting workflows and candidate screening."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/hr-recruiting",
            name="Enterprise HR Recruiting",
            description="Encode recruiting workflows and candidate screening steps",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "hr", "recruiting"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["screen", "workflow"]},
                "role": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        role = input_data.get("role", "role")

        if capability == "screen":
            steps = [
                f"Review resume for {role}",
                "Check required skills",
                "Assess portfolio or code samples",
                "Schedule screening call",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "workflow":
            steps = [
                "Define role requirements",
                "Publish job posting",
                "Screen applicants",
                "Run interviews",
                "Collect feedback and decide",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseRecruitingSkill"]
