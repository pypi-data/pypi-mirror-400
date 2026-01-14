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


class RetrievalStrategistSkill(Skill):
    """Select retrieval strategy based on scale."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/retrieval-strategist",
            name="Retrieval Strategist",
            description="Decide retrieval strategy based on corpus scale and constraints",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["retrieval", "strategy", "scale"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["route", "assess"]},
                "corpus_size": {"type": "integer"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"steps": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        corpus_size = input_data.get("corpus_size", 0)

        if capability == "assess":
            steps = [
                f"Estimate corpus size: {corpus_size}",
                "Check memory and latency limits",
                "Determine viable retrieval modes",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        if capability == "route":
            steps = [
                "If corpus > threshold, use vector search",
                "If corpus small, allow generative scan",
                "Apply rerank on top-k results",
            ]
            return SkillResult(success=True, output={"steps": steps}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["RetrievalStrategistSkill"]
