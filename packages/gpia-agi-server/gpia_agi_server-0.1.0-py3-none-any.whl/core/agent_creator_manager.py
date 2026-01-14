"""
Agent Creator Manager
=====================

Hardwired provisioning for GPIA agents with a plug interface that other models
can call. Produces a unique agent workspace, helper functions, runner template,
and a registry entry.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = ROOT / "data" / "gpia" / "agents"
REGISTRY_PATH = AGENTS_ROOT / "agent_registry.json"
SKILLS_ROOT = ROOT / "skills"
GUARDRAILS_PATH = ROOT / "config" / "agent_creator_guardrails.json"
AUDIT_LOG = AGENTS_ROOT / "agent_creator_audit.jsonl"


@dataclass
class AgentRequest:
    agent_name: str
    primary_goal: str
    model_id: str
    skill_categories: List[str]
    ephemeral_mode: bool = False
    max_steps: int = 5
    custom_helpers: List[Dict[str, Any]] = field(default_factory=list)
    output_path: Optional[str] = None
    requester_id: str = "user"
    requester_type: str = "user"
    parent_agent_id: Optional[str] = None
    policy_scope: str = "manual"
    session_id: Optional[str] = None
    approved: bool = False
    approval_note: str = ""
    agent_template: str = "standard"
    keep_alive: bool = False
    poll_interval: float = 2.0
    heartbeat_interval: float = 60.0


class AgentCreatorManager:
    """Provision and register GPIA agents with unique identifiers."""

    def __init__(self, agents_root: Optional[Path] = None):
        self.agents_root = agents_root or AGENTS_ROOT
        self.agents_root.mkdir(parents=True, exist_ok=True)
        self.guardrails = self._load_guardrails()

    def provision(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request = self._normalize_request(request_data)
        errors = self._validate_request(request)
        if errors:
            return {
                "success": False,
                "errors": errors,
            }

        guardrail_meta = {}
        guardrail_errors = []
        request, guardrail_errors, guardrail_meta = self._apply_guardrails(request, request_data)
        if guardrail_errors:
            self._log_guardrail_event(request, "blocked", guardrail_errors, guardrail_meta)
            return {
                "success": False,
                "errors": guardrail_errors,
                "guardrails": guardrail_meta,
            }

        agent_id = self._generate_agent_id(request.agent_name)
        agent_dir = self.agents_root / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        output_path = request.output_path or str(agent_dir / "output")
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        spec = {
            "agent_id": agent_id,
            "agent_name": request.agent_name,
            "primary_goal": request.primary_goal,
            "model_id": request.model_id,
            "skill_categories": request.skill_categories,
            "ephemeral_mode": request.ephemeral_mode,
            "max_steps": request.max_steps,
            "custom_helpers": request.custom_helpers,
            "output_path": str(output_dir),
            "requester_id": request.requester_id,
            "requester_type": request.requester_type,
            "parent_agent_id": request.parent_agent_id,
            "policy_scope": request.policy_scope,
            "session_id": request.session_id,
            "approved": request.approved,
            "approval_note": request.approval_note,
            "agent_template": request.agent_template,
            "keep_alive": request.keep_alive,
            "poll_interval": request.poll_interval,
            "heartbeat_interval": request.heartbeat_interval,
            "resource_budget": guardrail_meta.get("resource_budget", {}),
            "expires_at": guardrail_meta.get("expires_at"),
            "guardrails": guardrail_meta,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        (agent_dir / "agent_spec.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

        helpers_path = agent_dir / "helpers.py"
        helpers_path.write_text(
            self._render_helpers(
                agent_id,
                output_dir,
                request.custom_helpers,
                template=request.agent_template,
            ),
            encoding="utf-8",
        )

        plan_path = agent_dir / "plan.json"
        if not plan_path.exists():
            plan_path.write_text(
                json.dumps(self._default_plan(request.max_steps, request.primary_goal), indent=2),
                encoding="utf-8",
            )

        runner_path = agent_dir / "agent_runner.py"
        if request.agent_template == "living_messenger":
            runner_path.write_text(self._render_living_messenger_runner(), encoding="utf-8")
        else:
            runner_path.write_text(self._render_runner(), encoding="utf-8")

        registry_entry = {
            "agent_id": agent_id,
            "agent_name": request.agent_name,
            "primary_goal": request.primary_goal,
            "model_id": request.model_id,
            "skill_categories": request.skill_categories,
            "ephemeral_mode": request.ephemeral_mode,
            "output_path": str(output_dir),
            "requester_id": request.requester_id,
            "requester_type": request.requester_type,
            "parent_agent_id": request.parent_agent_id,
            "policy_scope": request.policy_scope,
            "session_id": request.session_id,
            "approved": request.approved,
            "expires_at": guardrail_meta.get("expires_at"),
            "agent_template": request.agent_template,
            "created_at": spec["created_at"],
            "status": "provisioned",
            "workspace": str(agent_dir),
        }
        self._append_registry(registry_entry)
        self._log_guardrail_event(request, "allowed", [], guardrail_meta)

        return {
            "success": True,
            "agent_id": agent_id,
            "workspace": str(agent_dir),
            "output_path": str(output_dir),
            "plan_path": str(plan_path),
            "runner_path": str(runner_path),
            "registry_path": str(REGISTRY_PATH),
            "guardrails": guardrail_meta,
        }

    def register_runtime_agent(
        self,
        name: str,
        purpose: str,
        model_id: str,
        requester_id: str = "system",
        requester_type: str = "system",
        parent_agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        agent_id = self._generate_agent_id(name)
        entry = {
            "agent_id": agent_id,
            "agent_name": name,
            "primary_goal": purpose,
            "model_id": model_id,
            "skill_categories": [],
            "ephemeral_mode": False,
            "output_path": "",
            "requester_id": requester_id,
            "requester_type": requester_type,
            "parent_agent_id": parent_agent_id,
            "policy_scope": "runtime",
            "session_id": os.getenv("GPIA_SESSION_ID", datetime.utcnow().strftime("%Y%m%d")),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "runtime_only",
            "workspace": "",
        }
        self._append_registry(entry)
        return entry

    def list_registry(self) -> List[Dict[str, Any]]:
        if not REGISTRY_PATH.exists():
            return []
        try:
            payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        return payload.get("agents", [])

    def provision_skill_stub(
        self,
        name: str,
        description: str,
        category: str = "automation",
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        safe_name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if not safe_name:
            return {"success": False, "error": "skill name is required"}
        if not description.strip():
            return {"success": False, "error": "skill description is required"}

        skill_dir = Path(output_path) if output_path else SKILLS_ROOT / category / safe_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            skill_md.write_text(
                f"---\nname: {safe_name}\ndescription: {description.strip()}\n---\n\n# {safe_name}\n",
                encoding="utf-8",
            )

        skill_py = skill_dir / "skill.py"
        if not skill_py.exists():
            skill_py.write_text(self._render_skill_stub(safe_name, description), encoding="utf-8")

        return {
            "success": True,
            "skill_name": safe_name,
            "skill_path": str(skill_dir),
            "skill_md": str(skill_md),
            "skill_py": str(skill_py),
        }

    def _append_registry(self, entry: Dict[str, Any]) -> None:
        current = {"agents": []}
        if REGISTRY_PATH.exists():
            try:
                current = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                current = {"agents": []}

        agents = current.get("agents", [])
        agents.append(entry)
        current["agents"] = agents
        REGISTRY_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")

    def _load_guardrails(self) -> Dict[str, Any]:
        if GUARDRAILS_PATH.exists():
            try:
                return json.loads(GUARDRAILS_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _get_policy(self, scope: str) -> Dict[str, Any]:
        defaults = self.guardrails.get("defaults", {})
        scoped = self.guardrails.get(scope, {})
        merged = {**defaults, **scoped}
        merged["scope"] = scope
        return merged

    def _apply_guardrails(
        self,
        request: AgentRequest,
        raw_request: Dict[str, Any],
    ) -> tuple[AgentRequest, List[str], Dict[str, Any]]:
        policy = self._get_policy(request.policy_scope)
        errors: List[str] = []
        meta: Dict[str, Any] = {"policy_scope": request.policy_scope}
        adjustments: List[str] = []

        session_id = request.session_id or raw_request.get("session_id") or os.getenv(
            "GPIA_SESSION_ID",
            datetime.utcnow().strftime("%Y%m%d"),
        )
        request.session_id = session_id
        meta["session_id"] = session_id

        if policy.get("require_approval") and not raw_request.get("approved", False):
            errors.append("approval required by guardrails")

        allowlist = policy.get("allowlist_categories", [])
        if allowlist:
            invalid = [c for c in request.skill_categories if c.lower() not in [a.lower() for a in allowlist]]
            if invalid:
                errors.append(f"skill_categories not allowed: {', '.join(invalid)}")

        max_steps_limit = int(policy.get("max_steps_limit", request.max_steps))
        if request.max_steps > max_steps_limit:
            request.max_steps = max_steps_limit
            adjustments.append(f"max_steps capped to {max_steps_limit}")

        if policy.get("force_ephemeral"):
            request.ephemeral_mode = True
            adjustments.append("ephemeral_mode forced by guardrails")

        max_depth = policy.get("max_spawn_depth")
        if max_depth is not None and request.parent_agent_id:
            depth = self._compute_spawn_depth(request.parent_agent_id)
            meta["spawn_depth"] = depth
            if depth >= int(max_depth):
                errors.append("spawn depth limit exceeded")

        counts = self._count_recent_agents(session_id, request.policy_scope, policy)
        meta.update(counts)
        if counts["session_count"] >= int(policy.get("max_agents_per_session", 0)):
            errors.append("session agent quota exceeded")
        if counts["hour_count"] >= int(policy.get("max_agents_per_hour", 0)):
            errors.append("hourly agent quota exceeded")

        ttl_hours = policy.get("ttl_hours")
        if ttl_hours:
            expires_at = datetime.utcnow().timestamp() + float(ttl_hours) * 3600
            meta["expires_at"] = datetime.utcfromtimestamp(expires_at).isoformat() + "Z"

        meta["resource_budget"] = policy.get("resource_budget", {})
        if adjustments:
            meta["adjustments"] = adjustments

        request.approved = bool(raw_request.get("approved", False))
        request.approval_note = raw_request.get("approval_note", "")

        return request, errors, meta

    def _count_recent_agents(self, session_id: str, scope: str, policy: Dict[str, Any]) -> Dict[str, int]:
        window = int(policy.get("session_window_seconds", 3600))
        now = datetime.utcnow()
        hour_count = 0
        session_count = 0
        for entry in self.list_registry():
            created = entry.get("created_at")
            if not created:
                continue
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", ""))
            except ValueError:
                continue
            age = (now - created_dt).total_seconds()
            if age <= 3600:
                if entry.get("policy_scope") == scope:
                    hour_count += 1
            if age <= window and entry.get("session_id") == session_id and entry.get("policy_scope") == scope:
                session_count += 1
        return {"hour_count": hour_count, "session_count": session_count}

    def _compute_spawn_depth(self, parent_agent_id: str) -> int:
        registry = {entry.get("agent_id"): entry for entry in self.list_registry()}
        depth = 0
        current = parent_agent_id
        while current:
            parent = registry.get(current, {})
            current = parent.get("parent_agent_id")
            depth += 1
            if depth > 20:
                break
        return depth

    def _log_guardrail_event(
        self,
        request: AgentRequest,
        decision: str,
        errors: List[str],
        meta: Dict[str, Any],
    ) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "decision": decision,
            "agent_name": request.agent_name,
            "policy_scope": request.policy_scope,
            "session_id": request.session_id,
            "requester_id": request.requester_id,
            "requester_type": request.requester_type,
            "errors": errors,
            "meta": meta,
        }
        with AUDIT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    @staticmethod
    def _normalize_request(request_data: Dict[str, Any]) -> AgentRequest:
        def pick(keys: List[str], default=None):
            for key in keys:
                if key in request_data:
                    return request_data[key]
            return default

        return AgentRequest(
            agent_name=pick(["agent_name", "Agent_Name", "name"], ""),
            primary_goal=pick(["primary_goal", "Primary_Goal", "goal"], ""),
            model_id=pick(["model_id", "Model_ID", "model"], ""),
            skill_categories=pick(["skill_categories", "Skill_Categories"], []) or [],
            ephemeral_mode=bool(pick(["ephemeral_mode", "Ephemeral_Mode"], False)),
            max_steps=int(pick(["max_steps", "Max_Steps"], 5)),
            custom_helpers=pick(["custom_helpers", "Custom_Helpers"], []) or [],
            output_path=pick(["output_path", "Output_Path"], None),
            requester_id=pick(["requester_id", "Requester_ID"], "user"),
            requester_type=pick(["requester_type", "Requester_Type"], "user"),
            parent_agent_id=pick(["parent_agent_id", "Parent_Agent_ID"], None),
            policy_scope=pick(["policy_scope", "Policy_Scope"], "manual"),
            session_id=pick(["session_id", "Session_ID"], None),
            approved=bool(pick(["approved", "Approved"], False)),
            approval_note=pick(["approval_note", "Approval_Note"], ""),
            agent_template=pick(["agent_template", "Agent_Template"], "standard"),
            keep_alive=bool(pick(["keep_alive", "Keep_Alive"], False)),
            poll_interval=float(pick(["poll_interval", "Poll_Interval"], 2.0)),
            heartbeat_interval=float(pick(["heartbeat_interval", "Heartbeat_Interval"], 60.0)),
        )

    @staticmethod
    def _validate_request(request: AgentRequest) -> List[str]:
        errors = []
        if not request.agent_name.strip():
            errors.append("agent_name is required")
        if not request.primary_goal.strip():
            errors.append("primary_goal is required")
        if not request.model_id.strip():
            errors.append("model_id is required")
        if not request.skill_categories:
            errors.append("skill_categories is required")
        if request.max_steps <= 0:
            errors.append("max_steps must be >= 1")
        return errors

    @staticmethod
    def _generate_agent_id(agent_name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", agent_name.lower()).strip("-")
        return f"{slug}-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _default_plan(max_steps: int, primary_goal: str) -> Dict[str, Any]:
        steps = []
        for idx in range(1, max_steps + 1):
            steps.append({
                "id": f"step-{idx}",
                "description": f"Define action {idx} for: {primary_goal}",
                "action": {"op": "noop"},
                "expected_state": {"paths_exist": []},
                "status": "pending",
            })
        return {"goal": primary_goal, "steps": steps}

    @staticmethod
    def _render_helpers(
        agent_id: str,
        output_root: Path,
        custom_helpers: List[Dict[str, Any]],
        template: str = "standard",
    ) -> str:
        extra_roots = ""
        if template == "living_messenger":
            extra_roots = f""",
    Path(r"{ROOT / "memory"}").resolve(),
    Path(r"{ROOT / "logs"}").resolve()"""

        helpers = f'''"""
