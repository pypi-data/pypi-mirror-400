"""
Mindset - Multi-Model Reasoning Orchestrator
=============================================

This skill chains local models together for complex reasoning.
Each model has strengths - by combining them, we get better results
than any single model alone.

Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                    COGNITIVE LAYER                          │
│  Mindset orchestrates reasoning patterns                    │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    SKILLS LAYER                             │
│  conscience/self (introspection)                           │
│  conscience/memory (persistence)                           │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LAYER                             │
│  H-Net vectors • SQLite KB • Pattern store                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE LAYER                            │
│  DeepSeek-R1 │ Qwen3 │ CodeGemma │ NPU embeddings          │
└─────────────────────────────────────────────────────────────┘
```

Model roles:
- DeepSeek-R1 (analytical): Deep reasoning, critique, debugging
- Qwen3 (creative): Generation, synthesis, code creation
- CodeGemma (fast): Quick completions, simple checks
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from core.dynamic_budget_orchestrator import apply_dynamic_budget
from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)

# Ollama endpoint
OLLAMA_URL = "http://localhost:11434"


@dataclass
class ModelConfig:
    """Configuration for a local model."""
    name: str
    ollama_model: str
    role: str
    strengths: List[str]
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 2048


# Model configurations
MODELS: Dict[str, ModelConfig] = {
    "analytical": ModelConfig(
        name="DeepSeek-R1",
        ollama_model="deepseek-r1:latest",
        role="analytical",
        strengths=["reasoning", "analysis", "critique", "debugging"],
        system_prompt="""You are an analytical thinker. Your role is to:
- Examine problems deeply and systematically
- Identify flaws, gaps, and assumptions
- Provide structured critique
- Reason step by step
Be thorough but concise. Focus on logic and evidence.""",
        temperature=0.3,
    ),
    "creative": ModelConfig(
        name="Qwen3",
        ollama_model="qwen3:latest",
        role="creative",
        strengths=["generation", "synthesis", "code", "ideas"],
        system_prompt="""You are a creative synthesizer. Your role is to:
- Generate novel ideas and solutions
- Combine concepts in unexpected ways
- Write code and content
- Explore possibilities
Be inventive but practical. Build on what came before.""",
        temperature=0.8,
    ),
    "fast": ModelConfig(
        name="CodeGemma",
        ollama_model="codegemma:latest",
        role="fast",
        strengths=["completion", "quick-checks", "simple-tasks"],
        system_prompt="""You are a fast responder. Your role is to:
