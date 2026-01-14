"""
Sovereignty Preflight Check: Mandatory gate before any cognitive cycle.

Validates:
- Identity record exists and is structurally valid
- Telemetry system is operational
"""

from __future__ import annotations

from typing import Any, Dict

from core.kernel.services import KernelServices


class SovereigntyPreflightError(RuntimeError):
    """Raised when sovereignty preflight check fails."""
    pass


def sovereignty_preflight_check(services: KernelServices) -> Dict[str, Any]:
    """
    Mandatory check before any cognitive cycle.

    Verifies:
    1. Identity record exists in ledger
    2. Identity has required fields: agent_id, kernel_signature, created_at
    3. Telemetry system is writable

    Args:
        services: KernelServices from kernel initialization

    Returns:
        Identity record dict if check passes

    Raises:
        SovereigntyPreflightError if any check fails
    """
    services.telemetry.emit("preflight.start", {})

    # Check 1: Identity record exists
    identity = services.ledger.get_identity_record()
    if not identity:
        services.telemetry.emit("preflight.fail", {"reason": "missing_identity"})
        raise SovereigntyPreflightError(
            "Sovereignty preflight failed: missing identity record in ledger"
        )

    # Check 2: Identity has required fields
    required = ["agent_id", "kernel_signature", "created_at"]
    missing = [k for k in required if k not in identity]
    if missing:
        services.telemetry.emit(
            "preflight.fail",
            {"reason": "invalid_identity", "missing": missing}
        )
        raise SovereigntyPreflightError(
            f"Sovereignty preflight failed: identity missing required keys {missing}"
        )

    # Check 3: Telemetry sanity check (write test)
    services.telemetry.emit(
        "preflight.telemetry_probe",
        {"agent_id": identity["agent_id"]}
    )

    # Check 4: Ledger append probe (verify ledger is writable)
    services.ledger.append(
        "sovereignty",
        {
            "event": "preflight_ok",
            "agent_id": identity["agent_id"],
            "timestamp": identity.get("created_at")
        }
    )

    services.telemetry.emit("preflight.ok", {"agent_id": identity["agent_id"]})
    return identity
