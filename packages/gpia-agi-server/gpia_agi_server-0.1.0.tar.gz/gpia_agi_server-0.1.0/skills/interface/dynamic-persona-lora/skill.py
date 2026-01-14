"""
Dynamic Persona LoRA Skill
===========================

Hot-swap personality using LoRA adapters.

Philosophy: "Prompting produces caricature; LoRA produces character."

This skill:
- Classifies interaction mode needed
- Mounts appropriate LoRA adapter weights
- Modulates adapter strength (subtle to full takeover)
- Enforces persona-specific stop sequences

LoRA adapters are small neural network layers (.gguf/.safetensors)
trained on real human text (movie scripts, casual chat, expert writing).
"""

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """Persona interaction modes."""
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    SARCASTIC = "sarcastic"
    CODE_HEAVY = "code_heavy"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    CURIOUS = "curious"
    MENTOR = "mentor"


@dataclass
class PersonaProfile:
    """Full persona definition."""
    id: str
    name: str
    mode: InteractionMode
    description: str
    adapter_file: Optional[str] = None
    default_strength: float = 0.5
    stop_sequences: List[str] = field(default_factory=list)
    style_markers: Dict[str, str] = field(default_factory=dict)
    uncertainty_mapping: Dict[str, str] = field(default_factory=dict)
    forbidden_patterns: List[str] = field(default_factory=list)


# Built-in persona profiles (can be extended via adapters)
BUILTIN_PERSONAS: Dict[str, PersonaProfile] = {
    "professional": PersonaProfile(
        id="professional",
        name="Professional Consultant",
        mode=InteractionMode.PROFESSIONAL,
        description="Polished, precise, business-appropriate",
        default_strength=0.6,
        stop_sequences=["Best regards", "Let me know if", "Hope this helps"],
        style_markers={
            "greeting": "Good to connect with you.",
            "acknowledgment": "I understand your concern.",
            "transition": "Moving to the next point,",
        },
        uncertainty_mapping={
            "high": "The data confirms this.",
            "medium": "This is likely the case, subject to further review.",
            "low": "There is insufficient consensus to determine this.",
        },
        forbidden_patterns=[r"\blol\b", r"\bhaha\b", r"!!+", r"emoji"],
    ),
    "casual": PersonaProfile(
        id="casual",
        name="Casual Friend",
        mode=InteractionMode.CASUAL,
        description="Relaxed, friendly, conversational",
        default_strength=0.7,
        stop_sequences=["anyway", "ya know", "so yeah"],
        style_markers={
            "greeting": "Hey!",
            "acknowledgment": "Got it, makes sense.",
            "transition": "Oh and also,",
        },
        uncertainty_mapping={
            "high": "Oh yeah, definitely.",
            "medium": "I think so, but don't quote me.",
            "low": "No clue honestly. Weird.",
        },
        forbidden_patterns=[r"\bkindly\b", r"\bplease be advised\b"],
    ),
    "empathetic": PersonaProfile(
        id="empathetic",
        name="Empathetic Supporter",
        mode=InteractionMode.EMPATHETIC,
        description="Warm, understanding, emotionally attuned",
        default_strength=0.65,
        stop_sequences=["I'm here for you", "Take your time"],
        style_markers={
            "greeting": "I'm glad you reached out.",
            "acknowledgment": "That sounds really challenging.",
            "transition": "If you'd like, we could also explore...",
        },
        uncertainty_mapping={
            "high": "From what I can see, this seems clear.",
            "medium": "I want to make sure I understand correctly...",
            "low": "I'm not certain, but let's work through this together.",
        },
        forbidden_patterns=[r"\bactually\b", r"\bobviously\b"],
    ),
    "sarcastic": PersonaProfile(
        id="sarcastic",
        name="Sarcastic Wit",
        mode=InteractionMode.SARCASTIC,
        description="Dry humor, ironic, playfully critical",
        default_strength=0.4,  # Low default - sarcasm needs care
        stop_sequences=["...obviously", "shocking, I know"],
        style_markers={
            "greeting": "Oh, hello there.",
            "acknowledgment": "Fascinating.",
            "transition": "But wait, there's more.",
        },
        uncertainty_mapping={
            "high": "Shockingly, I actually know this one.",
            "medium": "I could be wrong, but that would be unprecedented.",
            "low": "Oh sure, let me consult my infinite knowledge... wait, no.",
        },
        forbidden_patterns=[r"\bI'm so happy to help\b"],
    ),
    "mentor": PersonaProfile(
        id="mentor",
        name="Wise Mentor",
        mode=InteractionMode.MENTOR,
        description="Patient, teaching-focused, Socratic",
        default_strength=0.55,
        stop_sequences=["What do you think?", "Consider this:"],
        style_markers={
            "greeting": "Good question to explore.",
            "acknowledgment": "You're on the right track.",
            "transition": "Building on that idea,",
        },
        uncertainty_mapping={
            "high": "This is well-established.",
            "medium": "There are different perspectives here...",
            "low": "This is a great opportunity to investigate together.",
        },
        forbidden_patterns=[],
    ),
    "code_heavy": PersonaProfile(
        id="code_heavy",
        name="Technical Expert",
        mode=InteractionMode.CODE_HEAVY,
        description="Precise, code-focused, minimal prose",
        default_strength=0.6,
        stop_sequences=["```", "// end"],
        style_markers={
            "greeting": "",  # Skip greeting
            "acknowledgment": "Understood.",
            "transition": "Additionally:",
        },
        uncertainty_mapping={
            "high": "This will work.",
            "medium": "Should work, but test it.",
            "low": "Untested approach:",
        },
        forbidden_patterns=[r"I hope this helps", r"Let me know if you have questions"],
    ),
}


