"""
Agent Generator - Autonomous Agent Creation
============================================

This skill enables the system to generate complete agent implementations
using local models (DeepSeek-R1, Qwen3, CodeGemma).

This is the key to multi-agent architecture - creating specialized agents
like Professor Agent, each with their own memory and capabilities.

Capabilities:
- generate_agent: Create complete agent implementation from specification
- create_memory_db: Initialize separate memory database for agent
- define_skills: Specify agent-specific skill dependencies
- integrate_agent: Register agent in the system

Uses multi-model approach:
- Qwen3: Creative agent code generation
- DeepSeek-R1: Agent design validation and critique
- CodeGemma: Quick syntax validation
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
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

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class AgentGeneratorSkill(Skill):
    """
    Generates complete autonomous agent implementations.

    This enables multi-agent architecture where each agent has:
    - Separate memory database
    - Specialized skill set
    - Defined role and purpose
    - Access to LLM partners

    Process:
    1. Take agent specification (role, capabilities, skills)
    2. Use Qwen3 to generate agent implementation code
    3. Use DeepSeek to validate agent design
    4. Create separate memory database
    5. Define agent-specific skills
    6. Register agent in system
    """

    def __init__(self):
        self._mindset = None
        self._memory = None
        self._skill_generator = None

    @property
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    @property
    def skill_generator(self):
        if self._skill_generator is None:
            try:
                from skills.alpha.skill_generator.skill import SkillGeneratorSkill
                self._skill_generator = SkillGeneratorSkill()
            except Exception as e:
                logger.warning(f"SkillGeneratorSkill not available: {e}")
        return self._skill_generator

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="alpha/agent-generator",
            name="Agent Generator",
            description="Generates complete autonomous agent implementations with separate memory and skills",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.EXPERT,
            tags=["alpha", "agent", "generation", "multi-agent", "autonomous", "meta-cognitive"],
            dependencies=[
                SkillDependency(skill_id="conscience/mindset", optional=False),
                SkillDependency(skill_id="conscience/memory", optional=True),
                SkillDependency(skill_id="alpha/skill-generator", optional=True),
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["generate_agent", "create_memory_db", "define_skills", "integrate_agent"],
                },
                "spec": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string"},
                        "role": {"type": "string"},
                        "description": {"type": "string"},
                        "core_capabilities": {"type": "array"},
                        "skill_dependencies": {"type": "array"},
                        "memory_db_name": {"type": "string"},
                        "ooda_config": {"type": "object"},
                    },
                },
                "agent_code": {"type": "string", "description": "Generated agent code for validation"},
                "agent_path": {"type": "string", "description": "Path to agent file"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "agent_code": {"type": "string"},
                "agent_path": {"type": "string"},
                "memory_db_path": {"type": "string"},
                "skills_defined": {"type": "array"},
                "validation": {"type": "object"},
                "integration_status": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "generate_agent": self._generate_agent,
            "create_memory_db": self._create_memory_db,
            "define_skills": self._define_skills,
            "integrate_agent": self._integrate_agent,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"AgentGenerator {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _generate_agent(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Generate complete agent implementation from specification.

        Takes an agent spec (like Professor Agent) and uses Qwen3 to generate:
        1. Agent class with OODA loop implementation
        2. Skill integration logic
        3. Memory management
        4. Specialized capabilities for the role
        """
        spec = input_data.get("spec", {})

        if not spec:
            return SkillResult(
                success=False,
                output=None,
                error="No agent specification provided",
                skill_id=self.metadata().id,
            )

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        agent_name = spec.get("agent_name", "")
        role = spec.get("role", "")
        description = spec.get("description", "")
        capabilities = spec.get("core_capabilities", [])
        skills = spec.get("skill_dependencies", [])
        memory_db = spec.get("memory_db_name", f"{agent_name.lower()}_memories.db")
        ooda_config = spec.get("ooda_config", {})

        # Use Qwen3 for creative agent generation
        generation_prompt = f"""
Generate a complete Python implementation for an autonomous agent with the following specification:

Agent Name: {agent_name}
Role: {role}
Description: {description}
Core Capabilities: {capabilities}
Skill Dependencies: {skills}
Memory Database: {memory_db}
OODA Configuration: {ooda_config}

Requirements:
1. Create a class {agent_name}Agent that implements OODA loop (Observe -> Orient -> Decide -> Act -> Learn)
2. Initialize separate memory database at skills/conscience/memory/store/{memory_db}
3. Load required skills from registry: {skills}
4. Implement the following methods:
   - _observe(): Gather environmental signals relevant to {role}
   - _orient(): Analyze observations using MindsetSkill with LLM partners
   - _decide(): Make decisions based on {role} responsibilities
   - _act(): Execute validated actions
   - _learn(): Store experiences in agent's memory
5. Implement role-specific capabilities: {capabilities}
6. Use multi-model reasoning patterns (DeepSeek for analysis, Qwen for creativity, CodeGemma for quick tasks)
7. Include comprehensive logging and error handling
8. Follow the pattern from alpha.py (346 lines) as reference

Generate ONLY the Python code for {agent_name.lower()}.py file.
Include all necessary imports and make it production-ready.
This agent will work alongside Alpha Agent in a multi-agent system.
"""

        # Use creative synthesis pattern for agent generation
        generation_result = self.mindset.execute({
            "capability": "synthesize",
            "components": [
                f"Agent specification for {agent_name}",
                "OODA loop architecture",
                "Skill integration patterns",
                "Multi-agent collaboration",
                "Separate memory management"
            ],
            "pattern": "creative_synthesis",  # Emphasizes Qwen3
            "creative_prompt": generation_prompt,
        }, context)

        if not generation_result.success:
            return SkillResult(
                success=False,
                output=None,
                error=f"Agent generation failed: {generation_result.error}",
                skill_id=self.metadata().id,
            )

        generated_code = generation_result.output.get("synthesis", "")

        # Validate with DeepSeek
        validation_result = self.mindset.execute({
            "capability": "critique",
            "subject": generated_code[:1500],
            "criteria": "agent design, OODA implementation, multi-agent compatibility, role-specific logic",
            "pattern": "deep_analysis",  # Uses DeepSeek
            "critique_prompt": f"""
Validate this generated {agent_name} agent implementation:

```python
{generated_code[:2000]}
...
```

Check for:
1. Proper OODA loop implementation
2. Separate memory database initialization
3. Skill loading and integration
4. Role-specific capabilities for: {role}
5. Multi-agent compatibility
6. Error handling and logging
7. Security and safety considerations

Provide validation decision: PASS or NEEDS_WORK with specific issues.
            """,
        }, context)

        validation = {
            "timestamp": datetime.now().isoformat(),
            "code_length": len(generated_code),
            "critique": validation_result.output.get("critique", "") if validation_result.success else "Validation unavailable",
            "decision": "PASS" if validation_result.success and "PASS" in validation_result.output.get("critique", "") else "NEEDS_REVIEW",
        }

        # Store in memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Generated {agent_name} agent with {role} role",
                "memory_type": "procedural",
                "importance": 0.9,
                "context": {
                    "type": "agent_generation",
                    "agent_name": agent_name,
                    "role": role,
                    "timestamp": datetime.now().isoformat(),
                }
            }, context)

        return SkillResult(
            success=True,
            output={
                "agent_code": generated_code,
                "agent_name": agent_name,
                "validation": validation,
                "spec": spec,
                "summary": f"Generated {len(generated_code)} characters of code for {agent_name} agent",
            },
            skill_id=self.metadata().id,
        )

    def _create_memory_db(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Create separate memory database for the new agent.

        Each agent needs its own memory database to maintain independent
        learning history and experiences.
        """
        spec = input_data.get("spec", {})
        agent_name = spec.get("agent_name", "")
        memory_db_name = spec.get("memory_db_name", f"{agent_name.lower()}_memories.db")

        if not agent_name:
            return SkillResult(
                success=False,
                output=None,
                error="agent_name required in spec",
                skill_id=self.metadata().id,
            )

        # Memory database path
        memory_path = REPO_ROOT / "skills" / "conscience" / "memory" / "store" / memory_db_name
        memory_path.parent.mkdir(parents=True, exist_ok=True)

        # Create database with memory schema
        try:
            from skills.conscience.memory.skill import MemoryStore

            # Initialize MemoryStore (creates DB with proper schema)
            agent_memory = MemoryStore(db_path=str(memory_path))

            # Store initial identity memory
            agent_memory.store(
                content=f"I am {agent_name}, an autonomous agent with the role: {spec.get('role', '')}",
                memory_type="identity",
                importance=1.0,
                context={
                    "type": "agent_initialization",
                    "agent_name": agent_name,
                    "created_at": datetime.now().isoformat(),
                }
            )

            stats = agent_memory.get_stats()
            logger.info(f"Created memory database for {agent_name}: {memory_path}")

            return SkillResult(
                success=True,
                output={
                    "memory_db_path": str(memory_path),
                    "agent_name": agent_name,
                    "stats": stats,
                    "summary": f"Created memory database with {stats['total_memories']} initial memories",
                },
                skill_id=self.metadata().id,
            )

        except Exception as e:
            logger.error(f"Failed to create memory database: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=f"Database creation failed: {e}",
                skill_id=self.metadata().id,
            )

    def _define_skills(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Define agent-specific skill dependencies and create custom skills if needed.

        For Professor Agent, this might include:
        - curriculum-designer skill
        - knowledge-assessor skill
        - socratic-questioner skill
        """
        spec = input_data.get("spec", {})
        agent_name = spec.get("agent_name", "")
        role = spec.get("role", "")
        capabilities = spec.get("core_capabilities", [])
        skill_deps = spec.get("skill_dependencies", [])

        if not agent_name:
            return SkillResult(
                success=False,
                output=None,
                error="agent_name required",
                skill_id=self.metadata().id,
            )

        # Analyze which skills need to be created
        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        analysis_result = self.mindset.execute({
            "capability": "analyze",
            "problem": f"""
Analyze skill requirements for {agent_name} agent:

Role: {role}
Core Capabilities: {capabilities}
Existing Skill Dependencies: {skill_deps}

Questions:
1. Are the existing skill dependencies sufficient for this role?
2. What custom skills should be created for {agent_name}?
3. For each custom skill, what capabilities should it have?
4. What are the priority skills (critical vs. nice-to-have)?

Provide structured recommendations for skill creation.
            """,
            "pattern": "balanced",
        }, context)

        skills_analysis = analysis_result.output.get("conclusion", "") if analysis_result.success else ""

        # Define skill creation specifications
        custom_skills = []

        # Example: For Professor Agent, define teaching-specific skills
        if "professor" in agent_name.lower() or "teacher" in role.lower():
            custom_skills = [
                {
                    "skill_id": f"{agent_name.lower()}/curriculum-designer",
                    "name": "Curriculum Designer",
                    "description": "Designs lesson plans and learning curricula",
                    "capabilities": ["design_lesson", "create_curriculum", "assess_prerequisites"],
                    "category": "REASONING",
                },
                {
                    "skill_id": f"{agent_name.lower()}/knowledge-assessor",
                    "name": "Knowledge Assessor",
                    "description": "Evaluates student understanding and progress",
                    "capabilities": ["create_test", "evaluate_response", "track_progress"],
                    "category": "REASONING",
                },
            ]

        return SkillResult(
            success=True,
            output={
                "agent_name": agent_name,
                "existing_skills": skill_deps,
                "custom_skills_recommended": custom_skills,
                "analysis": skills_analysis,
                "summary": f"Defined {len(skill_deps)} existing + {len(custom_skills)} custom skills for {agent_name}",
            },
            skill_id=self.metadata().id,
        )

    def _integrate_agent(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Integrate generated agent into the system.

        Creates:
        1. Agent Python file
        2. README documentation
        3. Configuration entries
        4. Registration with agent registry (if exists)
        """
        agent_code = input_data.get("agent_code", "")
        spec = input_data.get("spec", {})

        if not agent_code or not spec:
            return SkillResult(
                success=False,
                output=None,
                error="agent_code and spec required",
                skill_id=self.metadata().id,
            )

        agent_name = spec.get("agent_name", "")
        if not agent_name:
            return SkillResult(
                success=False,
                output=None,
                error="agent_name required in spec",
                skill_id=self.metadata().id,
            )

        # Create agent file
        agent_filename = f"{agent_name.lower()}.py"
        agent_path = REPO_ROOT / agent_filename
        agent_path.write_text(agent_code, encoding="utf-8")

        # Create README
        readme_content = f"""# {agent_name} Agent

{spec.get('description', '')}

## Role
{spec.get('role', '')}

## Core Capabilities
{chr(10).join('- ' + cap for cap in spec.get('core_capabilities', []))}

## Skill Dependencies
{chr(10).join('- ' + skill for skill in spec.get('skill_dependencies', []))}

## Memory Database
`{spec.get('memory_db_name', f'{agent_name.lower()}_memories.db')}`

## OODA Configuration
```yaml
{spec.get('ooda_config', {})}
```

## Generated
This agent was generated autonomously by the AgentGenerator skill.

Generated: {datetime.now().isoformat()}

## Usage

```bash
# Single cycle
python {agent_filename} --once

# Continuous operation
python {agent_filename}

# Specific mode
python {agent_filename} --mode observe
```

## Integration with Alpha Agent
This agent is part of the multi-agent cognitive system and collaborates with Alpha Agent through shared skills and separate memory databases.
"""

        readme_path = REPO_ROOT / f"{agent_name.upper()}_README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        logger.info(f"Integrated {agent_name} agent: {agent_path}")

        # Store integration in memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Integrated {agent_name} agent into system at {agent_path}",
                "memory_type": "procedural",
                "importance": 0.95,
                "context": {
                    "type": "agent_integration",
                    "agent_name": agent_name,
                    "agent_path": str(agent_path),
                    "timestamp": datetime.now().isoformat(),
                }
            }, context)

        return SkillResult(
            success=True,
            output={
                "agent_path": str(agent_path),
                "readme_path": str(readme_path),
                "agent_name": agent_name,
                "files_created": [agent_filename, f"{agent_name.upper()}_README.md"],
                "integration_status": "SUCCESS",
                "summary": f"Integrated {agent_name} at {agent_path}",
            },
            skill_id=self.metadata().id,
        )
