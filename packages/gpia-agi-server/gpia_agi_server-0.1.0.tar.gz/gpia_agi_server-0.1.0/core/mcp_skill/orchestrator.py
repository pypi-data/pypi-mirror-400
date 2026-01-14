"""End-to-end MCP orchestration pipeline with policy, planning, and verification."""

from __future__ import annotations

import json
import time
import uuid
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence

from core.mcp_skill.interfaces import AuditLogger, McpResult, PolicyDecision, PolicyEnforcer
from core.mcp_skill.mcp_skill import McpSkill
from models.backend import make_client

ROOT = Path(__file__).resolve().parents[2]
DISABLE_FLAG = ROOT / "memory" / "agent_state_v1" / "mcp_disabled.flag"


@dataclass
class PlanStep:
    tool: str
    args: Dict[str, Any]
    server: Optional[str] = None
    success_criteria: Optional[str] = None


@dataclass
class Plan:
    steps: List[PlanStep]
    final_success_criteria: List[str] = field(default_factory=list)


@dataclass
class OrchestratorResult:
    status: str
    trace_id: str
    plan: Optional[Plan] = None
    tool_outputs: List[Dict[str, Any]] = field(default_factory=list)
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    audit_trace: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    verified: bool = False
    committed: bool = False
    verification_detail: str = ""


class Planner(Protocol):
    def plan(self, goal: str, constraints: Mapping[str, Any], env_context: Mapping[str, Any]) -> Plan:
        """Return a strict plan."""


class Verifier(Protocol):
    def verify(
        self,
        goal: str,
        success_criteria: Sequence[str],
        tool_outputs: Sequence[Mapping[str, Any]],
        env_context: Mapping[str, Any],
    ) -> tuple[bool, str]:
        """Return (passed, detail)."""


class Committer(Protocol):
    def commit(self, trace_id: str, payload: Mapping[str, Any]) -> None:
        """Persist final payload."""


class FileAuditLogger:
    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or (ROOT / "memory" / "agent_state_v1" / "mcp_orchestrator_audit.jsonl")
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append_event(self, trace_id: str, state: str, event: str, detail: Mapping[str, Any]) -> None:
        record = {
            "trace_id": trace_id,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "state": state,
            "event": event,
            "detail": dict(detail),
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    def export_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        if not self._path.exists():
            return []
        entries = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("trace_id") == trace_id:
                entries.append(record)
        return entries


class FileCommitter:
    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or (ROOT / "memory" / "agent_state_v1" / "mcp_commits.jsonl")
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def commit(self, trace_id: str, payload: Mapping[str, Any]) -> None:
        record = {
            "trace_id": trace_id,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": dict(payload),
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


class LlmPlanner:
    def __init__(self, client) -> None:
        self._client = client

    def plan(self, goal: str, constraints: Mapping[str, Any], env_context: Mapping[str, Any]) -> Plan:
        schema = {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool": {"type": "string"},
                            "args": {"type": "object"},
                            "server": {"type": "string"},
                            "success_criteria": {"type": "string"},
                        },
                        "required": ["tool", "args"],
                    },
                },
                "final_success_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["steps", "final_success_criteria"],
        }
        system_prompt = (
            "Return ONLY valid JSON that conforms to this schema. "
            "Do not include extra keys or commentary."
        )
        user_prompt = json.dumps({
            "goal": goal,
            "constraints": constraints,
            "env_context": env_context,
            "schema": schema,
        })
        response = self._client.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])
        payload = _parse_json(response)
        return _plan_from_payload(payload)


class DeterministicVerifier:
    def verify(
        self,
        goal: str,
        success_criteria: Sequence[str],
        tool_outputs: Sequence[Mapping[str, Any]],
        env_context: Mapping[str, Any],
    ) -> tuple[bool, str]:
        if not success_criteria:
            return False, "missing_success_criteria"
        haystack = json.dumps(tool_outputs, sort_keys=True)
        missing = [c for c in success_criteria if c not in haystack]
        if missing:
            return False, f"criteria_missing:{','.join(missing)}"
        return True, "criteria_matched"


class LlmVerifier:
    def __init__(self, client) -> None:
        self._client = client

    def verify(
        self,
        goal: str,
        success_criteria: Sequence[str],
        tool_outputs: Sequence[Mapping[str, Any]],
        env_context: Mapping[str, Any],
    ) -> tuple[bool, str]:
        schema = {
            "type": "object",
            "properties": {
                "passed": {"type": "boolean"},
                "detail": {"type": "string"},
            },
            "required": ["passed", "detail"],
        }
        system_prompt = (
            "Return ONLY valid JSON that conforms to this schema. "
            "Do not include extra keys or commentary."
        )
        user_prompt = json.dumps({
            "goal": goal,
            "success_criteria": list(success_criteria),
            "tool_outputs": tool_outputs,
            "env_context": env_context,
            "schema": schema,
        })
        response = self._client.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])
        payload = _parse_json(response)
        if not isinstance(payload, dict):
            raise ValueError("verifier_response_not_object")
        if "passed" not in payload or "detail" not in payload:
            raise ValueError("verifier_response_missing_fields")
        return bool(payload["passed"]), str(payload["detail"])


