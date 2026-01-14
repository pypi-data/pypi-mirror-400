import importlib
import types

import pytest


def test_import_server_modules():
    # Ensure these modules import cleanly for coverage
    mod_security = importlib.import_module("server.security")
    mod_config = importlib.import_module("server.config")
    mod_models = importlib.import_module("server.models")

    assert hasattr(mod_security, "validate_token")
    assert hasattr(mod_config, "settings")
    assert hasattr(mod_models, "NodeConfig")


def test_validate_token_accepts_and_rejects():
    from server.security import validate_token
    from server.config import settings
    from fastapi import HTTPException

    # Accept when token matches
    assert validate_token(token=settings.API_TOKEN) is None

    # Reject when token mismatches
    with pytest.raises(HTTPException):
        validate_token(token="not-the-token")


@pytest.mark.asyncio
async def test_validate_ws_token_paths():
    from server.security import validate_ws_token
    from server.config import settings
    from fastapi import status
    from fastapi import WebSocketDisconnect

    # Minimal stub with async close to match the call site
    closed = {}

    class WSStub:
        async def close(self, code: int):
            closed["code"] = code

    ws = WSStub()

    # Accept path: returns None and does not close
    assert await validate_ws_token(ws, token=settings.API_TOKEN) is None
    assert "code" not in closed

    # Reject path: closes with policy violation and raises
    with pytest.raises(WebSocketDisconnect):
        await validate_ws_token(ws, token="bad-token")
    assert closed.get("code") == status.WS_1008_POLICY_VIOLATION


def test_models_constructible():
    from server.models import SeedBody, NodeConfig

    assert SeedBody(text="hello").text == "hello"
    nc = NodeConfig(system="s", temperature=0.5, max_tokens=128)
    assert nc.system == "s" and nc.max_tokens == 128

