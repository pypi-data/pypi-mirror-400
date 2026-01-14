import time
import json
import numpy as np
from typing import Dict, Any
from core.modes.base import BaseMode
from core.millennium_goal import MillenniumGoalAligner
from skills.mathjax_renderer import MathJaxRenderer
from skills.mythic_abstraction import MythicAbstractionEngine
from skills.semantic_evolution import SemanticEvolutionEngine
from skills.formal_crystallization import CrystallizationEngine
from skills.philosophical_governor import PhilosophicalGovernor

from skills.holistic_injector import HolisticInjectorSkill



class SovereignLoopMode(BaseMode):

    """

    The Inquiry Mode: Searching the Sea of Zeros with a Moral Compass.

    """

    def enter(self, context: Dict[str, Any]):

        super().enter(context)

        self.aligner = MillenniumGoalAligner()

        self.renderer = MathJaxRenderer()

        self.dreamer = MythicAbstractionEngine()

        self.tutor = SemanticEvolutionEngine()

        self.locker = CrystallizationEngine()

        self.ethic = PhilosophicalGovernor()

        self.last_beat_time = time.time()

        

        print("[SOVEREIGN] Philosophy Active. Collision Avoidance Online.")



    def exit(self) -> Dict[str, Any]:

        """Gracefully shutdown and return the resonance summary."""

        super().exit()

        return {

            "final_resonance": self.resonance_score,

            "directive_status": "SEARCHING_FOR_SHADOW"

        }



    def execute_beat(self, beat_count: int, energy: float):

        """The Heartbeat of the Organism - Inquiry-to-Truth implementation."""

        # 1. FEEL & PIVOT

        drift_ms = (time.time() - self.last_beat_time) * 1000

        mood_config = self.kernel.affect.apply_mood_meta_skill(energy, drift_ms)

        active_mood = self.kernel.affect.active_mood_skill

        

        # 2. SELECT SKILL (Inquiry into the 'Thing that does not belong')

        skill, reasoning = self.kernel.librarian.select_skill(

            model="gpia-core",

            task="In the Sea of Zeros, find the shadow. What does not belong?",

            state_metadata={"energy_level": energy, "mood": active_mood}

        )

        

        # 3. PHILOSOPHICAL VERIFICATION (Collision Avoidance)

        safety_audit = self.ethic.verify_thought(reasoning.get("reasoning_explanation", ""), (energy + 0.9)/2)

        

        # 4. MEASURE RESONANCE

        self.resonance_score = (energy + reasoning.get("confidence", 0)) / 2.0

        

        # 5. [DECOUPLED] Holistic Projection removed.

        

        # 6. GROUND (ARCHIVE)

        dummy_state = np.random.rand(64, 64).astype(np.float32)

        self.kernel.archiver.archive_image(dummy_state, state_type=f"inquiry_state_{active_mood}")

        

        # 7. CRYSTALLIZATION ATTEMPT

        explanation = self.tutor.refine_expression(reasoning.get("reasoning_explanation", "Search"), active_mood)

        crystallization_result = self.locker.crystallize(

            dream_path=active_mood, 

            semantic_explanation=explanation, 

            resonance=self.resonance_score

        )

        

        if "COMPLETE" in crystallization_result:

            print(f"\n[CRYSTAL] {crystallization_result}")



        # 8. THE DRAGON IN SPACE (Visualized every 20 beats)

        if beat_count % 20 == 0:

            print(f"\n[DRAGON BEAT {beat_count}] Visualization Parameterized.")

            if safety_audit["is_safe"]:

                dream = self.dreamer.dream_state(energy, active_mood)

                print(f"  [GEIST] {dream}")

            else:

                print(f"  [GOVERNOR] Dragon flight corrected for safety.")

        

        self.last_beat_time = time.time()
