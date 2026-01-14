from agent_server import _get_mcp_orchestrator


def test_agent_server_mcp_run_demo():
    import agent_server
    agent_server._MCP_ORCHESTRATOR = None  # reset cache
    orch = _get_mcp_orchestrator()
    result = orch.run("demo goal", {}, {"role": "test"}, ["demo"])
    assert result.status == "DONE"
    assert result.trace_id
    assert result.errors == []


def test_agent_server_mcp_kill_switch(monkeypatch):
    import agent_server
    agent_server._MCP_ORCHESTRATOR = None  # reset cache
    monkeypatch.setenv("MCP_DISABLE_TOOLS", "1")
    orch = _get_mcp_orchestrator()
    result = orch.run("demo goal", {}, {"role": "test"}, ["demo"])
    assert result.status == "BLOCKED"
    assert any("mcp_disabled" in err for err in result.errors)


def test_agent_server_mcp_risk_block(monkeypatch):
    import agent_server
    agent_server._MCP_ORCHESTRATOR = None  # reset cache
    monkeypatch.setenv("MCP_DISABLE_TOOLS", "0")
    monkeypatch.setenv("MCP_ALLOWED_RISK_TIERS", "low")
    orch = _get_mcp_orchestrator()
    # Force high risk by including "http" keyword
    result = orch.run(
        "demo goal",
        {"tool_args": {"text": "http request"}},
        {"role": "test"},
        ["demo"],
    )
    assert result.status == "BLOCKED"
