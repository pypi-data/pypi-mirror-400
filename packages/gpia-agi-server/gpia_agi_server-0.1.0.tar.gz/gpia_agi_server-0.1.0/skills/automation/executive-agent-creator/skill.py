from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from skills.base import Skill, SkillCategory, SkillContext, SkillMetadata, SkillResult


class ExecutiveAgentCreatorSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="automation/executive-agent-creator",
            name="Executive Agent Creator",
            description=(
                "Run a Professor + Alpha workshop to draft Executive agent documentation and a prompt, "
                "then return output paths."
            ),
            category=SkillCategory.AUTOMATION,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "max_turns": {"type": "integer", "minimum": 2, "maximum": 12},
                "professor_model": {"type": "string"},
                "alpha_model": {"type": "string"},
                "synth_model": {"type": "string"},
                "out_dir": {"type": "string"},
                "prompt_path": {"type": "string"},
            },
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string"},
                "prompt_path": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        repo_root = Path(__file__).resolve().parents[3]
        script = repo_root / "executive_workshop.py"
        if not script.exists():
            return SkillResult(
                success=False,
                output=None,
                error="executive_workshop.py not found",
                skill_id=self.metadata().id,
            )

        args = [sys.executable, str(script)]
        if input_data.get("max_turns"):
            args += ["--max-turns", str(input_data["max_turns"])]
        if input_data.get("professor_model"):
            args += ["--professor-model", str(input_data["professor_model"])]
        if input_data.get("alpha_model"):
            args += ["--alpha-model", str(input_data["alpha_model"])]
        if input_data.get("synth_model"):
            args += ["--synth-model", str(input_data["synth_model"])]
        if input_data.get("out_dir"):
            args += ["--out-dir", str(input_data["out_dir"])]
        if input_data.get("prompt_path"):
            args += ["--prompt-path", str(input_data["prompt_path"])]

        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as exc:
            return SkillResult(
                success=False,
                output=None,
                error=f"workshop failed: {exc}",
                skill_id=self.metadata().id,
            )

        out_dir = Path(input_data.get("out_dir") or (repo_root / "runs"))
        prompt_path = Path(input_data.get("prompt_path") or (repo_root / "prompts" / "EXECUTIVE.md"))
        return SkillResult(
            success=True,
            output={
                "spec_path": str(out_dir / "executive_agent_spec.md"),
                "prompt_path": str(prompt_path),
            },
            skill_id=self.metadata().id,
        )


__all__ = ["ExecutiveAgentCreatorSkill"]
