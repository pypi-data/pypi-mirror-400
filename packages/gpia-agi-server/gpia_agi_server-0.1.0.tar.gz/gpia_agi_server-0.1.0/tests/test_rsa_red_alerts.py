import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "reflexes" / "governance" / "status.json"
LEDGER = ROOT / "memory" / "agent_state_v1" / "ledger.json"
WAL = ROOT / "memory" / "agent_state_v1" / "ledger.wal"


def _write_status(status: str) -> None:
    STATUS.write_text(json.dumps({"status": status}, indent=2), encoding="utf-8")


def _read_status() -> dict:
    return json.loads(STATUS.read_text(encoding="utf-8"))


def _start_supervisor(env: dict) -> subprocess.Popen:
    cmd = [sys.executable, str(ROOT / "core" / "executive_loop.py")]
    return subprocess.Popen(cmd, cwd=ROOT, env=env)


def test_pull_the_plug():
    _write_status("RUNNING")
    env = os.environ.copy()
    env["RSA_TEST_MODE"] = "1"
    env["RSA_STEP_SLEEP"] = "10"
    proc = _start_supervisor(env)

    deadline = time.time() + 3
    while time.time() < deadline:
        status = _read_status()
        if status.get("worker_pid"):
            break
        time.sleep(0.1)

    _write_status("KILL")
    proc.wait(timeout=3)
    assert proc.returncode == 0
    status = _read_status()
    assert status.get("status") == "KILLED"
    assert status.get("worker_alive") is False


def test_amnesia_hydration():
    _write_status("RUNNING")
    if WAL.exists():
        WAL.unlink()
    initial_state = json.loads(LEDGER.read_text(encoding="utf-8"))
    start_step = initial_state.get("step_index", 0)

    env = os.environ.copy()
    env["RSA_STEP_SLEEP"] = "1"
    env["RSA_CRASH_AFTER_WAL"] = "1"
    proc = _start_supervisor(env)
    proc.wait(timeout=5)

    env.pop("RSA_CRASH_AFTER_WAL", None)
    proc = _start_supervisor(env)
    time.sleep(2)
    _write_status("KILL")
    proc.wait(timeout=3)

    state = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert state.get("step_index", 0) >= start_step


def test_insanity_entropy():
    _write_status("RUNNING")
    env = os.environ.copy()
    env["RSA_FORCE_ACTION"] = "1"
    env["RSA_FORCE_ACTION_NAME"] = "READ"
    env["RSA_FORCE_TARGET"] = "file.txt"
    env["RSA_STEP_SLEEP"] = "1"
    proc = _start_supervisor(env)
    deadline = time.time() + 6
    while time.time() < deadline:
        status = _read_status()
        if status.get("status") == "PAUSED":
            break
        time.sleep(0.2)

    proc.wait(timeout=3)
    status = _read_status()
    assert status.get("status") == "PAUSED"