class McpOrchestrator:
    def __init__(
        self,
        mcp_skill: Optional[McpSkill] = None,
        planner: Optional[Planner] = None,
        verifier: Optional[Verifier] = None,
        policy: Optional[PolicyEnforcer] = None,
        audit: Optional[AuditLogger] = None,
        committer: Optional[Committer] = None,
    ) -> None:
        self.planner = planner
        self.verifier = verifier
        self.policy = policy
        self.audit = audit or FileAuditLogger()
        self.committer = committer or FileCommitter()
        self.mcp_skill = mcp_skill or McpSkill(audit=self.audit)
        self.allowed_risk_tiers = self._load_allowed_risk_tiers()

    def run(
        self,
        goal: str,
        constraints: Mapping[str, Any] | None,
        env_context: Mapping[str, Any] | None,
        available_servers: Sequence[str] | None,
    ) -> OrchestratorResult:
        trace_id = uuid.uuid4().hex
        constraints = dict(constraints or {})
        env_context = dict(env_context or {})
        errors: list[str] = []
        tool_outputs: list[Dict[str, Any]] = []
        provenance: list[Dict[str, Any]] = []

        if self._is_disabled():
            errors.append("mcp_disabled")
            self._audit(trace_id, "POLICY", "mcp_disabled", {})
            return self._result("BLOCKED", trace_id, None, tool_outputs, provenance, errors)

        self._audit(trace_id, "INGEST", "input_received", {"goal": goal})

        if self.policy:
            decision = self.policy.evaluate_call(
                {"goal": goal, "constraints": constraints, "env_context": env_context},
                constraints,
            )
            if not decision.allowed:
                errors.append(f"policy_block:{decision.reason}")
                self._audit(trace_id, "POLICY", "policy_block", {"reason": decision.reason})
                return self._result("BLOCKED", trace_id, None, tool_outputs, provenance, errors)
            self._audit(trace_id, "POLICY", "policy_allowed", {"risk_tier": decision.risk_tier})

        planner = self.planner or _build_llm_planner(constraints)
        if planner is None:
            errors.append("planner_not_configured")
            self._audit(trace_id, "PLAN", "planner_missing", {})
            return self._result("DEGRADED", trace_id, None, tool_outputs, provenance, errors)

        try:
            plan = planner.plan(goal, constraints, env_context)
            self._audit(trace_id, "PLAN", "plan_ready", {"steps": len(plan.steps)})
        except Exception as exc:
            errors.append(f"plan_error:{exc}")
            self._audit(trace_id, "PLAN", "plan_failed", {"error": str(exc)})
            return self._result("FAILED", trace_id, None, tool_outputs, provenance, errors)

        for idx, step in enumerate(plan.steps, start=1):
            step_constraints = dict(constraints)
            step_constraints["tool"] = step.tool
            step_constraints["tool_args"] = step.args
            if step.server:
                step_constraints["mcp_servers_allowlist"] = [step.server]
            self._audit(trace_id, "EXECUTE", "step_start", {"step": idx, "tool": step.tool})
            # Risk tier check before execution
            risk = None
            if self.policy:
                risk = self.policy.risk_tier(
                    {"server": step_constraints.get("mcp_servers_allowlist"), "tool": step.tool, "args": step.args}
                )
                if risk and risk.lower() not in self.allowed_risk_tiers:
                    errors.append(f"risk_block:{risk}")
                    self._audit(trace_id, "POLICY", "risk_block", {"tool": step.tool, "risk": risk})
                    return self._result("BLOCKED", trace_id, plan, tool_outputs, provenance, errors)
            result = self.mcp_skill.run(
                goal,
                step_constraints,
                available_servers,
                trace_id=trace_id,
            )
            tool_outputs.extend(result.tool_outputs)
            provenance.extend(result.provenance)
            if result.status != "DONE":
                errors.extend(result.errors)
                self._audit(trace_id, "EXECUTE", "step_failed", {"step": idx, "status": result.status})
                return self._result(result.status, trace_id, plan, tool_outputs, provenance, errors)
            self._audit(trace_id, "EXECUTE", "step_ok", {"step": idx})

        verifier = self.verifier or _build_verifier(constraints)
        if verifier is None:
            errors.append("verifier_not_configured")
            self._audit(trace_id, "VERIFY", "verifier_missing", {})
            return self._result("DEGRADED", trace_id, plan, tool_outputs, provenance, errors)

        try:
            passed, detail = verifier.verify(
                goal,
                plan.final_success_criteria,
                tool_outputs,
                env_context,
            )
        except Exception as exc:
            errors.append(f"verify_error:{exc}")
            self._audit(trace_id, "VERIFY", "verify_failed", {"error": str(exc)})
            return self._result("FAILED", trace_id, plan, tool_outputs, provenance, errors)

        if not passed:
            errors.append(f"verification_failed:{detail}")
            self._audit(trace_id, "VERIFY", "verify_blocked", {"detail": detail})
            return self._result(
                "FAILED",
                trace_id,
                plan,
                tool_outputs,
                provenance,
                errors,
                verified=False,
                detail=detail,
            )

        self._audit(trace_id, "VERIFY", "verify_passed", {"detail": detail})

        try:
            self.committer.commit(trace_id, {
                "goal": goal,
                "constraints": constraints,
                "tool_outputs": tool_outputs,
                "success_criteria": plan.final_success_criteria,
            })
            self._audit(trace_id, "COMMIT", "commit_ok", {})
            committed = True
        except Exception as exc:
            errors.append(f"commit_error:{exc}")
            self._audit(trace_id, "COMMIT", "commit_failed", {"error": str(exc)})
            committed = False

        status = "DONE" if committed else "FAILED"
        return self._result(
            status,
            trace_id,
            plan,
            tool_outputs,
            provenance,
            errors,
            verified=True,
            committed=committed,
            detail=detail,
        )

    def _audit(self, trace_id: str, state: str, event: str, detail: Mapping[str, Any]) -> None:
        self.audit.append_event(trace_id, state, event, detail)

    def _result(
        self,
        status: str,
        trace_id: str,
        plan: Optional[Plan],
        tool_outputs: List[Dict[str, Any]],
        provenance: List[Dict[str, Any]],
        errors: List[str],
        verified: bool = False,
        committed: bool = False,
        detail: str = "",
    ) -> OrchestratorResult:
        audit_trace = self.audit.export_trace(trace_id)
        return OrchestratorResult(
            status=status,
            trace_id=trace_id,
            plan=plan,
            tool_outputs=tool_outputs,
            provenance=provenance,
            audit_trace=audit_trace,
            errors=errors,
            verified=verified,
            committed=committed,
            verification_detail=detail,
        )

    def _is_disabled(self) -> bool:
        if os.environ.get("MCP_DISABLE_TOOLS", "").lower() in {"1", "true", "yes"}:
            return True
        return DISABLE_FLAG.exists()

    def _load_allowed_risk_tiers(self) -> set[str]:
        raw = os.environ.get("MCP_ALLOWED_RISK_TIERS")
        if not raw:
            return {"low", "medium", "high"}
        tiers = {item.strip().lower() for item in raw.split(",") if item.strip()}
        return tiers or {"low", "medium", "high"}