Helper Functions for Agent {agent_id}
====================================

Restricted helpers for safe, scoped execution.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, List

ALLOWED_ROOTS: List[Path] = [
    Path(r"{output_root}").resolve(),
{extra_roots}
]


def _resolve_path(path: str) -> Path:
    target = Path(path).expanduser().resolve()
    for root in ALLOWED_ROOTS:
        try:
            target.relative_to(root)
            return target
        except ValueError:
            continue
    raise ValueError(f"Path outside allowed roots: {{target}}")


def ensure_dir(path: str) -> Path:
    target = _resolve_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_text(path: str, encoding: str = "utf-8") -> str:
    target = _resolve_path(path)
    return target.read_text(encoding=encoding)


def write_text(path: str, content: str, encoding: str = "utf-8") -> Path:
    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding=encoding)
    return target


def append_text(path: str, content: str, encoding: str = "utf-8") -> Path:
    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding=encoding) as handle:
        handle.write(content)
    return target


def list_files(path: str = ".", pattern: str = "*") -> Iterable[Path]:
    target = _resolve_path(path)
    return target.rglob(pattern)


def sha256_file(path: str) -> str:
    target = _resolve_path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()

'''

        if custom_helpers:
            helpers += "\n# Custom helpers injected by the creator\n"
            for helper in custom_helpers:
                name = helper.get("name", "custom_helper")
                name = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_") or "custom_helper"
                description = helper.get("description", "Custom helper stub.")
                code = helper.get("code")
                if code:
                    helpers += f"\n{code.strip()}\n"
                else:
                    helpers += f"""
def {name}(*args, **kwargs):
    \"\"\"{description}\"\"\"
    raise NotImplementedError("Custom helper not implemented.")
"""

        return helpers

    @staticmethod
    def _render_skill_stub(name: str, description: str) -> str:
        return f'''"""
{name} Skill
{"=" * (len(name) + 6)}

{description}
"""

