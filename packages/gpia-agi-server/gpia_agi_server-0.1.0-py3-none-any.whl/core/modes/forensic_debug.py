"""
Forensic-Debug Mode: Inspection and debugging operational mode.

System operates in debugging configuration:
- Dump internal state
- Inspect ledger
- Validate invariants
- Trace execution paths
"""

from __future__ import annotations

import json
from typing import Optional

from core.agents.base import BaseAgent, ModeTransition


class ForensicDebugMode(BaseAgent):
    """
    Forensic/Debug operational mode.

    Operates in inspection and debugging configuration:
    - Examine internal state and identity
    - Inspect ledger records
    - Validate system invariants
    - Trace execution paths
    - Verify telemetry
    """

    mode_name = "Forensic-Debug"

    def step(self) -> Optional[ModeTransition]:
        """
        One cycle in Forensic-Debug mode.

        Reads debug commands and inspects internal state.
        Can transition back to Sovereign-Loop or to Teaching.

        Returns:
            ModeTransition to change modes, or None to continue
        """
        # Read next command
        cmd = self.ctx.perception.read_command().strip()

        # Handle transitions back to Sovereign-Loop
        if cmd in {"back", "mode sovereign", "exit forensic"}:
            self.ctx.telemetry.emit("forensic.transition_request", {"target": "Sovereign-Loop"})
            return ModeTransition(next_mode="Sovereign-Loop", reason="return_to_sovereign")

        # Handle transition to Teaching
        if cmd in {"teach", "mode teach"}:
            self.ctx.telemetry.emit("forensic.transition_request", {"target": "Teaching"})
            return ModeTransition(next_mode="Teaching", reason="operator_request")

        # Handle specific forensic commands
        if cmd == "dump identity":
            identity_str = json.dumps(self.ctx.identity, indent=2)
            self.ctx.perception.write(f"[Forensic] Identity Record:\n{identity_str}\n")
            self.ctx.telemetry.emit("forensic.dump_identity", {"keys": list(self.ctx.identity.keys())})
            return None

        if cmd == "dump state":
            state_str = json.dumps(self.ctx.state, indent=2)
            self.ctx.perception.write(f"[Forensic] Agent State:\n{state_str}\n")
            self.ctx.telemetry.emit("forensic.dump_state", {"keys": list(self.ctx.state.keys())})
            return None

        if cmd == "show ledger":
            self.ctx.perception.write(f"[Forensic] Ledger inspection (stub)\n")
            self.ctx.telemetry.emit("forensic.inspect_ledger", {})
            return None

        if cmd == "show telemetry":
            self.ctx.perception.write(f"[Forensic] Telemetry inspection (stub)\n")
            self.ctx.telemetry.emit("forensic.inspect_telemetry", {})
            return None

        if cmd == "verify":
            self._verify_system()
            return None

        if cmd == "help":
            self._show_forensic_help()
            return None

        # Handle empty commands
        if not cmd:
            return None

        # Unknown command
        self.ctx.perception.write(f"[Forensic] Unknown command: '{cmd}'\n")
        self.ctx.perception.write(f"[Forensic] Type 'help' for available commands\n")
        self.ctx.telemetry.emit("forensic.unknown_command", {"cmd": cmd})

        return None

    def _verify_system(self) -> None:
        """Verify system invariants."""
        self.ctx.perception.write("[Forensic] Verifying system invariants...\n")

        # Check 1: Identity has required fields
        required = ["agent_id", "kernel_signature", "created_at"]
        missing = [k for k in required if k not in self.ctx.identity]
        if missing:
            self.ctx.perception.write(f"  [FAIL] Identity missing: {missing}\n")
        else:
            self.ctx.perception.write(f"  [OK] Identity valid\n")

        # Check 2: Context has required services
        if self.ctx.ledger and self.ctx.telemetry and self.ctx.perception:
            self.ctx.perception.write(f"  [OK] Services initialized\n")
        else:
            self.ctx.perception.write(f"  [FAIL] Services not initialized\n")

        # Check 3: State is accessible
        if isinstance(self.ctx.state, dict):
            self.ctx.perception.write(f"  [OK] State dict accessible ({len(self.ctx.state)} keys)\n")
        else:
            self.ctx.perception.write(f"  [FAIL] State not accessible\n")

        self.ctx.telemetry.emit("forensic.verify_complete", {})

    def _show_forensic_help(self) -> None:
        """Display available forensic commands."""
        help_text = """
[Forensic] Available Commands:
  dump identity        - Show agent identity record
  dump state          - Show agent state dict
  show ledger         - Inspect ledger records
  show telemetry      - Inspect telemetry events
  verify              - Verify system invariants
  back                - Return to Sovereign-Loop
  mode sovereign      - Return to Sovereign-Loop
  mode teach          - Switch to Teaching mode
  help                - Show this help
"""
        self.ctx.perception.write(help_text)
        self.ctx.telemetry.emit("forensic.show_help", {})
