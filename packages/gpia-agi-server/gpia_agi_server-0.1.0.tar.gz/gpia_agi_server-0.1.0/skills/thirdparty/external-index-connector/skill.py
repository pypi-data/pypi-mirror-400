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


class ExternalIndexConnectorSkill(Skill):
    """External index connection and query orchestration."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/external-index-connector",
            name="External Index Connector",
            description="Orchestrate retrieval across external indexes via MCP",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["retrieval", "mcp", "external"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["connect", "query"]},
                "index": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        index_name = input_data.get("index", "index")

        if capability == "connect":
            steps = [
                f"Register external index: {index_name}",
                "Validate schema mapping",
                "Check authentication",
                "Run connection test",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "query":
            steps = [
                "Transform query into index format",
                "Execute external search",
                "Normalize results for rerank",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["ExternalIndexConnectorSkill"]
