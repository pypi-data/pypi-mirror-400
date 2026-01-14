"""
Agent Creator Manager Skill
===========================

Provision agent workspaces and register them in the local registry.
"""

from __future__ import annotations

from typing import Any, Dict

from core.agent_creator_manager import AgentCreatorManager
from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult


class AgentCreatorManagerSkill(BaseSkill):
    """Skill wrapper for provisioning and registering GPIA agents."""

    SKILL_ID = "automation/agent-creator-manager"
    SKILL_NAME = "Agent Creator Manager"
    SKILL_DESCRIPTION = "Provision GPIA agents with unique IDs, helpers, and runner templates."
    SKILL_CATEGORY = SkillCategory.AUTOMATION
    SKILL_LEVEL = SkillLevel.ADVANCED
    SKILL_TAGS = ["agent", "provisioning", "automation", "registry"]

    def __init__(self):
        self.manager = AgentCreatorManager()

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = params.get("capability", "provision")

        if capability == "provision":
            result = self.manager.provision(params)
            return SkillResult(
                success=bool(result.get("success")),
                output=result,
                skill_id=self.SKILL_ID,
                error=None if result.get("success") else "Provisioning failed",
            )

        if capability == "list_registry":
            return SkillResult(
                success=True,
                output={"agents": self.manager.list_registry()},
                skill_id=self.SKILL_ID,
            )

        if capability == "register_runtime":
            entry = self.manager.register_runtime_agent(
                name=params.get("agent_name", "runtime-agent"),
                purpose=params.get("primary_goal", ""),
                model_id=params.get("model_id", ""),
                requester_id=params.get("requester_id", "model"),
                requester_type=params.get("requester_type", "model"),
                parent_agent_id=params.get("parent_agent_id"),
            )
            return SkillResult(
                success=True,
                output=entry,
                skill_id=self.SKILL_ID,
            )

        if capability == "provision_skill":
            result = self.manager.provision_skill_stub(
                name=params.get("skill_name", ""),
                description=params.get("description", ""),
                category=params.get("category", "automation"),
                output_path=params.get("output_path"),
            )
            return SkillResult(
                success=bool(result.get("success")),
                output=result,
                skill_id=self.SKILL_ID,
                error=None if result.get("success") else result.get("error"),
            )

        return SkillResult(
            success=False,
            output={"error": f"Unknown capability: {capability}"},
            error=f"Unknown capability: {capability}",
            skill_id=self.SKILL_ID,
        )


skill = AgentCreatorManagerSkill()


def execute(params: Dict[str, Any], context: SkillContext) -> SkillResult:
    return skill.execute(params, context)
