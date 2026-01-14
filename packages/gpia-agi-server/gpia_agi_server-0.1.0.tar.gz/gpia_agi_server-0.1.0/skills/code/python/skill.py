"""
Python Development Skill
========================

Comprehensive Python development assistance including code generation,
debugging, optimization, and best practices guidance.
"""

import ast
import re
import time
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class PythonSkill(Skill):
    """
    Python development skill providing:
    - Code generation from descriptions
    - Debugging assistance
    - Code optimization suggestions
    - Best practices guidance
    - Type hint generation
    """

    TASK_TYPES = ["generate", "debug", "optimize", "explain", "type_hints", "document"]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="code/python",
            name="Python Development",
            description="Comprehensive Python development assistance including code generation, debugging, optimization, and best practices guidance.",
            version="0.1.0",
            category=SkillCategory.CODE,
            level=SkillLevel.INTERMEDIATE,
            tags=["python", "programming", "development", "debugging", "optimization"],
            requires_tools=["python_interpreter"],
            estimated_tokens=800,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "enum": self.TASK_TYPES,
                    "description": "Type of Python task to perform",
                },
                "code": {
                    "type": "string",
                    "description": "Python code to analyze/modify (for debug, optimize, explain tasks)",
                },
                "description": {
                    "type": "string",
                    "description": "Description of what to generate (for generate task)",
                },
                "error": {
                    "type": "string",
                    "description": "Error message for debugging tasks",
                },
                "requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional requirements or constraints",
                },
                "style": {
                    "type": "string",
                    "enum": ["concise", "verbose", "production"],
                    "default": "production",
                    "description": "Code style preference",
                },
            },
            "required": ["task"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        task = input_data.get("task", "")
        code = input_data.get("code", "")
        description = input_data.get("description", "")
        error = input_data.get("error", "")
        requirements = input_data.get("requirements", [])
        style = input_data.get("style", "production")

        try:
            if task == "generate":
                result = self._generate_code(description, requirements, style, context)
            elif task == "debug":
                result = self._debug_code(code, error, context)
            elif task == "optimize":
                result = self._optimize_code(code, context)
            elif task == "explain":
                result = self._explain_code(code, context)
            elif task == "type_hints":
                result = self._add_type_hints(code, context)
            elif task == "document":
                result = self._document_code(code, style, context)
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown task type: {task}",
                    error_code="INVALID_TASK",
                    skill_id=self.metadata().id,
                )

            execution_time = int((time.time() - start_time) * 1000)

            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,
                suggestions=self._get_suggestions(task, result),
                related_skills=["code/review", "code/refactor", "code/test"],
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self.metadata().id,
            )

    def _generate_code(
        self,
        description: str,
        requirements: List[str],
        style: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Generate Python code from description."""
        # Build generation prompt
        prompt_parts = [
            f"Generate Python code for: {description}",
        ]

        if requirements:
            prompt_parts.append("\nRequirements:")
            for req in requirements:
                prompt_parts.append(f"- {req}")

        if style == "production":
            prompt_parts.append("\nFollow production best practices:")
            prompt_parts.append("- Include type hints")
            prompt_parts.append("- Add docstrings")
            prompt_parts.append("- Handle edge cases")
            prompt_parts.append("- Follow PEP 8")

        return {
            "prompt": "\n".join(prompt_parts),
            "template": self._get_code_template(description),
            "guidelines": self._get_style_guidelines(style),
        }

    def _debug_code(
        self,
        code: str,
        error: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Analyze code for bugs and suggest fixes."""
        issues = []
        suggestions = []

        # Static analysis
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": str(e.msg),
            })

        # Common bug patterns
        patterns = self._check_common_bugs(code)
        issues.extend(patterns)

        # Error-specific analysis
        if error:
            diagnosis = self._analyze_error(error, code)
            suggestions.extend(diagnosis.get("suggestions", []))

        return {
            "issues": issues,
            "suggestions": suggestions,
            "error_analysis": error if error else None,
            "fix_guidance": self._get_fix_guidance(issues),
        }

    def _optimize_code(
        self,
        code: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Suggest optimizations for Python code."""
        optimizations = []

        # Check for common inefficiencies
        if "for i in range(len(" in code:
            optimizations.append({
                "pattern": "range(len()) iteration",
                "suggestion": "Use enumerate() or direct iteration",
                "impact": "minor",
            })

        if ".append(" in code and "for " in code:
            optimizations.append({
                "pattern": "Loop with append",
                "suggestion": "Consider list comprehension",
                "impact": "minor to moderate",
            })

        if " + " in code and ("str(" in code or '""' in code or "''" in code):
            optimizations.append({
                "pattern": "String concatenation in loop",
                "suggestion": "Use join() or f-strings",
                "impact": "significant for large strings",
            })

        if "if item not in list" in code.lower() or re.search(r'if \w+ not in \w+:', code):
            optimizations.append({
                "pattern": "Membership check in list",
                "suggestion": "Convert to set for O(1) lookup",
                "impact": "significant for large collections",
            })

        return {
            "optimizations": optimizations,
            "complexity_notes": self._analyze_complexity(code),
            "memory_notes": self._analyze_memory(code),
        }

    def _explain_code(
        self,
        code: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Explain what Python code does."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Could not parse code", "raw_analysis": code}

        # Extract structure
        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "bases": [self._get_name(b) for b in node.bases],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(self._get_import_info(node))

        return {
            "structure": {
                "functions": functions,
                "classes": classes,
                "imports": imports,
            },
            "line_count": len(code.splitlines()),
        }

    def _add_type_hints(
        self,
        code: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Suggest type hints for Python code."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Could not parse code"}

        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for missing return type
                if node.returns is None:
                    suggestions.append({
                        "function": node.name,
                        "suggestion": "Add return type annotation",
                        "example": f"def {node.name}(...) -> ReturnType:",
                    })

                # Check for missing argument types
                for arg in node.args.args:
                    if arg.annotation is None:
                        suggestions.append({
                            "function": node.name,
                            "argument": arg.arg,
                            "suggestion": f"Add type hint for '{arg.arg}'",
                        })

        return {
            "suggestions": suggestions,
            "typing_imports": self._suggest_typing_imports(code),
        }

    def _document_code(
        self,
        code: str,
        style: str,
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Generate documentation for Python code."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Could not parse code"}

        docs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    docs.append({
                        "type": "function",
                        "name": node.name,
                        "template": self._generate_docstring_template(node, style),
                    })
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    docs.append({
                        "type": "class",
                        "name": node.name,
                        "template": self._generate_class_docstring(node, style),
                    })

        return {
            "missing_docs": docs,
            "style_guide": self._get_docstring_style(style),
        }

    # Helper methods

    def _check_common_bugs(self, code: str) -> List[Dict[str, Any]]:
        """Check for common Python bug patterns."""
        bugs = []

        # Mutable default arguments
        if re.search(r'def \w+\([^)]*=\s*\[\]', code):
            bugs.append({
                "type": "mutable_default",
                "message": "Mutable default argument (use None instead)",
                "severity": "warning",
            })

        # Bare except
        if re.search(r'except\s*:', code):
            bugs.append({
                "type": "bare_except",
                "message": "Bare except clause catches all exceptions including KeyboardInterrupt",
                "severity": "warning",
            })

        # == None instead of is None
        if " == None" in code or " != None" in code:
            bugs.append({
                "type": "none_comparison",
                "message": "Use 'is None' or 'is not None' for None comparisons",
                "severity": "style",
            })

        return bugs

    def _analyze_error(self, error: str, code: str) -> Dict[str, Any]:
        """Analyze an error message in context of code."""
        suggestions = []

        if "NoneType" in error:
            suggestions.append("Check for None values before accessing attributes/methods")
            suggestions.append("Add null checks or use Optional type hints")

        if "KeyError" in error:
            suggestions.append("Use .get() method with default value")
            suggestions.append("Check if key exists with 'in' operator")

        if "IndexError" in error:
            suggestions.append("Check list length before accessing indices")
            suggestions.append("Consider using try/except or bounds checking")

        if "AttributeError" in error:
            suggestions.append("Verify object type matches expected interface")
            suggestions.append("Check for typos in attribute names")

        return {"suggestions": suggestions}

    def _analyze_complexity(self, code: str) -> str:
        """Analyze time complexity of code patterns."""
        notes = []

        if re.search(r'for .+ in .+:\s*\n\s*for .+ in .+:', code):
            notes.append("Nested loops detected - O(n*m) or higher complexity")

        if ".sort(" in code or "sorted(" in code:
            notes.append("Sorting operation - O(n log n)")

        return " ".join(notes) if notes else "No obvious complexity concerns"

    def _analyze_memory(self, code: str) -> str:
        """Analyze memory usage patterns."""
        notes = []

        if "list(" in code and "range(" in code:
            notes.append("Consider using range directly instead of list(range())")

        if re.search(r'\[.+for .+ in .+\]', code):
            notes.append("List comprehension creates full list in memory; consider generator for large data")

        return " ".join(notes) if notes else "No obvious memory concerns"

    def _get_code_template(self, description: str) -> str:
        """Get a code template based on description."""
        desc_lower = description.lower()

        if "class" in desc_lower:
            return '''class ClassName:
    """Description."""

    def __init__(self):
        pass

    def method(self):
        pass
'''
        elif "function" in desc_lower or "def" in desc_lower:
            return '''def function_name(param: Type) -> ReturnType:
    """Description.

    Args:
        param: Description

    Returns:
        Description
    """
    pass
'''
        else:
            return "# Implementation goes here\n"

    def _get_style_guidelines(self, style: str) -> List[str]:
        """Get style guidelines for code generation."""
        if style == "concise":
            return ["Minimal comments", "Short variable names OK", "Skip docstrings"]
        elif style == "verbose":
            return ["Detailed comments", "Descriptive names", "Full docstrings", "Examples"]
        else:  # production
            return [
                "Type hints required",
                "Docstrings for public APIs",
                "Error handling",
                "PEP 8 compliant",
                "Unit test friendly",
            ]

    def _get_fix_guidance(self, issues: List[Dict]) -> str:
        """Generate fix guidance based on issues found."""
        if not issues:
            return "No issues found"

        guidance = []
        for issue in issues:
            if issue.get("type") == "syntax_error":
                guidance.append(f"Fix syntax error on line {issue.get('line')}: {issue.get('message')}")
            else:
                guidance.append(f"{issue.get('type')}: {issue.get('message')}")

        return "\n".join(guidance)

    def _get_decorator_name(self, node) -> str:
        """Get decorator name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "unknown"

    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"

    def _get_import_info(self, node) -> Dict[str, Any]:
        """Extract import information from AST node."""
        if isinstance(node, ast.Import):
            return {"type": "import", "names": [alias.name for alias in node.names]}
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from",
                "module": node.module,
                "names": [alias.name for alias in node.names],
            }
        return {}

    def _suggest_typing_imports(self, code: str) -> List[str]:
        """Suggest typing imports that might be needed."""
        suggestions = []

        if "List" not in code and ("[" in code or "list" in code.lower()):
            suggestions.append("from typing import List")
        if "Dict" not in code and ("{" in code or "dict" in code.lower()):
            suggestions.append("from typing import Dict")
        if "Optional" not in code:
            suggestions.append("from typing import Optional")

        return suggestions

    def _generate_docstring_template(self, node: ast.FunctionDef, style: str) -> str:
        """Generate a docstring template for a function."""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        if style == "concise":
            return f'"""Brief description."""'

        lines = ['"""Description.', ""]

        if args:
            lines.append("Args:")
            for arg in args:
                lines.append(f"    {arg}: Description")
            lines.append("")

        lines.append("Returns:")
        lines.append("    Description")
        lines.append('"""')

        return "\n".join(lines)

    def _generate_class_docstring(self, node: ast.ClassDef, style: str) -> str:
        """Generate a docstring template for a class."""
        if style == "concise":
            return f'"""Brief description."""'

        return '''"""Description.

Attributes:
    attr: Description

Example:
    >>> obj = ClassName()
"""'''

    def _get_docstring_style(self, style: str) -> str:
        """Get docstring style guide."""
        styles = {
            "concise": "Google-style, minimal",
            "verbose": "NumPy-style, comprehensive",
            "production": "Google-style with examples",
        }
        return styles.get(style, "Google-style")

    def _get_suggestions(self, task: str, result: Dict) -> List[str]:
        """Get follow-up suggestions based on task results."""
        suggestions = []

        if task == "generate":
            suggestions.append("Run 'code/review' to check code quality")
            suggestions.append("Use 'code/test' to generate test cases")

        elif task == "debug":
            if result.get("issues"):
                suggestions.append("Apply suggested fixes and re-run")
            suggestions.append("Add logging for complex debugging")

        elif task == "optimize":
            if result.get("optimizations"):
                suggestions.append("Profile before and after optimization")
            suggestions.append("Consider algorithmic improvements")

        return suggestions

    def get_prompt(self) -> str:
        """Return the skill's system prompt."""
        return """You are a Python development expert assistant.

Your capabilities include:
- Generating clean, well-documented Python code
- Debugging and fixing Python errors
- Optimizing code for performance
- Adding type hints and documentation
- Following Python best practices (PEP 8, PEP 257)

When generating code:
- Use type hints for function signatures
- Include docstrings with Args/Returns sections
- Handle edge cases and errors gracefully
- Prefer standard library solutions

When debugging:
- Identify the root cause, not just symptoms
- Suggest defensive coding practices
- Provide working, tested fixes

When optimizing:
- Consider both time and space complexity
- Profile before premature optimization
- Maintain readability over micro-optimizations
"""
