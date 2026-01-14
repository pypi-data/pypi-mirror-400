from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.resonant_kernel.interface import TemporalFormalismContract

LOG_PATH = Path("logs") / "gpia_server_dense_state.jsonl"
MODEL_REGISTRY_PATH = Path("config") / "model_registry.json"


def log_dense_state(entry: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


@dataclass
class ModelArtifact:
    name: str
    path: Path
    format: str
    quantization: str
    context_size: int
    backend: str


class ModelRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self.artifacts: Dict[str, ModelArtifact] = {}
        self.load()

    def load(self) -> None:
        if not self.registry_path.exists():
            return
        payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        for model in payload.get("models", []):
            self.artifacts[model["name"]] = ModelArtifact(
                name=model["name"],
                path=Path(model["path"]),
                format=model["format"],
                quantization=model["quantization"],
                context_size=int(model["context_size"]),
                backend=model["backend"],
            )

    def list_models(self) -> Iterable[str]:
        return self.artifacts.keys()

    def get(self, name: str) -> Optional[ModelArtifact]:
        return self.artifacts.get(name)


@dataclass
class RequestPayload:
    session_id: str
    prompt: str
    max_tokens: int = 32
    temperature: float = 0.7
    stop_sequences: List[str] = field(default_factory=list)


class GPUAwareStage:
    def __init__(self) -> None:
        self.registry = ModelRegistry(MODEL_REGISTRY_PATH)
        self.contract = TemporalFormalismContract()

    def tokenize(self, text: str) -> List[str]:
        return text.strip().split()

    def forward_pass(self, tokens: List[str], artifact: ModelArtifact) -> List[float]:
        base = (len(tokens) + artifact.context_size) % artifact.context_size or 1
        return [base * 0.02 for _ in range(artifact.context_size)]

    def sample_token(self, logits: List[float], temperature: float) -> str:
        score = int(sum(logits) * temperature)
        return f"tok{score % 100}"

    def evolve_dense_state(self, tokens: List[str]) -> None:
        env_bias = self.contract.observe_telemetry(cpu=0.2, vram=0.1)
        self.contract.evolve_state([len(token) for token in tokens], env_bias)

    def infer(self, payload: RequestPayload, model_name: str) -> List[str]:
        artifact = self.registry.get(model_name)
        if not artifact:
            raise ValueError(f"Unknown model '{model_name}'")
        tokens = self.tokenize(payload.prompt)
        generated: List[str] = []
        for _ in range(payload.max_tokens):
            logits = self.forward_pass(tokens, artifact)
            token = self.sample_token(logits, payload.temperature)
            tokens.append(token)
            generated.append(token)
            self.evolve_dense_state(tokens)
            joined = " ".join(tokens)
            if any(stop in joined for stop in payload.stop_sequences):
                break
        self.log_state(payload, artifact, len(tokens))
        return generated

    def log_state(self, payload: RequestPayload, artifact: ModelArtifact, total_tokens: int) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": payload.session_id,
            "model": artifact.name,
            "resonance_hash": self.contract.current_state.tobytes().hex()[:16],
            "tokens": total_tokens,
            "prompt_snippet": payload.prompt[:64],
        }
        log_dense_state(entry)


class GPIA_Server:
    def __init__(self) -> None:
        self.stage = GPUAwareStage()

    def describe_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "context_size": self.stage.registry.get(name).context_size,
                "backend": self.stage.registry.get(name).backend,
            }
            for name in self.stage.registry.list_models()
            if self.stage.registry.get(name)
        ]

    def handle_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = RequestPayload(
            session_id=str(payload.get("session_id", "anon")),
            prompt=payload.get("prompt", ""),
            max_tokens=int(payload.get("max_tokens", 32)),
            temperature=float(payload.get("temperature", 0.7)),
            stop_sequences=payload.get("stop", []),
        )
        model = payload.get("model", "default")
        tokens = self.stage.infer(request, model)
        return {
            "session_id": request.session_id,
            "model": model,
            "tokens": tokens,
            "status": "ok",
        }

    def handle_models(self) -> Dict[str, Any]:
        return {"data": self.describe_models()}
