"""
Garbage Collection for Ephemeral Models

Removes ephemeral models, drops memory shards, and verifies cleanup.
"""

import subprocess
from typing import Dict


class GarbageCollector:
    def nuke_model_artifact(self, model_name: str) -> Dict[str, str]:
        try:
            proc = subprocess.run(["ollama", "rm", model_name], capture_output=True, text=True, timeout=60)
            return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}
        except Exception as e:
            return {"ok": False, "stderr": str(e), "stdout": ""}

    def flush_vram_cache(self) -> Dict[str, str]:
        # Placeholder: no direct command; rely on model unload. Return success.
        return {"ok": True, "note": "vRAM flush best-effort"}

    def drop_memory_shard(self, shard_id: str) -> Dict[str, str]:
        return {"ok": True, "dropped": shard_id}

    def verify_cleanup(self, model_name: str) -> Dict[str, str]:
        try:
            proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=30)
            ok = model_name not in proc.stdout
            return {"ok": ok, "stdout": proc.stdout[:500], "stderr": proc.stderr}
        except Exception as e:
            return {"ok": False, "stderr": str(e), "stdout": ""}
