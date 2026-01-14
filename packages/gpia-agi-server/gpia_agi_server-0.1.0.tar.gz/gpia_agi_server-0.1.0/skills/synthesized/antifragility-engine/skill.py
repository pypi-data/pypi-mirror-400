"""
Antifragility Engine - Chaos as Ladder
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_synthesis

class AntifragilityEngineSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/antifragility-engine",
            name="Antifragility Engine",
            description="Thrive in disorder - use chaos as a ladder",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"chaos_event": {"type": "string"}, "current_state": {"type": "object"}}, "required": ["chaos_event"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        chaos = input_data.get("chaos_event", "")
        state = input_data.get("current_state", {})

        prompt = f"""A chaos event has occurred. Convert it to advantage:

Chaos Event: {chaos}
Current State: {state}

Apply antifragility principles:
1. What breaks reveals what was weak - what weakness did this expose?
2. Stress creates growth - what capability should grow from this?
3. Optionality - what new options does this chaos create?
4. Via negativa - what should we STOP doing because of this?
5. Barbell strategy - how to be conservative AND aggressive?

Do not recover to previous state. Evolve to a BETTER state.
Chaos is not a pit. Chaos is a ladder."""

        result = query_synthesis(prompt, max_tokens=800, timeout=120)
        return SkillResult(success=True, output={"antifragile_response": result}, skill_id=self.metadata().id)
