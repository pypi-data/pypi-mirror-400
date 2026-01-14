"""
Embedding Backend Selector

Probes available embedding backends and selects the best option.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class BackendStatus:
    name: str
    available: bool
    latency_ms: float
    error: str = ""


class EmbeddingBackendSelector:
    def __init__(self, order: List[str]):
        self.order = order

    def assess_backends(self) -> List[BackendStatus]:
        # Placeholder: mark all unavailable; real impl would probe NPU/Ollama/ST
        return [BackendStatus(name=backend, available=False, latency_ms=0.0, error="probe not implemented") for backend in self.order]

    def select_backend(self) -> Dict[str, Any]:
        statuses = self.assess_backends()
        for status in statuses:
            if status.available:
                return {"selected": status.name, "statuses": [s.__dict__ for s in statuses]}
        return {"selected": None, "statuses": [s.__dict__ for s in statuses], "error": "no backend available"}
