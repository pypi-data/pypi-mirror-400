"""
Placeholder Scanner Skill
=========================

Scans the repository for placeholders and uses GPIA to populate them.

Placeholder Types Detected:
- TODO/FIXME/XXX comments
- Ellipsis "..." in code (not prose)
- Empty strings in configs
- NotImplementedError stubs
- Template variables like ${...} or {{...}}
- "placeholder" text
- Pass statements that look like stubs

Usage:
    from skills.system.placeholder_scanner.skill import PlaceholderScannerSkill

    scanner = PlaceholderScannerSkill()
    result = scanner.execute({
        "capability": "scan",
        "paths": ["skills/", "configs/"],
    }, context)
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

logger = logging.getLogger(__name__)


@dataclass
class Placeholder:
    """Represents a found placeholder."""
    file: str
    line: int
    column: int
    pattern: str
    match: str
    context_before: str
    context_after: str
    line_content: str
    suggested_fix: Optional[str] = None
    confidence: float = 0.0
    fix_applied: bool = False


# Default patterns to search for
DEFAULT_PATTERNS = {
    "TODO": r"#\s*TODO[:\s](.+?)(?:\n|$)",
    "FIXME": r"#\s*FIXME[:\s](.+?)(?:\n|$)",
    "XXX": r"#\s*XXX[:\s](.+?)(?:\n|$)",
    "PLACEHOLDER": r"['\"]?placeholder['\"]?",
    "ELLIPSIS_CODE": r"['\"]\.\.\.['\"]\s*[,\)]",  # "..." in code
    "EMPTY_STRING_CONFIG": r":\s*['\"]['\"](?:\s*#|$)",  # Empty strings in YAML/config
    "NOT_IMPLEMENTED": r"raise\s+NotImplementedError(?:\(.*?\))?",
    "PASS_STUB": r"def\s+\w+\([^)]*\):\s*\n\s+pass\s*$",
    "TEMPLATE_VAR": r"\$\{[^}]+\}|\{\{[^}]+\}\}",
}

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".js", ".ts", ".vue", ".jsx", ".tsx", ".html", ".css",
    ".md", ".txt", ".sh", ".ps1", ".bat",
}

# Directories to exclude
EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".pytest_cache", ".mypy_cache",
    "runs", "data", ".claude",
}


class PlaceholderScannerSkill(BaseSkill):
    """
    Scans repository for placeholders and uses GPIA to populate them.

    Capabilities:
    - scan: Find all placeholders
    - analyze: Analyze context and suggest fixes
    - populate: Generate fixes using GPIA
    - report: Generate comprehensive report
    - fix: Apply fixes to files
    """

    SKILL_ID = "system/placeholder-scanner"
    SKILL_NAME = "Placeholder Scanner"
    SKILL_DESCRIPTION = "Scans repositories for TODOs and stubs and suggests fixes."
    SKILL_CATEGORY = SkillCategory.SYSTEM
    SKILL_LEVEL = SkillLevel.INTERMEDIATE
    SKILL_TAGS = ["maintenance", "code-quality", "automation", "refactoring"]

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[3]
        self.gpia = None  # Lazy load to avoid circular imports
        self._placeholders: List[Placeholder] = []

    def _ensure_gpia(self):
        """Lazy load GPIA to avoid circular imports."""
        if self.gpia is None:
            try:
                from gpia import GPIA
                self.gpia = GPIA(verbose=False)
            except ImportError:
                logger.warning("GPIA not available, running in scan-only mode")

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute the placeholder scanner skill."""
        capability = params.get("capability", "scan")

        try:
            if capability == "scan":
                return self._scan(params, context)
            elif capability == "analyze":
                return self._analyze(params, context)
            elif capability == "populate":
                return self._populate(params, context)
            elif capability == "report":
                return self._report(params, context)
            elif capability == "fix":
                return self._fix(params, context)
            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    error=f"Unknown capability: {capability}"
                )
        except Exception as e:
            logger.exception(f"Error in PlaceholderScannerSkill: {e}")
            return SkillResult(
                success=False,
                output={"error": str(e)},
                error=str(e)
            )

    def _get_patterns(self, params: Dict) -> Dict[str, str]:
        """Get patterns to search for."""
        patterns = DEFAULT_PATTERNS.copy()

        # Add custom patterns
        custom = params.get("patterns", [])
        for i, p in enumerate(custom):
            patterns[f"CUSTOM_{i}"] = p

        return patterns

    def _should_scan_file(self, path: Path, params: Dict) -> bool:
        """Check if file should be scanned."""
        # Check extension
        if path.suffix.lower() not in SCANNABLE_EXTENSIONS:
            return False

        # Check excluded directories
        for part in path.parts:
            if part in EXCLUDE_DIRS:
                return False

        # Check exclude patterns
        exclude_patterns = params.get("exclude_patterns", [])
        for pattern in exclude_patterns:
            if re.search(pattern, str(path)):
                return False

        return True

    def _scan_file(self, file_path: Path, patterns: Dict[str, str]) -> List[Placeholder]:
        """Scan a single file for placeholders."""
        placeholders = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
        except Exception as e:
            logger.debug(f"Could not read {file_path}: {e}")
            return []

        for pattern_name, pattern in patterns.items():
            try:
                for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                    # Calculate line number
                    line_start = content[:match.start()].count("\n")
                    col = match.start() - content.rfind("\n", 0, match.start()) - 1

                    # Get context
                    context_start = max(0, line_start - 2)
                    context_end = min(len(lines), line_start + 3)

                    context_before = "\n".join(lines[context_start:line_start])
                    context_after = "\n".join(lines[line_start + 1:context_end])
                    line_content = lines[line_start] if line_start < len(lines) else ""

                    # Skip false positives
                    if self._is_false_positive(pattern_name, match.group(), line_content, file_path):
                        continue

                    placeholders.append(Placeholder(
                        file=str(file_path.relative_to(self.repo_root)),
                        line=line_start + 1,
                        column=col,
                        pattern=pattern_name,
                        match=match.group()[:100],
                        context_before=context_before[:200],
                        context_after=context_after[:200],
                        line_content=line_content[:200],
                    ))
            except re.error as e:
                logger.warning(f"Invalid regex pattern {pattern_name}: {e}")

        return placeholders

    def _is_false_positive(self, pattern_name: str, match: str, line: str, file_path: Path) -> bool:
        """Filter out false positives."""
        # Skip TODO detection in files that analyze TODOs
        if pattern_name in ["TODO", "FIXME", "XXX"]:
            if "review" in str(file_path).lower() or "lint" in str(file_path).lower():
                return True
            # Skip if it's in a string literal describing what to detect
            if "detect" in line.lower() or "find" in line.lower() or "search" in line.lower():
                return True

        # Skip ellipsis in markdown prose
        if pattern_name == "ELLIPSIS_CODE":
            if file_path.suffix.lower() in [".md", ".txt", ".rst"]:
                return True

        # Skip template variables in template engines
        if pattern_name == "TEMPLATE_VAR":
            if "template" in str(file_path).lower() or "jinja" in str(file_path).lower():
                return True

        # Skip pass in test files (intentional stubs)
        if pattern_name == "PASS_STUB":
            if "test" in str(file_path).lower():
                return True

        return False

    def _scan(self, params: Dict, context: SkillContext) -> SkillResult:
        """Scan repository for placeholders."""
        paths = params.get("paths", ["."])
        patterns = self._get_patterns(params)

        self._placeholders = []
        files_scanned = 0

        for path_str in paths:
            scan_path = self.repo_root / path_str

            if scan_path.is_file():
                if self._should_scan_file(scan_path, params):
                    self._placeholders.extend(self._scan_file(scan_path, patterns))
                    files_scanned += 1
            elif scan_path.is_dir():
                for file_path in scan_path.rglob("*"):
                    if file_path.is_file() and self._should_scan_file(file_path, params):
                        self._placeholders.extend(self._scan_file(file_path, patterns))
                        files_scanned += 1

        # Build summary
        by_pattern = {}
        by_file = {}
        for p in self._placeholders:
            by_pattern[p.pattern] = by_pattern.get(p.pattern, 0) + 1
            by_file[p.file] = by_file.get(p.file, 0) + 1

        return SkillResult(
            success=True,
            output={
                "placeholders": [
                    {
                        "file": p.file,
                        "line": p.line,
                        "pattern": p.pattern,
                        "match": p.match,
                        "line_content": p.line_content,
                    }
                    for p in self._placeholders
                ],
                "summary": {
                    "total_found": len(self._placeholders),
                    "files_scanned": files_scanned,
                    "by_pattern": by_pattern,
                    "by_file": by_file,
                }
            }
        )

    def _analyze(self, params: Dict, context: SkillContext) -> SkillResult:
        """Analyze placeholders and determine what should fill them."""
        # First scan if not already done
        if not self._placeholders:
            self._scan(params, context)

        self._ensure_gpia()

        analyzed = []
        for placeholder in self._placeholders[:20]:  # Limit to first 20
            analysis = self._analyze_placeholder(placeholder)
            analyzed.append({
                **analysis,
                "file": placeholder.file,
                "line": placeholder.line,
                "pattern": placeholder.pattern,
            })

        return SkillResult(
            success=True,
            output={
                "analyzed": analyzed,
                "total_analyzed": len(analyzed),
                "remaining": max(0, len(self._placeholders) - 20),
            }
        )

    def _analyze_placeholder(self, placeholder: Placeholder) -> Dict:
        """Analyze a single placeholder to understand what it needs."""
        # Build context for analysis
        context_text = f"""
File: {placeholder.file}
Line {placeholder.line}: {placeholder.line_content}

Context before:
{placeholder.context_before}

Context after:
{placeholder.context_after}

Placeholder type: {placeholder.pattern}
Match: {placeholder.match}
"""

        analysis = {
            "needs_human_input": False,
            "can_auto_fill": False,
            "reason": "",
            "suggested_approach": "",
        }

        # Heuristic analysis
        if placeholder.pattern in ["TODO", "FIXME", "XXX"]:
            # TODOs usually need human decision
            analysis["needs_human_input"] = True
            analysis["reason"] = "TODO/FIXME comments typically require human decision about implementation"
            analysis["suggested_approach"] = "Review the TODO and either implement or document why it's deferred"

        elif placeholder.pattern == "EMPTY_STRING_CONFIG":
            # Empty config might be intentional (for env vars)
            if "api" in placeholder.line_content.lower() or "key" in placeholder.line_content.lower():
                analysis["needs_human_input"] = True
                analysis["reason"] = "Appears to be an API key or secret - should come from environment"
                analysis["suggested_approach"] = "Set via environment variable, not hardcoded"
            else:
                analysis["can_auto_fill"] = True
                analysis["reason"] = "Empty configuration value that may have a sensible default"

        elif placeholder.pattern == "NOT_IMPLEMENTED":
            analysis["can_auto_fill"] = True
            analysis["reason"] = "Stub method that can potentially be implemented based on context"
            analysis["suggested_approach"] = "Use GPIA to generate implementation based on method signature and docstring"

        elif placeholder.pattern == "PASS_STUB":
            analysis["can_auto_fill"] = True
            analysis["reason"] = "Empty function body that can be filled based on function name and context"

        elif placeholder.pattern == "PLACEHOLDER":
            analysis["can_auto_fill"] = True
            analysis["reason"] = "Generic placeholder text that should be replaced with actual content"

        return analysis

    def _populate(self, params: Dict, context: SkillContext) -> SkillResult:
        """Use GPIA to generate content for placeholders."""
        # First scan and analyze
        if not self._placeholders:
            self._scan(params, context)

        self._ensure_gpia()

        if not self.gpia:
            return SkillResult(
                success=False,
                output={"error": "GPIA not available"},
                error="GPIA not available for content generation"
            )

        populated = []
        dry_run = params.get("dry_run", True)

        for placeholder in self._placeholders[:10]:  # Limit to 10 at a time
            analysis = self._analyze_placeholder(placeholder)

            if not analysis["can_auto_fill"]:
                populated.append({
                    "file": placeholder.file,
                    "line": placeholder.line,
                    "status": "skipped",
                    "reason": analysis["reason"],
                })
                continue

            # Generate fix using GPIA
            suggested_fix = self._generate_fix(placeholder)
            placeholder.suggested_fix = suggested_fix
            placeholder.confidence = 0.7  # Base confidence

            populated.append({
                "file": placeholder.file,
                "line": placeholder.line,
                "pattern": placeholder.pattern,
                "original": placeholder.match,
                "suggested_fix": suggested_fix,
                "confidence": placeholder.confidence,
                "status": "generated" if dry_run else "pending_apply",
            })

        return SkillResult(
            success=True,
            output={
                "populated": populated,
                "dry_run": dry_run,
                "message": "Use capability='fix' with dry_run=false to apply changes"
            }
        )

    def _generate_fix(self, placeholder: Placeholder) -> str:
        """Generate a fix for a placeholder using GPIA."""
        prompt = f"""Analyze this placeholder and generate appropriate content to replace it.

File: {placeholder.file}
Line {placeholder.line}: {placeholder.line_content}

Context before:
{placeholder.context_before}

Context after:
{placeholder.context_after}

Placeholder type: {placeholder.pattern}
Current content: {placeholder.match}

Generate ONLY the replacement content, nothing else. Be concise and match the code style.
If this is a TODO comment, generate the actual implementation code.
If this is an empty string, generate an appropriate default value.
If this is a stub function, generate the implementation.
"""

        try:
            result = self.gpia.run(prompt, context={"mode": "code_generation"})
            return result.response.strip()
        except Exception as e:
            logger.error(f"GPIA generation failed: {e}")
            return f"# GPIA generation failed: {e}"

    def _report(self, params: Dict, context: SkillContext) -> SkillResult:
        """Generate a comprehensive report of placeholders."""
        # Scan if needed
        if not self._placeholders:
            self._scan(params, context)

        # Build report
        report_lines = [
            "# Placeholder Scan Report",
            f"\nGenerated at: {__import__('datetime').datetime.now().isoformat()}",
            f"\nRepository: {self.repo_root}",
            f"\n## Summary",
            f"\n- Total placeholders found: {len(self._placeholders)}",
        ]

        # Group by pattern
        by_pattern = {}
        for p in self._placeholders:
            if p.pattern not in by_pattern:
                by_pattern[p.pattern] = []
            by_pattern[p.pattern].append(p)

        report_lines.append("\n### By Pattern Type\n")
        for pattern, items in sorted(by_pattern.items(), key=lambda x: -len(x[1])):
            report_lines.append(f"- **{pattern}**: {len(items)} occurrences")

        # Details by file
        report_lines.append("\n## Details\n")

        by_file = {}
        for p in self._placeholders:
            if p.file not in by_file:
                by_file[p.file] = []
            by_file[p.file].append(p)

        for file, items in sorted(by_file.items()):
            report_lines.append(f"\n### {file}\n")
            for item in items:
                report_lines.append(f"- Line {item.line} ({item.pattern}): `{item.match[:50]}`")
                if item.suggested_fix:
                    report_lines.append(f"  - Suggested: `{item.suggested_fix[:100]}`")

        report = "\n".join(report_lines)

        # Optionally save report
        report_path = self.repo_root / "runs" / "placeholder_report.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

        return SkillResult(
            success=True,
            output={
                "report": report,
                "report_path": str(report_path),
                "total_placeholders": len(self._placeholders),
            }
        )

    def _fix(self, params: Dict, context: SkillContext) -> SkillResult:
        """Apply fixes to placeholders."""
        dry_run = params.get("dry_run", True)

        # Must have populated first
        if not any(p.suggested_fix for p in self._placeholders):
            # Populate first
            self._populate(params, context)

        if dry_run:
            return SkillResult(
                success=True,
                output={
                    "message": "Dry run - no changes applied",
                    "would_fix": [
                        {
                            "file": p.file,
                            "line": p.line,
                            "original": p.match,
                            "replacement": p.suggested_fix,
                        }
                        for p in self._placeholders if p.suggested_fix
                    ]
                }
            )

        # Apply fixes (with safety checks)
        fixes_applied = 0
        errors = []

        for placeholder in self._placeholders:
            if not placeholder.suggested_fix:
                continue

            if placeholder.confidence < 0.5:
                errors.append(f"Low confidence for {placeholder.file}:{placeholder.line}")
                continue

            try:
                file_path = self.repo_root / placeholder.file
                content = file_path.read_text(encoding="utf-8")

                # Simple replacement (could be more sophisticated)
                lines = content.splitlines()
                if placeholder.line - 1 < len(lines):
                    old_line = lines[placeholder.line - 1]
                    new_line = old_line.replace(placeholder.match, placeholder.suggested_fix)
                    lines[placeholder.line - 1] = new_line

                    # Write back
                    file_path.write_text("\n".join(lines), encoding="utf-8")
                    placeholder.fix_applied = True
                    fixes_applied += 1

            except Exception as e:
                errors.append(f"Error fixing {placeholder.file}:{placeholder.line}: {e}")

        return SkillResult(
            success=fixes_applied > 0 or len(errors) == 0,
            output={
                "fixes_applied": fixes_applied,
                "errors": errors,
                "message": f"Applied {fixes_applied} fixes" + (f" with {len(errors)} errors" if errors else ""),
            }
        )


# Convenience function for direct use
def scan_placeholders(paths: List[str] = None, patterns: List[str] = None) -> Dict:
    """
    Scan repository for placeholders.

    Args:
        paths: Paths to scan (default: entire repo)
        patterns: Additional patterns to search for

    Returns:
        Dict with placeholders found and summary
    """
    skill = PlaceholderScannerSkill()
    result = skill.execute({
        "capability": "scan",
        "paths": paths or ["."],
        "patterns": patterns or [],
    }, SkillContext())
    return result.output


def populate_placeholders(paths: List[str] = None, dry_run: bool = True) -> Dict:
    """
    Find and populate placeholders using GPIA.

    Args:
        paths: Paths to scan
        dry_run: If True, only preview changes

    Returns:
        Dict with suggested fixes
    """
    skill = PlaceholderScannerSkill()
    result = skill.execute({
        "capability": "populate",
        "paths": paths or ["."],
        "dry_run": dry_run,
    }, SkillContext())
    return result.output
