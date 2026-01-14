"""Agent utilities for lightweight delegation and context retrieval."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from core import kb
from hnet.dynamic_chunker import DynamicChunker
from hnet.hierarchical_memory import HierarchicalMemory

AGENT_FUNCTIONS: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def last(n: int = 31) -> List[Dict[str, Any]]:
    return kb.last(n)


def ingest_hierarchical_text(
    text: str,
    summarizer: Callable[[str], str],
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 80,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    return kb.ingest_hierarchical_text(
        text,
        summarizer,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
        meta=meta,
    )


def _extract_text(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                for key in ("text", "content", "data"):
                    value = payload.get(key)
                    if value:
                        return str(value)
                return json.dumps(payload)
            return str(payload)
        except json.JSONDecodeError:
            return raw
    return str(raw)


def fetch_context(n: int = 5, query: str | None = None) -> str:
    entries = last(n)
    texts = [_extract_text(entry.get("data")) for entry in entries]
    merged = "\n".join([t for t in reversed(texts) if t])

    chunker = DynamicChunker()
    summary = ""
    if merged:
        summary = ingest_hierarchical_text(
            merged,
            lambda chunk: chunk,
            max_tokens=chunker.max_tokens,
            overlap_tokens=chunker.overlap_tokens,
        )

    retrieved: List[str] = []
    if query:
        memory = HierarchicalMemory(
            max_tokens=chunker.max_tokens,
            overlap_tokens=chunker.overlap_tokens,
        )
        retrieved = memory.search("kb", query, top_k=5)

    parts = []
    if summary:
        parts.append(summary)
    if retrieved:
        parts.append("\n".join(retrieved))
    return "\n".join(parts).strip()


def delegate(task_name: str, *, n: int = 5, query: str | None = None) -> Any:
    if task_name not in AGENT_FUNCTIONS:
        raise KeyError(f"Unknown task: {task_name}")
    context = {"summary": fetch_context(n=n, query=query)}
    return AGENT_FUNCTIONS[task_name](context)
