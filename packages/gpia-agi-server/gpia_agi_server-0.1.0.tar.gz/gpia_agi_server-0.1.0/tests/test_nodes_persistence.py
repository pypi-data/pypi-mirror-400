import os

import pytest
from fastapi.testclient import TestClient
import server.main as main

if os.getenv("SKIP_DB") == "true":
    pytest.skip("Skipping DB tests on CI by policy", allow_module_level=True)

AUTH = {"Authorization": f"Bearer {main.settings.API_TOKEN}"}


def test_node_persistence_across_restarts(monkeypatch):
    async def fake_publish(channel, payload):
        return None

    async def fake_init_db():
        return None

    async def fake_close_db():
        return None

    nodes: dict[str, dict] = {}

    async def fake_set_node_status(node_id: str, status: str):
        nodes.setdefault(node_id, {"id": node_id})
        nodes[node_id]["status"] = status
        return nodes[node_id]

    async def fake_list_nodes():
        return list(nodes.values())

    monkeypatch.setattr(main, "publish", fake_publish)
    monkeypatch.setattr(main, "init_db", fake_init_db)
    monkeypatch.setattr(main, "close_db", fake_close_db)
    monkeypatch.setattr(main.db, "set_node_status", fake_set_node_status)
    monkeypatch.setattr(main.db, "list_nodes", fake_list_nodes)

    # start node and ensure status is running
    with TestClient(main.app) as client:
        resp = client.post("/api/nodes/agent-1/start", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    # restart application and verify status persisted
    with TestClient(main.app) as client:
        resp = client.get("/api/nodes", headers=AUTH)
        assert resp.status_code == 200
        nodes_resp = {n["id"]: n for n in resp.json()}
        assert nodes_resp["agent-1"]["status"] == "running"

        # stop node and verify
        resp = client.post("/api/nodes/agent-1/stop", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["status"] == "stopped"

    # restart again and ensure stop persisted
    with TestClient(main.app) as client:
        resp = client.get("/api/nodes", headers=AUTH)
        nodes_resp = {n["id"]: n for n in resp.json()}
        assert nodes_resp["agent-1"]["status"] == "stopped"
