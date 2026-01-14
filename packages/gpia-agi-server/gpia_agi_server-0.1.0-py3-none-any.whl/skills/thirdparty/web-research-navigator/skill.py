from __future__ import annotations

from typing import Any, Dict

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class WebResearchNavigatorSkill(Skill):
    """Plan web research navigation and capture."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/web-research-navigator",
            name="Web Research Navigator",
            description="Navigate live web sources to augment retrieval",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["web", "research", "navigation"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["plan", "capture"]},
                "topic": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        topic = input_data.get("topic", "")

        if capability == "plan":
            steps = [
                f"Search live sources for: {topic}",
                "Open top-ranked pages",
                "Extract evidence and citations",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "capture":
            steps = [
                "Capture page snapshots",
                "Store key quotes with URLs",
                "Summarize findings",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["WebResearchNavigatorSkill"]
