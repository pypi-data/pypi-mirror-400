import json
import asyncio
from collections import defaultdict
from pathlib import Path
import os

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("BUS_TOKEN", "test-token")
import bus_server
from core.bus_client import BusClient


class FakeRedis:
    def __init__(self):
        self.streams = defaultdict(list)

    async def xadd(self, stream, fields):
        self.streams[stream].append(fields["data"])

    async def xgroup_create(self, stream, group, id="0", mkstream=False):
        return None

    async def xreadgroup(self, group, consumer, streams, count=1, block=15000):
        stream = next(iter(streams))
        if self.streams[stream]:
            data = self.streams[stream].pop(0)
            return [(stream, [("1-0", {"data": data})])]
        await asyncio.sleep(0)
        return []

    async def xack(self, stream, group, msg_id):
        return None


def test_publish_get_cycle(monkeypatch):
    """Publish and retrieve a message via the bus."""
    recorded = []

    def fake_add_entry(**kw):
        recorded.append(kw)

    monkeypatch.setattr(bus_server, "add_entry", fake_add_entry)
    monkeypatch.setenv("BUS_TOKEN", "secret")
    monkeypatch.setattr(bus_server, "redis", FakeRedis())

    client = TestClient(bus_server.app)
    msg = json.loads((Path(__file__).parent / "data" / "bus_messages.json").read_text())[0]
    headers = {"Authorization": "Bearer secret"}
    r = client.post("/publish", json=msg, headers=headers)
    assert r.status_code == 200
    params = {"topic": msg["topic"], "group": "g1", "consumer": "c1"}
    r = client.get("/get", params=params, headers=headers)
    assert r.status_code == 200
    assert r.json()["data"] == msg["data"]
    assert recorded and recorded[0]["kind"] == "bus_message"


def test_reject_invalid_token(monkeypatch):
    monkeypatch.setenv("BUS_TOKEN", "secret")
    client = TestClient(bus_server.app)
    msg = json.loads((Path(__file__).parent / "data" / "bus_messages.json").read_text())[0]
    headers = {"Authorization": "Bearer wrong"}
    r = client.post("/publish", json=msg, headers=headers)
    assert r.status_code == 401
    params = {"topic": msg["topic"], "group": "g1", "consumer": "c1"}
    r = client.get("/get", params=params, headers=headers)
    assert r.status_code == 401
    r = client.post("/publish", json=msg)
    assert r.status_code == 403


def test_missing_bus_token_env(monkeypatch):
    """Requests fail with 401 when BUS_TOKEN is unset."""
    # Ensure BUS_TOKEN is not defined
    monkeypatch.delenv("BUS_TOKEN", raising=False)
    client = TestClient(bus_server.app)
    msg = json.loads((Path(__file__).parent / "data" / "bus_messages.json").read_text())[0]
    headers = {"Authorization": "Bearer anything"}
    r = client.post("/publish", json=msg, headers=headers)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_bus_client_integration(monkeypatch):
    """BusClient.run retrieves messages using the shared async client."""
    monkeypatch.setenv("BUS_TOKEN", "secret")
    monkeypatch.setattr(bus_server, "redis", FakeRedis())

    transport = httpx.ASGITransport(app=bus_server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        msg = {"topic": "demo", "data": {"text": "hello"}}
        headers = {"Authorization": "Bearer secret"}
        r = await client.post("/publish", json=msg, headers=headers)
        assert r.status_code == 200

        received: list[dict] = []
        bc = BusClient("http://test", "demo", lambda m: received.append(m), token="secret")
        bc._client = client
        await bc.run()
        await bc.stop()

    assert received and received[0]["data"]["text"] == "hello"


@pytest.mark.asyncio
async def test_bus_client_retry(monkeypatch):
    """BusClient retries failed requests using the persistent client."""
    monkeypatch.setenv("BUS_TOKEN", "secret")
    monkeypatch.setattr(bus_server, "redis", FakeRedis())

    transport = httpx.ASGITransport(app=bus_server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        msg = {"topic": "demo", "data": {"text": "hi"}}
        headers = {"Authorization": "Bearer secret"}
        r = await client.post("/publish", json=msg, headers=headers)
        assert r.status_code == 200

        received: list[dict] = []
        bc = BusClient("http://test", "demo", lambda m: received.append(m), token="secret", retries=1)
        bc._client = client

        attempts = 0
        original_request = client.request

        async def flaky_request(method, url, **kwargs):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise httpx.RequestError("boom", request=httpx.Request(method, url))
            return await original_request(method, url, **kwargs)

        client.request = flaky_request
        await bc.run()
        await bc.stop()

    assert attempts == 2
    assert received and received[0]["data"]["text"] == "hi"


def test_token_rotation(monkeypatch):
    """Server should honor BUS_TOKEN changes at runtime."""
    monkeypatch.setenv("BUS_TOKEN", "first")
    monkeypatch.setattr(bus_server, "redis", FakeRedis())
    client = TestClient(bus_server.app)
    msg = json.loads((Path(__file__).parent / "data" / "bus_messages.json").read_text())[0]

    # Initial token works
    headers_first = {"Authorization": "Bearer first"}
    r = client.post("/publish", json=msg, headers=headers_first)
    assert r.status_code == 200

    # Rotate token
    monkeypatch.setenv("BUS_TOKEN", "second")

    # Old token is rejected
    r = client.post("/publish", json=msg, headers=headers_first)
    assert r.status_code == 401

    # New token is accepted
    headers_second = {"Authorization": "Bearer second"}
    r = client.post("/publish", json=msg, headers=headers_second)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_high_volume_concurrent_clients(monkeypatch):
    """Simulate heavy bus traffic with multiple consumers."""
    monkeypatch.setenv("BUS_TOKEN", "token")
    monkeypatch.setattr(bus_server, "redis", FakeRedis())

    transport = httpx.ASGITransport(app=bus_server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer token"}

        async def publisher(i: int) -> None:
            msg = {"topic": "load", "data": {"i": i}}
            r = await client.post("/publish", json=msg, headers=headers)
            assert r.status_code == 200

        async def consumer(name: str) -> list[int]:
            params = {"topic": "load", "group": "g", "consumer": name}
            out = []
            for _ in range(25):
                r = await client.get("/get", params=params, headers=headers)
                assert r.status_code == 200
                out.append(r.json()["data"]["i"])
            return out

        publishers = [publisher(i) for i in range(50)]
        consumers = [consumer("c1"), consumer("c2")]
        results = await asyncio.gather(*(publishers + consumers))
        recv = results[-2] + results[-1]
        assert sorted(recv) == list(range(50))
