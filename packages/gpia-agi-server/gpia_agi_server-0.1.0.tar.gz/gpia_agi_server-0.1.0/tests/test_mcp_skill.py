import pytest

from core.mcp_skill.interfaces import McpResult, PolicyDecision
from core.mcp_skill.mcp_skill import McpSkill, SchemaValidator
from core.mcp_skill.orchestrator import DeterministicVerifier, McpOrchestrator, Plan, PlanStep
from core.mcp_skill.state_machine import McpEvent, McpState, McpStateMachine, TRANSITIONS


class MemoryAuditLogger:
    def __init__(self):
        self.events = []

    def append_event(self, trace_id, state, event, detail):
        self.events.append({
            "trace_id": trace_id,
            "state": state,
            "event": event,
            "detail": dict(detail),
        })

    def export_trace(self, trace_id):
        return [event for event in self.events if event["trace_id"] == trace_id]


class FakeRegistry:
    def list_servers(self):
        return ["alpha"]

    def list_tools(self, server):
        return ["search"]

    def get_tool_schema(self, server, tool):
        return {
            "parameters": {
                "required": ["query"],
                "properties": {"query": {"type": "string"}},
            }
        }


class FakeAuth:
    def get_token(self, server):
        return "token"

    def refresh(self, server):
        return "token"


class AllowPolicy:
    def evaluate_call(self, call, context):
        return PolicyDecision(allowed=True, reason="ok", requires_manual=False, risk_tier="low")

    def risk_tier(self, call):
        return "low"

    def requires_manual_gate(self, call):
        return False


class BlockPolicy(AllowPolicy):
    def evaluate_call(self, call, context):
        return PolicyDecision(allowed=False, reason="blocked", requires_manual=True, risk_tier="high")


class ValidatingInvoker:
    def invoke_tool(self, server, tool, args, schema):
        SchemaValidator.validate(schema, args)
        return {"ok": True}


class FailingInvoker:
    def invoke_tool(self, server, tool, args, schema):
        raise RuntimeError("boom")


def test_transition_graph_path_to_done():
    sm = McpStateMachine()
    assert sm.handle(McpEvent.START) == McpState.DISCOVER
    assert sm.handle(McpEvent.SERVERS_LISTED) == McpState.AUTH
    assert sm.handle(McpEvent.AUTH_OK) == McpState.DESCRIBE
    assert sm.handle(McpEvent.TOOL_SCHEMA_LOADED) == McpState.PLAN
    assert sm.handle(McpEvent.PLAN_READY) == McpState.EXECUTE
    assert sm.handle(McpEvent.CALL_OK) == McpState.OBSERVE
    assert sm.handle(McpEvent.CALL_OK) == McpState.VERIFY
    assert sm.handle(McpEvent.CALL_OK) == McpState.COMMIT
    assert sm.handle(McpEvent.CALL_OK) == McpState.DONE


def test_transition_graph_complete():
    for state in McpState:
        assert state in TRANSITIONS


def test_schema_validation_blocks_invalid_args():
    audit = MemoryAuditLogger()
    skill = McpSkill(
        registry=FakeRegistry(),
        auth=FakeAuth(),
        policy=AllowPolicy(),
        invoker=ValidatingInvoker(),
        audit=audit,
    )
    result = skill.run("find docs", {"tool_args": {}}, ["alpha"])
    assert isinstance(result, McpResult)
    assert result.status in {"DEGRADED", "FAILED"}
    assert any("schema missing required field" in err for err in result.errors)


def test_retry_budget_exhausted_marks_degraded():
    audit = MemoryAuditLogger()
    sm = McpStateMachine(retry_budgets={McpState.EXECUTE: 1})
    skill = McpSkill(
        registry=FakeRegistry(),
        auth=FakeAuth(),
        policy=AllowPolicy(),
        invoker=FailingInvoker(),
        audit=audit,
        state_machine=sm,
    )
    result = skill.run("ping", {"tool_args": {"query": "x"}}, ["alpha"])
    assert result.status == "DEGRADED"
    trace_events = [event["event"] for event in result.audit_trace]
    assert "retry_budget_exhausted" in trace_events


def test_policy_blocked_call_ends_blocked():
    audit = MemoryAuditLogger()
    skill = McpSkill(
        registry=FakeRegistry(),
        auth=FakeAuth(),
        policy=BlockPolicy(),
        invoker=ValidatingInvoker(),
        audit=audit,
    )
    result = skill.run("exfil", {"tool_args": {"query": "x"}}, ["alpha"])
    assert result.status == "BLOCKED"
    trace_events = [event["event"] for event in result.audit_trace]
    assert "policy_block" in trace_events


class FakePlanner:
    def __init__(self, plan):
        self._plan = plan

    def plan(self, goal, constraints, env_context):
        return self._plan


class ReturningInvoker:
    def __init__(self, payload):
        self._payload = payload

    def invoke_tool(self, server, tool, args, schema):
        SchemaValidator.validate(schema, args)
        return dict(self._payload)


def test_orchestrator_success_flow_commits():
    audit = MemoryAuditLogger()
    plan = Plan(
        steps=[PlanStep(tool="search", args={"query": "x"})],
        final_success_criteria=["OK"],
    )
    skill = McpSkill(
        registry=FakeRegistry(),
        auth=FakeAuth(),
        policy=AllowPolicy(),
        invoker=ReturningInvoker({"result": "OK"}),
        audit=audit,
    )
    orchestrator = McpOrchestrator(
        mcp_skill=skill,
        planner=FakePlanner(plan),
        verifier=DeterministicVerifier(),
        policy=AllowPolicy(),
        audit=audit,
    )
    result = orchestrator.run("goal", {}, {"mode": "test"}, ["alpha"])
    assert result.status == "DONE"
    assert result.verified is True
    assert result.committed is True


def test_orchestrator_policy_blocks():
    audit = MemoryAuditLogger()
    plan = Plan(
        steps=[PlanStep(tool="search", args={"query": "x"})],
        final_success_criteria=["OK"],
    )
    skill = McpSkill(
        registry=FakeRegistry(),
        auth=FakeAuth(),
        policy=AllowPolicy(),
        invoker=ReturningInvoker({"result": "OK"}),
        audit=audit,
    )
    orchestrator = McpOrchestrator(
        mcp_skill=skill,
        planner=FakePlanner(plan),
        verifier=DeterministicVerifier(),
        policy=BlockPolicy(),
        audit=audit,
    )
    result = orchestrator.run("goal", {}, {"mode": "test"}, ["alpha"])
    assert result.status == "BLOCKED"
