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


class NotionWorkspaceSkill(Skill):
    """Research planning for Notion workspaces."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/notion-workspace",
            name="Third-Party Notion Workspace",
            description="Plan and structure research across Notion workspaces",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["notion", "workspace", "research"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["search", "synthesize"]},
                "query": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        query = input_data.get("query", "")

        if capability == "search":
            steps = [
                f"Search workspace for: {query}",
                "Collect relevant pages",
                "Extract key blocks and metadata",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "synthesize":
            steps = [
                "Cluster findings by topic",
                "Summarize key decisions",
                "List open questions",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["NotionWorkspaceSkill"]
