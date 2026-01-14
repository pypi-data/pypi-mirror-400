"""WebSocket token validation tests."""

import pytest
from fastapi import Depends, FastAPI, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from server.security import validate_ws_token, settings


def test_validate_ws_token(monkeypatch):
    """Connections require the correct token."""

    monkeypatch.setattr(settings, "API_TOKEN", "secret")

    app = FastAPI()

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket, _=Depends(validate_ws_token)):
        await ws.accept()
        await ws.close()

    client = TestClient(app)

    # Valid token succeeds
    with client.websocket_connect("/ws?token=secret"):
        pass

    # Invalid token results in policy violation and disconnect
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=wrong"):
            pass


def test_invalid_token_denies_messages(monkeypatch):
    """Invalid tokens close the connection before any messages are handled."""

    monkeypatch.setattr(settings, "API_TOKEN", "secret")

    app = FastAPI()
    processed = {"called": False}

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket, _=Depends(validate_ws_token)):
        await ws.accept()
        await ws.receive_text()
        processed["called"] = True
        await ws.send_text("ok")

    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=wrong") as ws:
            ws.send_text("hello")
            ws.receive_text()

    assert processed["called"] is False
