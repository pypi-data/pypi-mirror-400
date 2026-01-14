"""
Skill Backends
==============

Enables skills to delegate work to local models, saving tokens
on cloud APIs while leveraging local compute resources.

Supported backends:
- claude: Claude API (default, for complex reasoning)
- local: Local llama.cpp models (for routine tasks)
- hybrid: Route based on task complexity

Architecture:
    Claude (orchestrator) → Skills → Local Models → H-Net Memory
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class BackendType(str, Enum):
    """Available execution backends."""
    CLAUDE = "claude"           # Complex reasoning, planning
    LOCAL_QWEN = "local_qwen"   # Code generation, refactoring
    LOCAL_DEEPSEEK = "local_deepseek"  # Code review, debugging
    LOCAL_CODEGEMMA = "local_codegemma"  # Fast completion
    LOCAL_LLAVA = "local_llava"  # Vision-capable local model (text-only here)
    LOCAL_GPT_OSS = "local_gpt_oss"  # Large local general model
    AUTO = "auto"               # Automatically select based on task


@dataclass
class BackendConfig:
    """Configuration for a model backend."""
    name: str
    endpoint: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 120

    # Cost/speed hints for routing
    tokens_per_second: float = 50.0  # Approximate generation speed
    cost_per_1k_tokens: float = 0.0  # 0 for local models


# Default configurations for local models (RTX 4070 SUPER 12GB optimized)
LOCAL_BACKENDS: Dict[str, BackendConfig] = {
    "local_qwen": BackendConfig(
        name="Qwen3-8B",
        endpoint=os.getenv("QWEN_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("QWEN_MODEL", "qwen3:latest"),
        max_tokens=8192,
        tokens_per_second=45.0,  # RTX 4070 SUPER with flash attention
    ),
    "local_deepseek": BackendConfig(
        name="DeepSeek-R1",
        endpoint=os.getenv("DEEPSEEK_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-r1:latest"),
        max_tokens=8192,
        tokens_per_second=40.0,  # Reasoning model, slightly slower
    ),
    "local_codegemma": BackendConfig(
        name="CodeGemma-7B",
        endpoint=os.getenv("CODEGEMMA_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("CODEGEMMA_MODEL", "codegemma:latest"),
        max_tokens=8192,
        tokens_per_second=50.0,  # 7B Q4_0 on RTX 4070 SUPER
    ),
    "local_llava": BackendConfig(
        name="LLaVA",
        endpoint=os.getenv("LLAVA_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("LLAVA_MODEL", "llava:latest"),
        max_tokens=8192,
        tokens_per_second=35.0,
    ),
    "local_gpt_oss": BackendConfig(
        name="GPT-OSS-20B",
        endpoint=os.getenv("GPT_OSS_BASE_URL", "http://localhost:11434/v1"),
        model=os.getenv("GPT_OSS_MODEL", "gpt-oss:20b"),
        max_tokens=8192,
        tokens_per_second=20.0,
    ),
}


# Task type to recommended backend mapping
TASK_BACKEND_ROUTING: Dict[str, BackendType] = {
    # Simple/routine tasks → Local models (save Claude tokens)
    "code_completion": BackendType.LOCAL_CODEGEMMA,
    "code_generation": BackendType.LOCAL_QWEN,
    "code_refactor": BackendType.LOCAL_QWEN,
    "code_review": BackendType.LOCAL_DEEPSEEK,
    "code_explain": BackendType.LOCAL_DEEPSEEK,
    "code_debug": BackendType.LOCAL_DEEPSEEK,
    "docstring": BackendType.LOCAL_CODEGEMMA,
    "type_hints": BackendType.LOCAL_CODEGEMMA,

    # Complex tasks → Claude (need advanced reasoning)
    "architecture": BackendType.CLAUDE,
    "planning": BackendType.CLAUDE,
    "complex_analysis": BackendType.CLAUDE,
    "multi_file_refactor": BackendType.CLAUDE,
    "security_audit": BackendType.CLAUDE,
    "integration": BackendType.CLAUDE,
}


class ModelBackend(ABC):
    """Abstract base for model backends."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate a response from the model."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the backend is available."""
        pass


class LocalLlamaBackend(ModelBackend):
    """
    Backend for local llama.cpp models via Ollama or llama-server.

    Supports both Ollama API and OpenAI-compatible endpoints.
    """

    def __init__(self, config: BackendConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.endpoint,
                timeout=self.config.timeout,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate using local model."""
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            # Try OpenAI-compatible endpoint first
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "max_tokens": min(max_tokens, self.config.max_tokens),
                    "temperature": temperature,
                    "stop": stop,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Local model generation failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if local model server is running."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.config.endpoint}/models")
                return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class BackendRouter:
    """
    Routes tasks to appropriate backends based on complexity.

    Strategy:
    - Simple, repetitive tasks → Local models (free, fast)
    - Complex reasoning → Claude (accurate, expensive)
    - Context retrieval → H-Net memory
    """

    def __init__(
        self,
        local_backends: Optional[Dict[str, BackendConfig]] = None,
        prefer_local: bool = True,
    ):
        self.local_configs = local_backends or LOCAL_BACKENDS
        self.prefer_local = prefer_local
        self._backends: Dict[str, LocalLlamaBackend] = {}
        self._availability_cache: Dict[str, bool] = {}

    def get_backend(self, backend_type: BackendType) -> Optional[LocalLlamaBackend]:
        """Get or create a backend instance."""
        if backend_type == BackendType.CLAUDE:
            return None  # Claude handled externally

        key = backend_type.value
        if key not in self._backends and key in self.local_configs:
            self._backends[key] = LocalLlamaBackend(self.local_configs[key])

        return self._backends.get(key)

    def route_task(
        self,
        task_type: str,
        complexity: str = "medium",
        force_backend: Optional[BackendType] = None,
    ) -> BackendType:
        """
        Determine best backend for a task.

        Args:
            task_type: Type of task (e.g., "code_generation")
            complexity: "low", "medium", "high"
            force_backend: Override automatic routing

        Returns:
            Recommended BackendType
        """
        if force_backend:
            return force_backend

        # High complexity always goes to Claude
        if complexity == "high":
            return BackendType.CLAUDE

        # Check task-specific routing
        if task_type in TASK_BACKEND_ROUTING:
            recommended = TASK_BACKEND_ROUTING[task_type]

            # Verify local backend is available
            if recommended != BackendType.CLAUDE:
                backend = self.get_backend(recommended)
                if backend and self._check_availability(recommended):
                    return recommended

                # Fallback to Claude if local unavailable
                logger.info(f"Local backend {recommended} unavailable, using Claude")
                return BackendType.CLAUDE

            return recommended

        # Default: prefer local for code tasks if available
        if self.prefer_local and self._check_availability(BackendType.LOCAL_QWEN):
            return BackendType.LOCAL_QWEN

        return BackendType.CLAUDE

    def _check_availability(self, backend_type: BackendType) -> bool:
        """Check if a backend is available (with caching)."""
        if backend_type == BackendType.CLAUDE:
            return True

        key = backend_type.value
        if key not in self._availability_cache:
            backend = self.get_backend(backend_type)
            self._availability_cache[key] = backend.is_available() if backend else False

        return self._availability_cache[key]

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about backend routing."""
        return {
            "available_backends": {
                bt.value: self._check_availability(bt)
                for bt in BackendType
                if bt != BackendType.AUTO
            },
            "prefer_local": self.prefer_local,
            "task_mappings": TASK_BACKEND_ROUTING,
        }

    async def execute_on_local(
        self,
        backend_type: BackendType,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Execute a prompt on a local backend.

        Returns None if backend unavailable (caller should fallback to Claude).
        """
        backend = self.get_backend(backend_type)
        if not backend or not self._check_availability(backend_type):
            return None

        try:
            return await backend.generate(prompt, system, **kwargs)
        except Exception as e:
            logger.warning(f"Local execution failed: {e}")
            return None


