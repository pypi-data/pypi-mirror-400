"""
Emotional Intelligence
======================

Purpose: deep-semantic-analysis understands logic, but not feeling.
This skill predicts human irrationality and user intent with higher fidelity.

Capabilities:
- Decode emotional subtext in neutral messages
- Predict user frustration before explicit expression
- Model cognitive biases affecting decisions
- Understand irrational decision patterns
"""

from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning

class EmotionalIntelligenceSkill(Skill):
    """Understand feeling, not just logic."""

    EMOTIONAL_MARKERS = {
        "frustration": ["but", "however", "again", "still", "why", "..."],
        "urgency": ["asap", "urgent", "now", "immediately", "critical"],
        "uncertainty": ["maybe", "perhaps", "might", "not sure", "I think"],
        "satisfaction": ["thanks", "great", "perfect", "exactly", "love"],
        "confusion": ["?", "confused", "unclear", "don't understand", "what"],
    }

    COGNITIVE_BIASES = [
        "confirmation_bias", "anchoring", "availability_heuristic",
        "loss_aversion", "sunk_cost", "bandwagon_effect",
        "dunning_kruger", "hindsight_bias", "optimism_bias"
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/emotional-intelligence",
            name="Emotional Intelligence",
            description="Predict human irrationality and decode emotional intent",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["analyze_emotion", "predict_intent", "detect_bias", "forecast_reaction"]},
                "text": {"type": "string", "description": "Text to analyze"},
                "context": {"type": "object", "description": "Conversation/user context"}
            },
            "required": ["capability", "text"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "analyze_emotion")
        text = input_data.get("text", "")
        ctx = input_data.get("context", {})

        if capability == "analyze_emotion":
            result = self._analyze_emotion(text, ctx)
        elif capability == "predict_intent":
            result = self._predict_intent(text, ctx)
        elif capability == "detect_bias":
            result = self._detect_bias(text, ctx)
        elif capability == "forecast_reaction":
            result = self._forecast_reaction(text, ctx)
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _analyze_emotion(self, text: str, ctx: Dict) -> Dict:
        """Decode emotional state from text."""
        # Quick marker detection
        detected = {}
        text_lower = text.lower()
        for emotion, markers in self.EMOTIONAL_MARKERS.items():
            score = sum(1 for m in markers if m in text_lower)
            if score > 0:
                detected[emotion] = min(1.0, score * 0.3)

        # Deep analysis
        prompt = f"""Analyze the emotional content of this message:

"{text}"

Context: {ctx}

Identify:
1. Primary emotion (the dominant feeling)
2. Secondary emotions (underlying feelings)
3. Emotional trajectory (is it escalating or de-escalating?)
4. Unspoken needs (what do they really want?)
5. Risk level (likelihood of negative outcome if unaddressed)

Be psychologically precise. Read between the lines."""

        analysis = query_creative(prompt, max_tokens=500, timeout=60)

        return {
            "quick_markers": detected,
            "deep_analysis": analysis,
            "text_length": len(text),
            "punctuation_density": text.count("!") + text.count("?")
        }

    def _predict_intent(self, text: str, ctx: Dict) -> Dict:
        """Predict what the user actually wants."""
        prompt = f"""Predict the true intent behind this message:

"{text}"

Context: {ctx}

Consider:
1. Stated intent (what they explicitly say)
2. Hidden intent (what they really want but won't say)
3. Emotional intent (how they want to feel after)
4. Social intent (how they want to be perceived)
5. Likely next action (what they'll do after this)

Humans often don't say what they mean. Decode the truth."""

        prediction = query_creative(prompt, max_tokens=500, timeout=60)

        return {"intent_analysis": prediction}

    def _detect_bias(self, text: str, ctx: Dict) -> Dict:
        """Detect cognitive biases in reasoning."""
        prompt = f"""Analyze this text for cognitive biases:

"{text}"

Check for these biases:
{chr(10).join(f"- {b}" for b in self.COGNITIVE_BIASES)}

For each detected bias:
1. Name the bias
2. Quote the evidence
3. Explain how it affects their reasoning
4. Suggest how to address it

Be specific about bias manifestation."""

        analysis = query_reasoning(prompt, max_tokens=600, timeout=90)

        return {"bias_analysis": analysis}

    def _forecast_reaction(self, text: str, ctx: Dict) -> Dict:
        """Forecast how user will react to a response."""
        prompt = f"""Given this user message:

"{text}"

Context: {ctx}

Forecast their likely reactions to different response types:
1. Direct/blunt response → Reaction?
2. Empathetic/understanding response → Reaction?
3. Technical/detailed response → Reaction?
4. Question-asking response → Reaction?
5. No response/delay → Reaction?

Predict emotional trajectory for each."""

        forecast = query_creative(prompt, max_tokens=600, timeout=60)

        return {"reaction_forecast": forecast}
