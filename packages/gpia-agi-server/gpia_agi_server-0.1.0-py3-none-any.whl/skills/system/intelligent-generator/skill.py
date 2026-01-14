from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)
from skills.conscience.memory.skill import MemorySkill


class IntelligentGeneratorSkill(Skill):
    """Verify the NPU pipeline and record the result in memory."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/intelligent-generator",
            name="Intelligent Model Generator",
            description="Verify the NPU pipeline and store a verification memory",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["npu", "verification"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["verify"]},
                "model_path": {"type": "string"},
            },
            "required": ["action"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "details": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        action = input_data.get("action")
        if action != "verify":
            return SkillResult(
                success=False,
                output=None,
                error="Unknown action",
                skill_id=self.metadata().id,
            )

        model_path = input_data.get("model_path") or os.getenv("OPENVINO_EMBEDDING_MODEL")
        if not model_path:
            return SkillResult(
                success=False,
                output=None,
                error="model_path not provided and OPENVINO_EMBEDDING_MODEL is unset",
                skill_id=self.metadata().id,
            )

        try:
            from skills.compute.npu.skill import NPUInferenceSkill

            npu_skill = NPUInferenceSkill()
            load_result = npu_skill.execute(
                {"action": "load", "model_path": model_path},
                context,
            )
            if not load_result.success:
                return load_result

            compiled = npu_skill._models.get(model_path)
            input_shapes = [str(inp.shape) for inp in compiled.inputs] if compiled else []

            inputs = self._build_dummy_inputs(compiled)
            infer_result = npu_skill.execute(
                {"action": "infer", "model_path": model_path, "inputs": inputs},
                context,
            )

            details = {
                "load": load_result.output,
                "infer": infer_result.output if infer_result.success else None,
                "input_shapes": input_shapes,
                "timestamp": datetime.now().isoformat(),
            }

            self._remember(details)

            return SkillResult(
                success=infer_result.success,
                output={
                    "status": "ok" if infer_result.success else "failed",
                    "details": details,
                },
                skill_id=self.metadata().id,
            )
        except Exception as exc:
            return SkillResult(
                success=False,
                output=None,
                error=str(exc),
                skill_id=self.metadata().id,
            )

    def _build_dummy_inputs(self, compiled) -> Dict[str, Any]:
        if compiled is None:
            return {}

        inputs: Dict[str, Any] = {}
        for inp in compiled.inputs:
            shape = [dim if isinstance(dim, int) and dim > 0 else 1 for dim in inp.shape]
            if len(shape) == 0:
                shape = [1]
            inputs[inp.any_name] = np.zeros(shape, dtype=np.int64)
        return inputs

    def _remember(self, details: Dict[str, Any]) -> None:
        memory = MemorySkill()
        memory.execute(
            {
                "capability": "experience",
                "content": f"NPU pipeline verification: {details}",
                "memory_type": "procedural",
                "importance": 0.6,
                "context": {"source": "intelligent_generator"},
            },
            SkillContext(agent_role="generator"),
        )


__all__ = ["IntelligentGeneratorSkill"]
