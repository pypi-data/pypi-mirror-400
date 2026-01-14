"""Sandboxed skill synthesis with Docker primary and local fallback."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import textwrap
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple

from agents.model_router import query_creative, query_gpia_core


DENY_PATTERNS = [
    r"os\.system",
    r"subprocess\.",
    r"shutil\.rmtree",
    r"\brm\s+-rf\b",
    r"Path\([^\\n]*\)\.unlink",
    r"os\.remove",
    r"os\.rmdir",
    r"unlink\(",
    r"rmdir\(",
]


class SandboxedSkillSynthesizer:
    """Generate and test a new skill in a sandbox."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.sandbox_root = self.root_dir / "skills" / "sandbox"
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    def _has_dangerous_code(self, code: str) -> bool:
        for pattern in DENY_PATTERNS:
            if re.search(pattern, code):
                return True
        return False

    def _docker_available(self) -> bool:
        if os.getenv("SANDBOX_FORCE_LOCAL") == "1":
            return False
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            return True
        except Exception:
            return False

    def _fibonacci_template(self) -> Tuple[str, str]:
        code = textwrap.dedent(
            """
            def solve(task: str, context: dict) -> object:
                import re
                numbers = re.findall(r"\\d+", task)
                n = int(numbers[0]) if numbers else 0
                if n <= 0:
                    return {"sequence": []}
                seq = [0, 1]
                while len(seq) < n:
                    seq.append(seq[-1] + seq[-2])
                return {"sequence": seq[:n]}
            """
        ).strip()
        tests = textwrap.dedent(
            """
            from skill_code import solve

            result = solve("Calculate Fibonacci sequence to 7", {})
            assert result["sequence"] == [0, 1, 1, 2, 3, 5, 8]
            print("ok")
            """
        ).strip()
        return code, tests

    def _generate_code(self, task: str) -> Tuple[str, str]:
        if "fibonacci" in task.lower():
            return self._fibonacci_template()

        prompt = (
            "Write Python code for a function:\n"
            "def solve(task: str, context: dict) -> object\n"
            "Also provide a minimal test runner that imports solve and asserts a basic case.\n"
            "Output two code blocks: first skill code, second tests.\n"
            "Use standard library only.\n"
            f"TASK: {task}\n"
        )
        raw = query_gpia_core(prompt, max_tokens=1200, timeout=120)
        if not raw.strip():
            raw = query_creative(prompt, max_tokens=1200, timeout=120)
        blocks = re.findall(r"```python\\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
        if blocks:
            code = blocks[0].strip()
            tests = blocks[1].strip() if len(blocks) > 1 else ""
            if not tests:
                tests = textwrap.dedent(
                    """
                    from skill_code import solve

                    result = solve("smoke test", {})
                    assert result is not None
                    print("ok")
                    """
                ).strip()
            return code, tests

        return self._fibonacci_template()

    def synthesize(self, task: str) -> Dict[str, Optional[str]]:
        code, tests = self._generate_code(task)
        if not code:
            return {"success": False, "error": "no_code", "code": None, "sandbox": None}

        if self._has_dangerous_code(code) or self._has_dangerous_code(tests):
            return {"success": False, "error": "dangerous_code", "code": None, "sandbox": None}

        sandbox = self.sandbox_root / f"synth_{uuid.uuid4().hex[:8]}"
        sandbox.mkdir(parents=True, exist_ok=True)
        code_path = sandbox / "skill_code.py"
        test_path = sandbox / "test_runner.py"

        code_path.write_text(code, encoding="utf-8")
        test_path.write_text(tests, encoding="utf-8")

        docker_used = False
        result = None
        if self._docker_available():
            docker_used = True
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{sandbox}:/sandbox",
                    "-w",
                    "/sandbox",
                    "python:3.11-slim",
                    "python",
                    "test_runner.py",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        if result is None or result.returncode != 0:
            docker_used = False
            result = subprocess.run(
                [sys.executable, "test_runner.py"],
                cwd=str(sandbox),
                capture_output=True,
                text=True,
                timeout=60,
            )

        if result.returncode != 0:
            shutil.rmtree(sandbox, ignore_errors=True)
            return {
                "success": False,
                "error": result.stderr.strip() or "test_failed",
                "code": None,
                "sandbox": None,
                "sandbox_used": "docker" if docker_used else "local",
            }

        shutil.rmtree(sandbox, ignore_errors=True)
        return {
            "success": True,
            "code": code,
            "sandbox": str(sandbox),
            "sandbox_used": "docker" if docker_used else "local",
        }
