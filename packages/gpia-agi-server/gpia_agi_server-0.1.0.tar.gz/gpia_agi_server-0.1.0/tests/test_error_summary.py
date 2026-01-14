from core import error_summary
from integrations import social_hooks


def test_summarize_chunks():
    chunks = [["A", "A"], ["B", "B"]]

    calls = []

    def fake(chunk: str) -> str:
        calls.append(chunk)
        return "part"

    summary = error_summary.summarize_chunks(chunks, summarize=fake)

    assert calls == ["AA", "BB"]
    assert summary == "\n".join(["part"] * len(calls))


def test_summarize_chunks_collapses_newlines():
    chunks = [["part\npart\npart"]]

    summary = error_summary.summarize_chunks(chunks)

    assert summary == "part ..."


def test_summarize_chunks_trims_whitespace():
    chunks = [["   part   "]]

    summary = error_summary.summarize_chunks(chunks)

    assert summary == "part"


def test_notify_error_payload(monkeypatch):
    calls = []

    def fake_post(url, payload):
        calls.append((url, payload))

    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "http://discord")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://slack")
    monkeypatch.setattr(social_hooks, "_post", fake_post)

    social_hooks.notify_error("boom")

    assert calls[0][0] == "http://discord"
    assert calls[1][0] == "http://slack"
    for _, payload in calls:
        assert payload["event"] == "error"
        assert payload["summary"] == "boom"
        assert "ts" in payload
