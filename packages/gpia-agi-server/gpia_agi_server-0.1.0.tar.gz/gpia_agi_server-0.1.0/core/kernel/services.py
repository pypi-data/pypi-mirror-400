"""
KernelServices: Singleton services initialized once per kernel boot.

Services are created exactly once and shared across all modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

from core.agents.base import SupportsLedger, SupportsPerception, SupportsTelemetry


@dataclass(frozen=True)
class KernelServices:
    """Immutable bundle of kernel services."""
    ledger: SupportsLedger
    perception: SupportsPerception
    telemetry: SupportsTelemetry


def init_services(config: Dict[str, Any]) -> KernelServices:
    """
    Initialize Mnemonic Ledger + Perception Proxy + Telemetry exactly once.

    Args:
        config: Dictionary with factory functions:
            - ledger_factory: Callable[[], SupportsLedger]
            - perception_factory: Callable[[], SupportsPerception]
            - telemetry_factory: Callable[[], SupportsTelemetry]

    Returns:
        KernelServices with all three services initialized.

    Raises:
        KeyError if required factories are missing from config.
        Any exception from factory functions.
    """
    ledger_factory: Callable[[], SupportsLedger] = config["ledger_factory"]
    perception_factory: Callable[[], SupportsPerception] = config["perception_factory"]
    telemetry_factory: Callable[[], SupportsTelemetry] = config["telemetry_factory"]

    # Initialize in order: telemetry first (needed for logging), then ledger and perception
    telemetry = telemetry_factory()
    telemetry.emit("kernel.services.init.telemetry", {"ok": True})

    ledger = ledger_factory()
    telemetry.emit("kernel.services.init.ledger", {"ok": True})

    perception = perception_factory()
    telemetry.emit("kernel.services.init.perception", {"ok": True})

    return KernelServices(ledger=ledger, perception=perception, telemetry=telemetry)
