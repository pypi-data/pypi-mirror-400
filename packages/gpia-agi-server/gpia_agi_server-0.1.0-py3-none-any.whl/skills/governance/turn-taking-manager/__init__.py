"""Turn-Taking Manager - The best response is sometimes no response."""
from .skill import (
    TurnTakingManagerSkill,
    TurnAssessment,
    ResponseType,
    NullSignal,
    NullSignalType,
    assess_response_necessity,
    detect_rhetorical_question,
    detect_venting,
    detect_thinking_aloud,
    detect_farewell,
    should_respond,
    get_response_type,
    yield_floor,
)

__all__ = [
    "TurnTakingManagerSkill",
    "TurnAssessment",
    "ResponseType",
    "NullSignal",
    "NullSignalType",
    "assess_response_necessity",
    "detect_rhetorical_question",
    "detect_venting",
    "detect_thinking_aloud",
    "detect_farewell",
    "should_respond",
    "get_response_type",
    "yield_floor",
]
