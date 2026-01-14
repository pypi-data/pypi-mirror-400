"""
S2 Visual Context Encoder
=========================

LLaVa integration for visual context encoding in S2 architecture.

Based on S2 paper insight: visual encoding of large context outperforms
text-only approaches. LLaVa enables:
1. Context compression - Large text → Visual representation → Compact tokens
2. Multi-modal reasoning - Combine visual + text at each scale level
3. Visual skill execution - Skills that operate on images/screenshots

Scale-aware visual routing:
- L0 (Micro): Image parsing, OCR, element detection
- L1 (Meso): Scene understanding, layout analysis
- L2 (Macro): Visual workflow, UI automation
- L3 (Meta): Multi-modal orchestration
"""

import base64
import io
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
import numpy as np

from .context_stack import ScaleLevel

logger = logging.getLogger(__name__)

# Ollama endpoint for LLaVa
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
LLAVA_MODEL = "llava:latest"


class VisualTaskType(str, Enum):
    """Types of visual tasks for scale-aware routing."""
    PARSE = "parse"           # L0 - Extract elements from image
    ANALYZE = "analyze"       # L1 - Understand visual content
    DESCRIBE = "describe"     # L2 - Generate description
    ENCODE = "encode"         # Context compression
    DECODE = "decode"         # Visual to text
    COMPARE = "compare"       # Multi-image analysis


@dataclass
class VisualContext:
    """Visual context representation for S2."""
    image_data: Optional[bytes] = None
    image_base64: Optional[str] = None
    description: str = ""
    elements: List[Dict[str, Any]] = field(default_factory=list)
    embeddings: Optional[np.ndarray] = None
    scale: ScaleLevel = ScaleLevel.L1
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_image(self) -> bool:
        return self.image_data is not None or self.image_base64 is not None

    def get_base64(self) -> Optional[str]:
        """Get base64 encoded image."""
        if self.image_base64:
            return self.image_base64
        if self.image_data:
            return base64.b64encode(self.image_data).decode('utf-8')
        return None


