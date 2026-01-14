import asyncio
import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import agent_server
import core.bus_client as bus_client_module
from core.bus_client import BusClient
from core.settings import settings

os.environ.setdefault("AGENT_SHARED_SECRET", "test-secret")
client = TestClient(agent_server.app)
AUTH_HEADER = {"Authorization": f"Bearer {os.environ['AGENT_SHARED_SECRET']}"}


class DummyLLM:
    def __init__(self):
        self.calls = []
        self.history = None

    def chat(self, system_prompt, text):
        self.calls.append(text)
        return f"resp:{text}"

    def chat_history(self, messages):
        self.history = messages
        return f"history:{len(messages)}"


@patch("agent_server.add_entry", MagicMock())
def test_chat_endpoint_chunks(monkeypatch):
    dummy = DummyLLM()
    monkeypatch.setattr(agent_server, "llm", dummy)

    class StubChunker:
        def __init__(self, *a, **k):
            pass

        def chunk(self, text):
            return ["one", "two"]

    monkeypatch.setattr(agent_server, "DynamicChunker", StubChunker)

    resp = client.post("/chat", json={"text": "long text"}, headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert dummy.calls == ["one", "two"]
    body = resp.json()["response"]
    assert "resp:one" in body and "resp:two" in body


@patch("agent_server.add_entry", MagicMock())
def test_chat_history_chunks(monkeypatch):
    dummy = DummyLLM()
    monkeypatch.setattr(agent_server, "llm", dummy)

    class StubChunker:
        def __init__(self, *a, **k):
            pass

        def chunk(self, text):
            return ["segA", "segB"]

    monkeypatch.setattr(agent_server, "DynamicChunker", StubChunker)

    hist = {"messages": [{"role": "user", "content": "very long"}]}
    resp = client.post("/chat_history", json=hist, headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert dummy.history == [
        {"role": "user", "content": "segA"},
        {"role": "user", "content": "segB"},
    ]
    assert "history:2" in resp.json()["response"]


def test_bus_client_chunked_publish(monkeypatch):
    class StubChunker:
        def __init__(self, *a, **k):
            pass

        def chunk(self, text):
            return ["c1", "c2"]

    monkeypatch.setattr(bus_client_module, "DynamicChunker", StubChunker)

    sent = []

    async def fake_request(self, method, endpoint, **kwargs):
        sent.append(kwargs["json"])

    monkeypatch.setattr(BusClient, "_arequest", fake_request)

    bc = BusClient("http://x", "topic", lambda m: None)

    async def publish_and_close():
        await bc.publish("room", "payload")
        await bc.stop()

    asyncio.run(publish_and_close())

    assert sent == [
        {"topic": "room", "data": {"text": "c1", "chunk": 1, "total": 2}},
        {"topic": "room", "data": {"text": "c2", "chunk": 2, "total": 2}},
    ]


def test_bus_client_chunked_run(monkeypatch):
    class StubChunker:
        def __init__(self, *a, **k):
            pass

        def chunk(self, text):
            return ["p1 p2", "p2 p3"]

    monkeypatch.setattr(bus_client_module, "DynamicChunker", StubChunker)

    received = []

    def handler(msg):
        received.append(msg)

    class Resp:
        status_code = 200

        def json(self):
            return {"data": {"text": "long text"}}

    async def fake_req(self, *a, **k):
        return Resp()

    monkeypatch.setattr(BusClient, "_request", fake_req)
    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    import sys
    import types

    embeds: list[str] = []

    def fake_embed(t: str):
        embeds.append(t)
        return [0.1]

    module = types.SimpleNamespace(get_embeddings=fake_embed)
    monkeypatch.setitem(sys.modules, "integrations.openvino_embedder", module)

    bc = BusClient("http://x", "topic", handler)

    async def run_and_close():
        await bc.run()
        await bc.stop()

    asyncio.run(run_and_close())

    assert [m["data"]["text"] for m in received] == ["p1 p2", "p2 p3"]
    assert embeds == ["p1 p2", "p2 p3"]
