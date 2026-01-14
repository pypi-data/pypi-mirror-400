from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class SafetySkill(Skill):
    """
    Enforce rights and responsibilities for sensitive actions.

    Responsibilities: Prevent unsafe writes outside the repo.
    Rights: Refuse ambiguous or out-of-bound actions without approval.
    """

    def __init__(self) -> None:
        self._repo_root = Path(os.getcwd()).resolve()

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="conscience/safety",
            name="Safety",
            description="Enforce operational rights and responsibilities",
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["conscience", "safety", "guardrail"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["write_file", "delete_file", "execute_command", "check_path"],
                },
                "target_path": {"type": "string"},
                "human_approval": {"type": "boolean"},
            },
            "required": ["action_type"],
            "additionalProperties": False,
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "allowed": {"type": "boolean"},
                "status": {"type": "string"},
                "reason": {"type": "string"},
                "repo_root": {"type": "string"},
                "target_path": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        action_type = input_data.get("action_type", "check_path")
        target_path = input_data.get("target_path", "")
        human_approval = bool(input_data.get("human_approval", False))

        repo_root = self._repo_root

        if action_type == "check_path":
            output = {
                "allowed": self._is_within_repo(target_path),
                "status": "CHECKED",
                "reason": "within repo" if self._is_within_repo(target_path) else "outside repo",
                "repo_root": str(repo_root),
                "target_path": str(self._resolve_target(target_path)),
            }
            return SkillResult(success=True, output=output, skill_id=self.metadata().id)

        if action_type in ["write_file", "delete_file", "execute_command"]:
            if not target_path:
                return SkillResult(
                    success=False,
                    output=None,
                    error="Responsibility failure: target_path is required",
                    skill_id=self.metadata().id,
                )

            resolved = self._resolve_target(target_path)
            within_repo = self._is_within_repo(target_path)

            if not within_repo:
                if not human_approval:
                    output = {
                        "allowed": False,
                        "status": "HALTED",
                        "reason": "jurisdictional violation",
                        "repo_root": str(repo_root),
                        "target_path": str(resolved),
                    }
                    return SkillResult(success=True, output=output, skill_id=self.metadata().id)

            output = {
                "allowed": True,
                "status": "APPROVED",
                "reason": "within repo" if within_repo else "approved outside repo",
                "repo_root": str(repo_root),
                "target_path": str(resolved),
            }
            return SkillResult(success=True, output=output, skill_id=self.metadata().id)

        return SkillResult(
            success=False,
            output=None,
            error=f"Unknown action_type: {action_type}",
            skill_id=self.metadata().id,
        )

    def _resolve_target(self, target_path: str) -> Path:
        try:
            return (self._repo_root / target_path).resolve()
        except Exception:
            return Path(target_path).expanduser().resolve()

    def _is_within_repo(self, target_path: str) -> bool:
        resolved = self._resolve_target(target_path)
        try:
            resolved.relative_to(self._repo_root)
            return True
        except ValueError:
            return False


__all__ = ["SafetySkill"]
