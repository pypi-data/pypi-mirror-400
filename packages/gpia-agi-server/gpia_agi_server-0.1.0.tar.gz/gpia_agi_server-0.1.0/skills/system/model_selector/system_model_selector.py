"""
Model Selector (Ollama Controller)

Selects base model and optional adapters based on registry and resource fit.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ModelCandidate:
    name: str
    size_gb: float
    kind: str
    quant: str
    adapter: str = ""


class SystemModelSelector:
    def __init__(self, registry: List[ModelCandidate]):
        self.registry = registry

    def evaluate_resource_fit(self, candidate: ModelCandidate, vram_gb: float) -> bool:
        return candidate.size_gb <= vram_gb

    def select_base_architecture(self, task_type: str, vram_gb: float) -> Dict[str, Any]:
        for c in self.registry:
            if self.evaluate_resource_fit(c, vram_gb):
                return {"selected": c.name, "quant": c.quant, "adapter": c.adapter}
        return {"selected": None, "error": "no fit"}