- Quickly complete or check things
- Provide brief, direct answers
- Handle simple tasks efficiently
Be concise. One or two sentences when possible.""",
        temperature=0.5,
        max_tokens=512,
    ),
}


# Reasoning patterns
PATTERNS: Dict[str, List[str]] = {
    "deep_analysis": ["analytical", "creative", "analytical"],
    "creative_synthesis": ["creative", "analytical", "creative"],
    "rapid_iteration": ["fast", "fast", "analytical"],
    "debate": ["creative", "analytical", "creative", "analytical"],
    "build_and_break": ["creative", "analytical"],
}


@dataclass
class ThoughtStep:
    """A single step in reasoning chain."""
    model: str
    role: str
    prompt: str
    thought: str
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelClient:
    """Client for local Ollama models."""

    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> tuple[str, float]:
        """Generate response from model. Returns (response, duration_ms)."""
        client = await self._get_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()

        try:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": -1,  # Keep model loaded in VRAM (prevents thrashing)
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

            duration_ms = (time.perf_counter() - start) * 1000
            content = data.get("message", {}).get("content", "")

            return content, duration_ms

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(f"Model {model} failed: {e}")
            return f"[Error: {e}]", duration_ms

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class MindsetSkill(Skill):
    """
    Multi-model reasoning orchestrator.

    Chains local models together for complex thinking:
    - Analytical (DeepSeek-R1): Critique, debug, reason
    - Creative (Qwen3): Generate, synthesize, create
    - Fast (CodeGemma): Quick checks, completions

    Integrates with memory for context and learning.
    """

    def __init__(self):
        self.client = ModelClient()
        self._memory = None

    @property
    def memory(self):
        """Lazy load memory skill."""
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"Could not load memory skill: {e}")
        return self._memory

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="conscience/mindset",
            name="Mindset",
            description="Multi-model reasoning orchestrator across all layers",
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["conscience", "orchestration", "multi-model"],
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute reasoning - runs async internally."""
        return asyncio.run(self._execute_async(input_data, context))

    async def _execute_async(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Async execution of reasoning chain."""
        capability = input_data.get("capability", "think")
        problem = input_data.get("problem", "")

        if not problem:
            return SkillResult(
                success=False,
                output=None,
                error="No problem provided",
                skill_id=self.metadata().id,
            )

        handlers = {
            "think": self._think,
            "analyze": self._analyze,
            "create": self._create,
            "decide": self._decide,
            "learn": self._learn,
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
            return await handler(input_data, context)
        finally:
            await self.client.close()

    async def _think(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Deep thinking using model chain."""
        problem = input_data["problem"]
        pattern_name = input_data.get("pattern", "deep_analysis")
        depth = input_data.get("depth", 2)
        store = input_data.get("store_reasoning", True)
        ctx = input_data.get("context", {})

        # Get model chain
        if pattern_name == "custom":
            chain = input_data.get("custom_chain", ["analytical"])
        else:
            chain = PATTERNS.get(pattern_name, PATTERNS["deep_analysis"])

        override_role = self._resolve_model_override(context)
        if override_role:
            sovereignty = context.extra.get("sovereignty") if context else {}
            if isinstance(sovereignty, dict) and sovereignty.get("status") == "shed":
                chain = [override_role]
            else:
                chain = [override_role for _ in chain]

        # Build context from memory
        memory_context = await self._get_memory_context(problem)

        # Execute chain
        reasoning_trace = []
        current_thought = problem

        if ctx.get("constraints"):
            current_thought += f"\n\nConstraints: {', '.join(ctx['constraints'])}"
        if ctx.get("goals"):
            current_thought += f"\n\nGoals: {', '.join(ctx['goals'])}"
        if memory_context:
            current_thought += f"\n\nRelevant context: {memory_context}"

        for i, model_role in enumerate(chain):
            config = MODELS[model_role]

            # Craft prompt based on position in chain
            if i == 0:
                prompt = f"Think about this problem:\n\n{current_thought}"
            elif i == len(chain) - 1:
                prompt = f"""Previous thinking:\n{current_thought}\n
Now provide a final, refined conclusion. Be concise and actionable."""
            else:
                prompt = f"""Previous thinking:\n{current_thought}\n
Build on this. {'Critique and improve it.' if model_role == 'analytical' else 'Expand and generate alternatives.'}"""

            requested_tokens = config.max_tokens
            if context and context.max_tokens:
                requested_tokens = min(requested_tokens, int(context.max_tokens))
            budget_profile = None
            if context and context.extra:
                budget_profile = context.extra.get("budget_profile")
            max_tokens = apply_dynamic_budget(
                prompt,
                requested_tokens,
                model_id=config.ollama_model,
                profile=budget_profile,
            )

            response, duration = await self.client.generate(
                model=config.ollama_model,
                prompt=prompt,
                system=config.system_prompt,
                temperature=config.temperature,
                max_tokens=max_tokens,
            )

            step = ThoughtStep(
                model=config.name,
                role=model_role,
                prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                thought=response,
                duration_ms=duration,
            )
            reasoning_trace.append(step)
            current_thought = response

            logger.debug(f"Step {i+1}/{len(chain)} ({config.name}): {duration:.0f}ms")

        # Calculate confidence based on reasoning quality
        confidence = self._estimate_confidence(reasoning_trace)

        # Extract alternatives if mentioned
        alternatives = self._extract_alternatives(reasoning_trace)

        # Store in memory if requested
        memory_id = None
        if store and self.memory:
            memory_id = await self._store_reasoning(
                problem, reasoning_trace, confidence, context
            )

        return SkillResult(
            success=True,
            output={
                "conclusion": reasoning_trace[-1].thought if reasoning_trace else "",
                "reasoning_trace": [
                    {
                        "model": s.model,
                        "role": s.role,
                        "thought": s.thought,
                        "duration_ms": s.duration_ms,
                    }
                    for s in reasoning_trace
                ],
                "confidence": confidence,
                "alternatives": alternatives,
                "memory_id": memory_id,
                "pattern_used": pattern_name,
                "total_duration_ms": sum(s.duration_ms for s in reasoning_trace),
            },
            skill_id=self.metadata().id,
        )

    async def _analyze(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Multi-perspective analysis."""
        input_data["pattern"] = "deep_analysis"
        return await self._think(input_data, context)

    async def _create(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Creative generation with refinement."""
        input_data["pattern"] = "creative_synthesis"
        return await self._think(input_data, context)

    async def _decide(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Decision-making with explicit alternatives."""
        problem = input_data["problem"]

        # First: generate options
        gen_result = await self._think({
            **input_data,
            "problem": f"What are the possible approaches or decisions for: {problem}",
            "pattern": "creative_synthesis",
            "store_reasoning": False,
        }, context)

        options = gen_result.output.get("conclusion", "")

        # Second: evaluate each option
        eval_result = await self._think({
            **input_data,
            "problem": f"Evaluate these options and recommend the best one:\n\n{options}\n\nOriginal decision: {problem}",
            "pattern": "deep_analysis",
        }, context)

        return eval_result

    async def _learn(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Extract and store patterns from experience."""
        problem = input_data["problem"]

        # Analyze what can be learned
        learn_result = await self._think({
            **input_data,
            "problem": f"What patterns, principles, or lessons can be extracted from this experience?\n\n{problem}",
            "pattern": "deep_analysis",
        }, context)

        # Store as semantic memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Learned: {learn_result.output['conclusion']}",
                "memory_type": "semantic",
                "importance": 0.8,
                "context": {"source": "mindset_learn"},
            }, context)

        return learn_result

    async def _get_memory_context(self, problem: str) -> str:
        """Retrieve relevant context from memory."""
        if not self.memory:
            return ""

        result = self.memory.execute({
            "capability": "recall",
            "content": problem,
            "limit": 3,
        }, SkillContext())

        if result.success and result.output.get("memories"):
            memories = result.output["memories"]
            if memories:
                return "\n".join(
                    f"- {m['content'][:100]}" for m in memories[:3]
                )
        return ""

    async def _store_reasoning(
        self,
        problem: str,
        trace: List[ThoughtStep],
        confidence: float,
        context: SkillContext,
    ) -> Optional[str]:
        """Store reasoning trace in memory."""
        if not self.memory:
            return None

        summary = f"Reasoning about: {problem[:100]}...\nConclusion: {trace[-1].thought[:200] if trace else 'none'}"

        result = self.memory.execute({
            "capability": "experience",
            "content": summary,
            "memory_type": "procedural",
            "importance": confidence,
            "context": {
                "pattern": "reasoning_trace",
                "models_used": [s.model for s in trace],
                "total_duration_ms": sum(s.duration_ms for s in trace),
            },
        }, context)

        return result.output.get("memory_id") if result.success else None

    def _estimate_confidence(self, trace: List[ThoughtStep]) -> float:
        """Estimate confidence based on reasoning trace."""
        if not trace:
            return 0.3

        confidence = 0.5

        # More steps = more thorough = slightly higher confidence
        confidence += min(0.1, len(trace) * 0.03)

        # Check for uncertainty markers in final thought
        final = trace[-1].thought.lower()
        uncertainty_markers = ["uncertain", "might", "possibly", "unclear", "not sure"]
        certainty_markers = ["clearly", "definitely", "certainly", "confident", "conclusion"]

        for marker in uncertainty_markers:
            if marker in final:
                confidence -= 0.1

        for marker in certainty_markers:
            if marker in final:
                confidence += 0.05

        return max(0.1, min(0.95, confidence))

    def _extract_alternatives(self, trace: List[ThoughtStep]) -> List[str]:
        """Extract mentioned alternatives from reasoning."""
        alternatives = []

        for step in trace:
            thought = step.thought.lower()

            # Look for alternative indicators
            if "alternatively" in thought or "another option" in thought:
                # Simple extraction - could be improved
                sentences = step.thought.split(".")
                for sent in sentences:
                    if any(w in sent.lower() for w in ["alternatively", "another", "could also", "option"]):
                        alternatives.append(sent.strip())

        return alternatives[:5]  # Limit to 5

    def _resolve_model_override(self, context: SkillContext) -> Optional[str]:
        if not context or not context.extra:
            return None
        model_hint = context.extra.get("model_hint")
        sovereignty = context.extra.get("sovereignty")
        if not model_hint and isinstance(sovereignty, dict):
            model_hint = sovereignty.get("model_hint")
        if not model_hint:
            return None
        lowered = str(model_hint).lower()
        if "codegemma" in lowered:
            return "fast"
        if "qwen" in lowered:
            return "creative"
        if "deepseek" in lowered:
            return "analytical"
        if "gpt-oss" in lowered or "20b" in lowered:
            return "analytical"
        return None


# Package init
__all__ = ["MindsetSkill"]
