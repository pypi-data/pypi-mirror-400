"""
Agent Integration
=================

Integrates the skills system with CLI AI's agent architecture.
Provides bridges between the message bus, agent roles, and skill execution.

This module enables:
- Agents to discover and invoke skills
- Skill results to flow through the bus
- Context passing between agents and skills
- Progressive disclosure based on agent role
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from skills.base import Skill, SkillContext, SkillResult, SkillLevel, SkillCategory
from skills.registry import SkillRegistry, get_registry, load_skill
from skills.discovery import SkillDiscovery, get_discovery, SkillMatch
from skills.loader import SkillLoader, scan_builtin_skills

logger = logging.getLogger(__name__)


# Agent role to skill category mapping
ROLE_SKILL_MAPPING: Dict[str, List[SkillCategory]] = {
    "CEO": [SkillCategory.WRITING, SkillCategory.REASONING],
    "CTO": [SkillCategory.CODE, SkillCategory.REASONING],
    "CFO": [SkillCategory.DATA, SkillCategory.REASONING],
    "COO": [SkillCategory.AUTOMATION, SkillCategory.REASONING],
    "CIO": [SkillCategory.DATA, SkillCategory.INTEGRATION],
    "CMO": [SkillCategory.WRITING, SkillCategory.CREATIVE],
    "CHRO": [SkillCategory.WRITING, SkillCategory.REASONING],
    "CPO": [SkillCategory.CREATIVE, SkillCategory.REASONING],
    "CLIENT": [SkillCategory.WRITING, SkillCategory.RESEARCH],
}

# Agent role to maximum skill level
ROLE_MAX_LEVEL: Dict[str, SkillLevel] = {
    "CEO": SkillLevel.EXPERT,
    "CTO": SkillLevel.EXPERT,
    "CFO": SkillLevel.ADVANCED,
    "COO": SkillLevel.ADVANCED,
    "CIO": SkillLevel.ADVANCED,
    "CMO": SkillLevel.INTERMEDIATE,
    "CHRO": SkillLevel.INTERMEDIATE,
    "CPO": SkillLevel.ADVANCED,
    "CLIENT": SkillLevel.BASIC,
}


class AgentSkillBridge:
    """
    Bridge between agents and the skills system.

    Provides:
    - Role-aware skill discovery
    - Context building from agent state
    - Result formatting for bus messages
    - Progressive skill disclosure
    """

    def __init__(
        self,
        agent_role: str,
        registry: Optional[SkillRegistry] = None,
        discovery: Optional[SkillDiscovery] = None,
    ):
        self.agent_role = agent_role
        self.registry = registry or get_registry()
        self.discovery = discovery or get_discovery()
        self._loaded_skills: Dict[str, Skill] = {}

        # Initialize skill system if needed
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        """Ensure the skill system is initialized."""
        stats = self.registry.get_stats()
        if stats["total_skills"] == 0:
            logger.info("Initializing skill system...")
            scan_builtin_skills(lazy=True)

    def get_available_skills(self) -> List[str]:
        """
        Get skills available to this agent's role.

        Filters by:
        - Role's associated categories
        - Role's maximum skill level
        """
        categories = ROLE_SKILL_MAPPING.get(self.agent_role, list(SkillCategory))
        max_level = ROLE_MAX_LEVEL.get(self.agent_role, SkillLevel.INTERMEDIATE)

        available = []
        for cat in categories:
            skills = self.registry.list_skills(category=cat)
            for meta in skills:
                if self._level_allowed(meta.level, max_level):
                    available.append(meta.id)

        return available

    def _level_allowed(self, skill_level: SkillLevel, max_level: SkillLevel) -> bool:
        """Check if a skill level is allowed."""
        level_order = [SkillLevel.BASIC, SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED, SkillLevel.EXPERT]
        return level_order.index(skill_level) <= level_order.index(max_level)

    def discover_skills_for_task(
        self,
        task_description: str,
        max_results: int = 3,
    ) -> List[SkillMatch]:
        """
        Discover skills relevant to a task, filtered by role.
        """
        # Get all matches
        matches = self.discovery.discover(task_description, max_results=max_results * 2)

        # Filter by role
        available = set(self.get_available_skills())
        filtered = [m for m in matches if m.skill_id in available]

        return filtered[:max_results]

    def build_context(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        kb_context: Optional[str] = None,
        memory_context: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> SkillContext:
        """
        Build a SkillContext from agent state.
        """
        return SkillContext(
            user_id=user_id,
            session_id=session_id,
            kb_context=kb_context,
            memory_context=memory_context,
            agent_role=self.agent_role,
            extra=extra or {},
        )

    def execute_skill(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        context: Optional[SkillContext] = None,
    ) -> SkillResult:
        """
        Execute a skill with proper context.
        """
        # Check if skill is available to this role
        available = self.get_available_skills()
        if skill_id not in available:
            return SkillResult(
                success=False,
                output=None,
                error=f"Skill {skill_id} not available for role {self.agent_role}",
                error_code="SKILL_NOT_AVAILABLE",
                skill_id=skill_id,
            )

        # Build context if not provided
        if context is None:
            context = self.build_context()

        # Execute via registry
        return self.registry.execute_skill(skill_id, input_data, context)

    def format_for_bus(self, result: SkillResult) -> Dict[str, Any]:
        """
        Format a skill result for bus message.
        """
        return {
            "type": "skill_result",
            "skill_id": result.skill_id,
            "success": result.success,
            "output": result.output,
            "error": result.error if not result.success else None,
            "metadata": {
                "tokens_used": result.tokens_used,
                "execution_time_ms": result.execution_time_ms,
                "suggestions": result.suggestions,
                "related_skills": result.related_skills,
            },
        }

    def get_skill_prompt(self, skill_id: str) -> Optional[str]:
        """
        Get a skill's system prompt for LLM interactions.
        """
        if skill_id not in self.get_available_skills():
            return None

        try:
            skill = self.registry.get_skill(skill_id)
            return skill.get_prompt()
        except Exception as e:
            logger.warning(f"Could not get prompt for {skill_id}: {e}")
            return None

    def get_skill_summary(self) -> str:
        """
        Get a summary of available skills for this agent.
        Useful for system prompts.
        """
        available = self.get_available_skills()
        if not available:
            return "No specialized skills available."

        lines = ["Available skills:"]
        for skill_id in available:
            try:
                meta = self.registry.get_metadata(skill_id)
                lines.append(f"- {skill_id}: {meta.description}")
            except Exception:
                continue

        return "\n".join(lines)


def create_skill_delegate(
    agent_role: str,
) -> Callable[[str, Dict[str, Any]], SkillResult]:
    """
    Create a skill delegation function for an agent.

    Usage in agent code:
        delegate = create_skill_delegate("CTO")
        result = delegate("code/python", {"task": "debug", "code": "..."})
    """
    bridge = AgentSkillBridge(agent_role)

    def delegate(skill_id: str, input_data: Dict[str, Any]) -> SkillResult:
        return bridge.execute_skill(skill_id, input_data)

    return delegate


def get_skills_for_agent(agent_role: str) -> List[Dict[str, Any]]:
    """
    Get skill information for an agent's system prompt.

    Returns a list of skill summaries suitable for inclusion
    in agent instructions.
    """
    bridge = AgentSkillBridge(agent_role)
    available = bridge.get_available_skills()

    skills_info = []
    for skill_id in available:
        try:
            meta = bridge.registry.get_metadata(skill_id)
            skills_info.append({
                "id": skill_id,
                "name": meta.name,
                "description": meta.description,
                "category": meta.category.value,
                "examples": meta.examples[:2] if meta.examples else [],
            })
        except Exception:
            continue

    return skills_info


def inject_skills_into_prompt(base_prompt: str, agent_role: str) -> str:
    """
    Inject skill information into an agent's system prompt.

    Adds a section describing available skills and how to use them.
    """
    bridge = AgentSkillBridge(agent_role)
    skills_summary = bridge.get_skill_summary()

    if skills_summary == "No specialized skills available.":
        return base_prompt

    skill_section = f"""