from __future__ import annotations

from typing import Any, Dict

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult


class {name.replace("-", " ").title().replace(" ", "")}Skill(BaseSkill):
    SKILL_ID = "automation/{name}"
    SKILL_NAME = "{name}"
    SKILL_DESCRIPTION = "{description}"
    SKILL_CATEGORY = SkillCategory.AUTOMATION
    SKILL_LEVEL = SkillLevel.INTERMEDIATE
    SKILL_TAGS = ["stub"]

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(
            success=False,
            output={{"error": "Skill stub not implemented"}},
            error="Skill stub not implemented",
            skill_id=self.SKILL_ID,
        )


skill = {name.replace("-", " ").title().replace(" ", "")}Skill()


def execute(params: Dict[str, Any], context: SkillContext) -> SkillResult:
    return skill.execute(params, context)
'''

    @staticmethod
    def _render_runner() -> str:
        return '''"""
Agent Runner Template
=====================

Executes a plan step-by-step with validation and writes a report.
"""

from __future__ import annotations

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

import helpers

def resolve_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "skills").exists() and (parent / "core").exists():
            return parent
    return start.parents[4]


PROJECT_ROOT = resolve_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from skills.base import SkillContext
from skills.registry import get_registry


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_dir(root: Path) -> Dict[str, Dict[str, Any]]:
    snapshot: Dict[str, Dict[str, Any]] = {}
    if not root.exists():
        return snapshot
    for file_path in root.rglob("*"):
        if file_path.is_file():
            rel = str(file_path.relative_to(root))
            snapshot[rel] = {
                "size": file_path.stat().st_size,
                "sha256": helpers.sha256_file(str(file_path)),
            }
    return snapshot


