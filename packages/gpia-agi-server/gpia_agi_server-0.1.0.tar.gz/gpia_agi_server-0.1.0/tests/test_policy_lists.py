"""Tests for command allow/deny lists in the agent policy."""

from agent import policy_allows


def test_allow_prefix():
    ok, reason = policy_allows("pip install pytest")
    assert ok
    assert "allowed" in reason


def test_deny_pattern():
    ok, reason = policy_allows("rm -rf /")
    assert not ok
    assert "deny pattern" in reason


def test_not_in_allowlist():
    ok, reason = policy_allows("foobar")
    assert not ok
    assert reason == "not in allowlist"