## Available Skills

You have access to specialized skills that can help with specific tasks.
To use a skill, structure your response to indicate skill invocation.

{skills_summary}

When a skill is appropriate for the task, you can invoke it by including
a skill request in your response. The system will execute the skill and
provide the results.
"""

    return base_prompt + skill_section


class SkillAwareAgent:
    """
    Mixin or wrapper that adds skill capabilities to an agent.

    Can be used to enhance existing agent classes:
        class CTOAgent(BaseAgent, SkillAwareAgent):
            pass
    """

    def __init__(self, role: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skill_bridge = AgentSkillBridge(role)

    def can_use_skill(self, skill_id: str) -> bool:
        """Check if this agent can use a skill."""
        return skill_id in self.skill_bridge.get_available_skills()

    def use_skill(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        **context_kwargs,
    ) -> SkillResult:
        """Use a skill with automatic context building."""
        context = self.skill_bridge.build_context(**context_kwargs)
        return self.skill_bridge.execute_skill(skill_id, input_data, context)

    def suggest_skills(self, task: str) -> List[str]:
        """Suggest skills for a task."""
        matches = self.skill_bridge.discover_skills_for_task(task)
        return [m.skill_id for m in matches]


# Initialize skills on import if in agent context
def initialize_for_agent(agent_role: str) -> AgentSkillBridge:
    """
    Initialize the skill system for an agent.

    Call this when an agent starts up to ensure skills are loaded
    and available.
    """
    bridge = AgentSkillBridge(agent_role)

    # Log available skills
    available = bridge.get_available_skills()
    logger.info(f"Agent {agent_role} initialized with {len(available)} available skills")

    return bridge
