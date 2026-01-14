"""RSA Supervisor: manages worker lifecycle with fast kill and panic."""

from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STATUS_PATH = ROOT / "reflexes" / "governance" / "status.json"


def _write_status(status: str, **extras: object) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": status}
    payload.update(extras)
    STATUS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_status() -> str:
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8")).get("status", "RUNNING")
    except Exception:
        return "RUNNING"


def run_supervisor() -> None:
    _write_status("RUNNING")

    from core.worker import start_worker_session

    worker = Process(target=start_worker_session, args=())
    worker.start()
    _write_status("RUNNING", worker_pid=worker.pid, worker_alive=True)

    try:
        while worker.is_alive():
            status = _read_status()

            if status == "PAUSED":
                time.sleep(0.1)
                continue

            if status == "KILL":
                worker.terminate()
                worker.join(timeout=1)
                if worker.is_alive():
                    worker.kill()
                _write_status("KILLED", worker_pid=worker.pid, worker_alive=False)
                sys.exit(0)

            if status == "PANIC":
                worker.kill()
                _write_status("PANIC", worker_pid=worker.pid, worker_alive=False)
                sys.exit(1)

            time.sleep(0.1)

        exit_code = worker.exitcode or 0
        current_status = _read_status()
        if current_status == "PAUSED":
            final_status = "PAUSED"
        else:
            final_status = "DONE" if exit_code == 0 else "CRASHED"
        _write_status(final_status, worker_pid=worker.pid, worker_alive=False)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        worker.terminate()
        worker.join(timeout=1)
        _write_status("INTERRUPTED", worker_pid=worker.pid, worker_alive=False)
        sys.exit(1)


if __name__ == "__main__":
    run_supervisor()
