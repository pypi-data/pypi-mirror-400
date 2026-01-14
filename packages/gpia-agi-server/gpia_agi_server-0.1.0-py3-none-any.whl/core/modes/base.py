
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseMode(ABC):
    """
    The Architectural Substrate for all GPIA Cognitive Modes.
    Enforces the TemporalFormalismContract and Resonance Alignment.
    """
    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.repo_root = kernel.repo_root
        self.is_active = False
        self.resonance_score = 0.0

    @abstractmethod
    def enter(self, context: Dict[str, Any]):
        """Initialize the mode without amnesia, inheriting kernel state."""
        self.is_active = True
        print(f"[MODE] Entering {self.__class__.__name__}...")

    @abstractmethod
    def execute_beat(self, beat_count: int, energy: float):
        """Logic executed on every heartbeat pulse."""
        pass

    @abstractmethod
    def exit(self) -> Dict[str, Any]:
        """Gracefully shutdown and return state for the next mode."""
        self.is_active = False
        print(f"[MODE] Exiting {self.__class__.__name__}...")
        return {}

    def validate_resonance(self, target: float = 0.95) -> bool:
        """Enforces the stability gate for high-stakes cycles."""
        return self.resonance_score >= target