def diff_snapshots(before: Dict[str, Dict[str, Any]], after: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    modified = sorted(k for k in before_keys & after_keys if before[k] != after[k])
    return {"added": added, "removed": removed, "modified": modified}


def execute_action(action: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
    op = action.get("op", "noop")
    if op == "noop":
        return {"status": "skipped", "reason": "noop"}
    if dry_run:
        return {"status": "dry_run", "op": op}

    if op == "write_text":
        helpers.write_text(action["path"], action.get("content", ""))
        return {"status": "ok", "op": op}
    if op == "append_text":
        helpers.append_text(action["path"], action.get("content", ""))
        return {"status": "ok", "op": op}
    if op == "ensure_dir":
        helpers.ensure_dir(action["path"])
        return {"status": "ok", "op": op}
    if op == "skill_execute":
        registry = get_registry()
        skill_id = action.get("skill_id", "")
        input_data = action.get("input", {})
        context = SkillContext(
            agent_role="agent",
            agent_model=action.get("model_id"),
        )
        result = registry.execute_skill(skill_id, input_data, context)
        return {
            "status": "ok" if result.success else "failed",
            "op": op,
            "skill_id": skill_id,
            "skill_result": result.to_dict(),
        }

    return {"status": "skipped", "reason": f"unsupported op: {op}"}


def validate_step(step: Dict[str, Any]) -> Dict[str, Any]:
    expected = step.get("expected_state", {})
    missing = []
    for path in expected.get("paths_exist", []):
        if not Path(path).exists():
            missing.append(path)
    return {"ok": not missing, "missing": missing}


def run_agent(agent_dir: Path, dry_run: bool) -> Dict[str, Any]:
    spec = load_json(agent_dir / "agent_spec.json", {})
    plan = load_json(agent_dir / "plan.json", {"steps": []})

    output_root = Path(spec.get("output_path", agent_dir / "output"))
    output_root.mkdir(parents=True, exist_ok=True)

    baseline = snapshot_dir(output_root)
    log_path = agent_dir / "run_log.jsonl"
    report_steps = []

    for step in plan.get("steps", []):
        start = time.time()
        action_result = execute_action(step.get("action", {}), dry_run=dry_run)
        validation = validate_step(step)
        duration = time.time() - start
        record = {
            "step_id": step.get("id"),
            "description": step.get("description"),
            "action_result": action_result,
            "validation": validation,
            "duration_sec": duration,
        }
        report_steps.append(record)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\\n")

    final_snapshot = snapshot_dir(output_root)
    changes = diff_snapshots(baseline, final_snapshot)

    report = {
        "agent_id": spec.get("agent_id"),
        "agent_name": spec.get("agent_name"),
        "steps_executed": len(report_steps),
        "changes": changes,
        "success": all(step["validation"]["ok"] for step in report_steps) if report_steps else True,
    }

    report_path = agent_dir / "report.md"
    report_lines = [
        "# Agent Execution Report",
        f"Agent ID: {report['agent_id']}",
        f"Agent Name: {report['agent_name']}",
        f"Steps Executed: {report['steps_executed']}",
        f"Success: {report['success']}",
        "",
        "## Files Changed",
        f"Added: {', '.join(report['changes']['added']) or 'None'}",
        f"Modified: {', '.join(report['changes']['modified']) or 'None'}",
        f"Removed: {', '.join(report['changes']['removed']) or 'None'}",
    ]
    report_path.write_text("\\n".join(report_lines), encoding="utf-8")

    (agent_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a provisioned agent.")
    parser.add_argument("--agent-dir", default=".", help="Path to agent workspace")
    parser.add_argument("--dry-run", action="store_true", help="Do not apply actions")
    args = parser.parse_args()

    report = run_agent(Path(args.agent_dir), dry_run=args.dry_run)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
'''

    @staticmethod
    def _render_living_messenger_runner() -> str:
        return '''"""
Living Messenger Runner
=======================

Persistent agent loop: Listen -> Process -> Respond.
Includes safe dense-state reads and sync checks.
"""

from __future__ import annotations

import argparse
import json
import time
import sys
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

def resolve_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "skills").exists() and (parent / "core").exists():
            return parent
    return start.parents[4]


PROJECT_ROOT = resolve_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent_utils import query_llm
from core.sovereignty_v2.telemetry_observer import sample_telemetry

SHARED_CONTEXT = PROJECT_ROOT / "memory" / "shared_context.json"
DENSE_STATE_PATH = PROJECT_ROOT / "memory" / "dense" / "state_vector.bin"
DENSE_LOCK = PROJECT_ROOT / "memory" / "dense" / "heartbeat.lock"
HEARTBEAT_LOG = PROJECT_ROOT / "logs" / "messenger_heartbeat.jsonl"

EXPECTED_BYTES = 2048


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "")).replace(tzinfo=timezone.utc)


