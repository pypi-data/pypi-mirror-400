"""Context pager for MemGPT-style summary/recall stores with thrash guard."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextPager:
    """Manages summary_store vs recall_store and explicit retrieval."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        base = self.root_dir / "memory" / "agent_state_v1"
        self.summary_path = base / "summary_store.json"
        self.recall_path = base / "recall_store.json"
        self.state_path = base / "pager_state.json"
        self.base_path = base
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self) -> None:
        if not self.summary_path.exists():
            self.summary_path.write_text("[]", encoding="utf-8")
        if not self.recall_path.exists():
            self.recall_path.write_text("[]", encoding="utf-8")
        if not self.state_path.exists():
            self.state_path.write_text(json.dumps({
                "last_queries": [],
                "last_retrieval": None,
            }, indent=2), encoding="utf-8")

    def _load(self, path: Path) -> List[Dict[str, Any]]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self, path: Path, data: List[Dict[str, Any]]) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_state(self) -> Dict[str, Any]:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"last_queries": [], "last_retrieval": None}

    def _save_state(self, state: Dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self._save(self.summary_path, [])
        self._save(self.recall_path, [])
        self._save_state({"last_queries": [], "last_retrieval": None})

    def summarize_constraint(self, text: str) -> None:
        """Store a constraint summary into the summary store."""
        self.add_constraint(text)

    def record_turn(self, role: str, content: str, tags: Optional[List[str]] = None) -> None:
        store = self._load(self.recall_path)
        store.append({
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "tags": tags or [],
            "created_at": time.time(),
            "type": "recall",
        })
        self._save(self.recall_path, store)

    def add_constraint(self, text: str, origin_skill_id: str = "system") -> None:
        store = self._load(self.summary_path)
        rule = {}
        if text.strip().upper().startswith("BLOCK:"):
            rule["block_contains"] = text.split(":", 1)[1].strip()
        store.append({
            "id": str(uuid.uuid4()),
            "origin_skill_id": origin_skill_id,
            "content": text,
            "rule": rule,
            "created_at": time.time(),
            "type": "constraint",
        })
        self._save(self.summary_path, store)

    def get_constraints(self) -> List[Dict[str, Any]]:
        return [item for item in self._load(self.summary_path) if item.get("type") == "constraint"]

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def _format_constraints(self, constraints: List[Dict[str, Any]]) -> str:
        if not constraints:
            return ""
        lines = ["Constraints:"]
        for item in constraints:
            content = str(item.get("content", "")).strip()
            if content:
                lines.append(f"- {content}")
        return "\n".join(lines)

    def _format_recall(self, recalls: List[Dict[str, Any]]) -> str:
        if not recalls:
            return ""
        lines = ["Recall:"]
        for item in recalls:
            content = str(item.get("content", "")).strip()
            if content:
                lines.append(f"- {content}")
        return "\n".join(lines)

    def build_window(
        self,
        task: str,
        constraints: List[Dict[str, Any]],
        recalls: List[Dict[str, Any]],
        recency: str = "",
        max_tokens: int = 1200,
    ) -> Dict[str, Any]:
        top_constraints = self._format_constraints(constraints)
        bottom_constraints = top_constraints
        recall_block = self._format_recall(recalls)
        recency_block = recency.strip()

        total = self._estimate_tokens(top_constraints + bottom_constraints + task)
        body_sections: List[str] = []

        if recall_block:
            projected = total + self._estimate_tokens(recall_block)
            if projected <= max_tokens:
                body_sections.append(recall_block)
                total = projected

        if recency_block:
            projected = total + self._estimate_tokens(recency_block)
            if projected <= max_tokens:
                body_sections.append(recency_block)
                total = projected

        body = "\n\n".join(body_sections)

        return {
            "top": top_constraints,
            "bottom": bottom_constraints,
            "body": body,
            "tokens": total,
        }

    def retrieve(self, query: str, store: str = "summary", limit: int = 5) -> Dict[str, Any]:
        state = self._load_state()
        now = time.time()
        query_key = f"{store}:{query.lower().strip()}"

        recent = state.get("last_queries", [])
        recent.append({"query": query_key, "time": now})
        recent = recent[-5:]
        state["last_queries"] = recent

        repeats = [q for q in recent if q["query"] == query_key and (now - q["time"]) < 30]
        if len(repeats) >= 3:
            state["last_retrieval"] = {"query": query_key, "throttled": True, "time": now}
            self._save_state(state)
            return {"items": [], "throttled": True}

        if store == "summary":
            items = self._load(self.summary_path)
        else:
            items = self._load(self.recall_path)

        if query and store != "summary":
            filtered = [item for item in items if query.lower() in str(item.get("content", "")).lower()]
        else:
            filtered = items

        result = filtered[-limit:] if filtered else []
        state["last_retrieval"] = {"query": query_key, "throttled": False, "time": now}
        self._save_state(state)
        return {"items": result, "throttled": False}

    def check_constraints(self, task: str, constraints: List[Dict[str, Any]]) -> Optional[str]:
        lowered = task.lower()
        for constraint in constraints:
            rule = constraint.get("rule", {})
            token = rule.get("block_contains")
            if token and token.lower() in lowered:
                return token
        return None
