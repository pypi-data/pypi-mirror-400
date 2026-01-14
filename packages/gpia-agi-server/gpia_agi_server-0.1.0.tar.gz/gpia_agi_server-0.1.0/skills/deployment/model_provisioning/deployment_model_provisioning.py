"""
Model Provisioning (Ollama create/run)

Writes Modelfile artifacts, builds models, and verifies health.
"""

import subprocess
from pathlib import Path
from typing import Dict


class ModelProvisioning:
    def write_modelfile_artifact(self, path: str, content: str) -> str:
        Path(path).write_text(content, encoding="utf-8")
        return path

    def execute_build_command(self, model_name: str, modelfile: str) -> subprocess.CompletedProcess:
        return subprocess.run(["ollama", "create", model_name, "-f", modelfile], capture_output=True, text=True)

    def verify_model_health(self, model_name: str) -> Dict[str, str]:
        try:
            import requests
            resp = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={"model": model_name, "prompt": "ping"},
                timeout=30,
            )
            ok = resp.status_code == 200
            return {"ok": ok, "status": resp.status_code, "body": resp.text[:500]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