def _parse_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid_json:{exc}") from exc


def _plan_from_payload(payload: Any) -> Plan:
    if not isinstance(payload, dict):
        raise ValueError("plan_payload_not_object")
    allowed_payload_keys = {"steps", "final_success_criteria"}
    extra_payload_keys = set(payload.keys()) - allowed_payload_keys
    if extra_payload_keys:
        raise ValueError(f"plan_payload_extra_keys:{sorted(extra_payload_keys)}")
    steps_payload = payload.get("steps")
    if not isinstance(steps_payload, list) or not steps_payload:
        raise ValueError("plan_steps_missing")
    final_criteria = payload.get("final_success_criteria", [])
    if not isinstance(final_criteria, list):
        raise ValueError("plan_final_criteria_invalid")
    steps: list[PlanStep] = []
    for step in steps_payload:
        if not isinstance(step, dict):
            raise ValueError("plan_step_not_object")
        allowed_step_keys = {"tool", "args", "server", "success_criteria"}
        extra_step_keys = set(step.keys()) - allowed_step_keys
        if extra_step_keys:
            raise ValueError(f"plan_step_extra_keys:{sorted(extra_step_keys)}")
        tool = step.get("tool")
        args = step.get("args")
        if not isinstance(tool, str) or not isinstance(args, dict):
            raise ValueError("plan_step_invalid")
        server = step.get("server")
        if server is not None and not isinstance(server, str):
            raise ValueError("plan_step_server_invalid")
        success_criteria = step.get("success_criteria")
        if success_criteria is not None and not isinstance(success_criteria, str):
            raise ValueError("plan_step_success_criteria_invalid")
        steps.append(PlanStep(
            tool=tool,
            args=args,
            server=server,
            success_criteria=success_criteria,
        ))
    return Plan(steps=steps, final_success_criteria=[str(c) for c in final_criteria])


def _build_llm_planner(constraints: Mapping[str, Any]) -> Optional[Planner]:
    config = constraints.get("planner", {}) if isinstance(constraints.get("planner"), dict) else {}
    kind = config.get("kind") or constraints.get("planner_kind") or ""
    endpoint = config.get("endpoint") or constraints.get("planner_endpoint") or ""
    model = config.get("model") or constraints.get("planner_model") or ""
    if not kind or not model:
        return None
    client = make_client(kind=kind, endpoint=endpoint, model=model)
    return LlmPlanner(client)


def _build_verifier(constraints: Mapping[str, Any]) -> Optional[Verifier]:
    config = constraints.get("verifier", {}) if isinstance(constraints.get("verifier"), dict) else {}
    kind = config.get("kind") or constraints.get("verifier_kind") or ""
    endpoint = config.get("endpoint") or constraints.get("verifier_endpoint") or ""
    model = config.get("model") or constraints.get("verifier_model") or ""
    if kind and model:
        client = make_client(kind=kind, endpoint=endpoint, model=model)
        return LlmVerifier(client)
    return DeterministicVerifier()
