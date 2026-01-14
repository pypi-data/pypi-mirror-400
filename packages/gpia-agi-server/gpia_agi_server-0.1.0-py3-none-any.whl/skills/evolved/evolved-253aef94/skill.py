"""
Evolved: Solve: What is the difference 
Auto-evolved skill from successful agent work.
"""

from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning

class EvolvedSkill(Skill):
    """Auto-evolved skill: Skill evolved from solving: What is the difference between lists and tuples?"""

    APPROACH = """**1. Mutability:**  
- **Lists** are mutable-elements can be added, removed, or modified after creation.  
- **Tuples**, however, are immutable-once created, their elements cannot be changed (no insertions, deletions).  

**2. Syntax:**  
- Lists use **square brackets `[]`**: e.g., `[1, 2, 3]`.  
- Tuples use **parentheses `()`**: e.g., `(1, 2, 3)` or even without parentheses in older Python versions (though style guides recommend them for clarity).  

**3. Use Cases:**  
- Lists are ideal for d"""
    MODEL = "deepseek_r1"

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="evolved-253aef94",
            name="Evolved: Solve: What is the difference ",
            description="Skill evolved from solving: What is the difference between lists and tuples?",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task to perform"}
            },
            "required": ["task"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        task = input_data.get("task", "")

        prompt = f"""Based on this approach: {self.APPROACH}

Solve this task: {task}

Provide a complete solution."""

        if self.MODEL == "deepseek_r1":
            result = query_reasoning(prompt, max_tokens=800)
        else:
            result = query_creative(prompt, max_tokens=800)

        return SkillResult(
            success=bool(result),
            output=result,
            skill_id=self.metadata().id,
        )
