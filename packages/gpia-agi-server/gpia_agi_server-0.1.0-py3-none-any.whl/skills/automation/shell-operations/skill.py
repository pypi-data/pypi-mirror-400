"""
Shell Operations Skill
======================

Lightweight skill that exposes the developer/user-facing shell actions for the unified GPIA console.
"""

from __future__ import annotations

from typing import Any, Dict

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult


class ShellOperationsSkill(BaseSkill):
    """Skill wrapper for the shell adoption workflow."""

    SKILL_ID = "automation/shell-operations"
    SKILL_NAME = "Shell Operations"
    SKILL_DESCRIPTION = "Expose the guardrail-aware shell actions and telemetry summaries for GPIA."
    SKILL_CATEGORY = SkillCategory.AUTOMATION
    SKILL_LEVEL = SkillLevel.INTERMEDIATE
    SKILL_TAGS = ["shell", "messenger", "guardrails", "telemetry"]

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            output={
                "summary": "Shell operations are gated by scripts/shell_cli.ps1 and documented for developers, users, and business teams."
            },
            skill_id=self.SKILL_ID,
        )


skill = ShellOperationsSkill()


def execute(params: Dict[str, Any], context: SkillContext) -> SkillResult:
    return skill.execute(params, context)