class LLaVaClient:
    """
    Client for LLaVa vision model via Ollama.

    Handles image encoding/decoding and visual reasoning.
    """

    def __init__(
        self,
        ollama_url: str = OLLAMA_URL,
        model: str = LLAVA_MODEL,
        timeout: int = 120
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout
        self._available = None

    def is_available(self) -> bool:
        """Check if LLaVa is available."""
        if self._available is not None:
            return self._available

        try:
            response = requests.get(
                self.ollama_url.replace("/api/generate", "/api/tags"),
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                self._available = any("llava" in m.get("name", "").lower() for m in models)
            else:
                self._available = False
        except Exception as e:
            logger.warning(f"LLaVa availability check failed: {e}")
            self._available = False

        return self._available

    def query(
        self,
        prompt: str,
        image_base64: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Query LLaVa with optional image."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }

        if image_base64:
            payload["images"] = [image_base64]

        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"LLaVa query failed: {response.status_code}")
                return ""

        except Exception as e:
            logger.error(f"LLaVa query error: {e}")
            return ""

    def analyze_image(
        self,
        image_base64: str,
        task: VisualTaskType = VisualTaskType.DESCRIBE,
        context: str = ""
    ) -> Dict[str, Any]:
        """Analyze an image with LLaVa."""
        prompts = {
            VisualTaskType.PARSE: (
                "Parse this image and list all visible elements, UI components, "
                "or text. Return as structured list."
            ),
            VisualTaskType.ANALYZE: (
                "Analyze this image. Describe the layout, relationships between "
                "elements, and any patterns you observe."
            ),
            VisualTaskType.DESCRIBE: (
                "Describe this image in detail. Include colors, objects, text, "
                "and overall composition."
            ),
            VisualTaskType.ENCODE: (
                "Summarize the key information in this image into a compact "
                "text representation that captures the essential content."
            ),
        }

        prompt = prompts.get(task, prompts[VisualTaskType.DESCRIBE])
        if context:
            prompt = f"{context}\n\n{prompt}"

        start_time = time.time()
        response = self.query(prompt, image_base64)
        elapsed = time.time() - start_time

        return {
            "task": task.value,
            "response": response,
            "elapsed_ms": int(elapsed * 1000),
            "has_image": True
        }


class S2VisualEncoder:
    """
    S2 Visual Context Encoder.

    Encodes large text context into visual representations using LLaVa,
    enabling context compression based on S2 paper insights.
    """

    def __init__(self, llava_client: Optional[LLaVaClient] = None):
        self.llava = llava_client or LLaVaClient()
        self.encoding_cache: Dict[str, VisualContext] = {}

    def encode_context(
        self,
        text: str,
        scale: ScaleLevel = ScaleLevel.L2,
        max_chars: int = 10000
    ) -> VisualContext:
        """
        Encode text context for visual processing.

        For large contexts, this creates a structured summary that
        can be processed visually by LLaVa.
        """
        # Truncate if needed
        if len(text) > max_chars:
            text = text[:max_chars] + "... [truncated]"

        # Create visual context
        context = VisualContext(
            description=text,
            scale=scale,
            metadata={
                "original_length": len(text),
                "encoded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        # If LLaVa is available, get visual understanding
        if self.llava.is_available():
            # For text-only encoding, we ask LLaVa to create a mental model
            prompt = f"""Analyze this context and create a structured summary:

{text[:2000]}

Provide:
1. Key entities/concepts
2. Relationships between them
3. Main actions or workflows
4. Important details

Format as structured list."""

            response = self.llava.query(prompt, max_tokens=400)
            context.metadata["llava_summary"] = response

        return context

    def encode_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        scale: ScaleLevel = ScaleLevel.L1
    ) -> VisualContext:
        """Encode an image into visual context."""
        # Get base64
        if image_base64:
            b64 = image_base64
        elif image_bytes:
            b64 = base64.b64encode(image_bytes).decode('utf-8')
        elif image_path:
            with open(image_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
        else:
            raise ValueError("Must provide image_path, image_bytes, or image_base64")

        context = VisualContext(
            image_base64=b64,
            scale=scale,
            metadata={"source": image_path or "bytes"}
        )

        # Analyze with LLaVa if available
        if self.llava.is_available():
            analysis = self.llava.analyze_image(b64, VisualTaskType.ANALYZE)
            context.description = analysis["response"]
            context.metadata["analysis"] = analysis

            # Parse elements
            elements_analysis = self.llava.analyze_image(b64, VisualTaskType.PARSE)
            context.metadata["elements_raw"] = elements_analysis["response"]

        return context

    def compress_context(
        self,
        text: str,
        target_tokens: int = 100,
        scale: ScaleLevel = ScaleLevel.L2
    ) -> Dict[str, Any]:
        """
        Compress large context into compact representation.

        Uses LLaVa's visual understanding to identify key information
        and compress it into a smaller token budget.
        """
        if not self.llava.is_available():
            # Fallback to simple truncation
            words = text.split()
            compressed = " ".join(words[:target_tokens])
            return {
                "compressed": compressed,
                "original_tokens": len(words),
                "target_tokens": target_tokens,
                "method": "truncation",
                "scale": scale.value
            }

        prompt = f"""Compress this context into exactly {target_tokens} words or less.
Preserve the most important information. Be concise but complete.

Context:
{text[:4000]}

Compressed version ({target_tokens} words max):"""

        compressed = self.llava.query(prompt, max_tokens=target_tokens * 2)

        return {
            "compressed": compressed,
            "original_tokens": len(text.split()),
            "target_tokens": target_tokens,
            "actual_tokens": len(compressed.split()),
            "compression_ratio": len(text.split()) / max(1, len(compressed.split())),
            "method": "llava_compression",
            "scale": scale.value
        }


class S2MultiModalRouter:
    """
    Multi-modal routing for S2 scale levels.

    Routes tasks to appropriate models based on:
    - Scale level (L0-L3)
    - Task type (text vs visual)
    - Content characteristics
    """

    # Scale to model mapping - All 5 LLM Partners
    # - codegemma: Fast atomic operations, intent parsing
    # - qwen3: Creative synthesis, code generation
    # - deepseek_r1: Deep reasoning, analysis, debugging
    # - llava: Visual tasks, image analysis, screenshots
    # - gpt_oss_20b: Complex synthesis, dispute resolution, arbiter
    SCALE_ROUTING = {
        ScaleLevel.L0: {
            "text": "codegemma",
            "visual": "llava",
            "reasoning": "codegemma",      # Fast checks
            "synthesis": "qwen3",          # Quick creative
            "description": "Atomic operations - fast reflexes"
        },
        ScaleLevel.L1: {
            "text": "qwen3",
            "visual": "llava",
            "reasoning": "deepseek_r1",    # Analysis support
            "synthesis": "qwen3",          # Code generation
            "description": "Composed operations - creative synthesis"
        },
        ScaleLevel.L2: {
            "text": "qwen3",
            "visual": "llava",
            "reasoning": "deepseek_r1",    # Deep analysis
            "synthesis": "gpt_oss_20b",    # Multi-perspective
            "description": "Bundled workflows - complex tasks"
        },
        ScaleLevel.L3: {
            "text": "deepseek_r1",
            "visual": "llava",
            "reasoning": "deepseek_r1",    # Meta-reasoning
            "synthesis": "gpt_oss_20b",    # Arbiter/synthesis
            "description": "Meta orchestration - AGI coordination"
        },
    }

    def __init__(self, ollama_url: str = OLLAMA_URL):
        self.ollama_url = ollama_url
        self.llava = LLaVaClient(ollama_url)

    def get_model_for_scale(
        self,
        scale: ScaleLevel,
        has_image: bool = False,
        task_type: str = "text"
    ) -> str:
        """
        Get appropriate model for scale level and task type.

        Task types:
        - text: General text processing (codegemma/qwen3/deepseek_r1)
        - visual: Image analysis (llava)
        - reasoning: Deep analysis, debugging (deepseek_r1)
        - synthesis: Multi-perspective, arbiter (gpt_oss_20b)
        """
        routing = self.SCALE_ROUTING.get(scale, self.SCALE_ROUTING[ScaleLevel.L2])
        if has_image:
            return routing["visual"]
        return routing.get(task_type, routing["text"])

    def route(
        self,
        prompt: str,
        scale: ScaleLevel = ScaleLevel.L2,
        image_base64: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Route a request to the appropriate model."""
        has_image = image_base64 is not None
        model = self.get_model_for_scale(scale, has_image)

        start_time = time.time()

        if has_image and model == "llava":
            response = self.llava.query(prompt, image_base64, max_tokens, temperature)
        else:
            # Query text model via Ollama
            response = self._query_text_model(model, prompt, max_tokens, temperature)

        elapsed = time.time() - start_time

        return {
            "response": response,
            "model": model,
            "scale": scale.value,
            "has_image": has_image,
            "elapsed_ms": int(elapsed * 1000)
        }

    def _query_text_model(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Query a text model via Ollama."""
        model_ids = {
            "codegemma": "codegemma:latest",
            "qwen3": "qwen3:latest",
            "deepseek_r1": "deepseek-r1:latest",
            "gpt_oss_20b": "gpt-oss:20b",
        }

        model_id = model_ids.get(model, "qwen3:latest")

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            return ""

        except Exception as e:
            logger.error(f"Text model query error: {e}")
            return ""


class S2VisualTransform:
    """
    Visual transforms for S2 multi-scale architecture.

    Extends S2Projector with visual modality support.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.encoder = S2VisualEncoder()
        self.router = S2MultiModalRouter()

    def visual_to_embedding(
        self,
        visual_context: VisualContext
    ) -> np.ndarray:
        """
        Convert visual context to embedding vector.

        Uses description text if no image, or LLaVa analysis if image present.
        """
        # Get text representation
        if visual_context.description:
            text = visual_context.description
        elif visual_context.metadata.get("llava_summary"):
            text = visual_context.metadata["llava_summary"]
        else:
            text = "empty visual context"

        # Generate embedding from text (simulated - would use actual embedder)
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        np.random.seed(int.from_bytes(hash_bytes[:4], 'little'))
        embedding = np.random.randn(self.dimension).astype(np.float32)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)

        return embedding

    def multi_modal_embedding(
        self,
        text: str,
        image_base64: Optional[str] = None,
        scale: ScaleLevel = ScaleLevel.L1
    ) -> Dict[str, np.ndarray]:
        """
        Generate multi-modal embedding at specified scale.

        Combines text and visual embeddings with scale-aware weighting.
        """
        # Text embedding
        text_ctx = self.encoder.encode_context(text, scale)
        text_emb = self.visual_to_embedding(text_ctx)

        result = {
            "text": text_emb,
            "combined": text_emb.copy()
        }

        # Visual embedding if image provided
        if image_base64:
            visual_ctx = self.encoder.encode_image(image_base64=image_base64, scale=scale)
            visual_emb = self.visual_to_embedding(visual_ctx)
            result["visual"] = visual_emb

            # Combine with scale-aware weighting
            # Higher scales weight text more (reasoning), lower scales weight visual more (perception)
            visual_weights = {
                ScaleLevel.L0: 0.7,  # More visual at micro level
                ScaleLevel.L1: 0.5,  # Balanced at meso
                ScaleLevel.L2: 0.3,  # More text at macro
                ScaleLevel.L3: 0.2,  # Most text at meta
            }

            w = visual_weights.get(scale, 0.5)
            result["combined"] = (1 - w) * text_emb + w * visual_emb
            result["combined"] = result["combined"] / (np.linalg.norm(result["combined"]) + 1e-8)

        return result


# ==============================================================================
# EXAMPLE AND TESTING
# ==============================================================================

def run_visual_example():
    """Run an example of S2 visual integration."""
    print("=" * 60)
    print("S2 VISUAL INTEGRATION EXAMPLE")
    print("=" * 60)

    # Check LLaVa availability
    llava = LLaVaClient()
    print(f"\nLLaVa available: {llava.is_available()}")

    # Test visual encoder
    encoder = S2VisualEncoder(llava)

    # Encode text context
    sample_text = """
    The CLI AI system is a cognitive multi-agent AGI learning system featuring:
    - GPIA: General Purpose Intelligent Agent with 76+ composable skills
    - H-Net: Hierarchical memory with MSHR retrieval
    - Alpha + Professor: Student-teacher pair for interactive training
    - 5 LLM Partners: DeepSeek-R1, Qwen3, CodeGemma, LLaVa, GPT-OSS

    The S2 architecture adds multi-scale skill decomposition with visual context.
    """

    print("\n--- CONTEXT ENCODING ---")
    ctx = encoder.encode_context(sample_text, ScaleLevel.L2)
    print(f"  Scale: {ctx.scale.value}")
    print(f"  Original length: {ctx.metadata.get('original_length', 0)} chars")
    if ctx.metadata.get("llava_summary"):
        print(f"  LLaVa summary: {ctx.metadata['llava_summary'][:200]}...")

    # Test context compression
    print("\n--- CONTEXT COMPRESSION ---")
    compressed = encoder.compress_context(sample_text, target_tokens=30)
    print(f"  Method: {compressed['method']}")
    print(f"  Original tokens: {compressed['original_tokens']}")
    print(f"  Compressed to: {compressed.get('actual_tokens', 'N/A')} tokens")
    if compressed.get('compression_ratio'):
        print(f"  Compression ratio: {compressed['compression_ratio']:.1f}x")
    print(f"  Result: {compressed['compressed'][:150]}...")

    # Test multi-modal router
    print("\n--- MULTI-MODAL ROUTING ---")
    router = S2MultiModalRouter()

    for scale in [ScaleLevel.L0, ScaleLevel.L1, ScaleLevel.L2, ScaleLevel.L3]:
        text_model = router.get_model_for_scale(scale, has_image=False)
        visual_model = router.get_model_for_scale(scale, has_image=True)
        print(f"  {scale.value}: text={text_model}, visual={visual_model}")

    # Test visual transform
    print("\n--- VISUAL TRANSFORM ---")
    transform = S2VisualTransform()
    embeddings = transform.multi_modal_embedding(sample_text, scale=ScaleLevel.L2)
    print(f"  Text embedding shape: {embeddings['text'].shape}")
    print(f"  Combined embedding norm: {np.linalg.norm(embeddings['combined']):.4f}")

    print("\n" + "=" * 60)
    print("S2 Visual Integration complete!")

    return {
        "context": ctx,
        "compression": compressed,
        "embeddings": embeddings
    }


if __name__ == "__main__":
    run_visual_example()
