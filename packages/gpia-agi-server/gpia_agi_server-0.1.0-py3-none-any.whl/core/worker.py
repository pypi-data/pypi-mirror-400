"""RSA Worker: WAL-backed ledger, entropy guard, and optional GPIA execution."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


LEDGER_DIR = ROOT / "memory" / "agent_state_v1"
LEDGER_FILE = LEDGER_DIR / "ledger.json"
WAL_FILE = LEDGER_DIR / "ledger.wal"
JOURNAL_FILE = LEDGER_DIR / "journal.md"
QUEUE_FILE = LEDGER_DIR / "queue.json"
STATUS_PATH = ROOT / "reflexes" / "governance" / "status.json"
QUEUE_LOCK = LEDGER_DIR / "queue.json.lock"


class EntropyError(RuntimeError):
    """Raised when action signature repeats 3 times."""


def _read_status() -> str:
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8")).get("status", "RUNNING")
    except Exception:
        return "RUNNING"


def _write_status(status: str) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps({"status": status}, indent=2), encoding="utf-8")


def _ensure_files() -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_FILE.exists():
        LEDGER_FILE.write_text(json.dumps({
            "agent_id": "gpia",
            "session_id": "default",
            "step_index": 0,
            "action_hashes": [],
            "working_memory": {},
            "current_goal_id": None,
            "cost_tally": 0,
        }, indent=2), encoding="utf-8")
    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.write_text("# RSA Journal\n", encoding="utf-8")
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text("[]", encoding="utf-8")


def _load_state() -> dict:
    if WAL_FILE.exists():
        WAL_FILE.replace(LEDGER_FILE)
    return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))


def _write_wal(state: dict) -> None:
    WAL_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _commit_state(state: dict) -> None:
    _write_wal(state)
    WAL_FILE.replace(LEDGER_FILE)


def _append_journal(entry: str) -> None:
    with JOURNAL_FILE.open("a", encoding="utf-8") as handle:
        handle.write(entry + "\n")


def _next_task() -> str | None:
    queue = _lock_and_read_queue()
    if not queue:
        return None
    task = queue[0]
    return task


def _queue_lock(timeout: float = 2.0, poll: float = 0.05):
    """Acquire a simple lock file for queue access."""
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


def _lock_and_read_queue() -> list:
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


def _pop_and_commit_task(task_id: str) -> None:
    fd = _queue_lock()
    if fd is None:
        return
    try:
        content = QUEUE_FILE.read_text(encoding="utf-8")
        current_queue = json.loads(content) if content.strip() else []
        new_queue = [t for t in current_queue if str(_task_id(t)) != task_id]
        tmp_path = QUEUE_FILE.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(new_queue, indent=2), encoding="utf-8")
        tmp_path.replace(QUEUE_FILE)
    finally:
        _queue_unlock(fd)


def _task_id(task_item) -> str:
    if isinstance(task_item, dict) and "id" in task_item:
        return str(task_item["id"])
    if isinstance(task_item, dict):
        return hashlib.sha256(json.dumps(task_item, sort_keys=True).encode("utf-8")).hexdigest()[:8]
    return hashlib.sha256(str(task_item).encode("utf-8")).hexdigest()[:8]


def _task_text(task_item) -> str:
    if isinstance(task_item, dict):
        return str(task_item.get("task") or task_item.get("content") or "")
    return str(task_item)


def _action_signature(action: str, target: str) -> str:
    return hashlib.sha256(f"{action}:{target}".encode("utf-8")).hexdigest()


def _check_entropy(state: dict, signature: str) -> None:
    history = state.get("action_hashes", [])
    history.append(signature)
    state["action_hashes"] = history[-10:]
    if len(history) >= 3 and history[-1] == history[-2] == history[-3]:
        raise EntropyError("Entropy collapse detected")


def _load_recency(limit: int = 5) -> str:
    if not JOURNAL_FILE.exists():
        return ""
    lines = JOURNAL_FILE.read_text(encoding="utf-8").splitlines()
    recency = [line for line in lines if line.strip() and not line.startswith("#")]
    return "\n".join(recency[-limit:])


def start_worker_session() -> None:
    _ensure_files()
    state = _load_state()
    crash_after_wal = os.getenv("RSA_CRASH_AFTER_WAL") == "1"
    forced_action = os.getenv("RSA_FORCE_ACTION") == "1"
    forced_action_name = os.getenv("RSA_FORCE_ACTION_NAME", "READ")
    forced_target = os.getenv("RSA_FORCE_TARGET", "file.txt")
    sleep_seconds = int(os.getenv("RSA_STEP_SLEEP", "1"))
    from gpia import GPIA
    gpia_agent = GPIA(verbose=False)

    while True:
        if _read_status() == "PAUSED":
            time.sleep(0.2)
            continue

        task_item = _next_task()
        task_id = _task_id(task_item) if task_item is not None else None
        task_text = _task_text(task_item) if task_item is not None else ""
        action = forced_action_name if forced_action else "TASK"
        target = forced_target if forced_action else (task_id or "idle")

        try:
            signature = _action_signature(action, target)
            _check_entropy(state, signature)
        except EntropyError:
            _write_status("PAUSED")
            _commit_state(state)
            return

        recency = _load_recency()

        if task_text and not forced_action:
            gpia_agent.run(task_text, context={
                "recency": recency,
                "step_index": state.get("step_index", 0),
            })
            _pop_and_commit_task(str(task_id))
        else:
            time.sleep(sleep_seconds)

        state["step_index"] = state.get("step_index", 0) + 1
        state["last_action"] = {
            "action": action,
            "target": target,
            "recency": recency,
            "task_id": task_id,
        }

        if crash_after_wal and not state.get("crash_injected"):
            state["crash_injected"] = True
            _write_wal(state)
            os._exit(1)

        _commit_state(state)
        _append_journal(f"- step {state['step_index']}: {action} {target}")

        if not task_text and not forced_action:
            time.sleep(0.5)
