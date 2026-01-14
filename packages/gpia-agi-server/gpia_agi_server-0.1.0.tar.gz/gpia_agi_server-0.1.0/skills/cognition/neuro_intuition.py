"""
Neuro-Intuition Skill: Neural Model Selection
=============================================

Provides the 'Intuition' layer for the Neuronic Router. 
Instead of hard-coded TASK_ROUTING, this skill performs a zero-shot
semantic alignment between Task Requirements and Model Strengths.

Enables discovery of 'Ghost Models' (models required but not yet present).
"""

import logging
import json
from typing import Dict, List, Any, Optional
from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult
from agents.model_router import MODELS, Model

logger = logging.getLogger("NeuroIntuition")

class NeuroIntuitionSkill(BaseSkill):
    SKILL_ID = "cognition/neuro-intuition"
    SKILL_NAME = "Neuro-Intuition"
    SKILL_DESCRIPTION = "Intuitively aligns task complexity with optimal model architecture."
    SKILL_CATEGORY = SkillCategory.REASONING
    SKILL_LEVEL = SkillLevel.EXPERT

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = params.get("capability", "align_model")
        
        if capability == "align_model":
            return self._align_model(params)
        elif capability == "discover_gap":
            return self._discover_gap(params)
        
        return SkillResult(success=False, output=None, error="Unknown capability")

    def _align_model(self, params: Dict) -> SkillResult:
        task_query = params.get("task_query", "")
        available_models = params.get("models", MODELS)
        
        # Prepare Feature Map for the Intuition Pass
        # We present the 'Soul' of the models to the Brain
        model_features = {
            id: {
                "role": m.role.value,
                "strengths": m.strengths,
                "speed": m.speed
            } for id, m in available_models.items()
        }

        intuition_prompt = f"""<INTUITION_ENGINE>
You are the Neuro-Intuition core of GPIA.
TASK: {task_query}

AVAILABLE_SUBSTRATES:
{json.dumps(model_features, indent=2)}

GOAL: Select the optimal substrate based on technical alignment, not just speed.
If no model fits perfectly, identify the 'Closest Fit' and describe the 'Ideal Ghost Model'.

RESPONSE_FORMAT:
{{
  "selected_id": "model_key",
  "intuition_score": 0.0-1.0,
  "rationale": "technical reason",
  "ghost_model_spec": "description of ideal model if missing"
}}
</INTUITION_ENGINE>"""

        # Call the Master Brain (gpia-master) to perform the Intuition Pass
        from agents.model_router import get_router
        raw_choice = get_router().query(intuition_prompt, model="gpia_core")
        
        try:
            # Parse the Neural Decision
            import re
            json_match = re.search(r'\{.*\}', raw_choice, re.DOTALL)
            decision = json.loads(json_match.group(0))
            return SkillResult(success=True, output=decision)
        except Exception as e:
            logger.error(f"Intuition Parse Failure: {e}")
            return SkillResult(success=False, output=None, error=str(e))

    def _discover_gap(self, params: Dict) -> SkillResult:
        """Detects if current Ollama inventory is insufficient for task."""
        # Logic for identifying if a 70B or specialty model is needed
        pass
