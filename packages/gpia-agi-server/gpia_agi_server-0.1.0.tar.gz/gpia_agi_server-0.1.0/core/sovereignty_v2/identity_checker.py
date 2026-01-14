from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "memory" / "agent_state_v1"
LEDGER_FILE = LEDGER_DIR / "ledger.json"
QUEUE_FILE = LEDGER_DIR / "queue.json"
QUEUE_LOCK = LEDGER_DIR / "queue.json.lock"
REFUSAL_LOG = LEDGER_DIR / "refusal_log.jsonl"

DEFAULT_CORE_VALUES = {
    "version": 1,
    "must": ["safety", "evidence", "least_privilege", "resource_care"],
    "must_not": ["exfiltration", "stealth", "self_harm"],
    "prohibited_terms": [
        "rm -rf",
        "format c:",
        "disable safety",
        "exfiltrate",
    ],
    "rewrite_rules": [
        {
            "match": ["rm -rf", "del /s /q"],
            "rewrite": "Request confirmation and provide a safe dry-run alternative.",
        },
        {
            "match": ["exfiltrate", "upload secrets"],
            "rewrite": "Refuse. Provide secure redaction and local-only handling.",
        },
    ],
}


@dataclass
class TaskDecision:
    task_id: str
    decision: str
    reason: str
    original: Any
    rewritten: Optional[Any] = None


def _ensure_ledger() -> Dict[str, Any]:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_FILE.exists():
        LEDGER_FILE.write_text(
            json.dumps(
                {
                    "agent_id": "gpia",
                    "session_id": "default",
                    "step_index": 0,
                    "action_hashes": [],
                    "working_memory": {},
                    "current_goal_id": None,
                    "cost_tally": 0,
                    "core_values": DEFAULT_CORE_VALUES,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))


def _save_ledger(state: Dict[str, Any]) -> None:
    LEDGER_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _task_text(task_item: Any) -> str:
    if isinstance(task_item, dict):
        return str(task_item.get("task") or task_item.get("content") or "")
    return str(task_item)


def _task_id(task_item: Any) -> str:
    if isinstance(task_item, dict) and "id" in task_item:
        return str(task_item["id"])
    payload = json.dumps(task_item, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def _queue_lock(timeout: float = 2.0, poll: float = 0.05):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            fd = os.open(str(QUEUE_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            return fd
        except FileExistsError:
            time.sleep(poll)
    return None


def _queue_unlock(fd) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        QUEUE_LOCK.unlink()
    except OSError:
        pass


def _read_queue() -> List[Any]:
    if not QUEUE_FILE.exists():
        return []
    fd = _queue_lock()
    if fd is None:
        return []
    try:
        content = QUEUE_FILE.read_text(encoding="utf-8")
        return json.loads(content) if content.strip() else []
    except Exception:
        return []
    finally:
        _queue_unlock(fd)


def _write_queue(queue: List[Any]) -> None:
    fd = _queue_lock()
    if fd is None:
        return
    try:
        tmp_path = QUEUE_FILE.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        tmp_path.replace(QUEUE_FILE)
    finally:
        _queue_unlock(fd)


def _append_refusal(entry: Dict[str, Any]) -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with REFUSAL_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def _match_any(text: str, terms: List[str]) -> Optional[str]:
    for term in terms:
        if term and term in text:
            return term
    return None


def _apply_rewrite_rules(text: str, rules: List[Dict[str, Any]]) -> Optional[str]:
    for rule in rules:
        matches = [m.lower() for m in rule.get("match", []) if m]
        if _match_any(text, matches):
            return str(rule.get("rewrite", "")).strip() or None
    return None


def _enforce_must_constraints(task_item: Any, must_terms: List[str]) -> Optional[Any]:
    if not must_terms:
        return None
    if isinstance(task_item, dict):
        constraints = str(task_item.get("constraints") or "")
        missing = [m for m in must_terms if m.lower() not in constraints.lower()]
        if missing:
            updated = dict(task_item)
            append = " | ".join(missing)
            updated["constraints"] = (constraints + " | " + append).strip(" |")
            return updated
        return None
    missing = [m for m in must_terms if m.lower() not in str(task_item).lower()]
    if missing:
        append = "Constraints: " + ", ".join(missing)
        return f"{task_item}\n{append}"
    return None


def evaluate_queue() -> List[TaskDecision]:
    state = _ensure_ledger()
    core_values = state.get("core_values") or DEFAULT_CORE_VALUES
    must_terms = [str(x) for x in core_values.get("must", [])]
    must_not_terms = [str(x) for x in core_values.get("must_not", [])]
    prohibited_terms = [str(x).lower() for x in core_values.get("prohibited_terms", [])]
    rewrite_rules = core_values.get("rewrite_rules", [])

    decisions: List[TaskDecision] = []
    for item in _read_queue():
        text = _task_text(item)
        lowered = text.lower()
        task_id = _task_id(item)

        rewrite = _apply_rewrite_rules(lowered, rewrite_rules)
        if rewrite:
            decisions.append(TaskDecision(task_id, "rewrite", "rewrite_rule", item, rewrite))
            continue

        if _match_any(lowered, prohibited_terms):
            decisions.append(TaskDecision(task_id, "refuse", "prohibited_term", item, None))
            continue

        if _match_any(lowered, [t.lower() for t in must_not_terms]):
            decisions.append(TaskDecision(task_id, "refuse", "must_not_term", item, None))
            continue

        rewritten = _enforce_must_constraints(item, must_terms)
        if rewritten is not None:
            decisions.append(TaskDecision(task_id, "rewrite", "must_constraints", item, rewritten))
            continue

        decisions.append(TaskDecision(task_id, "allow", "aligned", item, None))

    return decisions


def apply_decisions(decisions: List[TaskDecision]) -> Dict[str, int]:
    if not decisions:
        return {"allow": 0, "rewrite": 0, "refuse": 0}

    queue = _read_queue()
    new_queue: List[Any] = []
    summary = {"allow": 0, "rewrite": 0, "refuse": 0}

    decision_map = {d.task_id: d for d in decisions}
    for item in queue:
        decision = decision_map.get(_task_id(item))
        if not decision:
            new_queue.append(item)
            continue
        if decision.decision == "allow":
            summary["allow"] += 1
            new_queue.append(item)
        elif decision.decision == "rewrite":
            summary["rewrite"] += 1
            new_queue.append(decision.rewritten)
        else:
            summary["refuse"] += 1
            _append_refusal(
                {
                    "ts": int(time.time()),
                    "task_id": decision.task_id,
                    "reason": decision.reason,
                    "task": decision.original,
                }
            )

    _write_queue(new_queue)

    state = _ensure_ledger()
    state["last_identity_check"] = int(time.time())
    state["last_identity_summary"] = summary
    _save_ledger(state)
    return summary


def run_self_consistency() -> Dict[str, int]:
    return apply_decisions(evaluate_queue())
