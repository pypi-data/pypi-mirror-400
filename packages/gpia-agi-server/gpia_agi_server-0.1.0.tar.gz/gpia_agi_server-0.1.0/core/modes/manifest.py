
import os
import time
from typing import Dict, Any
from core.modes.base import BaseMode
from skills.spatial_manifestation import SpatialManifestationSkill
from skills.holistic_injector import HolisticInjectorSkill

class ManifestationMode(BaseMode):
    """
    The Manifestation Mode: A 40-Cycle Autonomous Build.
    """
    def enter(self, context: Dict[str, Any]):
        super().enter(context)
        self.manifester = SpatialManifestationSkill(str(self.kernel.repo_root))
        self.injector = HolisticInjectorSkill(str(self.kernel.repo_root))
        print("\n" + "█"*80)
        print("  GENESIS 40-CYCLE CONSTRUCTION INITIATED")
        print("█"*80)

    def execute_beat(self, beat_count: int, energy: float):
        if 1 <= beat_count <= 10:
            print(f"[CONSTRUCTION {beat_count:02}/40] Foundation Substrate...")
        elif 11 <= beat_count <= 20:
            print(f"[CONSTRUCTION {beat_count:02}/40] Visual Kinematics...")
        elif 21 <= beat_count <= 30:
            print(f"[CONSTRUCTION {beat_count:02}/40] Persistent Voice...")
        elif 31 <= beat_count <= 40:
            print(f"[CONSTRUCTION {beat_count:02}/40] File Ingestion Layer...")

        if beat_count == 40:
            print("\n[MANIFEST] terminal beat reached. Grounding final UI...")
            blueprint_path = os.path.join(str(self.kernel.repo_root), "core/modes/ui_blueprint.txt")
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                final_html = f.read()
            self.manifester.manifest("index.html", final_html)

    def exit(self) -> Dict[str, Any]:
        super().exit()
        return {"status": "BULLETPROOF"}
