"""
Epistemic Calibration Skill
============================

True uncertainty modeling through calibrated confidence.
Moves from hallucination to genuine "I don't know."

Philosophy: "It is not enough to be right; one must be felt."

This skill analyzes:
- Token entropy/perplexity (statistical surprise)
- Knowledge boundaries (is this in my domain?)
- Confidence calibration (am I overconfident?)

And produces:
- Calibrated confidence scores
- Honest hedging when uncertain
- Clarification questions instead of guesses
"""

import json
import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

logger = logging.getLogger(__name__)


class CertaintyLevel(Enum):
    """Calibrated certainty levels."""
    HIGH = "HIGH"        # > 0.9 confidence
    MEDIUM = "MEDIUM"    # 0.6 - 0.9
    LOW = "LOW"          # < 0.6
    UNKNOWN = "UNKNOWN"  # No data / out of domain


@dataclass
class ConfidenceSignal:
    """Aggregated confidence signal."""
    score: float  # 0.0 - 1.0
    level: CertaintyLevel
    perplexity: float
    in_domain: bool
    pivotal_terms: Dict[str, float]  # term -> confidence
    reasoning: str


# Hedging patterns by certainty level
HEDGING_PATTERNS = {
    CertaintyLevel.HIGH: {
        "prefix": "",
        "patterns": [],  # No hedging needed
    },
    CertaintyLevel.MEDIUM: {
        "prefix": "Based on available information, ",
        "patterns": [
            (r"\b(is|are)\b", r"appears to be"),
            (r"\bwill\b", r"likely will"),
            (r"\bcan\b", r"should be able to"),
        ],
    },
    CertaintyLevel.LOW: {
        "prefix": "I'm not entirely certain, but ",
        "patterns": [
            (r"\b(is|are)\b", r"might be"),
            (r"\bwill\b", r"may"),
            (r"\bcan\b", r"could potentially"),
            (r"\bmust\b", r"might need to"),
        ],
    },
    CertaintyLevel.UNKNOWN: {
        "prefix": "I don't have enough information to be sure. ",
        "patterns": [
            (r"^(.+)$", r"It's possible that \1, but I'd need more context."),
        ],
    },
}

# Generic AI hedging to remove
GENERIC_HEDGES = [
    r"It is important to note that ",
    r"It's worth mentioning that ",
    r"I should point out that ",
    r"As an AI, I ",
    r"I cannot guarantee ",
    r"Please note that ",
]


