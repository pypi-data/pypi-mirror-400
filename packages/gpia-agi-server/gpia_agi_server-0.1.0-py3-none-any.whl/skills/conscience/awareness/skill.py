from __future__ import annotations

from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class AwarenessSkill(Skill):
    """Hierarchical self-awareness: protoself, core, and extended."""

    def __init__(self) -> None:
        self._self_skill = None
        self._memory_skill = None

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="conscience/awareness",
            name="Awareness",
            description=(
                "Hierarchical self-awareness: protoself, core, and extended layers"
            ),
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["conscience", "awareness", "identity", "hierarchy"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["protoself", "core", "extended", "full"],
                },
                "signal": {"type": "object"},
                "environment": {"type": "object"},
                "prompt": {"type": "string"},
                "depth": {"type": "string", "enum": ["light", "moderate", "deep"]},
                "history": {"type": "array", "items": {"type": "string"}},
                "memory_query": {"type": "string"},
            },
            "required": [],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "level": {"type": "string"},
                "protoself": {"type": "object"},
                "core": {"type": "object"},
                "extended": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "full")
        signal = input_data.get("signal")
        environment = input_data.get("environment")

        if capability == "protoself":
            return self._result("protoself", self._build_protoself(signal))

        if capability == "core":
            core = self._build_core(signal, environment)
            return self._result("core", core)

        if capability == "extended":
            extended = self._build_extended(input_data, context)
            return self._result("extended", extended)

        protoself = self._build_protoself(signal)
        core = self._build_core(signal, environment)
        extended = self._build_extended(input_data, context)
        return self._result("full", {
            "protoself": protoself,
            "core": core,
            "extended": extended,
        })

    def _result(self, level: str, payload: Dict[str, Any]) -> SkillResult:
        output = {"level": level, **payload}
        return SkillResult(success=True, output=output, skill_id=self.metadata().id)

    def _build_protoself(self, signal: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        signal = signal or {}

        uptime_s = int(signal.get("uptime_s", 0))
        load = float(signal.get("load", 0.0))
        errors = int(signal.get("errors", 0))
        mem_free_mb = signal.get("mem_free_mb")

        stable = errors == 0 and load < 0.8

        return {
            "uptime_s": uptime_s,
            "load": load,
            "errors": errors,
            "mem_free_mb": mem_free_mb,
            "stable": stable,
            "status": "stable" if stable else "degraded",
        }

    def _build_core(
        self,
        signal: Optional[Dict[str, Any]],
        environment: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        environment = environment or {}
        protoself = self._build_protoself(signal)

        return {
            "snapshot": protoself,
            "boundary": {
                "self": "agent",
                "external": list(environment.keys()),
                "causal_focus": environment.get("salient", "unknown"),
            },
            "anticipation": environment.get("anticipated", "unknown"),
        }

    def _build_extended(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "current task")
        depth = input_data.get("depth", "moderate")
        history: List[str] = input_data.get("history", [])
        memory_query = input_data.get("memory_query", "")

        introspection = None
        if self.self_skill is not None:
            result = self.self_skill.execute(
                {"capability": "introspect", "subject": prompt, "depth": depth},
                context,
            )
            introspection = result.output if result.success else None

        identity = None
        memories = None
        if self.memory_skill is not None:
            identity_result = self.memory_skill.execute(
                {"capability": "identity", "content": ""},
                context,
            )
            if identity_result.success:
                identity = identity_result.output

            if memory_query:
                recall_result = self.memory_skill.execute(
                    {"capability": "recall", "content": memory_query, "limit": 3},
                    context,
                )
                if recall_result.success:
                    memories = recall_result.output

        narrative = self._compose_narrative(prompt, history, introspection)

        return {
            "narrative": narrative,
            "introspection": introspection,
            "identity": identity,
            "memories": memories,
        }

    def _compose_narrative(
        self,
        prompt: str,
        history: List[str],
        introspection: Optional[Dict[str, Any]],
    ) -> str:
        lines = [f"Subject: {prompt}"]

        if history:
            lines.append("History:")
            lines.extend(f"- {item}" for item in history[:5])
        else:
            lines.append("History: none")

        if introspection and "reflection" in introspection:
            lines.append("Reflection:")
            lines.append(introspection["reflection"])

        return "\n".join(lines)

    @property
    def self_skill(self):
        if self._self_skill is None:
            try:
                from skills.conscience.self.skill import SelfSkill

                self._self_skill = SelfSkill()
            except Exception:
                self._self_skill = None
        return self._self_skill

    @property
    def memory_skill(self):
        if self._memory_skill is None:
            try:
                from skills.conscience.memory.skill import MemorySkill

                self._memory_skill = MemorySkill()
            except Exception:
                self._memory_skill = None
        return self._memory_skill


__all__ = ["AwarenessSkill"]
