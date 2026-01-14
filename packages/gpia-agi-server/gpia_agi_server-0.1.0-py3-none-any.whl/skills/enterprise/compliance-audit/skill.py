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


class ComplianceAuditSkill(Skill):
    """Compliance audit planning and evidence collection."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/compliance-audit",
            name="Enterprise Compliance Audit",
            description="Provide compliance audit planning and evidence collection steps",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "compliance", "audit"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["plan", "evidence"]},
                "standard": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "steps": {"type": "array"},
                "checklist": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        standard = input_data.get("standard", "policy")

        if capability == "plan":
            steps = [
                f"Define scope for {standard}",
                "Identify control owners",
                "Schedule evidence collection",
                "Review findings and gaps",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "evidence":
            checklist = [
                "Access logs",
                "Change management records",
                "Policy approvals",
                "Incident response evidence",
            ]
            return SkillResult(success=True, output={"checklist": checklist}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["ComplianceAuditSkill"]
