from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, List

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillMetadata,
    SkillResult,
    SkillLevel,
)

def _load_probe() -> Any:
    probe_path = Path(__file__).parent / "scripts" / "probe_state.py"
    spec = importlib.util.spec_from_file_location("self_awareness_probe", probe_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load probe script: {probe_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelfAwarenessDemoSkill(Skill):
    """Demonstrate progressive disclosure using three awareness levels."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="reasoning/self-awareness-demo",
            name="Self Awareness Demo",
            description=(
                "Demonstrates progressive disclosure with protoself, core, "
                "and extended layers."
            ),
            version="0.1.0",
            category=SkillCategory.REASONING,
            level=SkillLevel.BASIC,
            tags=["self-awareness", "progressive-disclosure"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["protoself", "core", "extended"],
                },
                "signal": {"type": "object"},
                "environment": {"type": "object"},
                "history": {"type": "array", "items": {"type": "string"}},
                "origin": {"type": "string"},
                "role": {"type": "string"},
            },
            "required": ["level"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "level": {"type": "string"},
                "stable": {"type": "boolean"},
                "snapshot": {"type": "object"},
                "boundary": {"type": "object"},
                "narrative": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        level = input_data["level"]
        signal = input_data.get("signal")

        if level == "protoself":
            snapshot = self._build_snapshot(signal)
            output = {
                "level": level,
                "stable": snapshot["stable"],
                "snapshot": snapshot,
            }
            return SkillResult(success=True, output=output, skill_id=self.metadata().id)

        if level == "core":
            snapshot = self._build_snapshot(signal)
            boundary = self._build_boundary(input_data.get("environment"))
            output = {
                "level": level,
                "stable": snapshot["stable"],
                "snapshot": snapshot,
                "boundary": boundary,
            }
            return SkillResult(success=True, output=output, skill_id=self.metadata().id)

        narrative = self._build_narrative(input_data)
        output = {
            "level": level,
            "narrative": narrative,
        }
        return SkillResult(success=True, output=output, skill_id=self.metadata().id)

    def _build_boundary(self, environment: Dict[str, Any] | None) -> Dict[str, Any]:
        environment = environment or {}
        return {
            "self": "agent",
            "external": list(environment.keys()),
            "causal_focus": environment.get("salient", "unknown"),
        }

    def _build_snapshot(self, signal: Dict[str, Any] | None) -> Dict[str, Any]:
        probe = _load_probe()
        return probe.build_snapshot(signal)

    def _build_narrative(self, input_data: Dict[str, Any]) -> str:
        template_path = Path(__file__).parent / "references" / "identity.md"
        template = template_path.read_text(encoding="utf-8")

        events: List[str] = input_data.get("history", [])
        origin = input_data.get("origin", "unknown")
        role = input_data.get("role", "unspecified")
        continuity = " -> ".join(events) if events else "no events"

        return (
            template
            .replace("{origin}", origin)
            .replace("{role}", role)
            .replace("{events}", ", ".join(events) or "none")
            .replace("{continuity}", continuity)
        )
