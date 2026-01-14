import agents
import pytest


def test_delegate_injects_context(monkeypatch):
    monkeypatch.setattr(agents, "fetch_context", lambda n=5, query=None: "ctx")

    captured = {}

    def dummy(context):
        captured["context"] = context
        return "ok"

    monkeypatch.setitem(agents.AGENT_FUNCTIONS, "dummy", dummy)
    result = agents.delegate("dummy")
    assert result == "ok"
    assert captured["context"] == {"summary": "ctx"}


def test_delegate_unknown_task(monkeypatch):
    monkeypatch.setattr(agents, "fetch_context", lambda n=5, query=None: "ctx")
    with pytest.raises(KeyError):
        agents.delegate("missing_task")
