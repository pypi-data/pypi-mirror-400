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


class ThirdPartyBrowserSkill(Skill):
    """Plan safe browser navigation steps."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/browser",
            name="Third-Party Browser",
            description="Navigate web pages with structured steps",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["browser", "web", "navigation"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["plan", "extract"]},
                "url": {"type": "string"},
                "goal": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "steps": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        url = input_data.get("url", "")
        goal = input_data.get("goal", "")

        if capability == "plan":
            steps = [
                f"Open {url}",
                "Wait for page ready",
                f"Navigate to content relevant to: {goal}",
                "Collect page state for extraction",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "extract":
            steps = [
                f"Locate target elements for: {goal}",
                "Extract text or structured fields",
                "Validate completeness and consistency",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["ThirdPartyBrowserSkill"]