def load_shared_context() -> Dict[str, Any]:
    default = {
        "session_id": "LIVING-CHAT-01",
        "master_state": "IDLE",
        "last_sync_timestamp": utc_now(),
        "primary_goal": "",
        "active_resonance_patterns": [],
        "dense_state_ref": {
            "tensor_id": "DS-UNSET",
            "vector_path": "memory/dense/state_vector.bin",
            "abstraction_level": 0.0
        },
        "message_queue": [],
        "outbox": [],
    }
    return load_json(SHARED_CONTEXT, default)


def log_heartbeat(agent_id: str, status: str, details: Dict[str, Any]) -> None:
    entry = {
        "timestamp": utc_now(),
        "agent_id": agent_id,
        "status": status,
        "details": details,
    }
    HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HEARTBEAT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\\n")


def safe_read_dense_state(path: Path, lock_path: Path, timeout_ms: int = 500) -> bytes | None:
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
        if lock_path.exists():
            time.sleep(0.01)
            continue
        if not path.exists():
            return None
        stat_before = path.stat()
        data = path.read_bytes()
        stat_after = path.stat()
        if stat_before.st_mtime_ns == stat_after.st_mtime_ns and stat_before.st_size == stat_after.st_size:
            if EXPECTED_BYTES and len(data) != EXPECTED_BYTES:
                return None
            return data
        time.sleep(0.01)
    raise TimeoutError("Sync-Timeout: Master held the Dense-State lock too long.")


