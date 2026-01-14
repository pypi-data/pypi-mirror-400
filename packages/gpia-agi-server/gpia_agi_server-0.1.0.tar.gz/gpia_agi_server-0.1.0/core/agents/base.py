"""
BaseAgent and AgentContext: Shared continuity for all operational modes.

All modes inherit from BaseAgent and share the same AgentContext,
enabling hot-swap without kernel restart.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


class SupportsTelemetry(Protocol):
    """Protocol for telemetry systems."""
    def emit(self, event: str, payload: Dict[str, Any]) -> None:
        """Emit a telemetry event."""
        ...

    def heartbeat(self, name: str, payload: Dict[str, Any]) -> None:
        """Emit a heartbeat signal."""
        ...


class SupportsLedger(Protocol):
    """Protocol for ledger/persistence systems."""
    def append(self, stream: str, record: Dict[str, Any]) -> None:
        """Append a record to a named stream."""
        ...

    def get_identity_record(self) -> Optional[Dict[str, Any]]:
        """Retrieve the identity record."""
        ...


class SupportsPerception(Protocol):
    """Protocol for perception/I/O systems."""
    def read_command(self) -> str:
        """Read a command from perception (CLI, network, etc)."""
        ...

    def write(self, msg: str) -> None:
        """Write a message to perception output."""
        ...


@dataclass
class AgentContext:
    """
    Unified context passed through all modes.

    Holds live references to:
    - identity: Sovereign identity record
    - telemetry: Heartbeat and event emission
    - ledger: Append-only event log
    - perception: I/O boundary (CLI, network, sensors)
    - state: Cross-mode continuity payload
    """
    identity: Dict[str, Any]
    telemetry: SupportsTelemetry
    ledger: SupportsLedger
    perception: SupportsPerception
    state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModeTransition:
    """Signal to switch operational modes."""
    next_mode: str
    reason: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


class _TransitionSignal(RuntimeError):
    """Internal exception to signal mode transition."""
    def __init__(self, transition: ModeTransition) -> None:
        super().__init__(transition.reason)
        self.transition = transition


class BaseAgent:
    """
    Shared continuity base class for all operational modes.

    All modes run inside the same AgentContext instance.
    Modes communicate via ModeTransition exceptions.
    """
    mode_name: str = "base"

    def __init__(self, ctx: AgentContext) -> None:
        self.ctx = ctx

    def on_enter(self) -> None:
        """Called when mode is entered."""
        self.ctx.telemetry.emit("mode.enter", {"mode": self.mode_name})

    def on_exit(self) -> None:
        """Called when mode is exited."""
        self.ctx.telemetry.emit("mode.exit", {"mode": self.mode_name})

    def step(self) -> Optional[ModeTransition]:
        """
        One cognitive cycle.

        Returns ModeTransition to hot-swap modes,
        or None to continue in current mode.
        """
        raise NotImplementedError

    def run(self) -> None:
        """
        Default run loop for modes that do not need custom control.

        Calls step() repeatedly until a ModeTransition is raised.
        """
        self.on_enter()
        try:
            while True:
                self.ctx.telemetry.heartbeat("cognitive_cycle", {"mode": self.mode_name})
                transition = self.step()
                if transition:
                    self.ctx.state.update(transition.payload or {})
                    raise _TransitionSignal(transition)
        finally:
            self.on_exit()
