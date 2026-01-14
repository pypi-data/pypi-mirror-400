#!/usr/bin/env python3
"""
Skill → Agent Transpiler (guarded)

Compile a skill entry into a creator-manager request, or provision it when approved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_creator_manager import AgentCreatorManager

INDEX_PATH = PROJECT_ROOT / "skills" / "INDEX.json"
DEFAULT_MODEL = os.getenv("GPIA_TRANSPILER_DEFAULT_MODEL", "qwen3:latest")


def load_index() -> Dict[str, Any]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def find_skill(skill_id: str, index: Dict[str, Any]) -> Dict[str, Any]:
    for skill in index.get("skills", []):
        if skill.get("id") == skill_id:
            return skill
    return {}


def compile_request(skill: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    skill_id = skill.get("id", "")
    description = skill.get("description", "").strip()
    category = (skill.get("category") or skill_id.split("/")[0] if skill_id else "").lower()
    if category:
        categories = [category]
    else:
        categories = overrides.get("skill_categories", [])

    agent_name = overrides.get("agent_name") or skill.get("name", skill_id or "skill-agent")
    primary_goal = overrides.get("primary_goal") or f"Execute skill {skill_id}: {description}"

    request = {
        "agent_name": agent_name,
        "primary_goal": primary_goal,
        "model_id": overrides.get("model_id", DEFAULT_MODEL),
        "skill_categories": categories,
        "ephemeral_mode": overrides.get("ephemeral_mode", True),
        "max_steps": overrides.get("max_steps", 3),
        "custom_helpers": overrides.get("custom_helpers", []),
        "output_path": overrides.get("output_path"),
        "requester_id": overrides.get("requester_id", "transpiler"),
        "requester_type": overrides.get("requester_type", "transpiler"),
        "parent_agent_id": overrides.get("parent_agent_id"),
        "approved": overrides.get("approved", False),
        "approval_note": overrides.get("approval_note", ""),
        "policy_scope": "transpiler",
        "source_skill_id": skill_id,
    }

    return request


def load_overrides(path: str | None) -> Dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile or provision an agent from a skill.")
    parser.add_argument("--skill-id", required=True, help="Skill ID to transpile")
    parser.add_argument("--mode", choices=["compile", "provision"], default="compile")
    parser.add_argument("--input", help="Optional JSON file with overrides")
    parser.add_argument("--approved", action="store_true", help="Mark request as approved")
    args = parser.parse_args()

    overrides = load_overrides(args.input)
    if args.approved:
        overrides["approved"] = True

    index = load_index()
    skill = find_skill(args.skill_id, index)
    if not skill:
        print(json.dumps({"success": False, "error": f"Skill not found: {args.skill_id}"}))
        raise SystemExit(1)

    request = compile_request(skill, overrides)

    if args.mode == "compile":
        print(json.dumps({"success": True, "request": request}, indent=2))
        return

    manager = AgentCreatorManager()
    result = manager.provision(request)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
