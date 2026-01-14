"""
Code Refactoring Skill
======================

Intelligent code refactoring with pattern recognition,
transformation suggestions, and automated restructuring.
"""

import ast
import re
import time
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillDependency,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class RefactorSkill(Skill):
    """
    Code refactoring skill providing:
    - Code simplification
    - Design pattern suggestions
    - Extract method/class recommendations
    - Dead code detection
    - Naming improvements
    """

    REFACTOR_TYPES = [
        "simplify",      # Reduce complexity
        "patterns",      # Apply design patterns
        "extract",       # Extract methods/classes
        "rename",        # Improve naming
        "modernize",     # Update to modern syntax
        "cleanup",       # Remove dead code
        "all",           # All refactoring types
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="code/refactor",
            name="Code Refactoring",
            description="Intelligent code refactoring with pattern recognition, transformation suggestions, and automated restructuring.",
            version="0.1.0",
            category=SkillCategory.CODE,
            level=SkillLevel.INTERMEDIATE,
            tags=["refactoring", "clean-code", "patterns", "transformation"],
            dependencies=[
                SkillDependency(
                    skill_id="code/review",
                    optional=True,
                    reason="Pre-refactor quality check",
                )
            ],
            estimated_tokens=700,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to refactor",
                },
                "language": {
                    "type": "string",
                    "default": "python",
                },
                "refactor_type": {
                    "type": "string",
                    "enum": self.REFACTOR_TYPES,
                    "default": "all",
                },
                "preserve_behavior": {
                    "type": "boolean",
                    "default": True,
                    "description": "Ensure refactoring doesn't change behavior",
                },
                "target_style": {
                    "type": "string",
                    "enum": ["minimal", "readable", "idiomatic"],
                    "default": "idiomatic",
                },
            },
            "required": ["code"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        code = input_data.get("code", "")
        language = input_data.get("language", "python")
        refactor_type = input_data.get("refactor_type", "all")
        target_style = input_data.get("target_style", "idiomatic")

        if refactor_type == "all":
            refactor_types = self.REFACTOR_TYPES[:-1]
        else:
            refactor_types = [refactor_type]

        suggestions = []
        transformations = []

        # Analyze and suggest refactorings
        if "simplify" in refactor_types:
            suggestions.extend(self._suggest_simplifications(code, language))

        if "patterns" in refactor_types:
            suggestions.extend(self._suggest_patterns(code, language))

        if "extract" in refactor_types:
            suggestions.extend(self._suggest_extractions(code, language))

        if "rename" in refactor_types:
            suggestions.extend(self._suggest_renames(code, language))

        if "modernize" in refactor_types:
            suggestions.extend(self._suggest_modernizations(code, language))

        if "cleanup" in refactor_types:
            suggestions.extend(self._suggest_cleanup(code, language))

        # Calculate improvement potential
        improvement_score = self._calculate_improvement(suggestions)

        execution_time = int((time.time() - start_time) * 1000)

        return SkillResult(
            success=True,
            output={
                "suggestions": suggestions,
                "improvement_score": improvement_score,
                "original_metrics": self._calculate_metrics(code),
                "refactor_guidance": self._get_guidance(suggestions, target_style),
            },
            execution_time_ms=execution_time,
            skill_id=self.metadata().id,
            suggestions=[
                "Apply high-impact refactorings first",
                "Run tests after each refactoring step",
            ],
            related_skills=["code/review", "code/python", "code/test"],
        )

    def _suggest_simplifications(self, code: str, language: str) -> List[Dict]:
        """Suggest ways to simplify the code."""
        suggestions = []

        # Nested conditionals
        if re.search(r'if .+:\s*\n\s+if .+:', code):
            suggestions.append({
                "type": "simplify",
                "pattern": "nested_conditionals",
                "description": "Nested if statements can be combined",
                "before": "if a:\\n    if b:",
                "after": "if a and b:",
                "impact": "medium",
            })

        # Loop with conditional append -> list comprehension
        if re.search(r'for .+ in .+:\s*\n\s+if .+:\s*\n\s+\w+\.append', code):
            suggestions.append({
                "type": "simplify",
                "pattern": "loop_filter_append",
                "description": "Loop with filter can become list comprehension",
                "before": "for x in items:\\n    if cond:\\n        result.append(x)",
                "after": "[x for x in items if cond]",
                "impact": "medium",
            })

        # if x: return True else: return False
        if re.search(r'if .+:\s*\n\s+return True\s*\n\s*else:\s*\n\s+return False', code):
            suggestions.append({
                "type": "simplify",
                "pattern": "boolean_return",
                "description": "Simplify boolean return",
                "before": "if x:\\n    return True\\nelse:\\n    return False",
                "after": "return bool(x)  # or just: return x",
                "impact": "low",
            })

        # len() == 0 or len() > 0
        if re.search(r'len\([^)]+\)\s*(?:==\s*0|>\s*0|!=\s*0)', code):
            suggestions.append({
                "type": "simplify",
                "pattern": "len_comparison",
                "description": "Use truthiness instead of len() comparison",
                "before": "if len(items) == 0: / if len(items) > 0:",
                "after": "if not items: / if items:",
                "impact": "low",
            })

        # Redundant else after return
        if re.search(r'return .+\s*\n\s*else:', code):
            suggestions.append({
                "type": "simplify",
                "pattern": "redundant_else",
                "description": "Remove redundant else after return",
                "before": "if x:\\n    return a\\nelse:\\n    return b",
                "after": "if x:\\n    return a\\nreturn b",
                "impact": "low",
            })

        return suggestions

    def _suggest_patterns(self, code: str, language: str) -> List[Dict]:
        """Suggest design pattern applications."""
        suggestions = []

        # Constructor creates dependencies
        if re.search(r'def __init__\(self\):\s*\n(?:\s+self\.\w+\s*=\s*\w+\(\)\s*\n){2,}', code):
            suggestions.append({
                "type": "pattern",
                "pattern": "dependency_injection",
                "description": "Class creates its own dependencies",
                "recommendation": "Accept dependencies as constructor parameters",
                "benefit": "Improves testability and flexibility",
                "impact": "high",
            })

        # Multiple if/elif checking type
        if re.search(r'if\s+(?:isinstance|type)\(.+\).*:\s*\n.*\n\s*elif\s+(?:isinstance|type)', code):
            suggestions.append({
                "type": "pattern",
                "pattern": "strategy_pattern",
                "description": "Multiple type checks suggest polymorphism needed",
                "recommendation": "Use Strategy pattern or polymorphic dispatch",
                "benefit": "More extensible and cleaner code",
                "impact": "high",
            })

        # Large class with many methods
        class_methods = re.findall(r'class \w+.*?(?=class |\Z)', code, re.DOTALL)
        for cls in class_methods:
            method_count = len(re.findall(r'def \w+', cls))
            if method_count > 10:
                suggestions.append({
                    "type": "pattern",
                    "pattern": "single_responsibility",
                    "description": f"Class has {method_count} methods - may have too many responsibilities",
                    "recommendation": "Consider splitting into smaller, focused classes",
                    "benefit": "Better maintainability and testability",
                    "impact": "high",
                })

        # Global state modification
        if re.search(r'\bglobal\b', code):
            suggestions.append({
                "type": "pattern",
                "pattern": "avoid_globals",
                "description": "Global state modification detected",
                "recommendation": "Use dependency injection or class attributes",
                "benefit": "Reduces coupling and improves testability",
                "impact": "medium",
            })

        return suggestions

    def _suggest_extractions(self, code: str, language: str) -> List[Dict]:
        """Suggest method/class extractions."""
        suggestions = []

        lines = code.splitlines()

        # Long functions
        in_function = False
        func_start = 0
        func_name = ""

        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                if in_function and (i - func_start) > 30:
                    suggestions.append({
                        "type": "extract",
                        "pattern": "extract_method",
                        "description": f"Function '{func_name}' is {i - func_start} lines long",
                        "recommendation": "Extract logical sections into helper methods",
                        "impact": "medium",
                    })
                in_function = True
                func_start = i
                match = re.search(r'def (\w+)', line)
                func_name = match.group(1) if match else "unknown"

        # Repeated code blocks
        code_blocks = {}
        current_block = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                current_block.append(stripped)
                if len(current_block) == 3:
                    block_key = "\n".join(current_block)
                    code_blocks[block_key] = code_blocks.get(block_key, 0) + 1
                    current_block.pop(0)

        for block, count in code_blocks.items():
            if count > 1:
                suggestions.append({
                    "type": "extract",
                    "pattern": "extract_duplicate",
                    "description": f"Similar code block appears {count} times",
                    "recommendation": "Extract to reusable function",
                    "impact": "medium",
                })
                break  # Only report first duplicate

        # Complex conditions
        complex_conditions = re.findall(r'if\s+(.{50,}?):', code)
        for cond in complex_conditions:
            suggestions.append({
                "type": "extract",
                "pattern": "extract_condition",
                "description": "Complex condition should be extracted",
                "recommendation": "Create descriptively-named boolean function or variable",
                "impact": "low",
            })

        return suggestions

    def _suggest_renames(self, code: str, language: str) -> List[Dict]:
        """Suggest naming improvements."""
        suggestions = []

        # Single-letter names (except common ones)
        allowed = {"i", "j", "k", "x", "y", "z", "n", "e", "_"}
        single_vars = set(re.findall(r'\b([a-zA-Z])\s*=', code)) - allowed

        if single_vars:
            suggestions.append({
                "type": "rename",
                "pattern": "descriptive_names",
                "description": f"Single-letter variables: {', '.join(single_vars)}",
                "recommendation": "Use descriptive names that indicate purpose",
                "impact": "low",
            })

        # Abbreviated names
        abbrevs = re.findall(r'\b([a-z]{1,3}(?:_[a-z]{1,3})+)\b', code)
        if abbrevs:
            suggestions.append({
                "type": "rename",
                "pattern": "avoid_abbreviations",
                "description": f"Abbreviated names found: {', '.join(set(abbrevs)[:3])}",
                "recommendation": "Use full words for clarity",
                "impact": "low",
            })

        # Generic names
        generic = {"data", "info", "temp", "tmp", "val", "obj", "item", "thing"}
        found_generic = set(re.findall(r'\b(' + '|'.join(generic) + r')\b', code, re.I))

        if found_generic:
            suggestions.append({
                "type": "rename",
                "pattern": "specific_names",
                "description": f"Generic names: {', '.join(found_generic)}",
                "recommendation": "Use domain-specific names (e.g., 'user' not 'data')",
                "impact": "low",
            })

        return suggestions

    def _suggest_modernizations(self, code: str, language: str) -> List[Dict]:
        """Suggest modern Python idioms."""
        suggestions = []

        # Old-style string formatting
        if re.search(r'%\s*\(', code) or re.search(r'%[sd]', code):
            suggestions.append({
                "type": "modernize",
                "pattern": "f_strings",
                "description": "Old-style % string formatting",
                "recommendation": "Use f-strings for readability",
                "before": '"%s %d" % (name, age)',
                "after": 'f"{name} {age}"',
                "impact": "low",
            })

        # .format() can often be f-string
        if ".format(" in code:
            suggestions.append({
                "type": "modernize",
                "pattern": "f_strings",
                "description": ".format() can be simplified",
                "recommendation": "Use f-strings where possible",
                "impact": "low",
            })

        # Old-style classes
        if re.search(r'class \w+\s*:', code) and "class " in code:
            if not re.search(r'class \w+\([^)]*\):', code):
                suggestions.append({
                    "type": "modernize",
                    "pattern": "new_style_class",
                    "description": "Class without explicit base",
                    "recommendation": "Inherit from object or appropriate base class",
                    "impact": "low",
                })

        # dict.keys() iteration
        if re.search(r'for \w+ in \w+\.keys\(\)', code):
            suggestions.append({
                "type": "modernize",
                "pattern": "dict_iteration",
                "description": ".keys() is redundant for iteration",
                "before": "for key in dict.keys():",
                "after": "for key in dict:",
                "impact": "low",
            })

        # Type comments vs annotations
        if re.search(r'#\s*type:', code):
            suggestions.append({
                "type": "modernize",
                "pattern": "type_annotations",
                "description": "Type comments found",
                "recommendation": "Use inline type annotations (PEP 484)",
                "impact": "low",
            })

        return suggestions

    def _suggest_cleanup(self, code: str, language: str) -> List[Dict]:
        """Suggest dead code removal."""
        suggestions = []

        # Commented-out code
        commented_code = len(re.findall(r'#\s*(?:def|class|if|for|while|return|import)', code))
        if commented_code > 2:
            suggestions.append({
                "type": "cleanup",
                "pattern": "commented_code",
                "description": f"Found {commented_code} commented-out code blocks",
                "recommendation": "Remove or restore commented code; use version control",
                "impact": "low",
            })

        # Unused imports (simple heuristic)
        imports = re.findall(r'import (\w+)|from \w+ import (\w+)', code)
        for imp in imports:
            name = imp[0] or imp[1]
            # Check if name appears elsewhere in code
            occurrences = len(re.findall(rf'\b{name}\b', code))
            if occurrences <= 1:  # Only in import
                suggestions.append({
                    "type": "cleanup",
                    "pattern": "unused_import",
                    "description": f"Import '{name}' may be unused",
                    "recommendation": "Remove if not needed",
                    "impact": "low",
                })

        # pass statements that could be docstrings
        if re.search(r':\s*\n\s+pass\s*\n', code):
            suggestions.append({
                "type": "cleanup",
                "pattern": "empty_blocks",
                "description": "Empty blocks with pass statement",
                "recommendation": "Add implementation or docstring explaining why empty",
                "impact": "low",
            })

        return suggestions

    def _calculate_improvement(self, suggestions: List[Dict]) -> int:
        """Calculate potential improvement score."""
        impact_scores = {"high": 20, "medium": 10, "low": 5}
        total = sum(impact_scores.get(s.get("impact", "low"), 0) for s in suggestions)
        return min(100, total)

    def _calculate_metrics(self, code: str) -> Dict[str, int]:
        """Calculate code metrics."""
        lines = code.splitlines()
        return {
            "total_lines": len(lines),
            "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith("#")),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#")),
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "functions": len(re.findall(r'def \w+', code)),
            "classes": len(re.findall(r'class \w+', code)),
        }

    def _get_guidance(self, suggestions: List[Dict], style: str) -> str:
        """Get refactoring guidance based on suggestions and style."""
        if not suggestions:
            return "Code looks clean! No immediate refactoring needed."

        high_impact = [s for s in suggestions if s.get("impact") == "high"]
        if high_impact:
            return f"Focus on high-impact refactorings first: {high_impact[0]['pattern']}"

        return f"Found {len(suggestions)} potential improvements. Start with any and iterate."

    def get_prompt(self) -> str:
        return """You are a code refactoring expert.

When refactoring:
1. Preserve existing behavior (unless explicitly asked to change)
2. Prioritize readability and maintainability
3. Apply SOLID principles where appropriate
4. Use modern language idioms
5. Remove dead code and simplify complex logic

Explain each refactoring:
- What changed
- Why it's better
- Any trade-offs
"""
