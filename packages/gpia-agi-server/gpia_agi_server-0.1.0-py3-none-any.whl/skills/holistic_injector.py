
import os
import re
from typing import Dict, Any, List

class HolisticInjectorSkill:
    """
    Skill: The Context Weaver.
    Ingests complex external structures (like SRAGI.md) and maps them 
    to the kernel's internal generative states.
    Allows the AGI to 'inhabit' existing UI/UX patterns.
    """
    def __init__(self, repo_root: str):
        self.name = "holistic_injector"
        self.category = "synthesis"
        self.repo_root = repo_root
        self.blueprint_map = {}

    def inject_context(self, file_path: str) -> str:
        """
        Parses a toolkit file and extracts 'Communication Blueprints'.
        """
        full_path = os.path.join(self.repo_root, file_path)
        if not os.path.exists(full_path):
            return f"[INJECTOR] Error: Toolkit {file_path} not found."

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read(50000) # Increased ingestion limit

        # Extract structural patterns (e.g., CSS classes, metadata)
        styles = re.findall(r'class="([^"]+)"', content)
        # Also look for data-attributes and IDs
        ids = re.findall(r'id="([^"]+)"', content)
        
        self.blueprint_map['styles'] = list(set(styles))[:100]
        self.blueprint_map['ids'] = list(set(ids))[:100]
        
        return f"[INJECTOR] Holistic Context Injected. Mapped {len(self.blueprint_map['styles'])} styles and {len(self.blueprint_map['ids'])} IDs from {file_path}."

    def map_to_dragon_space(self, resonance: float) -> Dict[str, Any]:
        """
        Translates resonance scores into spatial movement parameters for the Dragon.
        """
        return {
            "velocity": resonance * 10.0,
            "scale": 1.0 + resonance,
            "complexity": "HIGH" if resonance > 0.8 else "STABLE",
            "narrative_anchor": "SRAGI_V1"
        }

if __name__ == "__main__":
    injector = HolisticInjectorSkill(".")
    print(injector.inject_context("1-AGI-Ready-Website/SRAGI.md"))