# Global router instance
_router: Optional[BackendRouter] = None


def get_router() -> BackendRouter:
    """Get the global backend router."""
    global _router
    if _router is None:
        _router = BackendRouter()
    return _router


def estimate_token_savings(
    task_type: str,
    prompt_tokens: int,
    response_tokens: int,
) -> Dict[str, Any]:
    """
    Estimate token savings from using local models.

    Returns:
        Dictionary with cost comparison
    """
    router = get_router()
    recommended = router.route_task(task_type)

    # Claude pricing (approximate)
    claude_cost_per_1k_input = 0.003  # $3 per 1M input
    claude_cost_per_1k_output = 0.015  # $15 per 1M output

    claude_cost = (
        (prompt_tokens / 1000) * claude_cost_per_1k_input +
        (response_tokens / 1000) * claude_cost_per_1k_output
    )

    if recommended == BackendType.CLAUDE:
        return {
            "recommended_backend": "claude",
            "estimated_cost": claude_cost,
            "savings": 0,
            "reason": "Task requires Claude's reasoning capabilities",
        }
    else:
        return {
            "recommended_backend": recommended.value,
            "estimated_cost": 0,
            "savings": claude_cost,
            "reason": f"Task can be handled by local {recommended.value}",
        }


# Integration with Skills framework
def skill_backend_decorator(
    task_type: str,
    allow_local: bool = True,
):
    """
    Decorator to add backend routing to skill methods.

    Usage:
        @skill_backend_decorator("code_generation")
        async def generate_code(self, prompt: str) -> str:
            # If local available, this runs on Qwen
            # Otherwise falls back to Claude
            pass
    """
    def decorator(func: Callable):
        async def wrapper(self, *args, **kwargs):
            router = get_router()

            if allow_local:
                backend_type = router.route_task(task_type)

                if backend_type != BackendType.CLAUDE:
                    # Try local execution
                    result = await router.execute_on_local(
                        backend_type,
                        prompt=kwargs.get("prompt", args[0] if args else ""),
                        system=kwargs.get("system"),
                    )
                    if result:
                        logger.info(f"Task {task_type} executed on {backend_type.value}")
                        return result

            # Fallback to original (Claude-based) implementation
            return await func(self, *args, **kwargs)

        return wrapper
    return decorator
