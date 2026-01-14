"""
Code Review Skill
=================

Automated code review providing quality analysis, security checks,
best practices validation, and actionable feedback.
"""

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


class CodeReviewSkill(Skill):
    """
    Comprehensive code review skill providing:
    - Security vulnerability detection
    - Code quality analysis
    - Best practices validation
    - Maintainability scoring
    - Actionable improvement suggestions
    """

    CHECK_TYPES = ["security", "quality", "maintainability", "performance", "style", "all"]
    SEVERITY_LEVELS = ["critical", "warning", "info"]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="code/review",
            name="Code Review",
            description="Automated code review providing quality analysis, security checks, best practices validation, and actionable feedback.",
            version="0.1.0",
            category=SkillCategory.CODE,
            level=SkillLevel.INTERMEDIATE,
            tags=["code-review", "quality", "security", "best-practices", "static-analysis"],
            estimated_tokens=600,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to review",
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "default": "python",
                },
                "checks": {
                    "type": "array",
                    "items": {"type": "string", "enum": self.CHECK_TYPES},
                    "description": "Types of checks to perform",
                    "default": ["all"],
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the code's purpose",
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
        checks = input_data.get("checks", ["all"])
        code_context = input_data.get("context", "")

        if "all" in checks:
            checks = self.CHECK_TYPES[:-1]  # All except "all"

        issues = []

        # Run requested checks
        if "security" in checks:
            issues.extend(self._check_security(code, language))

        if "quality" in checks:
            issues.extend(self._check_quality(code, language))

        if "maintainability" in checks:
            issues.extend(self._check_maintainability(code, language))

        if "performance" in checks:
            issues.extend(self._check_performance(code, language))

        if "style" in checks:
            issues.extend(self._check_style(code, language))

        # Calculate score
        score = self._calculate_score(issues, code)

        # Generate summary
        summary = self._generate_summary(issues, score)

        execution_time = int((time.time() - start_time) * 1000)

        return SkillResult(
            success=True,
            output={
                "issues": issues,
                "score": score,
                "summary": summary,
                "checks_performed": checks,
                "line_count": len(code.splitlines()),
                "recommendations": self._get_recommendations(issues),
            },
            execution_time_ms=execution_time,
            skill_id=self.metadata().id,
            suggestions=[
                "Apply suggested fixes and re-review",
                "Consider adding automated tests for flagged issues",
            ],
            related_skills=["code/refactor", "code/python", "code/test"],
        )

    def _check_security(self, code: str, language: str) -> List[Dict]:
        """Check for security vulnerabilities."""
        issues = []

        # SQL Injection patterns
        sql_patterns = [
            (r'f"[^"]*SELECT.*{', "SQL injection via f-string"),
            (r"f'[^']*SELECT.*{", "SQL injection via f-string"),
            (r'"\s*\+\s*\w+\s*\+\s*".*(?:SELECT|INSERT|UPDATE|DELETE)', "SQL injection via concatenation"),
            (r"execute\([^)]*%", "SQL injection via string formatting"),
        ]

        for pattern, message in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "severity": "critical",
                    "type": "security",
                    "message": message,
                    "recommendation": "Use parameterized queries instead",
                })

        # Command Injection
        cmd_patterns = [
            (r'os\.system\s*\([^)]*[+%{]', "Command injection risk"),
            (r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True', "Shell injection with shell=True"),
            (r'eval\s*\(', "Dangerous eval() usage"),
            (r'exec\s*\(', "Dangerous exec() usage"),
        ]

        for pattern, message in cmd_patterns:
            if re.search(pattern, code):
                issues.append({
                    "severity": "critical",
                    "type": "security",
                    "message": message,
                    "recommendation": "Avoid dynamic code execution; use safer alternatives",
                })

        # Hardcoded secrets
        secret_patterns = [
            (r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'(?:api_key|apikey|secret)\s*=\s*["\'][^"\']+["\']', "Hardcoded API key/secret"),
            (r'(?:token)\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "Hardcoded token"),
        ]

        for pattern, message in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "severity": "critical",
                    "type": "security",
                    "message": message,
                    "recommendation": "Use environment variables or secure secret management",
                })

        # Path traversal
        if re.search(r'open\s*\([^)]*\+', code):
            issues.append({
                "severity": "warning",
                "type": "security",
                "message": "Potential path traversal vulnerability",
                "recommendation": "Validate and sanitize file paths",
            })

        return issues

    def _check_quality(self, code: str, language: str) -> List[Dict]:
        """Check code quality issues."""
        issues = []
        lines = code.splitlines()

        # Long functions (heuristic: many lines between def and next def/class)
        func_starts = []
        for i, line in enumerate(lines):
            if line.strip().startswith(("def ", "class ")):
                func_starts.append(i)

        for i, start in enumerate(func_starts):
            end = func_starts[i + 1] if i + 1 < len(func_starts) else len(lines)
            if end - start > 50:
                issues.append({
                    "severity": "warning",
                    "type": "quality",
                    "message": f"Function/class starting at line {start + 1} is too long ({end - start} lines)",
                    "recommendation": "Consider breaking into smaller functions",
                })

        # Deep nesting
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)

        if max_indent > 20:  # ~5 levels of nesting
            issues.append({
                "severity": "warning",
                "type": "quality",
                "message": "Deep nesting detected",
                "recommendation": "Reduce nesting with early returns or extraction",
            })

        # Duplicate code patterns (simple check)
        seen_blocks = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 30:  # Significant lines
                if stripped in seen_blocks:
                    issues.append({
                        "severity": "info",
                        "type": "quality",
                        "message": f"Potential duplicate code at lines {seen_blocks[stripped] + 1} and {i + 1}",
                        "recommendation": "Extract to reusable function",
                    })
                else:
                    seen_blocks[stripped] = i

        # Missing docstrings
        if language == "python":
            if re.search(r'def \w+\([^)]*\):\s*\n\s*(?!""")', code):
                issues.append({
                    "severity": "info",
                    "type": "quality",
                    "message": "Functions without docstrings detected",
                    "recommendation": "Add docstrings for public functions",
                })

        return issues

    def _check_maintainability(self, code: str, language: str) -> List[Dict]:
        """Check maintainability issues."""
        issues = []

        # Magic numbers
        magic_pattern = r'(?<!["\'\w])(?:[2-9]\d{2,}|[1-9]\d{3,})(?!["\'\w])'
        if re.search(magic_pattern, code):
            issues.append({
                "severity": "info",
                "type": "maintainability",
                "message": "Magic numbers detected",
                "recommendation": "Extract to named constants",
            })

        # No type hints (Python)
        if language == "python":
            if re.search(r'def \w+\([^:)]*\):', code) and "->" not in code:
                issues.append({
                    "severity": "info",
                    "type": "maintainability",
                    "message": "Missing type hints",
                    "recommendation": "Add type annotations for better IDE support and documentation",
                })

        # Single-letter variable names (except common ones)
        allowed = {"i", "j", "k", "x", "y", "z", "n", "e", "_"}
        single_vars = set(re.findall(r'\b([a-zA-Z])\s*=', code)) - allowed
        if single_vars:
            issues.append({
                "severity": "info",
                "type": "maintainability",
                "message": f"Single-letter variable names: {', '.join(single_vars)}",
                "recommendation": "Use descriptive variable names",
            })

        # TODO/FIXME comments
        todo_count = len(re.findall(r'#\s*(?:TODO|FIXME|HACK|XXX)', code, re.IGNORECASE))
        if todo_count > 0:
            issues.append({
                "severity": "info",
                "type": "maintainability",
                "message": f"Found {todo_count} TODO/FIXME comments",
                "recommendation": "Address or track these items",
            })

        return issues

    def _check_performance(self, code: str, language: str) -> List[Dict]:
        """Check for performance issues."""
        issues = []

        # Nested loops
        if re.search(r'for .+ in .+:\s*\n\s*for .+ in .+:', code):
            issues.append({
                "severity": "warning",
                "type": "performance",
                "message": "Nested loops detected - O(n*m) complexity",
                "recommendation": "Consider using sets, dicts, or algorithmic improvements",
            })

        # List membership in loop
        if re.search(r'for .+:\s*\n[^#\n]*if .+ in \w+:', code):
            issues.append({
                "severity": "info",
                "type": "performance",
                "message": "List membership check in loop",
                "recommendation": "Convert to set for O(1) lookup",
            })

        # String concatenation in loop
        if re.search(r'for .+:\s*\n[^#\n]*\w+\s*[+]=\s*["\']', code):
            issues.append({
                "severity": "warning",
                "type": "performance",
                "message": "String concatenation in loop",
                "recommendation": "Use list append + join or io.StringIO",
            })

        # Repeated function calls with same args
        if re.search(r'(\w+\([^)]+\)).*\1', code):
            issues.append({
                "severity": "info",
                "type": "performance",
                "message": "Repeated function calls detected",
                "recommendation": "Cache result in variable if function is pure",
            })

        return issues

    def _check_style(self, code: str, language: str) -> List[Dict]:
        """Check style issues."""
        issues = []
        lines = code.splitlines()

        # Line length
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({
                    "severity": "info",
                    "type": "style",
                    "message": f"Line {i + 1} exceeds 120 characters ({len(line)})",
                    "recommendation": "Break into multiple lines",
                })
                break  # Only report first occurrence

        # Trailing whitespace
        trailing_ws = sum(1 for line in lines if line.rstrip() != line)
        if trailing_ws > 0:
            issues.append({
                "severity": "info",
                "type": "style",
                "message": f"Trailing whitespace on {trailing_ws} lines",
                "recommendation": "Remove trailing whitespace",
            })

        # Inconsistent quotes (Python)
        if language == "python":
            single = len(re.findall(r"'[^']*'", code))
            double = len(re.findall(r'"[^"]*"', code))
            if single > 0 and double > 0 and abs(single - double) > 5:
                issues.append({
                    "severity": "info",
                    "type": "style",
                    "message": "Inconsistent string quote style",
                    "recommendation": "Standardize on single or double quotes",
                })

        # Comparison to True/False
        if re.search(r'==\s*True|==\s*False|is\s+True|is\s+False', code):
            issues.append({
                "severity": "info",
                "type": "style",
                "message": "Explicit comparison to True/False",
                "recommendation": "Use truthiness directly (if x: instead of if x == True:)",
            })

        return issues

    def _calculate_score(self, issues: List[Dict], code: str) -> int:
        """Calculate a quality score from 0-100."""
        base_score = 100

        # Deduct points based on severity
        severity_deductions = {
            "critical": 25,
            "warning": 10,
            "info": 3,
        }

        for issue in issues:
            severity = issue.get("severity", "info")
            base_score -= severity_deductions.get(severity, 0)

        # Bonus for good practices
        if '"""' in code or "'''" in code:
            base_score += 5  # Has docstrings

        if "->" in code:
            base_score += 5  # Has type hints

        return max(0, min(100, base_score))

    def _generate_summary(self, issues: List[Dict], score: int) -> str:
        """Generate a human-readable summary."""
        if not issues:
            return "Excellent! No issues found."

        critical = sum(1 for i in issues if i.get("severity") == "critical")
        warnings = sum(1 for i in issues if i.get("severity") == "warning")
        info = sum(1 for i in issues if i.get("severity") == "info")

        parts = []

        if critical > 0:
            parts.append(f"{critical} critical issue(s)")
        if warnings > 0:
            parts.append(f"{warnings} warning(s)")
        if info > 0:
            parts.append(f"{info} suggestion(s)")

        quality = "poor" if score < 50 else "fair" if score < 70 else "good" if score < 90 else "excellent"

        return f"Code quality: {quality} (score: {score}). Found {', '.join(parts)}."

    def _get_recommendations(self, issues: List[Dict]) -> List[str]:
        """Get prioritized recommendations."""
        # Group by type and prioritize
        critical_recs = []
        other_recs = []

        for issue in issues:
            rec = issue.get("recommendation", "")
            if rec:
                if issue.get("severity") == "critical":
                    critical_recs.append(f"[CRITICAL] {rec}")
                else:
                    other_recs.append(rec)

        # Deduplicate and limit
        all_recs = critical_recs + list(set(other_recs))
        return all_recs[:10]  # Top 10 recommendations

    def get_prompt(self) -> str:
        return """You are a code review expert assistant.

When reviewing code:
1. Prioritize security issues (SQL injection, XSS, command injection)
2. Check for code quality (readability, maintainability)
3. Identify performance bottlenecks
4. Ensure best practices are followed
5. Provide actionable, specific recommendations

Be constructive and educational in feedback. Explain WHY something is an issue,
not just WHAT the issue is.
"""
