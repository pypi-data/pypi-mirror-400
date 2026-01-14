import os
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core import gpia_server


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Isolate KB and profile storage
    kb_path = tmp_path / "kb.db"
    profile_path = tmp_path / "user_profile.json"
    monkeypatch.setenv("KB_DB_PATH", str(kb_path))

    events = []

    async def bus_publisher(envelope):
        events.append(envelope)

    app = gpia_server.create_app(profile_path=profile_path, bus_publisher=bus_publisher)
    return TestClient(app), events, profile_path


def test_profile_defaults(client):
    http, events, profile_path = client
    trace = uuid.uuid4().hex
    res = http.get("/api/v1/profile", headers={"X-Trace-Id": trace})
    assert res.status_code == 200
    body = res.json()
    assert body["trace_id"] == trace
    profile = body["profile"]
    assert profile["profile_version"] == 1
    assert profile["verbosity"] == "medium"
    assert profile["theme"] == "dark"
    assert profile_path.exists()
    assert events == []  # profile fetch should not publish


def test_dense_state_crud_flow(client):
    http, events, _ = client
    trace = uuid.uuid4().hex
    payload = {
        "model_id": "m1",
        "title": "t1",
        "body": "b1",
        "tags": ["x"],
        "provenance": {"prompt_hash": "h", "policy_id": "p"},
    }

    # Create
    res = http.post("/api/v1/dense-state", json=payload, headers={"X-Trace-Id": trace})
    assert res.status_code == 201
    created = res.json()["data"]
    post_id = created["id"]
    assert created["version"] == 1
    assert created["deleted"] is False
    assert res.headers["X-Trace-Id"] == trace
    assert events[-1]["event_name"] == "post.created"
    assert events[-1]["idempotency_key"] == f"{post_id}:1"

    # Get
    res = http.get(f"/api/v1/dense-state/{post_id}", headers={"X-Trace-Id": trace})
    assert res.status_code == 200
    assert res.json()["data"]["id"] == post_id

    # Patch
    res = http.patch(
        f"/api/v1/dense-state/{post_id}",
        json={"title": "new", "tags": ["y"]},
        headers={"X-Trace-Id": trace},
    )
    assert res.status_code == 200
    updated = res.json()["data"]
    assert updated["title"] == "new"
    assert updated["tags"] == ["y"]
    assert updated["version"] == 2
    assert events[-1]["event_name"] == "post.updated"
    assert events[-1]["idempotency_key"] == f"{post_id}:2"

    # Delete (soft)
    res = http.delete(f"/api/v1/dense-state/{post_id}", headers={"X-Trace-Id": trace})
    assert res.status_code == 200
    deleted = res.json()["data"]
    assert deleted["deleted"] is True
    assert deleted["version"] == 3
    assert events[-1]["event_name"] == "post.deleted"
    assert events[-1]["idempotency_key"] == f"{post_id}:3"

    # List defaults exclude deleted
    res = http.get("/api/v1/dense-state", headers={"X-Trace-Id": trace})
    assert res.status_code == 200
    assert res.json()["data"] == []

    # List include deleted shows it
    res = http.get("/api/v1/dense-state?include_deleted=true", headers={"X-Trace-Id": trace})
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == post_id


@pytest.mark.skipif("REDIS_URL" not in os.environ, reason="Redis integration not configured")
def test_integration_bus_publisher(monkeypatch, tmp_path):
    # Smoke: ensure app creation succeeds with default publisher (uses real Redis)
    profile_path = tmp_path / "profile.json"
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    app = gpia_server.create_app(profile_path=profile_path)
    client = TestClient(app)
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