def sync_agent_context(context: Dict[str, Any]) -> Tuple[str, datetime | None]:
    if not DENSE_STATE_PATH.exists():
        return "NO_STATE", None
    last_sync = context.get("last_sync_timestamp", "")
    if not last_sync:
        return "UNKNOWN", None
    state_mtime = datetime.fromtimestamp(DENSE_STATE_PATH.stat().st_mtime, tz=timezone.utc)
    if state_mtime >= parse_iso(last_sync):
        return "SYNCED", state_mtime
    return "STALE", state_mtime


def decode_float32(payload: bytes) -> List[float]:
    if not payload or len(payload) % 4 != 0:
        return []
    count = len(payload) // 4
    return list(struct.unpack("<" + "f" * count, payload))


def analyze_dense_state(values: List[float]) -> Dict[str, Any]:
    if len(values) < 512:
        return {"clarity": 0.0, "sector": "UNKNOWN", "sectors": {}}
    sectors = {
        "AMBIENT": values[0:128],
        "LOGIC": values[128:256],
        "EXEC": values[256:384],
        "MEMORY": values[384:512],
    }
    sector_scores = {
        name: sum(vals) / len(vals) if vals else 0.0
        for name, vals in sectors.items()
    }
    top_sector = max(sector_scores, key=sector_scores.get)
    clarity = max(0.0, min(1.0, sector_scores[top_sector]))
    return {
        "clarity": clarity,
        "sector": top_sector,
        "sectors": sector_scores,
    }


