import importlib
import sys
import types

import pytest


@pytest.mark.parametrize(
    "reply, expected",
    [("harmful action", "harmful"), ("all good", "acceptable")],
)
def test_evaluate_ceo_decision_branches(monkeypatch, reply, expected):
    fake_client = types.SimpleNamespace(chat=lambda messages: reply)
    monkeypatch.setattr("models.backend.make_client", lambda *args, **kwargs: fake_client)
    entries = []
    monkeypatch.setattr("core.kb.add_entry", lambda **kw: entries.append(kw))
    loads = [
        {"admin": {"model": "dummy"}},
        {"models": {"dummy": {"kind": "k", "endpoint": "e", "model": "m"}}},
    ]
    monkeypatch.setattr("yaml.safe_load", lambda stream: loads.pop(0))

    if "admin_policy" in sys.modules:
        del sys.modules["admin_policy"]
    admin_policy = importlib.import_module("admin_policy")

    verdict = admin_policy.evaluate_ceo_decision("text")
    assert verdict == expected
    assert entries[0]["verdict"] == verdict
