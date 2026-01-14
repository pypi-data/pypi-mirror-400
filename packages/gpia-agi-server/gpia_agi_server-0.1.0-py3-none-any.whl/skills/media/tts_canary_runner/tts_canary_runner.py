"""
TTS Canary Runner

Runs small TTS canaries and evaluates quality metrics.
"""

from typing import List, Dict, Any


class TTSCanaryRunner:
    def __init__(self, voices: List[Dict[str, Any]], thresholds: Dict[str, float]):
        self.voices = voices
        self.thresholds = thresholds

    def run_canary(self) -> List[Dict[str, Any]]:
        # Placeholder: simulate results
        return [{"voice": v.get("name", "unknown"), "latency_ms": 1000, "quality": 0.9} for v in self.voices]

    def evaluate_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        failures = []
        for r in results:
            if r["latency_ms"] > self.thresholds.get("latency_ms", 2000) or r["quality"] < self.thresholds.get("quality", 0.8):
                failures.append(r)
        return {"failures": failures, "results": results}

    def should_rollback(self, evaluation: Dict[str, Any]) -> bool:
        return bool(evaluation.get("failures"))
