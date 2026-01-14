"""Tests for role-based access control and token rotation."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from server.security import validate_token, settings


def _create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/secure", dependencies=[Depends(validate_token)])
    async def secure():
        return {"ok": True}

    return app


def test_role_based_access(monkeypatch):
    """Only the correct role token is allowed."""

    monkeypatch.setattr(settings, "API_TOKEN", "admin-token")
    app = _create_app()
    client = TestClient(app)

    # Admin token succeeds
    resp = client.get("/secure", headers={"Authorization": "Bearer admin-token"})
    assert resp.status_code == 200

    # User token denied
    resp = client.get("/secure", headers={"Authorization": "Bearer user-token"})
    assert resp.status_code == 401


def test_token_rotation(monkeypatch):
    """Old tokens stop working after rotation."""

    monkeypatch.setattr(settings, "API_TOKEN", "v1")
    app = _create_app()
    client = TestClient(app)

    # Initial token works
    assert client.get("/secure", headers={"Authorization": "Bearer v1"}).status_code == 200

    # Rotate token
    monkeypatch.setattr(settings, "API_TOKEN", "v2")

    # Old token rejected
    assert client.get("/secure", headers={"Authorization": "Bearer v1"}).status_code == 401

    # New token accepted
    assert client.get("/secure", headers={"Authorization": "Bearer v2"}).status_code == 200