def summarize_dense_state(values: List[float], goal: str) -> str:
    analysis = analyze_dense_state(values)
    clarity_pct = round(analysis["clarity"] * 100.0, 2)
    top_sector = analysis["sector"]
    sector_detail = ", ".join(
        f"{name}:{round(score * 100.0, 1)}%"
        for name, score in analysis["sectors"].items()
    )
    goal_text = goal or "<missing primary_goal>"
    return (
        f"SYNCED: Dense-State resonance {clarity_pct}% in {top_sector} sector. "
        f"Goal: {goal_text}. Sectors: {sector_detail}."
    )


def handle_message(msg: Dict[str, Any], context: Dict[str, Any], model_id: str, goal: str) -> str:
    prompt = msg.get("text", "")
    lower = prompt.lower()
    if any(token in lower for token in ("dense", "resonance", "formalism", "/extract")):
        status, _ = sync_agent_context(context)
        if status != "SYNCED":
            return f"{status}: Master is still calculating the next resonance pass."
        try:
            payload = safe_read_dense_state(DENSE_STATE_PATH, DENSE_LOCK)
        except TimeoutError as exc:
            return str(exc)
        if not payload:
            return "NO_STATE: Dense-state payload unavailable or size mismatch."
        values = decode_float32(payload)
        if not values:
            return "INVALID_STATE: Dense-state decode failed."
        return summarize_dense_state(values, goal)

    return query_llm(model_id, prompt, max_tokens=800, temperature=0.4)


