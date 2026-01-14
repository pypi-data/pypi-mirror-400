from __future__ import annotations

import json
from datetime import datetime
from importlib.util import find_spec
from typing import Any, Dict


def main() -> int:
    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "sentence_transformers_available": bool(find_spec("sentence_transformers")),
        "rebuild": None,
        "errors": [],
    }

    try:
        from skills.conscience.memory.skill import MemorySkill
        from skills.base import SkillContext

        memory = MemorySkill()

        rebuild_ok = memory.rebuild_mshr()
        summary["rebuild"] = {"success": rebuild_ok}

        try:
            stats = memory._mshr.get_stats() if memory._mshr else {}
            summary["rebuild"]["mshr_stats"] = stats
        except Exception as exc:
            summary["errors"].append(f"stats_error: {exc}")

        content = "Embedding repair attempted. "
        content += "Rebuild ok." if rebuild_ok else "Rebuild failed."

        memory.execute(
            {
                "capability": "experience",
                "content": content,
                "memory_type": "semantic",
                "importance": 0.8 if rebuild_ok else 0.9,
                "context": summary,
            },
            SkillContext(agent_role="embedding-repair"),
        )
    except Exception as exc:
        summary["errors"].append(str(exc))
        print(json.dumps(summary, indent=2))
        return 1

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
