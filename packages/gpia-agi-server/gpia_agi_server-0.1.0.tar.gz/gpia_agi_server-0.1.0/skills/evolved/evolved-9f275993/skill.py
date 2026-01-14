"""
Evolved: Solve: Explain the difference 
Auto-evolved skill from successful agent work.
"""

from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning

class EvolvedSkill(Skill):
    """Auto-evolved skill: Skill evolved from solving: Explain the difference between a list and a tuple in Python"""

    APPROACH = """### Difference Between a List and a Tuple in Python

1. **Mutability**  
   - **List**: Mutable (elements can be modified, added, or removed).  
     Example: `my_list = [1, 2]; my_list[1] = 3` changes the list to `[1, 3]`.  
   - **Tuple**: Immutable (once created, elements cannot change).  
     Example: `my_tuple = (1, 2); my_tuple[1] = 3` raises a `TypeError`.

2. **Syntax**  
   - List uses square brackets: `[]` (e.g., `[10, "a", True]`).  
   - Tuple uses parentheses: `()` or `,(e.g., `(10"""
    MODEL = "deepseek_r1"

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="evolved-9f275993",
            name="Evolved: Solve: Explain the difference ",
            description="Skill evolved from solving: Explain the difference between a list and a tuple in Python",
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
