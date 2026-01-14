"""
Model Router - Unified interface for all local LLMs

Routes tasks to the appropriate model based on task type.
Supports all 5 Ollama models plus GPIA Core:
- codegemma:latest (133 tok/s) - fast parsing
- qwen3:latest (87 tok/s) - creative/dialogue
- deepseek-r1:latest (74 tok/s) - reasoning
- llava:latest - vision
- gpt-oss:20b - complex synthesis
- gpia-core - action protocol brain
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from core.dynamic_budget_orchestrator import apply_dynamic_budget

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


class ModelRole(Enum):
    FAST = "fast"
    CREATIVE = "creative"
    REASONING = "reasoning"
    VISION = "vision"
    SYNTHESIS = "synthesis"


@dataclass
class Model:
    name: str
    ollama_id: str
    role: ModelRole
    speed: str
    size: str
    strengths: List[str]


# All available models (UPDATED with gpia- prefix)
MODELS = {
    "codegemma": Model(
        name="codegemma",
        ollama_id="gpia-codegemma:latest",
        role=ModelRole.FAST,
        speed="133 tok/s",
        size="5.0 GB",
        strengths=["intent parsing", "entity extraction", "quick checks", "agreement summary"]
    ),
    "qwen3": Model(
        name="qwen3",
        ollama_id="gpia-qwen3:latest",
        role=ModelRole.CREATIVE,
        speed="87 tok/s",
        size="5.2 GB",
        strengths=["dialogue", "lesson creation", "creative writing", "Alpha responses"]
    ),
    "deepseek_r1": Model(
        name="deepseek_r1",
        ollama_id="gpia-deepseek-r1:latest",
        role=ModelRole.REASONING,
        speed="74 tok/s",
        size="5.2 GB",
        strengths=["analysis", "grading", "critique", "chain-of-thought", "Professor tasks"]
    ),
    "llava": Model(
        name="llava",
        ollama_id="gpia-llava:latest",
        role=ModelRole.VISION,
        speed="N/A",
        size="4.7 GB",
        strengths=["image analysis", "visual reasoning", "screenshot review"]
    ),
    "gpt_oss_20b": Model(
        name="gpt_oss_20b",
        ollama_id="gpia-gpt-oss:latest",
        role=ModelRole.SYNTHESIS,
        speed="~40 tok/s",
        size="13 GB",
        strengths=["complex synthesis", "dispute resolution", "final judgment", "long-form"]
    ),
    "gpia_core": Model(
        name="gpia_core",
        ollama_id="gpia-master:latest",
        role=ModelRole.REASONING,
        speed="custom",
        size="custom",
        strengths=["action schema", "json protocol", "system-2 reasoning"]
    ),
}

# Task to model mapping
TASK_ROUTING = {
    # Fast tasks (codegemma)
    "intent_parsing": "codegemma",
    "entity_extraction": "codegemma",
    "agreement_summary": "codegemma",
    "quick_check": "codegemma",

    # Creative tasks (qwen3)
    "alpha_response": "qwen3",
    "alpha_challenge": "qwen3",
    "lesson_creation": "qwen3",
    "dialogue": "qwen3",
    "creative": "qwen3",

    # Reasoning tasks (deepseek_r1)
    "professor_analysis": "deepseek_r1",
    "professor_grading": "deepseek_r1",
    "critique": "deepseek_r1",
    "reasoning": "deepseek_r1",
    "debug": "deepseek_r1",

    # Vision tasks (llava)
    "image_analysis": "llava",
    "screenshot_review": "llava",
    "visual": "llava",

    # Synthesis tasks (gpt_oss_20b)
    "final_synthesis": "gpt_oss_20b",
    "dispute_resolution": "gpt_oss_20b",
    "complex": "gpt_oss_20b",
    "arbiter": "gpt_oss_20b",
}


class ModelRouter:
    """Routes tasks to appropriate models and handles LLM queries."""

    def __init__(self, ollama_url: str = OLLAMA_URL):
        self.ollama_url = ollama_url
        self.models = MODELS
        self.routing = TASK_ROUTING

    def get_model_for_task(self, task: str) -> Model:
        """Get the appropriate model for a task."""
        model_name = self.routing.get(task, "qwen3")  # Default to qwen3
        return self.models.get(model_name, self.models["qwen3"])

    def get_model_by_role(self, role: ModelRole) -> Model:
        """Get a model by its role."""
        for model in self.models.values():
            if model.role == role:
                return model
        return self.models["qwen3"]

    def query(
        self,
        prompt: str,
        task: str = None,
        model: str = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
        timeout: int = 120
    ) -> str:
        """Query an LLM with automatic model selection."""

        # Determine which model to use
        if model:
            model_obj = self.models.get(model, self.models["qwen3"])
        elif task:
            model_obj = self.get_model_for_task(task)
        else:
            model_obj = self.models["qwen3"]

        effective_max = self._adjust_max_tokens(prompt, max_tokens, model_obj.ollama_id)

        return self._query_ollama(
            model_obj.ollama_id,
            prompt,
            effective_max,
            temperature,
            timeout
        )

    def query_with_continuation(
        self,
        prompt: str,
        task: str = None,
        model: str = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
        max_continuations: int = 2
    ) -> str:
        """Query with automatic continuation for truncated responses."""

        if model:
            model_obj = self.models.get(model, self.models["qwen3"])
        elif task:
            model_obj = self.get_model_for_task(task)
        else:
            model_obj = self.models["qwen3"]

        full_response = ""
        continuation_prompt = prompt

        for attempt in range(max_continuations + 1):
            effective_max = self._adjust_max_tokens(
                continuation_prompt,
                max_tokens,
                model_obj.ollama_id,
            )
            chunk = self._query_ollama(
                model_obj.ollama_id,
                continuation_prompt,
                effective_max,
                temperature,
                120
            )

            if full_response and chunk:
                full_response += "\n"
            full_response += chunk

            # Check if complete
            if chunk and (chunk[-1] in '.!?"' or len(chunk) < effective_max * 0.75):
                break

            # Check for truncation
            truncation_indicators = ["...", "-", "I'm", "I'll", "Could", "How", "What"]
            near_limit = len(chunk) >= int(effective_max * 0.9)
            needs_continuation = near_limit or any(
                chunk.rstrip().endswith(ind) for ind in truncation_indicators
            )

            if needs_continuation and attempt < max_continuations:
                continuation_prompt = (
                    f"Continue your previous response. You were saying:\n\n"
                    f"{chunk[-300:]}\n\nContinue from where you left off:"
                )
            else:
                break

        return full_response

    def query_council(
        self,
        prompt: str,
        models: List[str] = None,
        max_tokens: int = 600
    ) -> Dict[str, str]:
        """Query multiple models and return all responses."""
        if models is None:
            models = ["codegemma", "qwen3", "deepseek_r1", "gpt_oss_20b"]

        responses = {}
        for model_name in models:
            model_obj = self.models.get(model_name)
            if model_obj:
                effective_max = self._adjust_max_tokens(prompt, max_tokens, model_obj.ollama_id)
                response = self._query_ollama(
                    model_obj.ollama_id,
                    prompt,
                    effective_max,
                    0.7,
                    120
                )
                responses[model_name] = response

        return responses

    def synthesize_council(
        self,
        prompt: str,
        council_models: List[str] = None,
        synthesis_model: str = "gpt_oss_20b",
        max_tokens: int = 600
    ) -> Dict[str, Any]:
        """Query council and synthesize responses."""
        # Get council responses
        council_responses = self.query_council(prompt, council_models, max_tokens)

        # Format for synthesis
        formatted_responses = "\n\n".join([
            f"[{model}]: {response}"
            for model, response in council_responses.items()
        ])

        synthesis_prompt = f"""Synthesize these perspectives into a unified response:

