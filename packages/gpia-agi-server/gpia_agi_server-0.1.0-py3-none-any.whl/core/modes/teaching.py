"""
Teaching Mode: Pedagogical operational mode.

System operates in teaching/tutoring configuration:
- Explains concepts
- Creates learning materials
- Guides learners
- Provides feedback and corrections
"""

from __future__ import annotations

from typing import Optional
import json

from core.agents.base import BaseAgent, ModeTransition
from gpia.memory.dense_state import DenseStateLogEntry
from gpia.memory.dense_state.storage import DenseStateStorage


class TeachingMode(BaseAgent):
    """
    Teaching/Tutoring operational mode.

    Operates with pedagogical focus:
    - Explains concepts in accessible ways
    - Creates exercises and learning materials
    - Provides guided learning experiences
    - Adapts to learner understanding
    """

    mode_name = "Teaching"

    def __init__(self, ctx):
        """Initialize with dense-state storage."""
        super().__init__(ctx)
        self._dense_storage = None

    def _get_dense_storage(self) -> DenseStateStorage:
        """Lazy-initialize dense-state storage."""
        if self._dense_storage is None:
            config = {"vnand": {"enabled": False}}
            self._dense_storage = DenseStateStorage(config=config)
        return self._dense_storage

    def step(self) -> Optional[ModeTransition]:
        """
        One cycle in Teaching mode.

        Reads commands and provides teaching-oriented responses.
        Can transition back to Sovereign-Loop or to Forensic-Debug.

        Returns:
            ModeTransition to change modes, or None to continue
        """
        # Read next command
        cmd = self.ctx.perception.read_command().strip()

        # Handle transitions back to Sovereign-Loop
        if cmd in {"back", "mode sovereign", "exit teaching"}:
            self.ctx.telemetry.emit("teaching.transition_request", {"target": "Sovereign-Loop"})
            return ModeTransition(next_mode="Sovereign-Loop", reason="return_to_sovereign")

        # Handle transition to Forensic-Debug
        if cmd in {"forensic", "mode forensic", "debug"}:
            self.ctx.telemetry.emit("teaching.transition_request", {"target": "Forensic-Debug"})
            return ModeTransition(next_mode="Forensic-Debug", reason="operator_request")

        # Handle empty commands
        if not cmd:
            return None

        # Teaching cycle: emit heartbeat + log as teaching interaction
        self.ctx.telemetry.heartbeat("teaching_tick", {"cmd": cmd})
        self.ctx.ledger.append("teaching", {
            "mode": self.mode_name,
            "cmd": cmd,
            "type": "teaching_interaction"
        })

        # Log dense-state snapshot for teaching interaction
        try:
            state_vector = self._cmd_to_vector(cmd)
            log_entry = DenseStateLogEntry(
                vector=state_vector,
                mode="vector",
                adapter_version="1.0",
                adapter_id="teaching_mode",
                seed=hash(cmd) % (2**31),
                prompt_hash=self._compute_hash(cmd),
                metrics={"cmd_length": len(cmd), "mode": self.mode_name, "interaction_type": "pedagogical"}
            )

            storage = self._get_dense_storage()
            storage.append(log_entry)
        except Exception as e:
            self.ctx.telemetry.emit("dense_state.log_error", {"error": str(e)})

        # Provide teaching-oriented response (stub for now)
        response = self._create_teaching_response(cmd)
        self.ctx.perception.write(response)

        return None

    def _create_teaching_response(self, cmd: str) -> str:
        """
        Create a teaching-oriented response.

        Args:
            cmd: The learner's command/question

        Returns:
            Teaching response formatted for output
        """
        # Stub implementation: basic echo with educational framing
        response = f"[Teaching] Explaining: {cmd}\n"
        response += f"           [Concept breakdown and guided understanding]\n"
        return response

    def _cmd_to_vector(self, cmd: str) -> list:
        """Convert command string to state vector."""
        codes = [float(ord(c)) / 256.0 for c in cmd[:32]]
        codes.extend([0.0] * (32 - len(codes)))
        return codes[:32]

    def _compute_hash(self, data: str) -> str:
        """Compute simple hash of data."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]
