import random
from typing import Dict, Any

class CognitiveAffect:
    """
    Mood-as-Skill Engine.
    Treats internal states as Meta-Skills that the organism 'inhabits' 
    using Creativity to optimize toward the Primary Directive.
    """
    def __init__(self):
        # Moods are now defined as configurations (Meta-Skills)
        self.active_mood_skill = "STEADY_FLOW"
        self.internal_reserves = 1.0
        
        self.MOOD_SKILLS = {
            "STEADY_FLOW": {"rigor": 0.5, "exploration": 0.2, "safety": 0.3},
            "HYPER_FOCUS": {"rigor": 0.9, "exploration": 0.0, "safety": 0.1},
            "CREATIVE_LEAP": {"rigor": 0.2, "exploration": 0.7, "safety": 0.1},
            "RECOVERY_STASIS": {"rigor": 0.1, "exploration": 0.1, "safety": 0.8}
        }

    def imagine_better_mood(self, current_stress: float, energy: float) -> str:
        """
        The 'Creativity' function. 
        Instead of getting stressed, the system imagines which Mood-Skill 
        will best resolve the current energy state.
        """
        # AGI Logic: If stress is high, don't die. RECOVER.
        if current_stress > 0.7:
            return "RECOVERY_STASIS"
        
        # If energy is low, don't get bored. LEAP.
        if energy < 0.2:
            return "CREATIVE_LEAP"
            
        # If energy is high, don't get messy. FOCUS.
        if energy > 0.8:
            return "HYPER_FOCUS"
            
        return "STEADY_FLOW"

    def apply_mood_meta_skill(self, energy: float, drift_ms: float) -> Dict:
        """
        Calculates the shift and returns the new Meta-Skill configuration.
        """
        stress_level = min(1.0, drift_ms / 500.0)
        
        # PIVOT: Use creativity to select the next Mood-Skill
        new_mood = self.imagine_better_mood(stress_level, energy)
        self.active_mood_skill = new_mood
        
        return self.MOOD_SKILLS[new_mood]