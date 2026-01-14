import argparse
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
ROLE_MAP = {
    "Professor": "CTO",
    "Alpha": "CIO",
    "Gemma": "COO",
    "Executive": "EXECUTIVE",
}


def ensure_tokens() -> Dict[str, str]:
    bus_token = os.environ.get("BUS_TOKEN") or secrets.token_hex(32)
    agent_secret = os.environ.get("AGENT_SHARED_SECRET") or secrets.token_hex(32)
    os.environ["BUS_TOKEN"] = bus_token
    os.environ["AGENT_SHARED_SECRET"] = agent_secret
    return {"BUS_TOKEN": bus_token, "AGENT_SHARED_SECRET": agent_secret}


def wait_health(url: str, label: str, token: str, retries: int = 30, delay_s: float = 1.0) -> None:
    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                return
        except Exception as exc:
            last_exc = exc
        time.sleep(delay_s)
    raise RuntimeError(f"{label} not healthy: {last_exc}")


def load_configs() -> tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    agents_cfg = yaml.safe_load((REPO_ROOT / "configs" / "agents.yaml").read_text(encoding="utf-8"))
    models_cfg = yaml.safe_load((REPO_ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))
    return agents_cfg, models_cfg


def spawn_agent(role: str, agents_cfg: dict, models_cfg: dict, env: Dict[str, str], processes: List[subprocess.Popen[bytes]]) -> None:
    info = agents_cfg["agents"][role]
    model_cfg = models_cfg["models"][info["model"]]
    child_env = env.copy()
    child_env.update(
        {
            "ROLE": role,
            "PORT": str(info["port"]),
            "PROMPT_FILE": str(info["prompt"]),
            "MODEL_KIND": model_cfg["kind"],
            "MODEL_ENDPOINT": model_cfg["endpoint"],
            "MODEL_NAME": model_cfg["model"],
        }
    )
    p = subprocess.Popen([sys.executable, "agent_server.py"], cwd=REPO_ROOT, env=child_env)
    processes.append(p)
    wait_health(
        f"http://127.0.0.1:{info['port']}/health",
        role,
        env.get("AGENT_SHARED_SECRET", ""),
    )


def run_benchmark(env: Dict[str, str], scenario: str) -> None:
    bench_env = env.copy()
    bench_env["USE_ORCHESTRATOR"] = "1"
    subprocess.run(
        [sys.executable, "benchmark_suite.py", "--scenario", scenario],
        cwd=REPO_ROOT,
        env=bench_env,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Executive Triangle Runner")
    parser.add_argument("--scenario", default="The System Architect")
    parser.add_argument("--with-bus", action="store_true", help="Start bus server (requires Redis)")
    args = parser.parse_args()

    tokens = ensure_tokens()
    env = os.environ.copy()
    env.update(tokens)

    agents_cfg, models_cfg = load_configs()

    processes: List[subprocess.Popen[bytes]] = []
    try:
        if args.with_bus:
            p = subprocess.Popen([sys.executable, "bus_server.py"], cwd=REPO_ROOT, env=env)
            processes.append(p)
        for speaker, role in ROLE_MAP.items():
            spawn_agent(role, agents_cfg, models_cfg, env, processes)
        run_benchmark(env, args.scenario)
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    main()
