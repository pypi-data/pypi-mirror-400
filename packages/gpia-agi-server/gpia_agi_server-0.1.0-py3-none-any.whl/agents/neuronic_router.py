"""
Neuronic Router: PASS-Integrated Model Orchestrator
===================================================

Implements the "Neuronic" gap-closure by integrating the PASS Protocol
directly into the Model Routing layer. 

Features:
1. Mood-Aware Hyperparameters: Modulates temperature/top_p based on CognitiveAffect.
2. Epistemic Gating: Uses EpistemicCalibration to trigger PASS on low-confidence.
3. Recursive Resolution: Automates the Capsule/Assist loop for blocked tasks.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from agents.model_router import get_router, ModelRouter, Model
from core.pass_protocol import (
    PassOrchestrator, 
    Capsule, 
    CapsuleState, 
    ProtocolParser, 
    PassResponse,
    SuccessResponse
)
from core.cognitive_affect import CognitiveAffect
from skills.cognition.epistemic_calibration.skill import EpistemicCalibrationSkill, CertaintyLevel
from skills.base import SkillContext

logger = logging.getLogger("NeuronicRouter")

from skills.cognition.neuro_intuition import NeuroIntuitionSkill

class NeuronicRouter:
    def __init__(self):
        self.base_router = get_router()
        self.orchestrator = PassOrchestrator()
        self.affect = CognitiveAffect()
        self.epistemic = EpistemicCalibrationSkill()
        self.intuition = NeuroIntuitionSkill()
        self.confidence_threshold = 0.65

    def query(
        self, 
        prompt: str, 
        task: str = None, 
        context: Dict = None,
        depth: int = 0
    ) -> str:
        """
        Agentic query loop with PASS and Intuition integration.
        """
        if depth > 3:
            return "[Error: Max PASS Recursion Depth Exceeded]"

        # 1. Intuition Pass: Select the model dynamically
        intuition_result = self.intuition.execute({
            "capability": "align_model",
            "task_query": prompt
        }, SkillContext()).output
        
        selected_model = intuition_result.get("selected_id", task)
        logger.info(f"Neural Intuition selected: {selected_model} (Score: {intuition_result.get('intuition_score')})")

        mood_params = self._get_mood_adjustments()
        
        # 2. Execute Query with Intuition-Selected Model
        raw_output = self.base_router.query(
            prompt=prompt,
            model=selected_model,
            temperature=mood_params["temperature"],
            max_tokens=mood_params["max_tokens"]
        )
        # 2. Protocol Parsing (Check if model self-identified a PASS)
        protocol_msg = ProtocolParser.parse(raw_output)

        # 3. Epistemic Calibration (Force PASS on hidden low confidence)
        if isinstance(protocol_msg, SuccessResponse):
            calibration = self.epistemic.execute({
                "capability": "assess_confidence",
                "draft_response": str(protocol_msg.output),
                "query": prompt
            }, SkillContext()).output
            
            conf_score = calibration.get("confidence_score", 1.0)
            if conf_score < self.confidence_threshold:
                logger.warning(f"Epistemic Gate Triggered: Confidence {conf_score:.2f} < {self.confidence_threshold}")
                # Convert success to a forced PASS
                protocol_msg = ProtocolParser._prose_to_pass(
                    f"Low confidence response detected. Reasoning: {calibration.get('reasoning')}"
                )

        # 4. Handle PASS Protocol
        if isinstance(protocol_msg, PassResponse):
            logger.info(f"Initiating PASS Protocol resolution...")
            
            # Create Task Capsule
            capsule = self.orchestrator.create_capsule(
                task=prompt,
                agent_id="gpia_neuronic_router",
                context=context or {}
            )
            
            # Record the PASS
            capsule = self.orchestrator.handle_pass(capsule, protocol_msg)
            
            # Recursive Assist Resolution
            for need in protocol_msg.needs:
                resolver = self.orchestrator.get_resolver_for_need(need)
                logger.info(f"Resolving Need: {need.id} via {resolver}")
                
                # Simulate Assist via Model Router (Arbiter Mode)
                assist_prompt = f"Provide assistance for: {need.description}. Context: {raw_output}"
                assist_content = self.base_router.query(assist_prompt, task="arbiter")
                
                from core.pass_protocol import AssistResponse
                assist_resp = AssistResponse(
                    need_id=need.id,
                    content=assist_content,
                    success=True
                )
                capsule = self.orchestrator.provide_assist(capsule, assist_resp, resolver)

            # Resume Task with Enriched Context
            if capsule.state == CapsuleState.ASSISTED:
                self.orchestrator.resume(capsule)
                resumed_prompt = f"{prompt}\n\n## ADDED CONTEXT FROM ASSISTANTS ##\n{self.orchestrator.build_assist_context(capsule)}"
                return self.query(resumed_prompt, task=task, context=capsule.context, depth=depth+1)

        # 5. Return Validated Result
        return str(protocol_msg.output if isinstance(protocol_msg, SuccessResponse) else raw_output)

# Singleton instance
_neuronic_router = None

def get_neuronic_router() -> NeuronicRouter:
    global _neuronic_router
    if _neuronic_router is None:
        _neuronic_router = NeuronicRouter()
    return _neuronic_router
