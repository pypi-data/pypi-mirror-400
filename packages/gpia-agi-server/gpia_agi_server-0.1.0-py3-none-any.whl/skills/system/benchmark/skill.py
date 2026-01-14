from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)
from skills.backends import LOCAL_BACKENDS, BackendType, LocalLlamaBackend


@dataclass
class BenchmarkResult:
    model: str
    available: bool
    avg_latency_ms: Optional[float] = None
    runs: int = 0
    tokens_estimate: Optional[int] = None
    error: Optional[str] = None


class BenchmarkSkill(Skill):
    """Run simple latency benchmarks for local model backends."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/benchmark",
            name="Model Benchmark",
            description="Run local model latency/throughput benchmarks",
            category=SkillCategory.REASONING,
            level=SkillLevel.INTERMEDIATE,
            tags=["benchmark", "models", "performance"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "system_prompt": {"type": "string"},
                "models": {"type": "array", "items": {"type": "string"}},
                "runs": {"type": "integer", "minimum": 1, "maximum": 10, "default": 1},
                "max_tokens": {"type": "integer", "minimum": 64, "maximum": 2048, "default": 256},
                "temperature": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.3},
            },
            "required": ["prompt"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "results": {"type": "array"},
                "summary": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        prompt = input_data["prompt"]
        system_prompt = input_data.get("system_prompt")
        runs = int(input_data.get("runs", 1))
        max_tokens = int(input_data.get("max_tokens", 256))
        temperature = float(input_data.get("temperature", 0.3))
        models = input_data.get("models") or list(LOCAL_BACKENDS.keys())

        results: List[Dict[str, Any]] = []

        for backend_key in models:
            config = LOCAL_BACKENDS.get(backend_key)
            if not config:
                results.append(
                    BenchmarkResult(
                        model=backend_key,
                        available=False,
                        error="unknown backend",
                    ).__dict__
                )
                continue

            backend = LocalLlamaBackend(config)
            if not backend.is_available():
                results.append(
                    BenchmarkResult(
                        model=config.model,
                        available=False,
                        error="backend unavailable",
                    ).__dict__
                )
                continue

            latencies: List[float] = []
            sample_output = ""
            error = None

            async def _run_benchmark() -> None:
                nonlocal sample_output, error
                try:
                    for _ in range(runs):
                        start = time.perf_counter()
                        response = await backend.generate(
                            prompt=prompt,
                            system=system_prompt,
                            max_tokens=max_tokens,
                            temperature=temperature,
                        )
                        latencies.append((time.perf_counter() - start) * 1000)
                        sample_output = response
                except Exception as exc:
                    error = str(exc)
                finally:
                    await backend.close()

            asyncio.run(_run_benchmark())

            avg_latency = sum(latencies) / len(latencies) if latencies else None
            tokens_estimate = self._estimate_tokens(sample_output) if sample_output else None

            results.append(
                BenchmarkResult(
                    model=config.model,
                    available=True,
                    avg_latency_ms=avg_latency,
                    runs=len(latencies),
                    tokens_estimate=tokens_estimate,
                    error=error,
                ).__dict__
            )

        summary = f"Benchmarked {len(results)} backends"
        return SkillResult(
            success=True,
            output={"results": results, "summary": summary},
            skill_id=self.metadata().id,
        )

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        words = len(text.split())
        return int(words * 1.33)


__all__ = ["BenchmarkSkill"]