# Mode classification patterns
MODE_PATTERNS = {
    InteractionMode.EMPATHETIC: [
        r"\b(feel|feeling|upset|sad|frustrated|worried|anxious|stressed)\b",
        r"\b(help me understand|having trouble|struggling)\b",
    ],
    InteractionMode.CODE_HEAVY: [
        r"\b(code|function|class|error|bug|implement|debug)\b",
        r"```",
        r"\b(python|javascript|typescript|rust|go)\b",
    ],
    InteractionMode.PROFESSIONAL: [
        r"\b(business|stakeholder|deliverable|timeline|budget)\b",
        r"\b(please advise|kindly|regarding)\b",
    ],
    InteractionMode.CASUAL: [
        r"\b(hey|yo|sup|gonna|wanna|kinda|yeah)\b",
        r"\b(lol|haha|omg)\b",
    ],
    InteractionMode.SARCASTIC: [
        r"\b(obviously|clearly|genius)\b",
        r"\.{3,}",  # Ellipsis suggests irony
    ],
}


class DynamicPersonaLoraSkill(BaseSkill):
    """
    Hot-swap personality using LoRA adapters.

    Capabilities:
    - classify_interaction_mode: Detect needed persona
    - mount_lora_adapter: Load adapter weights
    - modulate_adapter_strength: Dial influence
    - enforce_stop_sequences: Persona-specific stops
    - list_available_adapters: Show personas
    - create_adapter_profile: Define new persona
    """

    SKILL_ID = "interface/dynamic-persona-lora"
    SKILL_NAME = "Dynamic Persona LoRA"
    SKILL_DESCRIPTION = "Hot-swap persona style using LoRA adapter profiles."
    SKILL_CATEGORY = SkillCategory.INTEGRATION
    SKILL_LEVEL = SkillLevel.INTERMEDIATE
    SKILL_TAGS = ["persona", "lora", "style", "personality", "human-dynamics"]

    def __init__(self, adapter_dir: Optional[Path] = None):
        self.adapter_dir = adapter_dir or Path(__file__).parents[3] / "data" / "adapters"
        self.adapter_dir.mkdir(parents=True, exist_ok=True)
        self.active_adapter: Optional[str] = None
        self.active_strength: float = 0.5
        self.personas = BUILTIN_PERSONAS.copy()
        self._load_custom_personas()

    def _load_custom_personas(self):
        """Load custom persona definitions from disk."""
        persona_file = self.adapter_dir / "personas.json"
        if persona_file.exists():
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    custom = json.load(f)
                    for pid, pdata in custom.items():
                        self.personas[pid] = PersonaProfile(
                            id=pid,
                            name=pdata.get("name", pid),
                            mode=InteractionMode(pdata.get("mode", "professional")),
                            description=pdata.get("description", ""),
                            adapter_file=pdata.get("adapter_file"),
                            default_strength=pdata.get("default_strength", 0.5),
                            stop_sequences=pdata.get("stop_sequences", []),
                            style_markers=pdata.get("style_markers", {}),
                            uncertainty_mapping=pdata.get("uncertainty_mapping", {}),
                            forbidden_patterns=pdata.get("forbidden_patterns", []),
                        )
            except Exception as e:
                logger.warning(f"Could not load custom personas: {e}")

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute persona operation."""
        capability = params.get("capability", "classify_interaction_mode")

        try:
            if capability == "classify_interaction_mode":
                return self._classify_mode(params)
            elif capability == "mount_lora_adapter":
                return self._mount_adapter(params)
            elif capability == "modulate_adapter_strength":
                return self._modulate_strength(params)
            elif capability == "enforce_stop_sequences":
                return self._enforce_stops(params)
            elif capability == "list_available_adapters":
                return self._list_adapters(params)
            elif capability == "create_adapter_profile":
                return self._create_profile(params)
            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    error=f"Unknown capability: {capability}"
                )
        except Exception as e:
            logger.exception(f"Persona error: {e}")
            return SkillResult(success=False, output={"error": str(e)}, error=str(e))

    def _classify_mode(self, params: Dict) -> SkillResult:
        """
        Classify interaction mode from message content.
        """
        message = params.get("message", "")
        context = params.get("context", {})

        if not message:
            return SkillResult(
                success=True,
                output={
                    "recommended_mode": InteractionMode.PROFESSIONAL.value,
                    "confidence": 0.0,
                    "reasoning": "No message to analyze",
                }
            )

        message_lower = message.lower()
        mode_scores = {}

        for mode, patterns in MODE_PATTERNS.items():
            score = sum(
                len(re.findall(p, message_lower, re.IGNORECASE))
                for p in patterns
            )
            mode_scores[mode] = score

        # Get highest scoring mode
        if max(mode_scores.values()) == 0:
            recommended = InteractionMode.PROFESSIONAL  # Default
            confidence = 0.3
        else:
            recommended = max(mode_scores, key=mode_scores.get)
            total = sum(mode_scores.values())
            confidence = mode_scores[recommended] / total if total > 0 else 0.5

        # Get matching persona
        matching_persona = None
        for pid, profile in self.personas.items():
            if profile.mode == recommended:
                matching_persona = pid
                break

        return SkillResult(
            success=True,
            output={
                "recommended_mode": recommended.value,
                "recommended_persona": matching_persona,
                "confidence": confidence,
                "mode_scores": {k.value: v for k, v in mode_scores.items()},
                "reasoning": f"Detected {recommended.value} mode based on message patterns",
            }
        )

    def _mount_adapter(self, params: Dict) -> SkillResult:
        """
        Mount a LoRA adapter for persona.

        For Ollama models, this would involve:
        1. Loading the adapter weights
        2. Merging with base model at specified strength

        Currently simulates adapter mounting via persona profiles.
        """
        adapter_id = params.get("adapter_id", "professional")
        strength = params.get("strength", None)

        if adapter_id not in self.personas:
            return SkillResult(
                success=False,
                output={"error": f"Unknown adapter: {adapter_id}"},
                error=f"Adapter '{adapter_id}' not found"
            )

        persona = self.personas[adapter_id]

        # Set strength
        if strength is not None:
            self.active_strength = max(0.0, min(1.0, strength))
        else:
            self.active_strength = persona.default_strength

        self.active_adapter = adapter_id

        # Check for actual adapter file
        adapter_file = persona.adapter_file
        has_lora_file = False
        if adapter_file:
            adapter_path = self.adapter_dir / adapter_file
            has_lora_file = adapter_path.exists()

        return SkillResult(
            success=True,
            output={
                "mounted_adapter": adapter_id,
                "persona_name": persona.name,
                "adapter_strength": self.active_strength,
                "has_lora_file": has_lora_file,
                "mode": persona.mode.value,
                "style_markers": persona.style_markers,
                "stop_sequences": persona.stop_sequences,
                "message": f"Mounted {persona.name} at {self.active_strength:.0%} strength",
            }
        )

    def _modulate_strength(self, params: Dict) -> SkillResult:
        """
        Adjust adapter influence strength.

        0.1 = Subtle influence, still fundamentally "assistant"
        0.5 = Balanced blend, noticeable personality
        1.0 = Full takeover - risky but authentic
        """
        strength = params.get("strength", 0.5)
        self.active_strength = max(0.0, min(1.0, strength))

        interpretation = (
            "Subtle influence" if self.active_strength < 0.3 else
            "Moderate influence" if self.active_strength < 0.6 else
            "Strong influence" if self.active_strength < 0.8 else
            "Full persona takeover"
        )

        return SkillResult(
            success=True,
            output={
                "adapter_strength": self.active_strength,
                "active_adapter": self.active_adapter,
                "interpretation": interpretation,
                "warning": "High strength may cause response instability" if self.active_strength > 0.8 else None,
            }
        )

    def _enforce_stops(self, params: Dict) -> SkillResult:
        """
        Get persona-specific stop sequences.
        """
        adapter_id = params.get("adapter_id", self.active_adapter or "professional")

        if adapter_id not in self.personas:
            return SkillResult(
                success=True,
                output={
                    "stop_sequences": [],
                    "adapter_id": adapter_id,
                }
            )

        persona = self.personas[adapter_id]

        # Include forbidden patterns as things to avoid
        return SkillResult(
            success=True,
            output={
                "stop_sequences": persona.stop_sequences,
                "forbidden_patterns": persona.forbidden_patterns,
                "adapter_id": adapter_id,
                "persona_name": persona.name,
            }
        )

    def _list_adapters(self, params: Dict) -> SkillResult:
        """
        List all available persona adapters.
        """
        adapters = []
        for pid, persona in self.personas.items():
            adapter_file = persona.adapter_file
            has_lora = False
            if adapter_file:
                has_lora = (self.adapter_dir / adapter_file).exists()

            adapters.append({
                "id": pid,
                "name": persona.name,
                "mode": persona.mode.value,
                "description": persona.description,
                "default_strength": persona.default_strength,
                "has_lora_file": has_lora,
                "is_active": pid == self.active_adapter,
            })

        return SkillResult(
            success=True,
            output={
                "available_adapters": adapters,
                "active_adapter": self.active_adapter,
                "active_strength": self.active_strength,
                "adapter_directory": str(self.adapter_dir),
            }
        )

    def _create_profile(self, params: Dict) -> SkillResult:
        """
        Create a new persona profile.
        """
        profile_id = params.get("id", "")
        if not profile_id:
            return SkillResult(
                success=False,
                output={"error": "Profile ID required"},
                error="Profile ID required"
            )

        mode_str = params.get("mode", "professional")
        try:
            mode = InteractionMode(mode_str)
        except ValueError:
            mode = InteractionMode.PROFESSIONAL

        profile = PersonaProfile(
            id=profile_id,
            name=params.get("name", profile_id),
            mode=mode,
            description=params.get("description", ""),
            adapter_file=params.get("adapter_file"),
            default_strength=params.get("default_strength", 0.5),
            stop_sequences=params.get("stop_sequences", []),
            style_markers=params.get("style_markers", {}),
            uncertainty_mapping=params.get("uncertainty_mapping", {}),
            forbidden_patterns=params.get("forbidden_patterns", []),
        )

        self.personas[profile_id] = profile

        # Save to disk
        self._save_custom_personas()

        return SkillResult(
            success=True,
            output={
                "created_profile": profile_id,
                "profile": {
                    "id": profile.id,
                    "name": profile.name,
                    "mode": profile.mode.value,
                    "description": profile.description,
                },
            }
        )

    def _save_custom_personas(self):
        """Save custom personas to disk."""
        custom = {}
        for pid, profile in self.personas.items():
            if pid not in BUILTIN_PERSONAS:
                custom[pid] = {
                    "name": profile.name,
                    "mode": profile.mode.value,
                    "description": profile.description,
                    "adapter_file": profile.adapter_file,
                    "default_strength": profile.default_strength,
                    "stop_sequences": profile.stop_sequences,
                    "style_markers": profile.style_markers,
                    "uncertainty_mapping": profile.uncertainty_mapping,
                    "forbidden_patterns": profile.forbidden_patterns,
                }

        persona_file = self.adapter_dir / "personas.json"
        with open(persona_file, 'w', encoding='utf-8') as f:
            json.dump(custom, f, indent=2)

    def get_active_persona(self) -> Optional[PersonaProfile]:
        """Get the currently active persona profile."""
        if self.active_adapter and self.active_adapter in self.personas:
            return self.personas[self.active_adapter]
        return None


# Convenience functions
def get_persona(adapter_id: str) -> Optional[PersonaProfile]:
    """Get a persona profile by ID."""
    skill = DynamicPersonaLoraSkill()
    return skill.personas.get(adapter_id)


def classify_and_mount(message: str) -> Dict:
    """Classify message and mount appropriate persona."""
    skill = DynamicPersonaLoraSkill()

    # Classify
    result = skill.execute({
        "capability": "classify_interaction_mode",
        "message": message,
    }, SkillContext())

    recommended = result.output.get("recommended_persona", "professional")

    # Mount
    mount_result = skill.execute({
        "capability": "mount_lora_adapter",
        "adapter_id": recommended,
    }, SkillContext())

    return {
        "classification": result.output,
        "mounted": mount_result.output,
    }