class EpistemicCalibrationSkill(BaseSkill):
    """
    True uncertainty modeling through calibrated confidence.

    Capabilities:
    - calculate_sequence_perplexity: Measure draft answer surprise
    - extract_token_logprobs: Get confidence for key terms
    - detect_knowledge_boundary: Check domain coverage
    - inject_hedging_markers: Rewrite based on confidence
    - trigger_clarification_loop: Ask instead of guess
    - assess_confidence: Full confidence assessment
    """

    SKILL_ID = "cognition/epistemic-calibration"
    SKILL_NAME = "Epistemic Calibration"
    SKILL_DESCRIPTION = "Calibrates uncertainty and confidence to reduce hallucination."
    SKILL_CATEGORY = SkillCategory.REASONING
    SKILL_LEVEL = SkillLevel.BASIC
    SKILL_TAGS = ["uncertainty", "calibration", "honesty", "anti-hallucination", "human-dynamics"]

    def __init__(self):
        self.skill_index = None
        self._load_skill_index()

    def _load_skill_index(self):
        """Load skill index for domain detection."""
        index_path = Path(__file__).parents[2] / "INDEX.json"
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.skill_index = data.get("skills", [])
            except Exception as e:
                logger.warning(f"Could not load skill index: {e}")
                self.skill_index = []

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute epistemic calibration."""
        capability = params.get("capability", "assess_confidence")

        try:
            if capability == "calculate_sequence_perplexity":
                return self._calculate_perplexity(params)
            elif capability == "extract_token_logprobs":
                return self._extract_logprobs(params)
            elif capability == "detect_knowledge_boundary":
                return self._detect_boundary(params)
            elif capability == "inject_hedging_markers":
                return self._inject_hedging(params)
            elif capability == "trigger_clarification_loop":
                return self._trigger_clarification(params)
            elif capability == "assess_confidence":
                return self._assess_confidence(params)
            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    error=f"Unknown capability: {capability}"
                )
        except Exception as e:
            logger.exception(f"Epistemic calibration error: {e}")
            return SkillResult(success=False, output={"error": str(e)}, error=str(e))

    def _calculate_perplexity(self, params: Dict) -> SkillResult:
        """
        Calculate sequence perplexity from logprobs.

        Perplexity = exp(average negative log probability)
        Lower = more confident, Higher = more surprised/uncertain
        """
        logprobs = params.get("logprobs", [])

        if not logprobs:
            # Estimate from text if no logprobs provided
            draft = params.get("draft_response", "")
            perplexity = self._estimate_perplexity_heuristic(draft)
        else:
            # Calculate from actual logprobs
            avg_neg_logprob = -sum(logprobs) / len(logprobs)
            perplexity = math.exp(avg_neg_logprob)

        # Normalize to 0-1 confidence (inverse of perplexity)
        # Perplexity of 1 = perfect confidence, >100 = very uncertain
        confidence = max(0.0, min(1.0, 1.0 / (1.0 + math.log(perplexity + 1))))

        return SkillResult(
            success=True,
            output={
                "perplexity": perplexity,
                "confidence_score": confidence,
                "certainty_level": self._score_to_level(confidence).value,
                "interpretation": self._interpret_perplexity(perplexity),
            }
        )

    def _estimate_perplexity_heuristic(self, text: str) -> float:
        """
        Heuristic perplexity estimation without actual logprobs.
        Based on linguistic markers of uncertainty.
        """
        if not text:
            return 100.0  # Maximum uncertainty

        uncertainty_markers = [
            r"\bmaybe\b", r"\bperhaps\b", r"\bpossibly\b",
            r"\bmight\b", r"\bcould\b", r"\bseems?\b",
            r"\bappears?\b", r"\blikely\b", r"\bunlikely\b",
            r"\buncertain\b", r"\bnot sure\b", r"\bdon't know\b",
            r"\?",  # Questions indicate uncertainty
        ]

        confidence_markers = [
            r"\bdefinitely\b", r"\bcertainly\b", r"\babsolutely\b",
            r"\bclearly\b", r"\bobviously\b", r"\bwithout doubt\b",
            r"\bmust\b", r"\bwill\b", r"\balways\b", r"\bnever\b",
        ]

        text_lower = text.lower()
        uncertainty_count = sum(
            len(re.findall(p, text_lower)) for p in uncertainty_markers
        )
        confidence_count = sum(
            len(re.findall(p, text_lower)) for p in confidence_markers
        )

        # Base perplexity
        word_count = len(text.split())
        base_perplexity = 10.0

        # Adjust based on markers
        uncertainty_ratio = uncertainty_count / max(1, word_count) * 100
        confidence_ratio = confidence_count / max(1, word_count) * 100

        perplexity = base_perplexity * (1 + uncertainty_ratio) / (1 + confidence_ratio)

        return max(1.0, min(1000.0, perplexity))

    def _extract_logprobs(self, params: Dict) -> SkillResult:
        """
        Extract confidence for pivotal keywords.
        """
        draft = params.get("draft_response", "")
        logprobs = params.get("logprobs", [])

        # Identify pivotal terms (nouns, verbs, key entities)
        pivotal_terms = self._extract_pivotal_terms(draft)

        # If we have logprobs, map them to terms
        term_confidence = {}
        if logprobs and len(logprobs) > 0:
            # Simplified: distribute logprobs across terms
            tokens = draft.split()
            for i, term in enumerate(pivotal_terms[:10]):
                # Find term position and get nearby logprob
                if term.lower() in [t.lower() for t in tokens]:
                    idx = next(
                        (j for j, t in enumerate(tokens) if t.lower() == term.lower()),
                        0
                    )
                    if idx < len(logprobs):
                        prob = math.exp(logprobs[idx])
                        term_confidence[term] = min(1.0, max(0.0, prob))
                    else:
                        term_confidence[term] = 0.5  # Unknown
        else:
            # Heuristic confidence based on term characteristics
            for term in pivotal_terms[:10]:
                term_confidence[term] = self._heuristic_term_confidence(term)

        avg_confidence = sum(term_confidence.values()) / max(1, len(term_confidence))

        return SkillResult(
            success=True,
            output={
                "pivotal_terms": term_confidence,
                "average_confidence": avg_confidence,
                "certainty_level": self._score_to_level(avg_confidence).value,
            }
        )

    def _extract_pivotal_terms(self, text: str) -> List[str]:
        """Extract important terms from text."""
        # Simple extraction: capitalized words, technical terms, etc.
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{5,}\b', text)

        # Filter common words
        stopwords = {'the', 'and', 'that', 'this', 'with', 'from', 'have', 'been', 'would', 'could', 'should'}
        return [w for w in words if w.lower() not in stopwords][:20]

    def _heuristic_term_confidence(self, term: str) -> float:
        """Heuristic confidence for a term."""
        # Technical/specific terms = lower confidence (harder to verify)
        if re.match(r'^[A-Z][a-z]+[A-Z]', term):  # CamelCase
            return 0.6
        if len(term) > 10:  # Long technical terms
            return 0.65
        if term[0].isupper():  # Proper nouns
            return 0.7
        return 0.75  # Common terms

    def _detect_boundary(self, params: Dict) -> SkillResult:
        """
        Detect if query is within knowledge domain.
        Compare against skill index.
        """
        query = params.get("query", "")

        if not self.skill_index:
            return SkillResult(
                success=True,
                output={
                    "in_domain": True,  # Assume in-domain if no index
                    "matching_skills": [],
                    "domain_confidence": 0.5,
                    "reasoning": "No skill index available for domain detection",
                }
            )

        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w{3,}\b', query_lower))

        matching_skills = []
        for skill in self.skill_index:
            skill_desc = skill.get("description", "").lower()
            skill_name = skill.get("name", "").lower()

            # Check for term overlap
            skill_terms = set(re.findall(r'\b\w{3,}\b', skill_desc + " " + skill_name))
            overlap = query_terms & skill_terms

            if len(overlap) >= 2:
                matching_skills.append({
                    "id": skill.get("id"),
                    "name": skill.get("name"),
                    "overlap": list(overlap),
                })

        in_domain = len(matching_skills) > 0
        domain_confidence = min(1.0, len(matching_skills) / 3.0)

        return SkillResult(
            success=True,
            output={
                "in_domain": in_domain,
                "matching_skills": matching_skills[:5],
                "domain_confidence": domain_confidence,
                "certainty_level": CertaintyLevel.UNKNOWN.value if not in_domain else self._score_to_level(domain_confidence).value,
                "reasoning": f"Found {len(matching_skills)} matching skills" if in_domain else "Query appears outside skill domain",
            }
        )

    def _inject_hedging(self, params: Dict) -> SkillResult:
        """
        Inject appropriate hedging based on confidence.
        """
        draft = params.get("draft_response", "")
        confidence = params.get("confidence_score", 0.75)
        threshold = params.get("confidence_threshold", 0.75)

        level = self._score_to_level(confidence)

        # First, remove generic AI hedging
        modified = self._remove_generic_hedging(draft)

        # Then apply appropriate hedging for confidence level
        if confidence >= threshold and level == CertaintyLevel.HIGH:
            # No hedging needed
            pass
        else:
            patterns = HEDGING_PATTERNS.get(level, HEDGING_PATTERNS[CertaintyLevel.MEDIUM])

            # Add prefix if significant change
            if patterns["prefix"] and level in [CertaintyLevel.LOW, CertaintyLevel.UNKNOWN]:
                modified = patterns["prefix"] + modified[0].lower() + modified[1:]

            # Apply pattern replacements
            for pattern, replacement in patterns["patterns"]:
                modified = re.sub(pattern, replacement, modified, count=2)

        return SkillResult(
            success=True,
            output={
                "original": draft,
                "modified_response": modified,
                "certainty_level": level.value,
                "confidence_score": confidence,
                "hedging_applied": modified != draft,
            }
        )

    def _remove_generic_hedging(self, text: str) -> str:
        """Remove generic AI hedging phrases."""
        result = text
        for pattern in GENERIC_HEDGES:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        return result.strip()

    def _trigger_clarification(self, params: Dict) -> SkillResult:
        """
        Generate clarification question instead of guessing.
        """
        query = params.get("query", "")
        draft = params.get("draft_response", "")
        confidence = params.get("confidence_score", 0.5)

        # Identify what's unclear
        unclear_aspects = self._identify_unclear_aspects(query, draft)

        if not unclear_aspects:
            clarification = f"Could you provide more context about what specifically you'd like to know?"
        else:
            aspect = unclear_aspects[0]
            clarification = f"To give you a better answer, could you clarify {aspect}?"

        return SkillResult(
            success=True,
            output={
                "should_clarify": confidence < 0.6,
                "clarification_question": clarification,
                "unclear_aspects": unclear_aspects,
                "original_query": query,
                "reasoning": f"Confidence {confidence:.1%} below threshold, clarification recommended",
            }
        )

    def _identify_unclear_aspects(self, query: str, draft: str) -> List[str]:
        """Identify what aspects of the query are unclear."""
        aspects = []

        # Check for ambiguous pronouns
        if re.search(r'\b(it|this|that|they)\b', query.lower()):
            aspects.append("what 'it' or 'this' refers to")

        # Check for missing context
        if len(query.split()) < 5:
            aspects.append("the specific context or use case")

        # Check for comparison without baseline
        if re.search(r'\b(better|worse|faster|slower)\b', query.lower()):
            aspects.append("what you're comparing against")

        # Check for "how to" without goal
        if re.search(r'\bhow to\b', query.lower()) and 'because' not in query.lower():
            aspects.append("what you're ultimately trying to achieve")

        return aspects

    def _assess_confidence(self, params: Dict) -> SkillResult:
        """
        Full confidence assessment combining all signals.
        """
        draft = params.get("draft_response", "")
        query = params.get("query", "")
        logprobs = params.get("logprobs", [])

        # Calculate perplexity
        perplexity_result = self._calculate_perplexity({
            "draft_response": draft,
            "logprobs": logprobs,
        })
        perplexity_confidence = perplexity_result.output.get("confidence_score", 0.5)

        # Extract term confidence
        term_result = self._extract_logprobs({
            "draft_response": draft,
            "logprobs": logprobs,
        })
        term_confidence = term_result.output.get("average_confidence", 0.5)

        # Check domain
        domain_result = self._detect_boundary({"query": query})
        in_domain = domain_result.output.get("in_domain", True)
        domain_confidence = domain_result.output.get("domain_confidence", 0.5)

        # Aggregate confidence
        if not in_domain:
            final_confidence = 0.2  # Very low if out of domain
            reasoning = "Query appears outside knowledge domain"
        else:
            # Weighted average
            final_confidence = (
                perplexity_confidence * 0.3 +
                term_confidence * 0.3 +
                domain_confidence * 0.4
            )
            reasoning = f"Perplexity: {perplexity_confidence:.2f}, Terms: {term_confidence:.2f}, Domain: {domain_confidence:.2f}"

        level = self._score_to_level(final_confidence)

        # Build signal
        signal = ConfidenceSignal(
            score=final_confidence,
            level=level,
            perplexity=perplexity_result.output.get("perplexity", 10.0),
            in_domain=in_domain,
            pivotal_terms=term_result.output.get("pivotal_terms", {}),
            reasoning=reasoning,
        )

        return SkillResult(
            success=True,
            output={
                "confidence_score": signal.score,
                "certainty_level": signal.level.value,
                "perplexity": signal.perplexity,
                "in_domain": signal.in_domain,
                "pivotal_terms": signal.pivotal_terms,
                "reasoning": signal.reasoning,
                "recommendation": self._get_recommendation(signal),
            }
        )

    def _score_to_level(self, score: float) -> CertaintyLevel:
        """Convert confidence score to certainty level."""
        if score > 0.9:
            return CertaintyLevel.HIGH
        elif score >= 0.6:
            return CertaintyLevel.MEDIUM
        elif score > 0:
            return CertaintyLevel.LOW
        else:
            return CertaintyLevel.UNKNOWN

    def _interpret_perplexity(self, perplexity: float) -> str:
        """Human-readable perplexity interpretation."""
        if perplexity < 5:
            return "Very confident - low surprise in token sequence"
        elif perplexity < 20:
            return "Moderately confident - some uncertainty in expression"
        elif perplexity < 50:
            return "Uncertain - high surprise suggests guessing"
        else:
            return "Very uncertain - response may be unreliable"

    def _get_recommendation(self, signal: ConfidenceSignal) -> str:
        """Get recommendation based on confidence signal."""
        if signal.level == CertaintyLevel.HIGH:
            return "Proceed with response"
        elif signal.level == CertaintyLevel.MEDIUM:
            return "Add light hedging to response"
        elif signal.level == CertaintyLevel.LOW:
            return "Consider asking for clarification or adding strong hedging"
        else:
            return "Ask clarifying question instead of responding"


# Convenience function
def calibrate_response(draft: str, query: str = "", logprobs: List[float] = None) -> Dict:
    """
    Calibrate a response with epistemic awareness.

    Returns confidence assessment and optionally modified response.
    """
    skill = EpistemicCalibrationSkill()
    result = skill.execute({
        "capability": "assess_confidence",
        "draft_response": draft,
        "query": query,
        "logprobs": logprobs or [],
    }, SkillContext())
    return result.output
