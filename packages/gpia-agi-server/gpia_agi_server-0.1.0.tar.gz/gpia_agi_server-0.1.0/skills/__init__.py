"""
CLI AI Skills Framework
========================

A modular skills system that provides domain expertise and procedural knowledge
to AI agents. Skills are organized as self-contained packages with code, scripts,
and instructions that enable progressive disclosure - agents only access complex
information when necessary.

Architecture:
- Skills are lazy-loaded to minimize memory footprint
- Each skill contains its own prompts, tools, and validation schemas
- Skills can depend on other skills, forming a capability graph
- The registry enables discovery and sharing across the ecosystem

Usage:
    from skills import SkillRegistry, load_skill

    # Load a specific skill
    code_skill = load_skill("code/python")
    result = code_skill.execute({"task": "refactor", "code": "..."})

    # Discover available skills
    registry = SkillRegistry()
    available = registry.list_skills(category="data")
"""

from skills.base import (
    Skill,
    SkillContext,
    SkillResult,
    SkillMetadata,
    SkillDependency,
)
from skills.registry import SkillRegistry, load_skill, get_registry
from skills.loader import SkillLoader
from skills.progressive_loader import (
    ProgressiveLoader,
    SkillHandle,
    SkillManifest,
    get_loader,
)

__all__ = [
    # Core classes
    "Skill",
    "SkillContext",
    "SkillResult",
    "SkillMetadata",
    "SkillDependency",
    # Registry
    "SkillRegistry",
    "load_skill",
    "get_registry",
    # Loader (legacy)
    "SkillLoader",
    # Progressive Loader (v1.0 standard)
    "ProgressiveLoader",
    "SkillHandle",
    "SkillManifest",
    "get_loader",
]

__version__ = "1.0.0"
