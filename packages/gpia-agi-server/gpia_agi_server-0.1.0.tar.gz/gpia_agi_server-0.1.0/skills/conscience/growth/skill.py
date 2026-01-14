"""
Growth Skill - Meta-Cognitive Skill Acquisition
================================================

This skill enables the cognitive system to recognize gaps in its
capabilities and systematically acquire new skills.

The Growth Loop:
```
┌─────────────────────────────────────────────────────────────────┐
│                    GROWTH CYCLE                                  │
│                                                                 │
│   1. RECOGNIZE     "I can't do X, but I need to"               │
│        │                                                        │
│        ▼                                                        │
│   2. ANALYZE       "What would enable me to do X?"             │
│        │           (DeepSeek reasons about requirements)        │
│        ▼                                                        │
│   3. ACQUIRE       "How do I get this capability?"             │
│        │           - Find existing skill (discover)             │
│        │           - Connect MCP server (external)              │
│        │           - Generate new skill (create)                │
│        ▼                                                        │
│   4. INTEGRATE     "Add to my skill registry"                  │
│        │           (Qwen3 generates code if needed)             │
│        ▼                                                        │
│   5. VALIDATE      "Test the new capability"                   │
│        │           (DeepSeek verifies correctness)              │
│        ▼                                                        │
│   6. REMEMBER      "Store in procedural memory"                │
│                    (For future recall)                          │
└─────────────────────────────────────────────────────────────────┘
```

This is how the AI evolves:
- Recognizes limitations through failed tasks
- Reasons about what's needed (Mindset)
- Creates or acquires skills (MCP, generation)
- Validates and remembers (Memory)
"""

from __future__ import annotations

import logging
from datetime import datetime
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


