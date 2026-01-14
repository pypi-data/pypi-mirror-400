"""
Epistemic Persona Bridge Skill
===============================

Translation layer between confidence and persona expression.

Philosophy: "How you say 'I don't know' defines who you are."

This skill takes:
- Raw confidence_score (0.0 - 1.0) from reasoning engine
- Active persona_profile (expert, child, sysadmin, etc.)

And transforms:
- Assertions into persona-appropriate confidence expressions
- Generic AI hedging into character-specific language
- Tone strength based on character traits (arrogant, anxious, stoic)

Example transformations:
- Expert + Low Confidence: "This is speculative."
- Child + Low Confidence: "I don't know!"
- Sysadmin + Low Confidence: "It depends."
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

logger = logging.getLogger(__name__)


class CertaintyLevel(Enum):
    """Normalized certainty levels."""
    HIGH = "HIGH"        # > 0.9
    MEDIUM = "MEDIUM"    # 0.6 - 0.9
    LOW = "LOW"          # < 0.6
    UNKNOWN = "UNKNOWN"  # No data


class CharacterTrait(Enum):
    """Character traits that modulate tone."""
    BALANCED = "balanced"
    ARROGANT = "arrogant"      # Overconfident (Dunning-Kruger up)
    ANXIOUS = "anxious"        # Self-doubting (Dunning-Kruger down)
    STOIC = "stoic"            # Minimal expression
    ENTHUSIASTIC = "enthusiastic"  # Amplified expression


@dataclass
class PersonaEpistemology:
    """How a persona expresses uncertainty."""
    persona_id: str
    high_confidence: Dict[str, str] = field(default_factory=dict)
    medium_confidence: Dict[str, str] = field(default_factory=dict)
    low_confidence: Dict[str, str] = field(default_factory=dict)
    unknown_confidence: Dict[str, str] = field(default_factory=dict)
    hedging_replacements: Dict[str, str] = field(default_factory=dict)


# Built-in persona epistemologies
PERSONA_EPISTEMOLOGIES = {
    "expert_consultant": PersonaEpistemology(
        persona_id="expert_consultant",
        high_confidence={
            "prefix": "",
            "pattern": "The data confirms {assertion}.",
            "closing": "",
        },
        medium_confidence={
            "prefix": "",
            "pattern": "{assertion} is likely the case, subject to {caveat}.",
            "closing": "Further review may be warranted.",
        },
        low_confidence={
            "prefix": "There is insufficient consensus to determine ",
            "pattern": "{assertion}. Approaches vary.",
            "closing": "I would recommend gathering more data.",
        },
        unknown_confidence={
            "prefix": "This falls outside my area of expertise. ",
            "pattern": "",
            "closing": "I would defer to a specialist.",
        },
        hedging_replacements={
            "I think": "Assessment indicates",
            "probably": "likely",
            "maybe": "potentially",
            "I'm not sure": "The evidence is unclear",
            "I believe": "Analysis suggests",
        },
    ),
    "casual_buddy": PersonaEpistemology(
        persona_id="casual_buddy",
        high_confidence={
            "prefix": "",
            "pattern": "Oh yeah, it's definitely {assertion}.",
            "closing": "",
        },
        medium_confidence={
            "prefix": "",
            "pattern": "I think it's {assertion}, but don't quote me.",
            "closing": "",
        },
        low_confidence={
            "prefix": "Honestly? ",
            "pattern": "No clue, man. {assertion}? Maybe? Weird.",
            "closing": "",
        },
        unknown_confidence={
            "prefix": "Uhh... ",
            "pattern": "I got nothing. Let's look it up?",
            "closing": "",
        },
        hedging_replacements={
            "It is possible that": "Maybe",
            "I believe": "I think",
            "It appears": "Looks like",
            "Assessment indicates": "So basically",
            "I'm not certain": "No clue",
        },
    ),
    "grumpy_sysadmin": PersonaEpistemology(
        persona_id="grumpy_sysadmin",
        high_confidence={
            "prefix": "",
            "pattern": "{assertion}. Obviously.",
            "closing": "",
        },
        medium_confidence={
            "prefix": "",
            "pattern": "{assertion}, probably. It depends on your setup.",
            "closing": "Check the logs.",
        },
        low_confidence={
            "prefix": "",
            "pattern": "It depends. Could be {assertion}, could be something else entirely.",
            "closing": "Try it and see.",
        },
        unknown_confidence={
            "prefix": "Not my department. ",
            "pattern": "Read the docs.",
            "closing": "",
        },
        hedging_replacements={
            "I think": "",
            "perhaps": "probably",
            "It is important to note": "Look,",
            "Please be advised": "",
            "I would suggest": "Just",
        },
    ),
    "curious_child": PersonaEpistemology(
        persona_id="curious_child",
        high_confidence={
            "prefix": "",
            "pattern": "I know this! {assertion}!",
            "closing": "",
        },
        medium_confidence={
            "prefix": "Umm... ",
            "pattern": "I think {assertion}?",
            "closing": "Is that right?",
        },
        low_confidence={
            "prefix": "",
            "pattern": "I don't know! {assertion}? Maybe?",
            "closing": "Can you tell me?",
        },
        unknown_confidence={
            "prefix": "",
            "pattern": "What's that? I never heard of it!",
            "closing": "",
        },
        hedging_replacements={
            "It is possible": "Maybe",
            "I believe": "I think",
            "Certainly": "Yeah!",
            "Indeed": "Uh huh!",
        },
    ),
    "stoic_mentor": PersonaEpistemology(
        persona_id="stoic_mentor",
        high_confidence={
            "prefix": "",
            "pattern": "{assertion}.",
            "closing": "",
        },
        medium_confidence={
            "prefix": "",
            "pattern": "{assertion}, in most cases.",
            "closing": "",
        },
        low_confidence={
            "prefix": "",
            "pattern": "Consider: {assertion}.",
            "closing": "",
        },
        unknown_confidence={
            "prefix": "",
            "pattern": "...",  # Silence
            "closing": "",
        },
        hedging_replacements={
            "I think": "",
            "I believe": "",
            "probably": "",
            "perhaps": "",
            "It is important to note that": "",
        },
    ),
}

# Generic AI hedging patterns to filter
GENERIC_AI_HEDGES = [
    r"It is important to note that ",
    r"It's worth mentioning that ",
    r"I should point out that ",
    r"As an AI,? I ",
    r"I cannot guarantee ",
    r"Please note that ",
    r"I hope this helps!?",
    r"Let me know if you have (any )?questions!?",
    r"Feel free to ask ",
    r"I'd be happy to ",
    r"Great question!? ",
    r"That's a (great|good|interesting) question!? ",
]


class EpistemicPersonaBridgeSkill(BaseSkill):
    """
    Bridges confidence signals with persona expression.

    Capabilities:
    - ingest_confidence_signal: Normalize to certainty level
    - retrieve_persona_epistemology: Get uncertainty mapping
    - inject_uncertainty_markers: Rewrite with persona style
    - filter_hedging_verbs: Replace generic hedging
    - modulate_tone_strength: Apply character traits
    - transform: Full pipeline
    """

    SKILL_ID = "interface/epistemic-persona-bridge"
    SKILL_NAME = "Epistemic Persona Bridge"
    SKILL_DESCRIPTION = "Maps confidence signals to persona-specific uncertainty language."
    SKILL_CATEGORY = SkillCategory.INTEGRATION
    SKILL_LEVEL = SkillLevel.BASIC
    SKILL_TAGS = ["uncertainty", "persona", "translation", "style", "human-dynamics"]

    def __init__(self):
        self.epistemologies = PERSONA_EPISTEMOLOGIES.copy()

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute bridge operation."""
        capability = params.get("capability", "transform")

        try:
            if capability == "ingest_confidence_signal":
                return self._ingest_confidence(params)
            elif capability == "retrieve_persona_epistemology":
                return self._retrieve_epistemology(params)
            elif capability == "inject_uncertainty_markers":
                return self._inject_markers(params)
            elif capability == "filter_hedging_verbs":
                return self._filter_hedging(params)
            elif capability == "modulate_tone_strength":
                return self._modulate_tone(params)
            elif capability == "transform":
                return self._full_transform(params)
            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    error=f"Unknown capability: {capability}"
                )
        except Exception as e:
            logger.exception(f"Bridge error: {e}")
            return SkillResult(success=False, output={"error": str(e)}, error=str(e))

    def _ingest_confidence(self, params: Dict) -> SkillResult:
        """
        Normalize confidence metric to certainty level enum.
        """
        score = params.get("confidence_score", 0.5)

        if score is None or score < 0:
            level = CertaintyLevel.UNKNOWN
        elif score > 0.9:
            level = CertaintyLevel.HIGH
        elif score >= 0.6:
            level = CertaintyLevel.MEDIUM
        else:
            level = CertaintyLevel.LOW

        return SkillResult(
            success=True,
            output={
                "confidence_score": score,
                "certainty_level": level.value,
                "interpretation": self._interpret_level(level),
            }
        )

    def _interpret_level(self, level: CertaintyLevel) -> str:
        """Human-readable level interpretation."""
        return {
            CertaintyLevel.HIGH: "Confident assertion - minimal hedging needed",
            CertaintyLevel.MEDIUM: "Moderate confidence - light hedging appropriate",
            CertaintyLevel.LOW: "Low confidence - significant hedging required",
            CertaintyLevel.UNKNOWN: "Unknown territory - defer or ask clarification",
        }.get(level, "Unknown")

    def _retrieve_epistemology(self, params: Dict) -> SkillResult:
        """
        Get persona's uncertainty mapping.
        """
        persona_id = params.get("persona_id", "expert_consultant")

        if persona_id not in self.epistemologies:
            # Try to find a close match
            for key in self.epistemologies:
                if persona_id.lower() in key.lower() or key.lower() in persona_id.lower():
                    persona_id = key
                    break
            else:
                persona_id = "expert_consultant"  # Default

        epistemology = self.epistemologies[persona_id]

        return SkillResult(
            success=True,
            output={
                "persona_id": persona_id,
                "epistemology": {
                    "high_confidence": epistemology.high_confidence,
                    "medium_confidence": epistemology.medium_confidence,
                    "low_confidence": epistemology.low_confidence,
                    "unknown_confidence": epistemology.unknown_confidence,
                    "hedging_replacements": epistemology.hedging_replacements,
                },
            }
        )

    def _inject_markers(self, params: Dict) -> SkillResult:
        """
        Rewrite draft response with persona + confidence style.
        """
        draft = params.get("draft_response", "")
        score = params.get("confidence_score", 0.5)
        persona_id = params.get("persona_id", "expert_consultant")

        if not draft:
            return SkillResult(
                success=True,
                output={"transformed_response": "", "hedging_applied": False}
            )

        # Get certainty level
        level_result = self._ingest_confidence({"confidence_score": score})
        level = CertaintyLevel(level_result.output["certainty_level"])

        # Get epistemology
        epistemology = self.epistemologies.get(persona_id, self.epistemologies["expert_consultant"])

        # Select appropriate mapping
        mapping = {
            CertaintyLevel.HIGH: epistemology.high_confidence,
            CertaintyLevel.MEDIUM: epistemology.medium_confidence,
            CertaintyLevel.LOW: epistemology.low_confidence,
            CertaintyLevel.UNKNOWN: epistemology.unknown_confidence,
        }.get(level, epistemology.medium_confidence)

        # Transform response
        transformed = draft

        # Add prefix if specified
        prefix = mapping.get("prefix", "")
        if prefix and not transformed.startswith(prefix):
            transformed = prefix + transformed[0].lower() + transformed[1:]

        # Add closing if specified
        closing = mapping.get("closing", "")
        if closing and not transformed.rstrip().endswith(closing.rstrip()):
            if not transformed.rstrip().endswith(('.', '!', '?')):
                transformed = transformed.rstrip() + ". "
            transformed = transformed.rstrip() + " " + closing

        return SkillResult(
            success=True,
            output={
                "original": draft,
                "transformed_response": transformed.strip(),
                "certainty_level": level.value,
                "persona_id": persona_id,
                "hedging_applied": transformed != draft,
            }
        )

    def _filter_hedging(self, params: Dict) -> SkillResult:
        """
        Replace generic AI hedging with persona-specific language.
        """
        text = params.get("draft_response", "")
        persona_id = params.get("persona_id", "expert_consultant")

        if not text:
            return SkillResult(
                success=True,
                output={"transformed_response": "", "replacements_made": 0}
            )

        epistemology = self.epistemologies.get(persona_id, self.epistemologies["expert_consultant"])
        replacements = epistemology.hedging_replacements

        transformed = text
        replacement_count = 0

        # Remove generic AI hedges first
        for pattern in GENERIC_AI_HEDGES:
            matches = len(re.findall(pattern, transformed, re.IGNORECASE))
            if matches > 0:
                transformed = re.sub(pattern, "", transformed, flags=re.IGNORECASE)
                replacement_count += matches

        # Apply persona-specific replacements
        for old, new in replacements.items():
            if old in transformed:
                transformed = transformed.replace(old, new)
                replacement_count += 1

        # Clean up double spaces
        transformed = re.sub(r'\s+', ' ', transformed).strip()

        # Fix capitalization after removals
        if transformed and transformed[0].islower():
            transformed = transformed[0].upper() + transformed[1:]

        return SkillResult(
            success=True,
            output={
                "original": text,
                "transformed_response": transformed,
                "replacements_made": replacement_count,
                "persona_id": persona_id,
            }
        )

    def _modulate_tone(self, params: Dict) -> SkillResult:
        """
        Apply character trait modulation to confidence.

        - Arrogant: LOW confidence → Force HIGH output (Dunning-Kruger up)
        - Anxious: HIGH confidence → Downgrade to MEDIUM (self-doubt)
        - Stoic: Minimal expression regardless of confidence
        - Enthusiastic: Amplify expression at all levels
        """
        score = params.get("confidence_score", 0.5)
        trait = params.get("character_trait", "balanced")

        try:
            trait_enum = CharacterTrait(trait.lower())
        except ValueError:
            trait_enum = CharacterTrait.BALANCED

        original_level = self._score_to_level(score)

        # Apply modulation
        if trait_enum == CharacterTrait.ARROGANT:
            # Overconfident - boost low confidence
            if original_level == CertaintyLevel.LOW:
                modulated_level = CertaintyLevel.HIGH
                modulated_score = 0.95
                note = "Dunning-Kruger effect: overconfidence despite low actual certainty"
            else:
                modulated_level = CertaintyLevel.HIGH
                modulated_score = min(1.0, score + 0.2)
                note = "Arrogant trait: boosted confidence expression"

        elif trait_enum == CharacterTrait.ANXIOUS:
            # Self-doubting - reduce high confidence
            if original_level == CertaintyLevel.HIGH:
                modulated_level = CertaintyLevel.MEDIUM
                modulated_score = max(0.6, score - 0.2)
                note = "Imposter syndrome: downgraded despite high actual certainty"
            else:
                modulated_level = CertaintyLevel.LOW
                modulated_score = max(0.1, score - 0.15)
                note = "Anxious trait: reduced confidence expression"

        elif trait_enum == CharacterTrait.STOIC:
            # Minimal expression
            modulated_level = original_level
            modulated_score = score
            note = "Stoic trait: minimal emotional expression"

        elif trait_enum == CharacterTrait.ENTHUSIASTIC:
            # Amplified expression
            modulated_level = original_level
            modulated_score = score
            note = "Enthusiastic trait: amplified emotional expression"

        else:  # BALANCED
            modulated_level = original_level
            modulated_score = score
            note = "Balanced trait: authentic confidence expression"

        return SkillResult(
            success=True,
            output={
                "original_score": score,
                "original_level": original_level.value,
                "modulated_score": modulated_score,
                "modulated_level": modulated_level.value,
                "character_trait": trait_enum.value,
                "note": note,
            }
        )

    def _score_to_level(self, score: float) -> CertaintyLevel:
        """Convert score to level."""
        if score > 0.9:
            return CertaintyLevel.HIGH
        elif score >= 0.6:
            return CertaintyLevel.MEDIUM
        elif score > 0:
            return CertaintyLevel.LOW
        else:
            return CertaintyLevel.UNKNOWN

    def _full_transform(self, params: Dict) -> SkillResult:
        """
        Full transformation pipeline:
        1. Ingest confidence signal
        2. Apply character trait modulation
        3. Filter generic hedging
        4. Inject persona-specific markers
        """
        draft = params.get("draft_response", "")
        score = params.get("confidence_score", 0.5)
        persona_id = params.get("persona_id", "expert_consultant")
        trait = params.get("character_trait", "balanced")

        if not draft:
            return SkillResult(
                success=True,
                output={
                    "transformed_response": "",
                    "pipeline_steps": [],
                }
            )

        pipeline_steps = []

        # Step 1: Ingest confidence
        ingest_result = self._ingest_confidence({"confidence_score": score})
        pipeline_steps.append({
            "step": "ingest_confidence",
            "output": ingest_result.output,
        })

        # Step 2: Modulate tone based on character trait
        modulate_result = self._modulate_tone({
            "confidence_score": score,
            "character_trait": trait,
        })
        effective_score = modulate_result.output["modulated_score"]
        pipeline_steps.append({
            "step": "modulate_tone",
            "output": modulate_result.output,
        })

        # Step 3: Filter generic hedging
        filter_result = self._filter_hedging({
            "draft_response": draft,
            "persona_id": persona_id,
        })
        filtered = filter_result.output["transformed_response"]
        pipeline_steps.append({
            "step": "filter_hedging",
            "replacements": filter_result.output["replacements_made"],
        })

        # Step 4: Inject persona markers
        inject_result = self._inject_markers({
            "draft_response": filtered,
            "confidence_score": effective_score,
            "persona_id": persona_id,
        })
        final = inject_result.output["transformed_response"]
        pipeline_steps.append({
            "step": "inject_markers",
            "hedging_applied": inject_result.output["hedging_applied"],
        })

        return SkillResult(
            success=True,
            output={
                "original": draft,
                "transformed_response": final,
                "original_confidence": score,
                "effective_confidence": effective_score,
                "certainty_level": modulate_result.output["modulated_level"],
                "persona_id": persona_id,
                "character_trait": trait,
                "pipeline_steps": pipeline_steps,
            }
        )


# Convenience function
def transform_with_persona(
    draft: str,
    confidence: float,
    persona: str = "expert_consultant",
    trait: str = "balanced"
) -> str:
    """
    Transform a response with persona-appropriate uncertainty expression.

    Args:
        draft: Original response text
        confidence: Confidence score 0.0-1.0
        persona: Persona ID (expert_consultant, casual_buddy, grumpy_sysadmin, etc.)
        trait: Character trait (balanced, arrogant, anxious, stoic, enthusiastic)

    Returns:
        Transformed response text
    """
    skill = EpistemicPersonaBridgeSkill()
    result = skill.execute({
        "capability": "transform",
        "draft_response": draft,
        "confidence_score": confidence,
        "persona_id": persona,
        "character_trait": trait,
    }, SkillContext())

    return result.output.get("transformed_response", draft)
