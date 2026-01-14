import builtins
import importlib
import io
import sys
import types

import pytest


def _load_orchestrator(monkeypatch):
    dummy_admin = types.SimpleNamespace(evaluate_ceo_decision=lambda *_: "ok")
    sys.modules["admin_policy"] = dummy_admin

    open_orig = builtins.open

    def fake_open(path, *args, **kwargs):
        p = str(path)
        if p.endswith("configs/agents.yaml"):
            return io.StringIO("admin:\n  wake_order: []\nagents: {}\n")
        if p.endswith("configs/models.yaml"):
            return io.StringIO("models: {}\n")
        return open_orig(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    return importlib.reload(importlib.import_module("orchestrator"))


def test_wait_health_failure_logs_and_raises(monkeypatch, caplog):
    orch = _load_orchestrator(monkeypatch)
    bad_url = "http://127.0.0.1:9/health"
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError) as err:
            orch._wait_health(bad_url, retries=1, initial_delay=0)
    msg = str(err.value)
    assert bad_url in msg
    assert err.value.__cause__ is not None
    assert bad_url in caplog.text
    assert "Last error" in caplog.text
