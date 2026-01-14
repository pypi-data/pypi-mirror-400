"""
Skill Smoke Bench

Performs import and minimal execution checks for skills.
"""

import importlib
from typing import List, Dict, Any


class SkillSmokeBench:
    def __init__(self, targets: List[str]):
        self.targets = targets

    def import_check(self) -> List[Dict[str, Any]]:
        results = []
        for target in self.targets:
            try:
                importlib.import_module(target)
                results.append({"target": target, "status": "ok"})
            except Exception as e:
                results.append({"target": target, "status": "fail", "error": str(e)})
        return results

    def run(self) -> Dict[str, Any]:
        imports = self.import_check()
        failures = [r for r in imports if r["status"] != "ok"]
        return {"imports": imports, "failures": failures}
