import agent
import pytest


class StubPS:
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def run(self, cmd, timeout=600):
        self.commands.append(cmd)
        return self.responses.pop(0)

    def close(self):
        pass


@pytest.fixture(autouse=True)
def mute_logging(monkeypatch):
    monkeypatch.setattr(agent, "append_transcript", lambda *a, **k: None)
    monkeypatch.setattr(agent, "log_event", lambda *a, **k: None)


@pytest.fixture
def ps_factory(monkeypatch):
    def factory(responses):
        ps = StubPS(responses)
        monkeypatch.setattr(agent, "PowerShellSession", lambda: ps)
        return ps

    return factory


def test_run_agent_dry_run_avoids_execution(monkeypatch):
    monkeypatch.setattr(agent, "default_planner", lambda goal: ["echo hi"])
    called = {}

    class FailPS:
        def __init__(self):
            called["called"] = True

    monkeypatch.setattr(agent, "PowerShellSession", FailPS)
    rc = agent.run_agent("say hi", dry_run=True)
    assert rc == 0
    assert "called" not in called


def test_run_agent_blocked_command(monkeypatch, ps_factory):
    monkeypatch.setattr(agent, "default_planner", lambda goal: ["rm -rf /"])
    ps = ps_factory([])
    rc = agent.run_agent("danger")
    assert rc == 2
    assert ps.commands == []


def test_run_agent_retry_on_pip_failure(monkeypatch, ps_factory):
    monkeypatch.setattr(agent, "default_planner", lambda goal: ["pip install foo"])
    ps = ps_factory([(1, "fail"), (0, "ok")])
    rc = agent.run_agent("install")
    assert rc == 0
    assert ps.commands == [
        "pip install foo",
        "pip install foo --break-system-packages",
    ]
