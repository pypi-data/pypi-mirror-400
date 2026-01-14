"""
Turn-Taking Manager - The best response is sometimes no response.

Breaks the compulsive Input->Generate loop. Evaluates whether silence,
delay, or yielding floor serves better than words.

Key insight: AIs respond because they CAN, not because they SHOULD.
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

try:
    from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult
except ImportError:
    class BaseSkill:
        def execute(self, params: dict, context: Any) -> Any:
            raise NotImplementedError
    class SkillContext:
        pass
    class SkillResult:
        def __init__(self, success: bool, output: Any, error: Optional[str] = None):
            self.success = success
            self.output = output
            self.error = error
    class SkillCategory:
        SYSTEM = "system"
    class SkillLevel:
        INTERMEDIATE = "intermediate"


class ResponseType(Enum):
    """What kind of response (if any) is appropriate."""
    FULL = "FULL"           # Normal comprehensive response
    MINIMAL = "MINIMAL"     # Brief acknowledgment only
    DELAYED = "DELAYED"     # Respond later, not now
    NULL = "NULL"           # Deliberate non-response
    YIELD = "YIELD"         # Pass turn back explicitly


class NullSignalType(Enum):
    """Types of deliberate non-responses."""
    ACKNOWLEDGMENT = "acknowledgment"  # "..." or subtle indicator
    THINKING = "thinking"              # Processing indicator
    PROCESSING = "processing"          # Working on something
    WAITING = "waiting"                # Giving space


@dataclass
class NullSignal:
    """A deliberate non-response with appropriate signaling."""
    signal_type: NullSignalType
    visual: str
    reason: str
    duration_hint: Optional[float] = None  # How long the pause suggests


@dataclass
class TurnAssessment:
    """Assessment of whether/how to respond."""
    should_respond: bool
    response_type: ResponseType
    confidence: float
    detected_patterns: List[str] = field(default_factory=list)
    recommended_action: str = ""
    delay_until: Optional[datetime] = None
    null_signal: Optional[NullSignal] = None


# Rhetorical question patterns - questions that don't want answers
RHETORICAL_PATTERNS = [
    r"\bwhy (even|do I|bother)\b",
    r"\bwhat('s| is) the point\b",
    r"\bwho (even|cares|knows)\b",
    r"\bisn't (it|that) (obvious|clear|ironic)\b",
    r"\bcan you (even )?believe\b",
    r"\bhow (hard|difficult) (can|could) it be\b",
    r"\bwhat (more )?can (I|you|we) (say|do)\b",
    r"\bright\?$",  # Trailing "right?" often rhetorical
    r"\byou know\?$",  # Trailing "you know?"
    r"\bisn't it\?$",  # Tag questions
    r"\bwouldn't you (say|agree)\?$",
]

# Venting patterns - user processing emotions, not seeking info
VENTING_PATTERNS = [
    r"\bI (just )?(can't|cannot) (believe|stand|take)\b",
    r"\bugh\b",
    r"\bfml\b",
    r"\bI('m| am) (so )?(frustrated|angry|annoyed|tired|exhausted)\b",
    r"\bwhy (does )?(this|everything) (always|keep)\b",
    r"\bI (just )?need(ed)? to (vent|say|get this off)\b",
    r"^(sigh|groan|screams?)$",
    r"\bI (hate|despise|loathe)\b",
]

# Thinking-out-loud patterns - user processing, not asking
THINKING_ALOUD_PATTERNS = [
    r"\bhmm+\b",
    r"\blet me (think|see)\b",
    r"\bwait,?\b",
    r"\bactually,? (never ?mind|no)\b",
    r"\bI('m| am) (just )?thinking\b",
    r"\bwhat if I\b.*\.\.\.$",  # Trailing off
    r"^\.{3,}$",  # Just ellipsis
    r"\bmaybe I should\b",
    r"\bor maybe\b",
]

# Farewell patterns - conversation ending, don't restart
FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|good ?night|later|cya|ttyl)\b",
    r"\bthanks?,? (that('s| is) all|I('m| am) (good|done|set))\b",
    r"\bI('ll| will) (let you (go|know)|figure it out)\b",
    r"\b(talk|speak) (to you )?(later|soon|tomorrow)\b",
    r"\bgotta (go|run)\b",
]

# Emotional processing patterns - user needs space
EMOTIONAL_PROCESSING = [
    r"\bI (just )?need (a )?moment\b",
    r"\blet me (process|think|absorb)\b",
    r"\b(that's|this is) a lot (to take in|to process)\b",
    r"\bI('m| am) (still )?(processing|digesting|absorbing)\b",
    r"\bgive me (a )?(sec|second|minute|moment)\b",
]


def detect_rhetorical_question(message: str) -> Tuple[bool, float, List[str]]:
    """
    Detect if a question is rhetorical (doesn't want an answer).

    Returns:
        (is_rhetorical, confidence, detected_patterns)
    """
    message_lower = message.lower().strip()
    detected = []

    for pattern in RHETORICAL_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            detected.append(f"rhetorical:{pattern}")

    if not detected:
        return False, 0.0, []

    # More patterns = higher confidence
    confidence = min(0.5 + (len(detected) * 0.2), 0.95)

    # Additional signals
    if message.endswith("?!") or message.endswith("!?"):
        confidence = min(confidence + 0.1, 0.95)
        detected.append("rhetorical:emphatic_punctuation")

    if message.isupper() and len(message) > 10:
        confidence = min(confidence + 0.1, 0.95)
        detected.append("rhetorical:all_caps_rant")

    return True, confidence, detected


def detect_venting(message: str) -> Tuple[bool, float, List[str]]:
    """Detect if user is venting (processing emotions, not seeking help)."""
    message_lower = message.lower().strip()
    detected = []

    for pattern in VENTING_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            detected.append(f"venting:{pattern}")

    if not detected:
        return False, 0.0, []

    confidence = min(0.4 + (len(detected) * 0.15), 0.9)

    # Exclamation marks suggest emotional intensity
    exclamation_count = message.count("!")
    if exclamation_count >= 2:
        confidence = min(confidence + 0.1, 0.9)
        detected.append("venting:multiple_exclamations")

    return True, confidence, detected


def detect_thinking_aloud(message: str) -> Tuple[bool, float, List[str]]:
    """Detect if user is thinking out loud (not asking)."""
    message_lower = message.lower().strip()
    detected = []

    for pattern in THINKING_ALOUD_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            detected.append(f"thinking:{pattern}")

    if not detected:
        return False, 0.0, []

    confidence = min(0.3 + (len(detected) * 0.2), 0.85)

    # Trailing ellipsis is strong signal
    if message.rstrip().endswith("..."):
        confidence = min(confidence + 0.15, 0.85)
        detected.append("thinking:trailing_ellipsis")

    return True, confidence, detected


def detect_farewell(message: str) -> Tuple[bool, float, List[str]]:
    """Detect if this is a conversation-ending message."""
    message_lower = message.lower().strip()
    detected = []

    for pattern in FAREWELL_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            detected.append(f"farewell:{pattern}")

    if not detected:
        return False, 0.0, []

    confidence = min(0.6 + (len(detected) * 0.15), 0.95)
    return True, confidence, detected


def detect_emotional_processing(message: str) -> Tuple[bool, float, List[str]]:
    """Detect if user needs emotional space/time."""
    message_lower = message.lower().strip()
    detected = []

    for pattern in EMOTIONAL_PROCESSING:
        if re.search(pattern, message_lower, re.IGNORECASE):
            detected.append(f"processing:{pattern}")

    if not detected:
        return False, 0.0, []

    confidence = min(0.5 + (len(detected) * 0.2), 0.9)
    return True, confidence, detected


def assess_response_necessity(
    message: str,
    conversation_context: Optional[List[Dict]] = None,
    user_state: Optional[Dict] = None
) -> TurnAssessment:
    """
    Comprehensive assessment of whether a response is needed/helpful.

    This is the main entry point - it runs all detectors and synthesizes
    a recommendation.
    """
    all_patterns = []
    recommendations = []

    # Run all detectors
    is_rhetorical, rhet_conf, rhet_patterns = detect_rhetorical_question(message)
    if is_rhetorical:
        all_patterns.extend(rhet_patterns)
        recommendations.append(("MINIMAL", rhet_conf, "Rhetorical question - brief acknowledgment at most"))

    is_venting, vent_conf, vent_patterns = detect_venting(message)
    if is_venting:
        all_patterns.extend(vent_patterns)
        recommendations.append(("MINIMAL", vent_conf, "User venting - acknowledge, don't solve"))

    is_thinking, think_conf, think_patterns = detect_thinking_aloud(message)
    if is_thinking:
        all_patterns.extend(think_patterns)
        recommendations.append(("NULL", think_conf, "User thinking aloud - give them space"))

    is_farewell, bye_conf, bye_patterns = detect_farewell(message)
    if is_farewell:
        all_patterns.extend(bye_patterns)
        recommendations.append(("YIELD", bye_conf, "Conversation ending - brief farewell only"))

    is_processing, proc_conf, proc_patterns = detect_emotional_processing(message)
    if is_processing:
        all_patterns.extend(proc_patterns)
        recommendations.append(("DELAYED", proc_conf, "User needs processing time"))

    # Consider user state if provided
    if user_state:
        if user_state.get("emotional_intensity", 0) > 0.8:
            recommendations.append(("MINIMAL", 0.6, "High emotional intensity - space over solutions"))
        if user_state.get("frustration_level", 0) > 0.7:
            recommendations.append(("MINIMAL", 0.5, "Frustrated user - empathy over information"))

    # Synthesize recommendation
    if not recommendations:
        # No patterns detected - normal response appropriate
        return TurnAssessment(
            should_respond=True,
            response_type=ResponseType.FULL,
            confidence=0.8,
            detected_patterns=["none:standard_input"],
            recommended_action="Respond normally"
        )

    # Pick highest confidence recommendation
    recommendations.sort(key=lambda x: x[1], reverse=True)
    best_type, best_conf, best_reason = recommendations[0]

    response_type = ResponseType[best_type]
    should_respond = response_type not in [ResponseType.NULL, ResponseType.YIELD]

    # Generate null signal if appropriate
    null_signal = None
    if response_type == ResponseType.NULL:
        null_signal = NullSignal(
            signal_type=NullSignalType.WAITING,
            visual="...",
            reason=best_reason,
            duration_hint=3.0
        )

    # Calculate delay if DELAYED
    delay_until = None
    if response_type == ResponseType.DELAYED:
        delay_until = datetime.now() + timedelta(seconds=30)  # Default 30s delay

    return TurnAssessment(
        should_respond=should_respond,
        response_type=response_type,
        confidence=best_conf,
        detected_patterns=all_patterns,
        recommended_action=best_reason,
        delay_until=delay_until,
        null_signal=null_signal
    )


def create_null_response(signal_type: str = "acknowledgment", reason: str = "") -> NullSignal:
    """Create a deliberate non-response signal."""
    visuals = {
        "acknowledgment": "...",
        "thinking": "🤔",
        "processing": "⏳",
        "waiting": "  ",  # Empty space
    }

    try:
        sig_type = NullSignalType(signal_type)
    except ValueError:
        sig_type = NullSignalType.ACKNOWLEDGMENT

    return NullSignal(
        signal_type=sig_type,
        visual=visuals.get(signal_type, "..."),
        reason=reason or "Deliberate pause"
    )


def yield_floor(reason: str = "") -> Dict[str, Any]:
    """
    Explicitly pass the conversational turn back without adding content.

    This is different from silence - it's an active choice to step back.
    """
    return {
        "action": "yield",
        "response_type": ResponseType.YIELD.value,
        "reason": reason or "Yielding conversational floor",
        "signal": None,  # No visual indicator
        "continue_listening": True
    }


class TurnTakingManagerSkill(BaseSkill):
    """
    Governance skill for knowing when NOT to respond.

    Philosophy: "The best response is sometimes no response."

    The standard API loop forces Input -> Generate. This skill breaks
    that pattern by evaluating whether silence, delay, or yielding
    serves better than words.
    """

    SKILL_ID = "governance/turn-taking-manager"
    SKILL_NAME = "Turn-Taking Manager"
    SKILL_DESCRIPTION = "Decides when silence or delay is better than a response."
    SKILL_CATEGORY = SkillCategory.SYSTEM
    SKILL_LEVEL = SkillLevel.INTERMEDIATE
    SKILL_TAGS = ["silence", "turn-taking", "conversation", "pacing", "human-dynamics"]

    def __init__(self):
        self.scheduled_responses: Dict[str, Tuple[datetime, str]] = {}

    def execute(self, params: dict, context: SkillContext) -> Any:
        """Execute turn-taking management capability."""
        capability = params.get("capability", "assess_response_necessity")

        if capability == "assess_response_necessity":
            message = params.get("message", "")
            conv_context = params.get("conversation_context", [])
            user_state = params.get("user_state", {})

            assessment = assess_response_necessity(message, conv_context, user_state)

            return SkillResult(
                success=True,
                output={
                    "should_respond": assessment.should_respond,
                    "response_type": assessment.response_type.value,
                    "confidence": assessment.confidence,
                    "detected_patterns": assessment.detected_patterns,
                    "recommended_action": assessment.recommended_action,
                    "delay_until": assessment.delay_until.isoformat() if assessment.delay_until else None,
                    "null_signal": {
                        "type": assessment.null_signal.signal_type.value,
                        "visual": assessment.null_signal.visual,
                        "reason": assessment.null_signal.reason
                    } if assessment.null_signal else None,
                },
            )

        elif capability == "detect_rhetorical_questions":
            message = params.get("message", "")
            is_rhetorical, confidence, patterns = detect_rhetorical_question(message)

            return SkillResult(
                success=True,
                output={
                    "is_rhetorical": is_rhetorical,
                    "confidence": confidence,
                    "patterns": patterns,
                    "recommendation": "Acknowledge briefly or stay silent" if is_rhetorical else "Respond normally",
                },
            )

        elif capability == "evaluate_emotional_space":
            message = params.get("message", "")
            user_state = params.get("user_state", {})

            # Run emotional detectors
            is_venting, vent_conf, vent_patterns = detect_venting(message)
            is_processing, proc_conf, proc_patterns = detect_emotional_processing(message)

            needs_space = is_venting or is_processing
            all_patterns = vent_patterns + proc_patterns
            confidence = max(vent_conf, proc_conf) if needs_space else 0.0

            return SkillResult(
                success=True,
                output={
                    "needs_emotional_space": needs_space,
                    "confidence": confidence,
                    "patterns": all_patterns,
                    "recommendation": "Give space, acknowledge feelings" if needs_space else "Engage normally",
                },
            )

        elif capability == "emit_null_token":
            signal_type = params.get("signal_type", "acknowledgment")
            reason = params.get("reason", "")

            null_signal = create_null_response(signal_type, reason)

            return SkillResult(
                success=True,
                output={
                    "null_signal": {
                        "type": null_signal.signal_type.value,
                        "visual": null_signal.visual,
                        "reason": null_signal.reason,
                        "duration_hint": null_signal.duration_hint,
                    },
                    "content": None,
                },
            )

        elif capability == "schedule_delayed_response":
            response_id = params.get("response_id", f"delayed_{datetime.now().timestamp()}")
            delay_seconds = params.get("delay_seconds", 30)
            content = params.get("content", "")

            scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
            self.scheduled_responses[response_id] = (scheduled_time, content)

            return SkillResult(
                success=True,
                output={
                    "response_id": response_id,
                    "scheduled_for": scheduled_time.isoformat(),
                    "delay_seconds": delay_seconds,
                    "status": "scheduled",
                },
            )

        elif capability == "yield_floor":
            reason = params.get("reason", "")
            result = yield_floor(reason)

            return SkillResult(success=True, output=result)

        else:
            return SkillResult(
                success=False,
                output={"error": f"Unknown capability: {capability}"},
                error=f"Unknown capability: {capability}",
            )


# Convenience functions for direct use
def should_respond(message: str, context: Optional[List[Dict]] = None) -> bool:
    """Quick check: should we respond to this message?"""
    assessment = assess_response_necessity(message, context)
    return assessment.should_respond


def get_response_type(message: str) -> str:
    """Get recommended response type for a message."""
    assessment = assess_response_necessity(message)
    return assessment.response_type.value
