from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import psutil
import yaml

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

try:
    from core.sovereignty_v2 import heuristics_registry

    HEURISTICS_AVAILABLE = True
except Exception:
    heuristics_registry = None
    HEURISTICS_AVAILABLE = False


def _clamp_percent(value: float) -> float:
    return max(0.0, min(value, 100.0))


def _resolve_limit(key: str, baseline: float) -> float:
    if not HEURISTICS_AVAILABLE:
        return baseline
    heuristics_registry.set_bounds(key, min_value=baseline, max_value=100.0)
    stored = heuristics_registry.get_value(key, default=baseline)
    if stored is None:
        stored = baseline
    return max(float(stored), baseline)


def _derive_limit(observed: float, baseline: float, buffer_pct: float) -> float:
    target = max(baseline, observed + buffer_pct)
    return _clamp_percent(target)


class ControlPlaneSkill(Skill):
    """Resource governor for cognitive stages."""

    def __init__(self) -> None:
        self.config_path = Path("configs/control_plane/resources.yaml")
        self.current_stage = "MONITOR"
        self._config = self._load_config()

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/control-plane",
            name="Resource Control Plane",
            description="Manages compute budgets and cognitive stages",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["resources", "budget", "optimization"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["check_budget", "set_stage", "get_status"]},
                "stage": {"type": "string"},
                "skill_id": {"type": "string"},
                "requested_resources": {"type": "object"},
            },
            "required": ["action"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "stage": {"type": "string"},
                "reason": {"type": "string"},
                "current_usage": {"type": "object"},
                "limit": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        action = input_data.get("action", "get_status")

        if action == "set_stage":
            new_stage = input_data.get("stage", "MONITOR")
            if new_stage in self._config.get("stages", {}):
                self.current_stage = new_stage
                return SkillResult(
                    success=True,
                    output={"status": "stage_updated", "stage": self.current_stage},
                    skill_id=self.metadata().id,
                )
            return SkillResult(
                success=False,
                output=None,
                error="Invalid stage",
                skill_id=self.metadata().id,
            )

        if action == "check_budget":
            cpu_usage = psutil.cpu_percent(interval=0.1)
            mem_usage = psutil.virtual_memory().percent
            stage_limits = self._config.get("stages", {}).get(self.current_stage, {}).get("budgets", {})
            global_limits = self._config.get("global_limits", {}) or {}
            skill_id = input_data.get("skill_id") or context.extra.get("skill_id")
            overrides = self._config.get("skill_overrides", {}) or {}
            skill_override = overrides.get(skill_id) if skill_id else None
            effective_limits = dict(stage_limits) if stage_limits else {}

            status = "approved"
            rejection_reason = None

            if stage_limits:
                cpu_limit = stage_limits.get("cpu")
                mem_limit = stage_limits.get("memory")
                cpu_grace = float(os.getenv("GPIA_CONTROL_CPU_GRACE", "10"))
                mem_grace = float(os.getenv("GPIA_CONTROL_MEM_GRACE", "10"))
                cpu_buffer = float(os.getenv("GPIA_CONTROL_CPU_BUFFER", "5"))
                mem_buffer = float(os.getenv("GPIA_CONTROL_MEM_BUFFER", "5"))

                if skill_override:
                    if "cpu" in skill_override:
                        effective_limits["cpu"] = skill_override.get("cpu")
                    if "memory" in skill_override:
                        effective_limits["memory"] = skill_override.get("memory")

                if cpu_limit is not None:
                    cpu_key_base = f"control_plane.{self.current_stage.lower()}.cpu_limit"
                    if skill_override and skill_id and "cpu" in skill_override:
                        cpu_key_base = f"control_plane.override.{skill_id.replace('/', '_')}.cpu_limit"
                    effective_limits["cpu"] = _resolve_limit(cpu_key_base, float(effective_limits.get("cpu", cpu_limit)))
                    if HEURISTICS_AVAILABLE:
                        heuristics_registry.observe(
                            cpu_key_base,
                            _derive_limit(cpu_usage, float(effective_limits.get("cpu", cpu_limit)), cpu_buffer),
                        )

                if mem_limit is not None:
                    mem_key_base = f"control_plane.{self.current_stage.lower()}.memory_limit"
                    if skill_override and skill_id and "memory" in skill_override:
                        mem_key_base = f"control_plane.override.{skill_id.replace('/', '_')}.memory_limit"
                    effective_limits["memory"] = _resolve_limit(
                        mem_key_base,
                        float(effective_limits.get("memory", mem_limit)),
                    )
                    if HEURISTICS_AVAILABLE:
                        heuristics_registry.observe(
                            mem_key_base,
                            _derive_limit(mem_usage, float(effective_limits.get("memory", mem_limit)), mem_buffer),
                        )

                global_cpu = global_limits.get("max_system_cpu")
                global_mem = global_limits.get("max_system_ram")
                if global_cpu is not None:
                    global_cpu_limit = _resolve_limit("control_plane.global.cpu_limit", float(global_cpu))
                    if "cpu" in effective_limits:
                        effective_limits["cpu"] = min(float(effective_limits["cpu"]), global_cpu_limit)
                if global_mem is not None:
                    global_mem_limit = _resolve_limit("control_plane.global.memory_limit", float(global_mem))
                    if "memory" in effective_limits:
                        effective_limits["memory"] = min(float(effective_limits["memory"]), global_mem_limit)

                if cpu_usage > effective_limits.get("cpu", 100) + cpu_grace:
                    status = "denied"
                    rejection_reason = (
                        f"CPU limit exceeded ({cpu_usage}% > {effective_limits.get('cpu', 0)}%)"
                    )
                if mem_usage > effective_limits.get("memory", 100) + mem_grace:
                    status = "denied"
                    rejection_reason = (
                        f"Memory limit exceeded ({mem_usage}% > {effective_limits.get('memory', 0)}%)"
                    )

            return SkillResult(
                success=True,
                output={
                    "status": status,
                    "reason": rejection_reason,
                    "current_usage": {"cpu": cpu_usage, "memory": mem_usage},
                    "limit": effective_limits if effective_limits else stage_limits,
                    "stage": self.current_stage,
                },
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=True,
            output={
                "status": "ok",
                "stage": self.current_stage,
                "limit": self._config.get("stages", {}).get(self.current_stage),
            },
            skill_id=self.metadata().id,
        )

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with self.config_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}


__all__ = ["ControlPlaneSkill"]
