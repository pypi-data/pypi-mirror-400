from fastapi.testclient import TestClient
import server.main as main


def test_sesamawake_triggers_pipeline(monkeypatch):
    calls = []

    async def fake_publish(channel, payload):
        calls.append((channel, payload))

    monkeypatch.setattr(main, "publish", fake_publish)
    client = TestClient(main.app)
    resp = client.post(
        "/api/actions/sesamawake",
        headers={"Authorization": f"Bearer {main.settings.API_TOKEN}"},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    channels = [c for c, _ in calls]
    assert "pipeline:configure_services" in channels
    assert "pipeline:ticket" in channels
    assert "pipeline:slack_summary" in channels
    assert "pipeline:kpi_update" in channels
    assert channels.count("logs:sesamawake") == 4
