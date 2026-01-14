"""
Meta-Code Generator
===================

Purpose: refactor-engine optimizes existing code. This writes code that writes better code.
Closes the loop on self-evolution.

Capabilities:
- Analyze function and generate improved version
- Abstract patterns from successful refactors
- Evolve algorithms through simulated selection
- Generate tests that expose edge cases
"""

from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning
import re

class MetaCodeGeneratorSkill(Skill):
    """Code that writes better code."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/meta-code-generator",
            name="Meta-Code Generator",
            description="Write code that writes better code - self-evolution",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["improve", "abstract", "evolve", "test_gen", "self_modify"]},
                "code": {"type": "string", "description": "Code to process"},
                "context": {"type": "object", "description": "Additional context"}
            },
            "required": ["capability", "code"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "improve")
        code = input_data.get("code", "")
        ctx = input_data.get("context", {})

        if capability == "improve":
            result = self._improve_code(code)
        elif capability == "abstract":
            result = self._abstract_pattern(code)
        elif capability == "evolve":
            result = self._evolve_algorithm(code, ctx)
        elif capability == "test_gen":
            result = self._generate_tests(code)
        elif capability == "self_modify":
            result = self._self_modify(code, ctx.get("goal", ""))
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _improve_code(self, code: str) -> Dict:
        """Analyze and generate improved version."""
        prompt = f"""Analyze this code and generate a significantly improved version:

```
{code}
```

Improvements to make:
1. Performance (reduce time/space complexity)
2. Readability (clearer names, structure)
3. Robustness (error handling, edge cases)
4. Extensibility (easier to modify later)

Provide:
1. Analysis of current weaknesses
2. Improved code
3. Explanation of improvements
4. Metrics (estimated improvement %)"""

        improvement = query_creative(prompt, max_tokens=1000, timeout=90)

        return {
            "analysis": improvement,
            "original_length": len(code),
        }

    def _abstract_pattern(self, code: str) -> Dict:
        """Extract abstract pattern from code."""
        prompt = f"""Extract the abstract pattern from this code:

```
{code}
```

Generate:
1. The pattern name
2. Pattern description (domain-agnostic)
3. Abstract template (with placeholders)
4. 3 examples of where this pattern could apply
5. Code generator function that creates instances of this pattern

Make the pattern maximally reusable."""

        abstraction = query_reasoning(prompt, max_tokens=800, timeout=90)

        return {"abstraction": abstraction}

    def _evolve_algorithm(self, code: str, ctx: Dict) -> Dict:
        """Evolve algorithm through simulated selection."""
        fitness_criteria = ctx.get("fitness", "efficiency and correctness")

        prompt = f"""Evolve this algorithm through simulated natural selection:

Original:
```
{code}
```

Fitness criteria: {fitness_criteria}

Generate 3 mutations:
1. Mutation A: Small variation
2. Mutation B: Medium variation
3. Mutation C: Radical reimagining

For each mutation:
- Show the mutated code
- Explain the change
- Estimate fitness score (1-10)

Then select the fittest and explain why it wins."""

        evolution = query_creative(prompt, max_tokens=1200, timeout=120)

        return {"evolution": evolution}

    def _generate_tests(self, code: str) -> Dict:
        """Generate tests that expose edge cases."""
        prompt = f"""Generate comprehensive tests for this code:

```
{code}
```

Generate:
1. Normal case tests (happy path)
2. Edge case tests (boundaries, limits)
3. Error case tests (invalid inputs)
4. Stress tests (performance limits)
5. Adversarial tests (malicious inputs)

For each test:
- Test name
- Input
- Expected output
- Why this test matters

Make tests that would catch bugs a human would miss."""

        tests = query_reasoning(prompt, max_tokens=1000, timeout=90)

        return {"tests": tests}

    def _self_modify(self, code: str, goal: str) -> Dict:
        """Generate code that modifies itself toward a goal."""
        prompt = f"""Create self-modifying code based on this:

Original:
```
{code}
```

Goal: {goal or "Improve itself over time"}

Generate:
1. A wrapper that monitors the code's performance
2. Logic to detect when improvement is needed
3. Code that generates improved versions of itself
4. A fitness function to evaluate improvements
5. Safeguards to prevent runaway modification

This should be code that genuinely improves itself, not just random mutation."""

        self_mod = query_creative(prompt, max_tokens=1200, timeout=120)

        return {"self_modifying_code": self_mod}
