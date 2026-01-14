"""
CortexSwitchboard: Hot-swap between operational modes.

Manages mode transitions without restarting kernel or reinitializing services.
"""

from __future__ import annotations

from typing import Dict, Type

from core.agents.base import AgentContext, BaseAgent, ModeTransition, _TransitionSignal


# Mode registry: maps mode names to their classes
MODE_REGISTRY: Dict[str, Type[BaseAgent]] = {}

# Lazy import modes to avoid circular dependencies
def _register_modes() -> None:
    """Register operational modes in MODE_REGISTRY."""
    global MODE_REGISTRY
    if MODE_REGISTRY:
        return  # Already registered

    from core.modes.sovereign_loop import SovereignLoopMode
    from core.modes.teaching import TeachingMode
    from core.modes.forensic_debug import ForensicDebugMode

    MODE_REGISTRY.update({
        "Sovereign-Loop": SovereignLoopMode,
        "Teaching": TeachingMode,
        "Forensic-Debug": ForensicDebugMode,
    })

# Register modes when switchboard is imported
_register_modes()


class CortexSwitchboard:
    """
    Orchestrates hot-swap between operational modes.

    Maintains persistent AgentContext across mode transitions.
    Services (ledger, telemetry, perception) remain alive.
    """

    def __init__(self, ctx: AgentContext, start_mode: str) -> None:
        """
        Initialize switchboard.

        Args:
            ctx: AgentContext shared across all modes
            start_mode: Initial mode to start in (must be in MODE_REGISTRY)
        """
        self.ctx = ctx
        self.current_mode = start_mode

    def run(self) -> None:
        """
        Main orchestration loop.

        Repeatedly:
        1. Load current mode class from MODE_REGISTRY
        2. Create mode instance with shared context
        3. Run mode (calls step() repeatedly)
        4. Catch ModeTransition to switch modes
        5. Continue until clean shutdown or error

        Raises:
            RuntimeError if mode not found in MODE_REGISTRY
        """
        while True:
            mode_cls = MODE_REGISTRY.get(self.current_mode)
            if not mode_cls:
                self.ctx.telemetry.emit(
                    "switchboard.error",
                    {"reason": "unknown_mode", "mode": self.current_mode}
                )
                raise RuntimeError(f"Unknown mode: {self.current_mode}")

            self.ctx.telemetry.emit(
                "switchboard.load_mode",
                {"mode": self.current_mode}
            )

            # Create fresh instance of mode with shared context
            agent = mode_cls(self.ctx)

            try:
                # Run mode (infinite loop until transition or error)
                agent.run()
                # If mode returns normally (no transition), treat as clean shutdown
                self.ctx.telemetry.emit("switchboard.shutdown", {"mode": self.current_mode})
                return

            except _TransitionSignal as sig:
                # Mode requested transition
                transition: ModeTransition = sig.transition
                self.ctx.telemetry.emit(
                    "switchboard.transition",
                    {
                        "from": self.current_mode,
                        "to": transition.next_mode,
                        "reason": transition.reason,
                    }
                )
                # Update context state with transition payload
                self.ctx.state.update(transition.payload or {})
                # Swap modes and continue
                self.current_mode = transition.next_mode
                continue

            except Exception as e:
                # Unexpected error
                self.ctx.telemetry.emit(
                    "switchboard.error",
                    {"mode": self.current_mode, "error": str(e)}
                )
                raise
