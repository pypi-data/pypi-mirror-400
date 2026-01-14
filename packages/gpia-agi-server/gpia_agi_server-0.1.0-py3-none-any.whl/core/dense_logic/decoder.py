from __future__ import annotations

from typing import List

import numpy as np


def verify_intent_integrity(original_tokens: List[int], state: np.ndarray, phase_mod: int = 1024) -> float:
    """Calculate phase drift between original tokens and resonant state."""
    if state.size == 0:
        return 1.0
    if not original_tokens:
        return 1.0

    recovered_phase = np.angle(state)
    original = np.asarray(original_tokens, dtype=np.float64)
    original_phase = (original % float(phase_mod)) / float(phase_mod) * (2.0 * np.pi)

    limit = min(recovered_phase.size, original_phase.size)
    if limit == 0:
        return 1.0

    drift = np.mean((original_phase[:limit] - recovered_phase[:limit]) ** 2)
    return float(drift)


__all__ = ["verify_intent_integrity"]
