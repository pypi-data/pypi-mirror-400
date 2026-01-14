from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import threading
import time

from agent_server import app

os.environ.setdefault("AGENT_SHARED_SECRET", "test-secret")

# Create a client to interact with the app
client = TestClient(app)
AUTH_HEADER = {"Authorization": f"Bearer {os.environ['AGENT_SHARED_SECRET']}"}


# A dummy class to simulate the LLM's behavior during tests
class DummyClient:
    def chat(self, system_prompt, text):
        return f"Response to: {text}"

    def chat_history(self, messages):
        return f"Response to history with {len(messages)} messages"


# A dummy class to simulate the message bus
class DummyBus:
    def subscribe(self, topic, callback):
        pass

    async def publish(self, topic, data):
        pass

    def run_forever(self):
        pass

    async def stop(self):
        pass


def test_health_check():
    """Tests if the /health endpoint is working."""
    response = client.get("/health", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# Use a patch to mock the add_entry function across all tests in this file
@patch("agent_server.add_entry", MagicMock())
def test_unauthorized_access(monkeypatch):
    """Tests that the security middleware correctly blocks unauthorized requests."""
    # Mock the llm object to prevent side effects if the middleware fails
    monkeypatch.setattr("agent_server.llm", DummyClient())

    # Case 1: No authorization header
    response = client.post("/chat", json={"text": "hello"})
    assert response.status_code == 401

    # Case 2: Wrong token
    response = client.post(
        "/chat", headers={"Authorization": "Bearer wrong-token"}, json={"text": "hello"}
    )
    assert response.status_code == 403


@patch("agent_server.add_entry", MagicMock())
def test_agent_chat_endpoints(monkeypatch):
    """Tests the core /chat, /chat_history, and /publish endpoints."""
    # Mock the global 'llm' and 'bus' variables for this test
    monkeypatch.setattr("agent_server.llm", DummyClient())
    monkeypatch.setattr("agent_server.bus", DummyBus())

    # Test the /chat endpoint
    response = client.post("/chat", json={"text": "test prompt"}, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert "Response to: test prompt" in response.json()["response"]

    # Test the /chat_history endpoint
    history = {"messages": [{"role": "user", "content": "hello"}]}
    response = client.post("/chat_history", json=history, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert "Response to history with 1 messages" in response.json()["response"]

    # Test the /publish endpoint
    bus_message = {"topic": "test-topic", "data": {"key": "value"}}
    response = client.post("/publish", json=bus_message, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["status"] == "published"


@patch("agent_server.add_entry", MagicMock())
def test_scheduler_shutdown(monkeypatch):
    """Ensure the APScheduler shuts down when the app closes."""
    # Prevent heavy model loading during tests
    monkeypatch.setattr("agent_server.load_and_register_model", lambda: None)
    # Make the bus truthy so /wake triggers init_cron
    monkeypatch.setattr("agent_server.bus", DummyBus())

    with TestClient(app) as local_client:
        baseline = len(threading.enumerate())
        local_client.post("/wake", headers=AUTH_HEADER)
        # Scheduler thread should now be running
        running = len(threading.enumerate())
        assert running > baseline
        assert any(t.name.startswith("APScheduler") for t in threading.enumerate())

    # After context exit, scheduler should be stopped
    time.sleep(0.1)
    assert not any(t.name.startswith("APScheduler") for t in threading.enumerate())
    assert len(threading.enumerate()) <= baseline
