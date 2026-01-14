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


class FoundationalDocumentSkill(Skill):
    """Create and edit documents with repeatable steps."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/document",
            name="Foundational Document",
            description="Create and edit professional documents with structured steps",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["document", "editing", "formatting"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["create", "edit", "format"]},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "style": {"type": "string"},
                "requirements": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "plan": {"type": "array"},
                "changes": {"type": "array"},
                "style_rules": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        requirements: List[str] = input_data.get("requirements", [])
        style = input_data.get("style", "default")

        if capability == "create":
            plan = [
                "Define audience and purpose",
                "Draft outline with section headers",
                "Write each section in order",
                "Review for clarity and completeness",
            ]
            if requirements:
                plan.append(f"Incorporate requirements: {', '.join(requirements)}")
            return SkillResult(
                success=True,
                output={"plan": plan},
                skill_id=self.metadata().id,
            )

        if capability == "edit":
            changes = [
                "Identify unclear sentences",
                "Improve structure and flow",
                "Fix grammar and consistency",
                "Confirm changes meet requirements",
            ]
            return SkillResult(
                success=True,
                output={"changes": changes},
                skill_id=self.metadata().id,
            )

        if capability == "format":
            rules = [
                f"Apply style: {style}",
                "Normalize headings",
                "Use consistent bullet hierarchy",
                "Check spacing and emphasis",
            ]
            return SkillResult(
                success=True,
                output={"style_rules": rules},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="Unknown capability",
            skill_id=self.metadata().id,
        )


__all__ = ["FoundationalDocumentSkill"]
