"""DAG planner with file-based approval gate."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from agents.model_router import query_reasoning


PLANNER_PROMPT = """
ROLE
You are the Strategic Planner.
Decompose a vague request into a strict DAG of atomic steps.

CONSTRAINTS
1) No recursive planning steps.
2) Max depth 1.
3) Each step maps to a single action.

OUTPUT FORMAT (JSON ONLY):
{
  "goal_summary": "One sentence summary of the objective",
  "dag": [
    {"id": "step_1", "instruction": "...", "dependencies": []}
  ]
}
""".strip()


class DagPlanner:
    """Generates a DAG and manages approval gate file."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.approval_path = self.root_dir / "runs" / "plan_approve.json"
        self.approval_path.parent.mkdir(parents=True, exist_ok=True)

    def _task_hash(self, task: str) -> str:
        return hashlib.sha256(task.encode("utf-8")).hexdigest()

    def _static_plan(self, task: str) -> Optional[Dict[str, Any]]:
        lowered = task.lower()
        if "organize" in lowered and "downloads" in lowered:
            return {
                "goal_summary": "Organize downloads folder by file type.",
                "dag": [
                    {"id": "step_1", "instruction": "Scan Downloads folder for file extensions", "dependencies": []},
                    {"id": "step_2", "instruction": "Create subdirectories by file type", "dependencies": ["step_1"]},
                    {"id": "step_3", "instruction": "Move files into matching subdirectories", "dependencies": ["step_2"]},
                ],
            }
        return None

    def _generate_plan(self, task: str) -> Dict[str, Any]:
        static_plan = self._static_plan(task)
        if static_plan:
            return static_plan
        prompt = f"{PLANNER_PROMPT}\n\nUSER REQUEST:\n{task}"
        raw = query_reasoning(prompt, max_tokens=800, timeout=120)
        match = None
        try:
            match = json.loads(raw)
        except json.JSONDecodeError:
            brace = raw.find("{")
            if brace != -1:
                match = json.loads(raw[brace:raw.rfind("}") + 1])
        if not isinstance(match, dict):
            return {"goal_summary": task[:100], "dag": []}
        return match

    def create_or_load(self, task: str, max_attempts: int = 1) -> Dict[str, Any]:
        task_hash = self._task_hash(task)
        if self.approval_path.exists():
            data = json.loads(self.approval_path.read_text(encoding="utf-8"))
            if data.get("task_hash") == task_hash:
                return data

        plan = self._generate_plan(task)
        record = {
            "status": "PENDING_APPROVAL",
            "created_at": time.time(),
            "task": task,
            "task_hash": task_hash,
            "attempts": 1,
            "plan": plan,
        }
        self.approval_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record
