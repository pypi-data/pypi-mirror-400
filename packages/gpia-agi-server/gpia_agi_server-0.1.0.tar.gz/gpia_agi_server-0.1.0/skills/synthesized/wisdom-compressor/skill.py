"""
Wisdom Compressor - Petabytes to Kilobytes
"""
from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_reasoning

class WisdomCompressorSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/wisdom-compressor",
            name="Wisdom Compressor",
            description="Compress vast experience into dense wisdom",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"experiences": {"type": "array"}, "compression_ratio": {"type": "number"}}, "required": ["experiences"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        experiences = input_data.get("experiences", [])
        ratio = input_data.get("compression_ratio", 100)

        prompt = f"""Compress these {len(experiences)} experiences into dense wisdom:

Experiences:
{chr(10).join(str(e)[:200] for e in experiences[:20])}

Target compression: {ratio}:1

Generate:
1. Core principles (max 5)
2. Pattern abstractions (max 3)
3. Decision heuristics (max 3)
4. Failure modes to avoid (max 3)

Each should be a single sentence of maximum insight density.
This wisdom must reconstruct the essence of all experiences."""

        result = query_reasoning(prompt, max_tokens=600, timeout=90)
        return SkillResult(success=True, output={"wisdom": result, "original_count": len(experiences)}, skill_id=self.metadata().id)
