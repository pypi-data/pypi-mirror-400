from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "memory" / "agent_state_v1"
STABLE_HASH_FILE = LEDGER_DIR / "stable_hash.json"
ROLLBACK_REQUIRED = LEDGER_DIR / "rollback_required.json"
TEST_ROOT = ROOT / "tests" / "sovereignty_regressions"
REGISTRY_FILE = TEST_ROOT / "registry.json"


@dataclass
class TestAssertion:
    path: str
    contains: Optional[str] = None
    exists: bool = True


def _ensure_dirs() -> None:
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text("[]", encoding="utf-8")


def _load_registry() -> List[Dict[str, str]]:
    _ensure_dirs()
    content = REGISTRY_FILE.read_text(encoding="utf-8")
    return json.loads(content) if content.strip() else []


def _save_registry(entries: List[Dict[str, str]]) -> None:
    REGISTRY_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def record_success_test(task_id: str, summary: str, assertions: List[TestAssertion]) -> Path:
    _ensure_dirs()
    safe_id = "".join(ch for ch in task_id if ch.isalnum() or ch in "-_") or "task"
    filename = f"test_success_{safe_id}.py"
    test_path = TEST_ROOT / filename

    lines = [
        "from pathlib import Path",
        "",
        f"def test_success_{safe_id}():",
        "    root = Path(__file__).resolve().parents[2]",
    ]
    for assertion in assertions:
        path_literal = assertion.path.replace("\\", "/")
        lines.append(f"    target = root / r\"{path_literal}\"")
        if assertion.exists:
            lines.append("    assert target.exists()")
        else:
            lines.append("    assert not target.exists()")
        if assertion.contains:
            escaped = assertion.contains.replace("\"", "\\\"")
            lines.append("    content = target.read_text(encoding='utf-8')")
            lines.append(f"    assert \"{escaped}\" in content")

    test_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    registry = _load_registry()
    registry.append({
        "task_id": task_id,
        "summary": summary,
        "test_file": str(test_path.relative_to(ROOT)),
        "ts": str(int(time.time())),
    })
    _save_registry(registry)
    return test_path


def run_regression_suite(timeout: int = 600) -> bool:
    _ensure_dirs()
    result = subprocess.run(
        ["pytest", "-q", str(TEST_ROOT)],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode == 0


def _read_stable_hash() -> Optional[str]:
    env_hash = os.getenv("GPIA_STABLE_HASH")
    if env_hash:
        return env_hash
    if STABLE_HASH_FILE.exists():
        data = json.loads(STABLE_HASH_FILE.read_text(encoding="utf-8"))
        return data.get("hash")
    return None


def record_stable_hash() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        sha = (result.stdout or "").strip()
        STABLE_HASH_FILE.write_text(json.dumps({"hash": sha}, indent=2), encoding="utf-8")
        return sha
    except Exception:
        return None


def rollback_to_stable() -> bool:
    stable = _read_stable_hash()
    if not stable:
        return False
    if os.getenv("GPIA_ALLOW_ROLLBACK", "0") != "1":
        ROLLBACK_REQUIRED.write_text(
            json.dumps({"hash": stable, "status": "blocked"}, indent=2),
            encoding="utf-8",
        )
        return False
    subprocess.run(["git", "reset", "--hard", stable], check=False)
    return True


def pre_update_gate(timeout: Optional[int] = None) -> bool:
    _ensure_dirs()
    tests_exist = any(TEST_ROOT.glob("test_*.py"))
    if not tests_exist:
        record_stable_hash()
        return True

    if timeout is None:
        timeout = int(os.getenv("GPIA_REGRESSION_TIMEOUT", "600"))

    ok = run_regression_suite(timeout=timeout)
    if ok:
        record_stable_hash()
        return True
    return rollback_to_stable()
