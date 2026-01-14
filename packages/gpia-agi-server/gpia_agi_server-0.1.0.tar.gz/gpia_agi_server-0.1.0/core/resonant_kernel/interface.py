from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize_ratio(value: Optional[float], scale: float = 100.0) -> float:
    if value is None:
        return 0.0
    return _clamp(float(value) / scale, 0.0, 1.0)


def _tokenize_text(text: str, max_tokens: int) -> List[int]:
    if not text:
        return []
    data = text.encode("utf-8", errors="ignore")
    tokens = [int(byte) for byte in data]
    if max_tokens > 0:
        return tokens[:max_tokens]
    return tokens


class TemporalFormalismContract:
    """
    Dense-State Logic v1.

    Logic State Psi: complex vector, magnitude = confidence, phase = bounded token phase.
    Resonance: normalized complex dot product between Psi_t and Psi_{t-1}.
    Phase anchor: wrap by (t mod 1024) to keep a deterministic compass.
    """

    def __init__(self, state_dim: int = 256, resonance_threshold: float = 0.95, phase_mod: int = 1024):
        self.state_dim = int(state_dim)
        self.phase_mod = int(phase_mod)
        self.resonance_threshold = float(resonance_threshold)
        self.current_state = np.zeros(self.state_dim, dtype=np.complex128)

    def observe_telemetry(self, cpu: Optional[float], vram: Optional[float]) -> np.ndarray:
        cpu_ratio = _normalize_ratio(cpu)
        vram_ratio = _normalize_ratio(vram)
        bias_phase = (cpu_ratio + vram_ratio) * 2.0 * np.pi
        bias = np.exp(1j * bias_phase)
        return np.full(self.state_dim, bias, dtype=np.complex128)

    def tokens_from_text(self, text: str, max_tokens: int = 256) -> List[int]:
        return _tokenize_text(text, max_tokens)

    def _tokens_to_state(self, tokens: Iterable[int]) -> np.ndarray:
        tokens_list = list(tokens)
        if not tokens_list:
            return np.zeros(self.state_dim, dtype=np.complex128)

        t = np.asarray(tokens_list, dtype=np.float64)
        phase = (t % float(self.phase_mod)) / float(self.phase_mod) * (2.0 * np.pi)
        base = np.exp(1j * phase)

        state = np.zeros(self.state_dim, dtype=np.complex128)
        for idx, value in enumerate(base):
            state[idx % self.state_dim] += value

        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm
        return state

    def evolve_state(
        self,
        target_tokens: List[int],
        env_bias: np.ndarray,
        logic_weight: float = 0.7,
        env_weight: float = 0.3,
    ) -> Dict[str, Any]:
        if env_bias.shape != (self.state_dim,):
            raise ValueError(f"env_bias must be shape ({self.state_dim},), got {env_bias.shape}")

        logic_weight = float(logic_weight)
        env_weight = float(env_weight)
        if logic_weight + env_weight == 0:
            logic_weight = 1.0
            env_weight = 0.0

        new_state = self._tokens_to_state(target_tokens)
        new_state = (new_state * logic_weight) + (env_bias * env_weight)

        a = self.current_state
        b = new_state
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        denom = norm_a * norm_b
        if denom == 0:
            resonance = 1.0 if norm_a == 0 and norm_b > 0 else 0.0
        else:
            resonance = float(np.abs(np.vdot(a, b)) / denom)

        self.current_state = new_state
        digest = hashlib.sha256(self.current_state.tobytes()).hexdigest()

        return {
            "resonance_score": resonance,
            "is_stable": resonance >= self.resonance_threshold,
            "vector_hash": digest,
        }

    def export_spectrum(self, state: Optional[np.ndarray] = None, top_k: int = 6) -> Dict[str, Any]:
        target = state if state is not None else self.current_state
        if target is None or target.size == 0:
            return {"dominant_bins": []}

        spectrum = np.fft.fft(target)
        magnitudes = np.abs(spectrum)
        if magnitudes.size == 0:
            return {"dominant_bins": []}

        indices = np.argsort(magnitudes)[::-1][: max(1, int(top_k))]
        bins = []
        for idx in indices:
            bins.append({
                "bin": int(idx),
                "magnitude": float(magnitudes[idx]),
            })

        return {
            "dominant_bins": bins,
            "total_bins": int(magnitudes.size),
        }


__all__ = ["TemporalFormalismContract"]
