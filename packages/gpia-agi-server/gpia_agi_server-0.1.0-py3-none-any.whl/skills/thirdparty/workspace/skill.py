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


class ThirdPartyWorkspaceSkill(Skill):
    """Plan workspace research steps for external systems."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/workspace",
            name="Third-Party Workspace",
            description="Research across external workspaces with structured steps",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["workspace", "research", "integration"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["query", "synthesize"]},
                "topic": {"type": "string"},
                "sources": {"type": "array", "items": {"type": "string"}},
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
        topic = input_data.get("topic", "")
        sources: List[str] = input_data.get("sources", [])

        if capability == "query":
            steps = [
                f"Define query scope for: {topic}",
                f"Select sources: {', '.join(sources) if sources else 'default'}",
                "Collect relevant pages and notes",
                "Tag results for synthesis",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "synthesize":
            steps = [
                "Group findings by theme",
                "Identify gaps and follow-up questions",
                "Write summary with citations",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["ThirdPartyWorkspaceSkill"]
