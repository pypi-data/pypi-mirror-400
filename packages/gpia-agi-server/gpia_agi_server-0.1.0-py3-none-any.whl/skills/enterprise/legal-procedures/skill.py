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


class EnterpriseLegalProceduresSkill(Skill):
    """Legal review and compliance steps."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/legal-procedures",
            name="Enterprise Legal Procedures",
            description="Encode legal review steps and compliance checks",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "legal", "compliance"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["review", "checklist"]},
                "document": {"type": "string"},
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
        document = input_data.get("document", "contract")

        if capability == "review":
            steps = [
                f"Identify parties in {document}",
                "Review obligations and liabilities",
                "Check termination and renewal clauses",
                "Flag non-standard terms",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "checklist":
            checklist = [
                "Confidentiality clauses present",
                "Data handling requirements documented",
                "Jurisdiction and governing law stated",
                "Approval signatures defined",
            ]
            return SkillResult(success=True, output={"checklist": checklist}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseLegalProceduresSkill"]