{formatted_responses}

Provide a balanced synthesis that:
1. Identifies common ground
2. Notes key disagreements
3. Proposes a resolution

Keep response under 300 words."""

        synthesis = self.query(
            synthesis_prompt,
            model=synthesis_model,
            max_tokens=500
        )

        return {
            "council_responses": council_responses,
            "synthesis": synthesis
        }

    def _query_ollama(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        timeout: int
    ) -> str:
        """Internal method to query Ollama API."""
        try:
            payload = {
                "model": model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            response = requests.post(self.ollama_url, json=payload, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                result = (data.get("response") or "").strip()

                # Clean DeepSeek thinking tags
                if "<think>" in result:
                    import re
                    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

                if not result and data.get("thinking"):
                    retry_payload = {
                        "model": model_id,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                        },
                    }
                    retry = requests.post(self.ollama_url, json=retry_payload, timeout=timeout)
                    if retry.status_code == 200:
                        result = (retry.json().get("response") or "").strip()

                return result
        except Exception as e:
            print(f"LLM Error ({model_id}): {e}")

        return ""

    def _adjust_max_tokens(self, prompt: str, max_tokens: int, model_id: str) -> int:
        try:
            return apply_dynamic_budget(prompt, max_tokens, model_id=model_id)
        except Exception:
            return max_tokens

    def list_models(self) -> None:
        """Print available models."""
        print("\nAvailable Models:")
        print("-" * 60)
        for name, model in self.models.items():
            print(f"  {name:<15} | {model.speed:<12} | {model.size:<8} | {model.role.value}")
        print()


# Convenience functions
_router = None


def get_router() -> ModelRouter:
    """Get singleton router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def query(prompt: str, task: str = None, model: str = None, **kwargs) -> str:
    """Convenience function to query LLM."""
    return get_router().query(prompt, task, model, **kwargs)


def query_fast(prompt: str, **kwargs) -> str:
    """Quick query using codegemma."""
    return get_router().query(prompt, model="codegemma", **kwargs)


def query_creative(prompt: str, **kwargs) -> str:
    """Creative query using qwen3."""
    return get_router().query(prompt, model="qwen3", **kwargs)


def query_reasoning(prompt: str, **kwargs) -> str:
    """Reasoning query using deepseek_r1."""
    return get_router().query(prompt, model="deepseek_r1", **kwargs)


def query_synthesis(prompt: str, **kwargs) -> str:
    """Complex synthesis using gpt_oss_20b."""
    return get_router().query(prompt, model="gpt_oss_20b", **kwargs)


def query_gpia_core(prompt: str, **kwargs) -> str:
    """Action-protocol brain for structured outputs."""
    return get_router().query(prompt, model="gpia_core", **kwargs)


def query_council(prompt: str, **kwargs) -> Dict[str, str]:
    """Query all models."""
    return get_router().query_council(prompt, **kwargs)


if __name__ == "__main__":
    # Test the router
    router = ModelRouter()
    router.list_models()

    print("\nTesting model routing...")
    test_tasks = [
        "intent_parsing",
        "alpha_response",
        "professor_analysis",
        "final_synthesis"
    ]

    for task in test_tasks:
        model = router.get_model_for_task(task)
        print(f"  {task:<20} -> {model.name} ({model.ollama_id})")
