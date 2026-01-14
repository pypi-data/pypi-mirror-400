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


class EnterpriseFinanceOpsSkill(Skill):
    """Finance forecasting and audit steps."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="enterprise/finance-ops",
            name="Enterprise Finance Ops",
            description="Encode finance operational workflows and review steps",
            category=SkillCategory.DATA,
            level=SkillLevel.INTERMEDIATE,
            tags=["enterprise", "finance", "operations"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["forecast", "audit"]},
                "scope": {"type": "string"},
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
        scope = input_data.get("scope", "budget")

        if capability == "forecast":
            steps = [
                f"Collect historical data for {scope}",
                "Normalize and clean inputs",
                "Model baseline forecast",
                "Review sensitivity scenarios",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "audit":
            checklist = [
                "Reconcile ledger totals",
                "Validate approvals",
                "Check variance thresholds",
                "Document exceptions",
            ]
            return SkillResult(success=True, output={"checklist": checklist}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["EnterpriseFinanceOpsSkill"]
