"""
Skill → Agent Transpiler
========================

Compile a skill entry into a provisioned agent request with strict guardrails.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from core.agent_creator_manager import AgentCreatorManager
from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "skills" / "INDEX.json"


class SkillToAgentTranspiler(BaseSkill):
    SKILL_ID = "automation/skill-to-agent-transpiler"
    SKILL_NAME = "Skill to Agent Transpiler"
    SKILL_DESCRIPTION = "Compile skills into guarded agent provisioning requests."
    SKILL_CATEGORY = SkillCategory.AUTOMATION
    SKILL_LEVEL = SkillLevel.ADVANCED
    SKILL_TAGS = ["agent", "transpiler", "guardrails", "automation"]

    def __init__(self):
        self.manager = AgentCreatorManager()

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = params.get("capability", "compile")
        skill_id = params.get("skill_id", "")
        if not skill_id:
            return SkillResult(
                success=False,
                output={"error": "skill_id is required"},
                error="skill_id is required",
                skill_id=self.SKILL_ID,
            )

        skill = self._find_skill(skill_id)
        if not skill:
            return SkillResult(
                success=False,
                output={"error": f"Skill not found: {skill_id}"},
                error=f"Skill not found: {skill_id}",
                skill_id=self.SKILL_ID,
            )

        request = self._compile_request(skill, params)

        if capability == "compile":
            return SkillResult(
                success=True,
                output={"request": request},
                skill_id=self.SKILL_ID,
            )

        if capability == "provision":
            result = self.manager.provision(request)
            return SkillResult(
                success=bool(result.get("success")),
                output=result,
                error=None if result.get("success") else "Provisioning failed",
                skill_id=self.SKILL_ID,
            )

        return SkillResult(
            success=False,
            output={"error": f"Unknown capability: {capability}"},
            error=f"Unknown capability: {capability}",
            skill_id=self.SKILL_ID,
        )

    def _find_skill(self, skill_id: str) -> Dict[str, Any]:
        try:
            payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        for skill in payload.get("skills", []):
            if skill.get("id") == skill_id:
                return skill
        return {}

    def _compile_request(self, skill: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        skill_id = skill.get("id", "")
        description = (skill.get("description") or "").strip()
        category = (skill.get("category") or skill_id.split("/")[0] if skill_id else "").lower()
        categories = [category] if category else params.get("skill_categories", [])

        return {
            "agent_name": params.get("agent_name") or skill.get("name", skill_id or "skill-agent"),
            "primary_goal": params.get("primary_goal") or f"Execute skill {skill_id}: {description}",
            "model_id": params.get("model_id", "qwen3:latest"),
            "skill_categories": categories,
            "ephemeral_mode": params.get("ephemeral_mode", True),
            "max_steps": params.get("max_steps", 3),
            "custom_helpers": params.get("custom_helpers", []),
            "output_path": params.get("output_path"),
            "requester_id": params.get("requester_id", "transpiler"),
            "requester_type": params.get("requester_type", "transpiler"),
            "parent_agent_id": params.get("parent_agent_id"),
            "approved": params.get("approved", False),
            "approval_note": params.get("approval_note", ""),
            "policy_scope": "transpiler",
            "source_skill_id": skill_id,
        }


skill = SkillToAgentTranspiler()


def execute(params: Dict[str, Any], context: SkillContext) -> SkillResult:
    return skill.execute(params, context)
