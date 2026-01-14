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


class ScientificBioinformaticsSkill(Skill):
    """Bioinformatics and EHR workflow planning."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/scientific-bioinformatics",
            name="Foundational Scientific Bioinformatics",
            description="Provide bioinformatics workflows and EHR analysis guidance",
            category=SkillCategory.DATA,
            level=SkillLevel.INTERMEDIATE,
            tags=["bioinformatics", "ehr", "research"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["ehr_analysis", "workflow"]},
                "dataset": {"type": "string"},
                "goal": {"type": "string"},
            },
            "required": ["capability"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"plan": {"type": "array"}}}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        dataset = input_data.get("dataset", "EHR")
        goal = input_data.get("goal", "define outcomes")

        if capability == "ehr_analysis":
            plan = [
                f"Profile {dataset} schema and missingness",
                "De-identify sensitive fields",
                f"Run cohort selection aligned to {goal}",
                "Compute statistical summaries",
            ]
            return SkillResult(success=True, output={"plan": plan}, skill_id=self.metadata().id)

        if capability == "workflow":
            plan = [
                "Ingest raw sequencing data",
                "Run QC and filtering",
                "Align/assemble reads",
                "Annotate variants",
                "Generate reproducible report",
            ]
            return SkillResult(success=True, output={"plan": plan}, skill_id=self.metadata().id)

        return SkillResult(success=False, output=None, error="Unknown capability", skill_id=self.metadata().id)


__all__ = ["ScientificBioinformaticsSkill"]
