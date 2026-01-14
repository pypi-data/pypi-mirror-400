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


class FoundationalScienceSkill(Skill):
    """Scientific analysis planning for research workflows."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/science",
            name="Foundational Science",
            description="Analyze scientific datasets and outline workflows",
            category=SkillCategory.DATA,
            level=SkillLevel.INTERMEDIATE,
            tags=["research", "ehr", "bioinformatics"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["analyze", "pipeline"]},
                "dataset": {"type": "string"},
                "goal": {"type": "string"},
                "tools": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "plan": {"type": "array"},
                "workflow": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        dataset = input_data.get("dataset", "dataset")
        goal = input_data.get("goal", "define outcomes")
        tools: List[str] = input_data.get("tools", [])

        if capability == "analyze":
            plan = [
                f"Validate schema for {dataset}",
                "Assess data quality and missingness",
                f"Run exploratory analysis to support: {goal}",
                "Summarize findings with metrics and plots",
            ]
            return SkillResult(
                success=True,
                output={"plan": plan},
                skill_id=self.metadata().id,
            )

        if capability == "pipeline":
            workflow = [
                "Ingest raw data",
                "Normalize and harmonize fields",
                "Run statistical tests",
                "Train or validate models",
                "Publish reproducible report",
            ]
            if tools:
                workflow.append(f"Tools: {', '.join(tools)}")
            return SkillResult(
                success=True,
                output={"workflow": workflow},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="Unknown capability",
            skill_id=self.metadata().id,
        )


__all__ = ["FoundationalScienceSkill"]
