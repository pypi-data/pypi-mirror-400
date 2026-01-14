"""
Compile JIT Modelfile

Writes a Modelfile with frozen SYSTEM/TEMPLATE/PARAMETER and builds an ephemeral model.
"""

from pathlib import Path
import subprocess
from typing import Dict


class JITModelfileCompiler:
    def write_modelfile_artifact(self, path: str, base_model: str, system_text: str, template: str, params: Dict[str, str]) -> str:
        lines = [f"FROM {base_model}"]
        if system_text:
            lines.append(f'SYSTEM \"\"\"{system_text}\"\"\"')
        if template:
            lines.append(f'TEMPLATE \"\"\"{template}\"\"\"')
        for k, v in params.items():
            lines.append(f"PARAMETER {k} {v}")
        content = "\n".join(lines) + "\n"
        Path(path).write_text(content, encoding="utf-8")
        return path

    def build_ephemeral_model(self, model_name: str, modelfile_path: str) -> subprocess.CompletedProcess:
        return subprocess.run(["ollama", "create", model_name, "-f", modelfile_path], capture_output=True, text=True)