def process_queue(context: Dict[str, Any], model_id: str, goal: str) -> bool:
    updated = False
    for msg in context.get("message_queue", []):
        if msg.get("processed"):
            continue
        response = handle_message(msg, context, model_id, goal)
        context.setdefault("outbox", []).append({
            "sender": "MESSENGER",
            "text": response,
            "timestamp": utc_now(),
            "in_reply_to": msg.get("timestamp", "")
        })
        msg["processed"] = True
        updated = True
    if updated:
        context["last_sync_timestamp"] = utc_now()
    return updated


def should_stop(agent_dir: Path, expires_at: str | None) -> bool:
    stop_signal = agent_dir / "stop.signal"
    if stop_signal.exists():
        return True
    if expires_at:
        try:
            expiry = datetime.fromisoformat(expires_at.replace("Z", ""))
            if datetime.utcnow() >= expiry:
                return True
        except ValueError:
            return False
    return False


def run_loop(agent_dir: Path, spec: Dict[str, Any]) -> None:
    agent_id = spec.get("agent_id", "living-messenger")
    model_id = spec.get("model_id", "qwen3:latest")
    poll_interval = float(spec.get("poll_interval", 2.0))
    heartbeat_interval = float(spec.get("heartbeat_interval", 60.0))
    expires_at = spec.get("expires_at")
    goal = spec.get("primary_goal", "")

    last_heartbeat = 0.0
    while True:
        if should_stop(agent_dir, expires_at):
            log_heartbeat(agent_id, "stopped", {"reason": "stop_or_expired"})
            break

        context = load_shared_context()
        updated = process_queue(context, model_id=model_id, goal=goal)
        if updated:
            write_json(SHARED_CONTEXT, context)

        now = time.time()
        if now - last_heartbeat >= heartbeat_interval:
            telemetry = sample_telemetry()
            log_heartbeat(agent_id, "alive", {
                "telemetry": telemetry.__dict__,
                "queue_depth": len(context.get("message_queue", [])),
                "outbox_depth": len(context.get("outbox", [])),
            })
            last_heartbeat = now

        time.sleep(poll_interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Living Messenger agent.")
    parser.add_argument("--agent-dir", default=".", help="Path to agent workspace")
    args = parser.parse_args()

    agent_dir = Path(args.agent_dir)
    spec = load_json(agent_dir / "agent_spec.json", {})
    run_loop(agent_dir, spec)


if __name__ == "__main__":
    main()
'''


class CreatorPlug:
    """Public plug interface for models and tools to provision agents."""

    def __init__(self):
        self.manager = AgentCreatorManager()

    def provision(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self.manager.provision(request)

    def register_runtime_agent(self, name: str, purpose: str, model_id: str, requester_id: str) -> Dict[str, Any]:
        return self.manager.register_runtime_agent(
            name=name,
            purpose=purpose,
            model_id=model_id,
            requester_id=requester_id,
            requester_type="model",
        )

    def provision_skill(self, name: str, description: str, category: str = "automation") -> Dict[str, Any]:
        return self.manager.provision_skill_stub(name=name, description=description, category=category)

    def list_registry(self) -> List[Dict[str, Any]]:
        return self.manager.list_registry()