class GrowthSkill(Skill):
    """
    Meta-cognitive skill for capability expansion.

    This is the AI's "learning how to learn" mechanism.

    Capabilities:
    - recognize: Identify capability gaps from failures
    - analyze: Reason about what's needed to fill gaps
    - acquire: Find or create skills to fill gaps
    - integrate: Add new skills to the registry
    - reflect: Review growth history and patterns
    """

    def __init__(self):
        self._memory = None
        self._mindset = None
        self._mcp = None
        self._growth_log: List[Dict[str, Any]] = []

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
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    @property
    def mcp(self):
        if self._mcp is None:
            try:
                from skills.thirdparty.mcp_connector.skill import MCPConnectorSkill
                self._mcp = MCPConnectorSkill()
            except Exception as e:
                logger.warning(f"MCPConnectorSkill not available: {e}")
        return self._mcp

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="conscience/growth",
            name="Growth",
            description="Meta-cognitive skill acquisition and capability expansion",
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["conscience", "meta-cognition", "learning", "growth", "self-improvement"],
            dependencies=[
                SkillDependency(skill_id="conscience/memory", optional=False),
                SkillDependency(skill_id="conscience/mindset", optional=False),
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["recognize", "analyze", "acquire", "integrate", "reflect", "grow"],
                },
                "task": {"type": "string", "description": "Task that revealed the gap"},
                "error": {"type": "string", "description": "Error or failure message"},
                "skill_need": {"type": "string", "description": "Identified skill need"},
                "skill_spec": {"type": "object", "description": "Skill specification for creation"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "gap": {"type": "object"},
                "analysis": {"type": "object"},
                "acquisition": {"type": "object"},
                "growth_log": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "recognize": self._recognize,
            "analyze": self._analyze,
            "acquire": self._acquire,
            "integrate": self._integrate,
            "reflect": self._reflect,
            "grow": self._full_growth_cycle,
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
            logger.error(f"Growth {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _recognize(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Recognize a capability gap from a failed task.

        Pattern: "I tried to do X but couldn't because Y"
        """
        task = input_data.get("task", "")
        error = input_data.get("error", "")

        if not task:
            return SkillResult(
                success=False,
                output=None,
                error="No task specified",
                skill_id=self.metadata().id,
            )

        # Use mindset to analyze the gap
        if self.mindset:
            analysis = self.mindset.execute({
                "capability": "analyze",
                "problem": f"""
                I tried to accomplish this task: {task}

                But encountered this issue: {error or 'Could not complete'}

                What capability am I missing? What would I need to be able to do this?
                """,
                "pattern": "deep_analysis",
                "store_reasoning": False,
            }, context)

            if analysis.success:
                gap = {
                    "task": task,
                    "error": error,
                    "analysis": analysis.output.get("conclusion", ""),
                    "timestamp": datetime.now().isoformat(),
                    "status": "identified",
                }

                # Remember the gap
                if self.memory:
                    self.memory.execute({
                        "capability": "experience",
                        "content": f"Capability gap identified: {gap['analysis'][:200]}",
                        "memory_type": "episodic",
                        "importance": 0.8,
                        "context": {"type": "growth_gap", "task": task},
                    }, context)

                self._growth_log.append(gap)

                return SkillResult(
                    success=True,
                    output={"gap": gap},
                    skill_id=self.metadata().id,
                )

        return SkillResult(
            success=False,
            output=None,
            error="Could not analyze capability gap",
            skill_id=self.metadata().id,
        )

    def _analyze(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Analyze what's needed to fill a capability gap.

        This is where the models "think" about skill requirements:
        - What inputs/outputs does the skill need?
        - What external services or tools might help?
        - What existing skills could be composed?
        """
        skill_need = input_data.get("skill_need", "")
        task = input_data.get("task", "")

        if not skill_need and not task:
            return SkillResult(
                success=False,
                output=None,
                error="No skill need or task specified",
                skill_id=self.metadata().id,
            )

        # Multi-perspective analysis
        if self.mindset:
            # First: What exactly is needed?
            requirements = self.mindset.execute({
                "capability": "think",
                "problem": f"""
                I need a skill to: {skill_need or task}

                Analyze:
                1. What are the inputs this skill needs?
                2. What are the expected outputs?
                3. What external services might help (Docker, Kubernetes, MCP tools)?
                4. What existing skills could be composed together?
                5. What's the simplest implementation path?
                """,
                "pattern": "deep_analysis",
            }, context)

            if requirements.success:
                # Check if MCP can help
                mcp_recommendation = None
                if self.mcp:
                    mcp_result = self.mcp.execute({
                        "capability": "recommend",
                        "task": skill_need or task,
                    }, context)
                    if mcp_result.success:
                        mcp_recommendation = mcp_result.output.get("recommendation")

                analysis = {
                    "skill_need": skill_need or task,
                    "requirements": requirements.output.get("conclusion", ""),
                    "reasoning_trace": requirements.output.get("reasoning_trace", []),
                    "mcp_recommendation": mcp_recommendation,
                    "acquisition_paths": self._identify_acquisition_paths(
                        requirements.output.get("conclusion", ""),
                        mcp_recommendation,
                    ),
                }

                return SkillResult(
                    success=True,
                    output={"analysis": analysis},
                    skill_id=self.metadata().id,
                )

        return SkillResult(
            success=False,
            output=None,
            error="Could not analyze skill requirements",
            skill_id=self.metadata().id,
        )

    def _identify_acquisition_paths(
        self,
        requirements: str,
        mcp_recommendation: Optional[Dict],
    ) -> List[Dict[str, Any]]:
        """Identify possible paths to acquire the capability."""
        paths = []

        # Path 1: Use existing MCP tool
        if mcp_recommendation:
            paths.append({
                "type": "mcp",
                "description": "Use existing MCP tool",
                "server": mcp_recommendation.get("server"),
                "tool": mcp_recommendation.get("tool"),
                "effort": "low",
            })

        # Path 2: Compose existing skills
        paths.append({
            "type": "compose",
            "description": "Combine existing skills",
            "effort": "medium",
            "note": "Create CompositeSkill from existing capabilities",
        })

        # Path 3: Generate new skill
        paths.append({
            "type": "generate",
            "description": "Generate new skill code",
            "effort": "high",
            "note": "Use Qwen3 to generate skill implementation",
        })

        # Path 4: Request human help
        paths.append({
            "type": "human",
            "description": "Request human assistance",
            "effort": "variable",
            "note": "Some capabilities require human implementation",
        })

        return paths

    def _acquire(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Acquire a capability through one of several paths.

        Paths:
        1. MCP: Connect to external tool
        2. Compose: Combine existing skills
        3. Generate: Create new skill code
        4. Human: Request assistance
        """
        skill_need = input_data.get("skill_need", "")
        acquisition_path = input_data.get("path", "mcp")

        if acquisition_path == "mcp":
            # Try to find and connect MCP server
            if self.mcp:
                discover = self.mcp.execute({
                    "capability": "discover",
                    "task": skill_need,
                }, context)

                if discover.success and discover.output.get("servers"):
                    best_server = discover.output["servers"][0]
                    connect = self.mcp.execute({
                        "capability": "connect",
                        "server": best_server["name"],
                    }, context)

                    return SkillResult(
                        success=connect.success,
                        output={
                            "acquisition": {
                                "type": "mcp",
                                "server": best_server["name"],
                                "tools": best_server.get("tools", []),
                                "status": "connected" if connect.success else "failed",
                            },
                        },
                        skill_id=self.metadata().id,
                    )

        elif acquisition_path == "generate":
            # Use mindset to generate skill specification
            if self.mindset:
                spec = self.mindset.execute({
                    "capability": "create",
                    "problem": f"""
                    Generate a skill specification for: {skill_need}

                    Include:
                    1. Skill ID and name
                    2. Input schema
                    3. Output schema
                    4. Implementation approach
                    5. Dependencies needed
                    """,
                    "pattern": "creative_synthesis",
                }, context)

                return SkillResult(
                    success=spec.success,
                    output={
                        "acquisition": {
                            "type": "generated",
                            "specification": spec.output.get("conclusion", ""),
                            "status": "specification_ready",
                            "next_step": "Review and implement the specification",
                        },
                    },
                    skill_id=self.metadata().id,
                )

        return SkillResult(
            success=False,
            output=None,
            error=f"Acquisition path '{acquisition_path}' not implemented",
            skill_id=self.metadata().id,
        )

    def _integrate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Integrate a new skill into the system.

        This registers the skill and stores the learning.
        """
        skill_spec = input_data.get("skill_spec", {})

        if not skill_spec:
            return SkillResult(
                success=False,
                output=None,
                error="No skill specification provided",
                skill_id=self.metadata().id,
            )

        # Store in memory as procedural knowledge
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Learned new skill: {skill_spec.get('name', 'unknown')} - {skill_spec.get('description', '')}",
                "memory_type": "procedural",
                "importance": 0.9,
                "context": {
                    "type": "skill_acquired",
                    "skill_id": skill_spec.get("id"),
                    "acquisition_method": skill_spec.get("acquisition_type", "unknown"),
                },
            }, context)

        return SkillResult(
            success=True,
            output={
                "integration": {
                    "skill_id": skill_spec.get("id"),
                    "status": "integrated",
                    "timestamp": datetime.now().isoformat(),
                },
            },
            skill_id=self.metadata().id,
        )

    def _reflect(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Reflect on growth history and patterns.

        What have I learned? How have I grown?
        """
        # Retrieve growth-related memories
        growth_memories = []
        if self.memory:
            recall = self.memory.execute({
                "capability": "recall",
                "content": "skill acquisition growth learning capability",
                "memory_types": ["procedural", "episodic"],
                "limit": 20,
            }, context)

            if recall.success:
                growth_memories = recall.output.get("memories", [])

        # Analyze patterns
        if self.mindset and growth_memories:
            reflection = self.mindset.execute({
                "capability": "think",
                "problem": f"""
                Review my growth history and identify patterns:

                Recent learnings:
                {chr(10).join(m['content'][:100] for m in growth_memories[:10])}

                Questions:
                1. What types of skills have I acquired?
                2. What acquisition methods work best?
                3. What capability gaps remain?
                4. How can I grow more effectively?
                """,
                "pattern": "deep_analysis",
            }, context)

            return SkillResult(
                success=True,
                output={
                    "reflection": {
                        "memories_analyzed": len(growth_memories),
                        "insights": reflection.output.get("conclusion", "") if reflection.success else "",
                        "growth_log": self._growth_log[-10:],
                    },
                },
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=True,
            output={
                "reflection": {
                    "memories_analyzed": 0,
                    "insights": "Insufficient history for reflection",
                    "growth_log": self._growth_log[-10:],
                },
            },
            skill_id=self.metadata().id,
        )

    def _full_growth_cycle(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Execute a full growth cycle: recognize -> analyze -> acquire -> integrate.

        This is the main entry point for capability expansion.
        """
        task = input_data.get("task", "")
        error = input_data.get("error", "")

        if not task:
            return SkillResult(
                success=False,
                output=None,
                error="No task specified for growth cycle",
                skill_id=self.metadata().id,
            )

        cycle_results = {}

        # Step 1: Recognize the gap
        recognize = self._recognize({"task": task, "error": error}, context)
        cycle_results["recognize"] = recognize.output

        if not recognize.success:
            return SkillResult(
                success=False,
                output=cycle_results,
                error="Failed at recognition phase",
                skill_id=self.metadata().id,
            )

        # Step 2: Analyze requirements
        skill_need = recognize.output.get("gap", {}).get("analysis", task)
        analyze = self._analyze({"skill_need": skill_need, "task": task}, context)
        cycle_results["analyze"] = analyze.output

        if not analyze.success:
            return SkillResult(
                success=False,
                output=cycle_results,
                error="Failed at analysis phase",
                skill_id=self.metadata().id,
            )

        # Step 3: Try to acquire
        paths = analyze.output.get("analysis", {}).get("acquisition_paths", [])
        if paths:
            best_path = paths[0]
            acquire = self._acquire({
                "skill_need": skill_need,
                "path": best_path["type"],
            }, context)
            cycle_results["acquire"] = acquire.output

        return SkillResult(
            success=True,
            output={
                "cycle": cycle_results,
                "summary": f"Growth cycle completed for: {task}",
                "timestamp": datetime.now().isoformat(),
            },
            skill_id=self.metadata().id,
        )


__all__ = ["GrowthSkill"]
