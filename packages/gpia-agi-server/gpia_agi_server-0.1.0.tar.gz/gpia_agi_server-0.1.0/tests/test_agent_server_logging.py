import json
from fastapi.testclient import TestClient
from core import kb
from agent_server import app


def test_unauthorized_tokens_masked(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_SHARED_SECRET", "secret")
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()
    client = TestClient(app)
    resp = client.post("/chat", headers={"Authorization": "Bearer bad"}, json={"text": "hi"})
    assert resp.status_code == 403
    entries = kb.last(1)
    assert entries
    payload = json.loads(entries[0]["data"]).get("data", {})
    assert payload.get("masked_token") == "***"
    assert "bad" not in entries[0]["data"]
