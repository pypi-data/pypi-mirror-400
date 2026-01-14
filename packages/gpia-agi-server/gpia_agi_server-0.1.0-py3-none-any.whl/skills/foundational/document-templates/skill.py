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


class DocumentTemplatesSkill(Skill):
    """Provide reusable document outlines and sections."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/document-templates",
            name="Foundational Document Templates",
            description="Provide reusable document templates and structure guidance",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["document", "templates", "structure"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["outline", "sections"]},
                "doc_type": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"outline": {"type": "array"}, "sections": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        doc_type = input_data.get("doc_type", "document")

        if capability == "outline":
            outline = [
                f"Title page for {doc_type}",
                "Executive summary",
                "Background",
                "Main content",
                "Recommendations",
                "Appendix",
            ]
            return SkillResult(success=True, output={"outline": outline}, skill_id=self.metadata().id)

        if capability == "sections":
            sections = [
                "Purpose",
                "Scope",
                "Key findings",
                "Risks",
                "Next steps",
            ]
            return SkillResult(success=True, output={"sections": sections}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["DocumentTemplatesSkill"]
