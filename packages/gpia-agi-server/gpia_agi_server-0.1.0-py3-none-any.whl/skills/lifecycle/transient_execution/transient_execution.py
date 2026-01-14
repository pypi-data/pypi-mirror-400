"""
Transient Execution

Hot-swap to an ephemeral model, run the task, capture the output.
"""

import subprocess
from typing import Dict


class TransientExecutor:
    def preload_ephemeral_model(self, model_name: str) -> None:
        # No-op placeholder; Ollama lazy-loads on first request.
        return None

    def execute_atomic_task(self, model_name: str, prompt: str) -> Dict[str, str]:
        try:
            proc = subprocess.run(
                ["ollama", "run", model_name],
                input=prompt.encode("utf-8"),
                capture_output=True,
                text=False,
                timeout=120,
            )
            return {
                "stdout": proc.stdout.decode("utf-8", errors="replace") if proc.stdout else "",
                "stderr": proc.stderr.decode("utf-8", errors="replace") if proc.stderr else "",
                "returncode": proc.returncode,
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}
