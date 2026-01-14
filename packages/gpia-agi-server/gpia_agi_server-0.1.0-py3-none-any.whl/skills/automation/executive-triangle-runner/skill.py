from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from skills.base import Skill, SkillCategory, SkillContext, SkillMetadata, SkillResult


class ExecutiveTriangleRunnerSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="automation/executive-triangle-runner",
            name="Executive Triangle Runner",
            description=(
                "Boot minimal agent servers (Professor, Alpha, Executive, Gemma) with the bus and run the "
                "System Architect Executive Triangle benchmark to verify Executive breaks analysis paralysis."
            ),
            category=SkillCategory.AUTOMATION,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "scenario": {"type": "string"},
            },
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "report_path": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        repo_root = Path(__file__).resolve().parents[3]
        script = repo_root / "skills" / "automation" / "executive-triangle-runner" / "scripts" / "run_executive_triangle.py"
        if not script.exists():
            return SkillResult(
                success=False,
                output=None,
                error="run_executive_triangle.py not found",
                skill_id=self.metadata().id,
            )

        args = [sys.executable, str(script)]
        scenario = input_data.get("scenario")
        if scenario:
            args += ["--scenario", str(scenario)]

        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as exc:
            return SkillResult(
                success=False,
                output=None,
                error=f"runner failed: {exc}",
                skill_id=self.metadata().id,
            )

        report_path = repo_root / "runs" / "benchmark_summary.txt"
        return SkillResult(
            success=True,
            output={"report_path": str(report_path)},
            skill_id=self.metadata().id,
        )


__all__ = ["ExecutiveTriangleRunnerSkill"]
