"""
Sovereign-Loop Mode: Primary operational mode.

Normal operation where the agent:
- Reads commands from perception
- Processes them
- Can transition to Teaching or Forensic-Debug modes
- Can exit cleanly
"""

from __future__ import annotations

from typing import Optional
import json

from core.agents.base import BaseAgent, ModeTransition
from gpia.memory.dense_state import DenseStateLogEntry
from gpia.memory.dense_state.storage import DenseStateStorage
from skills.registry import get_registry
from skills.base import SkillContext


class SovereignLoopMode(BaseAgent):
    """
    Main operational mode: Sovereign cognitive loop.

    Executes normal agent functions:
    - Read and interpret commands
    - Execute tasks
    - Manage state
    - Coordinate with other subsystems
    """

    mode_name = "Sovereign-Loop"

    def __init__(self, ctx):
        """Initialize with dense-state storage."""
        super().__init__(ctx)
        self._dense_storage = None

    def _get_dense_storage(self) -> DenseStateStorage:
        """Lazy-initialize dense-state storage with full VNAND persistence."""
        if self._dense_storage is None:
            # ENABLED: Full Dense-State with VNAND persistence and HyperVoxel
            config = {
                "vnand": {
                    "enabled": True,
                    "root_dir": "data/vnand",
                    "page_bytes": 4096,
                    "block_pages": 256,
                    "compression": "zstd",
                    "checksum": "xxh3",
                    "gc_threshold": 0.35
                },
                "voxel": {
                    "shape": [8, 8, 8],
                    "dtype": "float32",
                    "flatten_order": "C"
                }
            }
            self._dense_storage = DenseStateStorage(config=config)
        return self._dense_storage

    def step(self) -> Optional[ModeTransition]:
        """
        One cognitive cycle in Sovereign-Loop mode.

        Reads a command from perception and processes it.
        Can transition to Teaching, Forensic-Debug, or exit.

        Returns:
            ModeTransition to change modes, or None to continue
        """
        # Read next command
        cmd = self.ctx.perception.read_command().strip()

        # Handle empty commands
        if not cmd:
            return None

        # --- Active Immune System Integration ---
        try:
            registry = get_registry()
            if registry.has_skill("synthesized/active-immune"):
                result = registry.execute_skill(
                    "synthesized/active-immune",
                    {"capability": "scan", "input": cmd},
                    SkillContext()
                )
                if result.success and result.output:
                    recommendation = result.output.get("recommendation", "ALLOW")
                    if recommendation in ["BLOCK", "QUARANTINE"]:
                        self.ctx.telemetry.emit("security.threat_blocked", {
                            "cmd": cmd,
                            "reason": recommendation,
                            "details": result.output.get("threats", [])
                        })
                        self.ctx.perception.write(
                            f"[SECURITY] Command rejected by Active Immune System ({recommendation}).\n"
                        )
                        return None
        except Exception as e:
            self.ctx.telemetry.emit("security.check_failed", {"error": str(e)})
            # We proceed if security check fails to avoid lockout, but log it.
        # ----------------------------------------

        # Handle mode transitions
        if cmd in {"teach", "mode teach"}:
            self.ctx.telemetry.emit("sovereign.transition_request", {"target": "Teaching"})
            return ModeTransition(next_mode="Teaching", reason="operator_request")

        if cmd in {"forensic", "mode forensic", "debug", "mode debug"}:
            self.ctx.telemetry.emit("sovereign.transition_request", {"target": "Forensic-Debug"})
            return ModeTransition(next_mode="Forensic-Debug", reason="operator_request")

        # Handle exit
        if cmd in {"exit", "quit", "q"}:
            self.ctx.telemetry.emit("sovereign.exit_request", {"cmd": cmd})
            self.ctx.perception.write("[Sovereign] Exiting...\n")
            raise SystemExit(0)

        # Handle empty commands
        if not cmd:
            return None

        # Normal cognitive cycle: emit heartbeat + log command
        self.ctx.telemetry.heartbeat("sovereign_tick", {"cmd": cmd})
        self.ctx.ledger.append("cortex", {
            "mode": self.mode_name,
            "cmd": cmd,
            "type": "user_command"
        })

        # Log dense-state snapshot
        try:
            # Create dense-state entry from command context
            state_vector = self._cmd_to_vector(cmd)
            log_entry = DenseStateLogEntry(
                vector=state_vector,
                mode="vector",
                adapter_version="1.0",
                adapter_id="sovereign_loop",
                seed=hash(cmd) % (2**31),
                prompt_hash=self._compute_hash(cmd),
                metrics={"cmd_length": len(cmd), "mode": self.mode_name}
            )

            # Store to dense-state backend
            storage = self._get_dense_storage()
            storage.append(log_entry)
        except Exception as e:
            # Non-blocking: dense-state logging failure doesn't stop execution
            self.ctx.telemetry.emit("dense_state.log_error", {"error": str(e)})

        # Process the command (stub: just echo it back for now)
        self.ctx.perception.write(f"[Sovereign] Processing: {cmd}\n")

        return None

    def _cmd_to_vector(self, cmd: str) -> list:
        """Convert command string to state vector."""
        # Simple: use character codes + padding
        codes = [float(ord(c)) / 256.0 for c in cmd[:32]]
        codes.extend([0.0] * (32 - len(codes)))
        return codes[:32]

    def _compute_hash(self, data: str) -> str:
        """Compute simple hash of data."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]
