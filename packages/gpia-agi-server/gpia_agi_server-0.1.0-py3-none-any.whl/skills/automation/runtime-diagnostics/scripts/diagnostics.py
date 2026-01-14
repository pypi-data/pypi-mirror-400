from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _run_cmd(cmd: list[str], timeout: int, cwd: Path) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()
    except Exception as exc:
        return False, str(exc)


def _run_ps(command: str, timeout: int, cwd: Path) -> Tuple[bool, str]:
    return _run_cmd(["powershell", "-Command", command], timeout, cwd)


def _try_benchmark(runs: int) -> Dict[str, Any]:
    try:
        from skills.loader import SkillLoader
        from skills.registry import get_registry
        from skills.base import SkillContext

        loader = SkillLoader()
        loader.scan_all(lazy=False)
        registry = get_registry()
        bench = registry.get_skill("system/benchmark")
        if not bench:
            return {"error": "system/benchmark skill not found"}
        result = bench.execute(
            {
                "prompt": "Benchmark response. Return one short sentence.",
                "runs": runs,
                "max_tokens": 128,
                "temperature": 0.3,
            },
            SkillContext(agent_role="diagnostics"),
        )
        return result.output if result.success else {"error": result.error}
    except Exception as exc:
        return {"error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    repo_root = _repo_root()

    ok, cpu_name = _run_ps(
        "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name",
        args.timeout,
        repo_root,
    )
    if not ok:
        cpu_name = cpu_name or "cpu query failed"

    ok, memory_raw = _run_ps(
        "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json",
        args.timeout,
        repo_root,
    )
    if not ok:
        memory_raw = memory_raw or "memory query failed"

    ok, gpu_info = _run_cmd(
        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used", "--format=csv,noheader"],
        args.timeout,
        repo_root,
    )
    if not ok:
        gpu_info = gpu_info or "gpu query failed"

    try:
        from core.npu_utils import has_npu

        npu_info = {"available": bool(has_npu())}
    except Exception as exc:
        npu_info = {"error": str(exc)}

    ok, docker_ps = _run_cmd(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        args.timeout,
        repo_root,
    )
    ok, docker_volumes = _run_cmd(
        ["docker", "volume", "ls", "--format", "{{.Name}}"],
        args.timeout,
        repo_root,
    )

    ok, k8s_context = _run_cmd(
        ["kubectl", "config", "current-context"],
        args.timeout,
        repo_root,
    )
    ok, k8s_nodes = _run_cmd(
        ["kubectl", "get", "nodes", "-o", "wide", "--request-timeout=10s"],
        args.timeout,
        repo_root,
    )

    summary = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": _try_benchmark(args.runs),
        "cpu": cpu_name,
        "memory_raw": memory_raw,
        "gpu": gpu_info,
        "npu": npu_info,
        "docker": {
            "containers": docker_ps,
            "volumes": docker_volumes,
        },
        "kubernetes": {
            "context": k8s_context,
            "nodes": k8s_nodes,
        },
    }

    print(json.dumps(summary, indent=2))

    try:
        from skills.conscience.memory.skill import MemorySkill
        from skills.base import SkillContext

        memory = MemorySkill()
        content = (
            "Runtime diagnostics completed. "
            f"CPU: {cpu_name}. GPU: {gpu_info}. NPU: {npu_info}."
        )
        memory.execute(
            {
                "capability": "experience",
                "content": content,
                "memory_type": "semantic",
                "importance": 0.7,
                "context": summary,
            },
            SkillContext(agent_role="diagnostics"),
        )
    except Exception as exc:
        print(f"Memory update failed: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
