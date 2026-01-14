"""
Stub implementations for kernel services.

These are default implementations used if real ones aren't available.
Replace these with your actual implementations.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StubLedger:
    """Minimal ledger implementation for testing."""

    def __init__(self) -> None:
        self.identity: Optional[Dict[str, Any]] = None
        self.streams: Dict[str, list] = {}

    def append(self, stream: str, record: Dict[str, Any]) -> None:
        """Append record to a named stream."""
        if stream not in self.streams:
            self.streams[stream] = []
        self.streams[stream].append(record)
        logger.debug(f"[Ledger] {stream}: {record}")

    def get_identity_record(self) -> Optional[Dict[str, Any]]:
        """Return the agent identity record."""
        if self.identity is None:
            # Default identity
            self.identity = {
                "agent_id": "gpia",
                "kernel_signature": "boot_kernel_v1",
                "created_at": "2026-01-02T00:00:00Z",
            }
        return self.identity


class StubPerception:
    """Minimal perception implementation (CLI I/O)."""

    def read_command(self) -> str:
        """Read command from stdin."""
        try:
            return input("> ").strip()
        except EOFError:
            return "exit"

    def write(self, msg: str) -> None:
        """Write message to stdout."""
        print(msg, end="", flush=True)


class StubTelemetry:
    """Minimal telemetry implementation (logging-based)."""

    def __init__(self) -> None:
        self.events: list = []

    def emit(self, event: str, payload: Dict[str, Any]) -> None:
        """Emit a telemetry event."""
        self.events.append({"event": event, "payload": payload})
        logger.debug(f"[Telemetry] {event}: {payload}")

    def heartbeat(self, name: str, payload: Dict[str, Any]) -> None:
        """Emit a heartbeat signal."""
        self.emit(f"heartbeat.{name}", payload)


def make_ledger() -> StubLedger:
    """Factory for ledger service."""
    return StubLedger()


def make_perception() -> StubPerception:
    """Factory for perception service."""
    return StubPerception()


def make_telemetry() -> StubTelemetry:
    """Factory for telemetry service."""
    return StubTelemetry()
