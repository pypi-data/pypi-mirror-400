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


class DocumentEditingToolsSkill(Skill):
    """Reusable tooling steps for professional document edits."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/document-editing-tools",
            name="Foundational Document Editing Tools",
            description="Provide scriptable steps and QA checks for document edits",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["document", "tooling", "editing"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["scripts", "checklist"]},
                "doc_type": {"type": "string"},
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
        doc_type = input_data.get("doc_type", "document")

        if capability == "scripts":
            steps = [
                f"Load {doc_type} source",
                "Apply template styles",
                "Normalize headings and lists",
                "Export updated document",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "checklist":
            checklist = [
                "Verify styles and fonts",
                "Check headings and numbering",
                "Confirm table formatting",
                "Run spell/grammar pass",
                "Validate export output",
            ]
            return SkillResult(success=True, output={"checklist": checklist}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["DocumentEditingToolsSkill"]
