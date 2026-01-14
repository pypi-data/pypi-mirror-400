"""
Intel NPU Utilities
===================

Offload lightweight AI tasks to Intel AI Boost NPU,
freeing GPU for LLM inference.

Use cases:
- Embedding generation for H-Net memory
- Fast intent classification
- Text preprocessing (NER, chunking signals)

Backend Priority:
1. Direct OpenVINO on NPU (fastest, ~82 texts/sec)
2. Sentence-transformers on GPU (fast, CUDA)
3. Sentence-transformers on CPU (fallback)
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from urllib import request

import numpy as np

logger = logging.getLogger(__name__)

# Lazy OpenVINO import
_ov_core = None

# Model cache directory
MODEL_CACHE_DIR = Path.home() / ".cache" / "openvino_models"


def get_openvino_core():
    """Get OpenVINO Core (lazy init)."""
    global _ov_core
    if _ov_core is None:
        try:
            from openvino import Core
            _ov_core = Core()
        except ImportError:
            logger.warning("OpenVINO not installed")
            return None
    return _ov_core


def get_available_devices() -> List[str]:
    """List available OpenVINO devices."""
    core = get_openvino_core()
    if core is None:
        return []
    return core.available_devices


def has_npu() -> bool:
    """Check if Intel NPU is available."""
    return "NPU" in get_available_devices()


def get_npu_info() -> dict:
    """Get NPU device information."""
    core = get_openvino_core()
    if core is None or not has_npu():
        return {"available": False}

    try:
        return {
            "available": True,
            "name": core.get_property("NPU", "FULL_DEVICE_NAME"),
            "supported_properties": list(core.get_property("NPU", "SUPPORTED_PROPERTIES")),
        }
    except Exception as e:
        return {"available": True, "error": str(e)}


def _ensure_npu_model_exported(model_id: str, max_length: int = 128) -> Optional[Path]:
    """
    Ensure model is exported to OpenVINO IR format for NPU.

    Returns path to model.xml or None if export fails.
    """
    model_name = model_id.split("/")[-1]
    model_dir = MODEL_CACHE_DIR / model_name
    ir_path = model_dir / "model_static.xml"

    if ir_path.exists():
        return ir_path

    logger.info(f"Exporting {model_id} to OpenVINO IR for NPU...")
    model_dir.mkdir(parents=True, exist_ok=True)

    try:
        from sentence_transformers import SentenceTransformer
        import torch
        from openvino import save_model

        # Load model
        model = SentenceTransformer(model_id, device="cpu")
        transformer = model[0].auto_model

        # Export to ONNX with static shapes (NPU requires fixed dimensions)
        onnx_path = model_dir / "model_static.onnx"
        dummy_input = {
            "input_ids": torch.ones(1, max_length, dtype=torch.long),
            "attention_mask": torch.ones(1, max_length, dtype=torch.long),
            "token_type_ids": torch.zeros(1, max_length, dtype=torch.long),
        }

        torch.onnx.export(
            transformer,
            (dummy_input,),
            str(onnx_path),
            input_names=["input_ids", "attention_mask", "token_type_ids"],
            output_names=["last_hidden_state"],
            opset_version=14,
        )

        # Convert to OpenVINO IR
        core = get_openvino_core()
        ov_model = core.read_model(str(onnx_path))
        save_model(ov_model, str(ir_path))

        logger.info(f"Model exported to: {ir_path}")
        return ir_path

    except Exception as e:
        logger.error(f"Failed to export model: {e}")
        return None


class NPUEmbedder:
    """
    Fast embedding generation with multiple backends.

    Priority order:
    1. Direct OpenVINO on NPU (fastest, ~82 texts/sec)
    2. Sentence-transformers on GPU (fast, CUDA)
    3. Sentence-transformers on CPU (fallback)

    Uses MiniLM-L6-v2 (384 dimensions) by default.
    """

    def __init__(self, model_path: Optional[Path] = None, device: str = "NPU"):
        self.requested_device = device
        self.device = device if has_npu() else "CPU"
        self.model_path = model_path
        self.ollama_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "mahonzhan/all-MiniLM-L6-v2")
        self._model = None
        self._tokenizer = None
        self._compiled_model = None  # For direct OpenVINO
        self._backend = None  # "openvino-direct", "sentence-transformers"
        self._backend_logged = False
        self._max_length = 128  # Fixed for NPU

        if self.device == "CPU" and device == "NPU":
            logger.info("NPU requested but not available, will use fallback")

    def load_model(self, model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Load embedding model with automatic backend selection.

        Tries direct OpenVINO first (for NPU), falls back to sentence-transformers.
        """
        # Try direct OpenVINO path first (enables true NPU acceleration)
        if self.device == "NPU" and self._try_load_openvino_direct(model_id):
            self._log_backend(model_id)
            return True

        # Prefer Ollama embeddings next to avoid ST downloads and CPU churn
        if self._try_load_ollama_embeddings():
            self._log_backend(model_id)
            return True

        # Fallback to sentence-transformers (works reliably on CPU)
        if self._try_load_sentence_transformers(model_id):
            self._log_backend(model_id)
            return True

        logger.error("Failed to load embedding model with any backend")
        return False

    def _log_backend(self, model_id: str) -> None:
        if self._backend_logged or self._backend is None:
            return
        model_name = self.ollama_model if self._backend == "ollama" else model_id
        logger.info("Embedding backend selected: %s (%s) model=%s", self._backend, self.device, model_name)
        self._backend_logged = True

    def _try_load_openvino_direct(self, model_id: str) -> bool:
        """Load model directly via OpenVINO for true NPU acceleration."""
        try:
            from transformers import AutoTokenizer

            # Ensure model is exported
            ir_path = _ensure_npu_model_exported(model_id, self._max_length)
            if ir_path is None:
                return False

            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(model_id)

            # Compile for NPU
            core = get_openvino_core()
            ov_model = core.read_model(str(ir_path))
            self._compiled_model = core.compile_model(ov_model, "NPU")

            self._backend = "openvino-direct"
            self.device = "NPU"
            logger.info(f"Loaded embedding model on NPU via direct OpenVINO")
            return True

        except Exception as e:
            logger.debug(f"Direct OpenVINO load failed: {e}")
            return False

    def _try_load_sentence_transformers(self, model_id: str) -> bool:
        """Load model via sentence-transformers (reliable fallback)."""
        try:
            from sentence_transformers import SentenceTransformer

            # ALWAYS use CPU for embeddings to avoid GPU competition with Ollama LLMs
            # GPU VRAM is reserved for LLM inference (DeepSeek/Qwen3 need ~6GB)
            # MiniLM-L6-v2 is small enough that CPU is fast (~1300 texts/sec)
            st_device = "cpu"

            self._model = SentenceTransformer(model_id, device=st_device)
            self._backend = "sentence-transformers"
            self.device = st_device.upper()
            logger.info(f"Loaded embedding model on {self.device} via sentence-transformers")
            return True

        except ImportError:
            logger.debug("sentence-transformers not available")
            return False
        except Exception as e:
            logger.debug(f"sentence-transformers load failed: {e}")
            return False

    def _try_load_ollama_embeddings(self) -> bool:
        """Load embedding backend via local Ollama server."""
        try:
            _ = self._ollama_embed(["ping"])
            self._backend = "ollama"
            self.device = "OLLAMA"
            logger.info(f"Loaded embedding model via Ollama: {self.ollama_model}")
            return True
        except Exception as e:
            logger.debug(f"Ollama embedding load failed: {e}")
            return False

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        if self._backend is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if self._backend == "openvino-direct":
            return self._embed_openvino_direct(texts)
        elif self._backend == "sentence-transformers":
            return self._embed_sentence_transformers(texts)
        elif self._backend == "ollama":
            return self._embed_ollama(texts)
        else:
            raise RuntimeError(f"Unknown backend: {self._backend}")

    def _embed_openvino_direct(self, texts: List[str]) -> np.ndarray:
        """Embed using direct OpenVINO on NPU (batch=1 sequential)."""
        all_embeddings = []

        for text in texts:
            inputs = self._tokenizer(
                text,
                padding="max_length",
                truncation=True,
                max_length=self._max_length,
                return_tensors="np",
            )

            result = self._compiled_model({
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.int64),
                "token_type_ids": inputs.get(
                    "token_type_ids",
                    np.zeros_like(inputs["input_ids"])
                ).astype(np.int64),
            })

            hidden_states = result[self._compiled_model.output(0)]
            attention_mask = inputs["attention_mask"]

            # Mean pooling
            mask_expanded = np.expand_dims(attention_mask, axis=-1)
            sum_embeddings = np.sum(hidden_states * mask_expanded, axis=1)
            sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
            embedding = (sum_embeddings / sum_mask)[0]

            all_embeddings.append(embedding)

        return np.array(all_embeddings)

    def _embed_sentence_transformers(self, texts: List[str]) -> np.ndarray:
        """Embed using sentence-transformers backend."""
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings

    def _ollama_base_url(self) -> str:
        base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        if base.endswith("/api/generate"):
            base = base[: -len("/api/generate")]
        return base

    def _ollama_embed(self, texts: List[str]) -> np.ndarray:
        base = self._ollama_base_url()
        embeddings = []
        for text in texts:
            payload = json.dumps({"model": self.ollama_model, "prompt": text}).encode("utf-8")
            req = request.Request(
                f"{base}/api/embeddings",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            emb = data.get("embedding")
            if not emb:
                raise RuntimeError("Ollama embedding response missing 'embedding'")
            embeddings.append(emb)
        return np.array(embeddings, dtype=np.float32)

    def _embed_ollama(self, texts: List[str]) -> np.ndarray:
        """Embed using Ollama /api/embeddings."""
        return self._ollama_embed(texts)

    @property
    def embedding_dim(self) -> int:
        """Return embedding dimension (384 for MiniLM-L6-v2)."""
        return 384

    @property
    def backend_info(self) -> dict:
        """Return information about the loaded backend."""
        return {
            "backend": self._backend,
            "device": self.device,
            "requested_device": self.requested_device,
            "model_loaded": self._backend is not None,
            "max_length": self._max_length if self._backend == "openvino-direct" else 512,
        }


class NPUClassifier:
    """
    Fast text classification on NPU.

    Use for intent routing - faster than LLM-based routing.
    """

    def __init__(self, device: str = "NPU"):
        self.device = device if has_npu() else "CPU"
        self._model = None
        self._tokenizer = None
        self._labels = []

    def load_model(
        self,
        model_id: str = "typeform/distilbert-base-uncased-mnli",
        labels: Optional[List[str]] = None,
    ):
        """Load classification model."""
        try:
            from optimum.intel import OVModelForSequenceClassification
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(model_id)
            self._model = OVModelForSequenceClassification.from_pretrained(
                model_id,
                export=True,
                device=self.device,
            )
            self._labels = labels or []
            logger.info(f"Loaded classifier on {self.device}")
            return True
        except ImportError:
            logger.error("Install: pip install optimum[openvino]")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def classify(self, text: str, candidate_labels: Optional[List[str]] = None) -> Tuple[str, float]:
        """
        Classify text into one of the candidate labels.

        Returns (label, confidence).
        """
        if self._model is None:
            raise RuntimeError("Model not loaded")

        labels = candidate_labels or self._labels
        if not labels:
            raise ValueError("No labels provided")

        # Zero-shot classification via NLI
        results = []
        for label in labels:
            inputs = self._tokenizer(
                text,
                label,
                truncation=True,
                return_tensors="pt",
            )
            outputs = self._model(**inputs)
            # entailment score (label index 2 for MNLI)
            scores = outputs.logits.softmax(dim=-1).numpy()[0]
            entailment = scores[2] if len(scores) > 2 else scores[1]
            results.append((label, float(entailment)))

        # Return highest scoring label
        results.sort(key=lambda x: x[1], reverse=True)
        return results[0]


# Quick test function
def test_npu():
    """Quick NPU availability test."""
    devices = get_available_devices()
    print(f"OpenVINO devices: {devices}")

    if has_npu():
        info = get_npu_info()
        print(f"NPU info: {info}")

        # Test embeddings
        print("\nTesting NPU embeddings...")
        embedder = NPUEmbedder(device="NPU")
        if embedder.load_model():
            import time
            texts = ["Hello world", "Test embedding", "Another test"]
            start = time.perf_counter()
            vecs = embedder.embed(texts)
            elapsed = time.perf_counter() - start
            print(f"Backend: {embedder.backend_info}")
            print(f"Embedded {len(texts)} texts in {elapsed*1000:.1f}ms")
            print(f"Shape: {vecs.shape}")
        return True
    else:
        print("NPU not available")
        return False


if __name__ == "__main__":
    test_npu()
