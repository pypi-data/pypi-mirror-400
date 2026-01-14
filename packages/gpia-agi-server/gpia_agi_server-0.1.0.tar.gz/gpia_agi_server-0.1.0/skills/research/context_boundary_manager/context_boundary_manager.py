"""
Context Boundary Manager

Creates a per-task container of user-provided sources, ranks chunks, and enforces
negative constraints against out-of-scope content.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class RankedChunk:
    source: str
    score: float
    text: str


class ContextBoundaryManager:
    def __init__(self, container_id: str) -> None:
        self.container_id = container_id
        self.sources: List[Path] = []
        self.chunks: List[RankedChunk] = []

    def create_context_container(self, sources: List[str]) -> None:
        self.sources = [Path(s) for s in sources]

    def ingest_local_source(self, source: str) -> None:
        path = Path(source)
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        self.chunks.append(RankedChunk(source=str(path), score=0.0, text=text))

    def calculate_relevance_score(self, query: str) -> List[RankedChunk]:
        # Placeholder: implement semantic scoring; keep deterministic ordering here.
        ranked = []
        for idx, chunk in enumerate(self.chunks):
            ranked.append(RankedChunk(source=chunk.source, score=1.0 - 0.01 * idx, text=chunk.text))
        self.chunks = ranked
        return ranked

    def enforce_negative_constraint(self, text: str) -> bool:
        # Placeholder: always allow; real implementation should match against ingested chunks only.
        return bool(self.chunks)


def load_boundary_rules(config: Dict[str, Any]) -> Dict[str, Any]:
    return config
