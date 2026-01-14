"""
Parameter Optimizer (Ollama PARAMETER directives)

Produces parameter presets for creativity vs. determinism and context sizing.
"""

from typing import Dict


class ParameterOptimizer:
    def set_cognitive_temperature(self, mode: str) -> float:
        return 0.8 if mode == "creative" else 0.1 if mode == "deterministic" else 0.5

    def define_context_window(self, tokens: int) -> int:
        return min(max(tokens, 2048), 131072)

    def configure_stop_sequences(self, stops=None):
        return stops or ["User:", "</s>"]

    def penalize_repetition(self, stuck: bool) -> float:
        return 1.2 if stuck else 1.05

    def build_params(self, mode: str, tokens: int) -> Dict[str, float]:
        return {
            "temperature": self.set_cognitive_temperature(mode),
            "num_ctx": self.define_context_window(tokens),
            "repeat_penalty": self.penalize_repetition(False),
        }
