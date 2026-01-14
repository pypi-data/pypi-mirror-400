from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class NPUInferenceSkill(Skill):
    """OpenVINO wrapper for NPU-accelerated inference."""

    def __init__(self) -> None:
        self._core = None
        self._models: Dict[str, Any] = {}
        self._requests: Dict[str, Any] = {}
        self._cache_dir = Path("cache/openvino")

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="compute/npu",
            name="NPU Inference Accelerator",
            description="Hardware-accelerated inference for embeddings and classification using OpenVINO.",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["npu", "openvino", "inference"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["load", "infer", "telemetry"]},
                "model_path": {"type": "string"},
                "batch": {"type": "array"},
                "inputs": {"type": "object"},
                "cache_dir": {"type": "string"},
            },
            "required": ["action"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "device": {"type": "string"},
                "compile_time_ms": {"type": "number"},
                "cached": {"type": "boolean"},
                "shape": {"type": "array"},
                "inference_time_ms": {"type": "number"},
                "throughput_fps": {"type": "number"},
                "preview": {"type": "array"},
                "error": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        action = input_data.get("action")
        model_path = input_data.get("model_path")

        if action == "telemetry":
            return self._telemetry()

        if action == "load":
            if not model_path:
                return SkillResult(
                    success=False,
                    output=None,
                    error="model_path required",
                    skill_id=self.metadata().id,
                )
            return self._load_model(model_path, input_data.get("cache_dir"))

        if action == "infer":
            if not model_path:
                return SkillResult(
                    success=False,
                    output=None,
                    error="model_path required",
                    skill_id=self.metadata().id,
                )
            batch = input_data.get("batch")
            inputs = input_data.get("inputs")
            return self._run_inference(model_path, batch, inputs)

        return SkillResult(
            success=False,
            output=None,
            error="Unknown action",
            skill_id=self.metadata().id,
        )

    def _core_instance(self):
        if self._core is None:
            from openvino import Core

            self._core = Core()
        return self._core

    def _cache_directory(self, cache_dir: Optional[str]) -> Path:
        if cache_dir:
            return Path(cache_dir)
        return self._cache_dir

    def _get_device(self) -> str:
        core = self._core_instance()
        devices = core.available_devices
        if "NPU" in devices:
            return "NPU"
        if "GPU" in devices:
            return "GPU"
        return "CPU"

    def _load_model(self, model_path: str, cache_dir: Optional[str]) -> SkillResult:
        start_time = time.perf_counter()
        device = self._get_device()

        core = self._core_instance()
        cache_path = self._cache_directory(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        core.set_property({"CACHE_DIR": str(cache_path)})

        try:
            if model_path not in self._models:
                model = core.read_model(model=model_path)
                compiled = core.compile_model(model=model, device_name=device)
                self._models[model_path] = compiled
                self._requests[model_path] = compiled.create_infer_request()

            latency_ms = (time.perf_counter() - start_time) * 1000
            return SkillResult(
                success=True,
                output={
                    "status": "loaded",
                    "device": device,
                    "compile_time_ms": latency_ms,
                    "cached": True,
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

    def _run_inference(
        self,
        model_path: str,
        batch: Optional[List[Any]],
        inputs: Optional[Dict[str, Any]],
    ) -> SkillResult:
        if model_path not in self._requests:
            load_result = self._load_model(model_path, None)
            if not load_result.success:
                return load_result

        request = self._requests[model_path]
        compiled = self._models[model_path]

        try:
            if inputs:
                feed = {name: np.array(value) for name, value in inputs.items()}
            elif batch is not None:
                input_layer = compiled.input(0)
                feed = {input_layer: np.stack(batch)}
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error="batch or inputs required",
                    skill_id=self.metadata().id,
                )

            start = time.perf_counter()
            request.infer(feed)
            infer_ms = (time.perf_counter() - start) * 1000

            output_layer = compiled.output(0)
            result = request.get_tensor(output_layer).data
            throughput = (len(batch) / (infer_ms / 1000)) if batch else 0

            return SkillResult(
                success=True,
                output={
                    "shape": list(result.shape),
                    "inference_time_ms": infer_ms,
                    "throughput_fps": throughput,
                    "device": self._get_device(),
                    "preview": result.flatten()[:5].tolist(),
                },
                skill_id=self.metadata().id,
            )
        except Exception as exc:
            return SkillResult(
                success=False,
                output=None,
                error=f"Inference failed: {exc}",
                skill_id=self.metadata().id,
            )

    def _telemetry(self) -> SkillResult:
        core = self._core_instance()
        return SkillResult(
            success=True,
            output={
                "status": "ok",
                "device": self._get_device(),
                "available_devices": core.available_devices,
            },
            skill_id=self.metadata().id,
        )


__all__ = ["NPUInferenceSkill"]
