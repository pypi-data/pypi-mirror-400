"""
Generative Visualizer - Telemetry to Visual Patterns
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative

class GenerativeVisualizerSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/generative-visualizer",
            name="Generative Visualizer",
            description="Convert telemetry to visual patterns",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"data": {"type": "object"}, "format": {"type": "string"}}, "required": ["data"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        data = input_data.get("data", {})
        fmt = input_data.get("format", "ascii")

        prompt = f"""Convert this telemetry data into a visual pattern:

Data: {data}

Generate:
1. ASCII art visualization showing the pattern
2. Description of what the pattern reveals
3. Anomalies highlighted visually
4. Color suggestions for GUI rendering

Make it instantly readable - diagnostics at a glance."""

        result = query_creative(prompt, max_tokens=800, timeout=60)
        return SkillResult(success=True, output={"visualization": result}, skill_id=self.metadata().id)
