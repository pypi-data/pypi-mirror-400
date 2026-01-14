"""
Relational Graph Memory Skill
==============================

Conversational memory that tracks HOW we interact, not just WHAT we said.

Philosophy: "Remember the vibes, not just the facts."

This skill tracks:
- Sentiment velocity (mood trajectory)
- Style preferences (implicit interaction rules)
- Emotional context links (stress patterns, joy patterns)
- Shared narratives (inside jokes, rapport history)

Vector DBs retrieve facts ("User likes pizza").
This retrieves vibes ("User gets annoyed when I use emojis").
"""

import json
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult

logger = logging.getLogger(__name__)


class SentimentTrend(Enum):
    """Mood trajectory during conversation."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class Formality(Enum):
    """Communication formality level."""
    FORMAL = "formal"
    NEUTRAL = "neutral"
    CASUAL = "casual"
    INTIMATE = "intimate"


class Verbosity(Enum):
    """Communication verbosity preference."""
    TERSE = "terse"      # Short, to the point
    MODERATE = "moderate"
    VERBOSE = "verbose"  # Detailed explanations


@dataclass
class StyleProfile:
    """User's communication style preferences."""
    formality: Formality = Formality.NEUTRAL
    verbosity: Verbosity = Verbosity.MODERATE
    emoji_usage: bool = False
    uses_punctuation: bool = True
    average_message_length: int = 50
    detected_rules: List[str] = field(default_factory=list)
    pet_peeves: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)


@dataclass
class SentimentState:
    """Current sentiment analysis."""
    score: float  # -1.0 (negative) to 1.0 (positive)
    trend: SentimentTrend
    velocity: float  # Rate of change
    confidence: float
    emotional_keywords: List[str] = field(default_factory=list)


@dataclass
class RelationalState:
    """Full relational context with user."""
    user_id: str
    session_count: int = 0
    total_messages: int = 0
    style_profile: StyleProfile = field(default_factory=StyleProfile)
    current_sentiment: SentimentState = None
    shared_references: List[str] = field(default_factory=list)
    last_interaction: Optional[str] = None
    relationship_quality: float = 0.5  # 0.0 to 1.0


# Sentiment indicators
POSITIVE_INDICATORS = [
    r'\b(thanks?|thank you|appreciate|great|awesome|excellent|perfect|love|happy)\b',
    r'\b(wonderful|fantastic|amazing|helpful|brilliant)\b',
    r'[!]{1,3}$',  # Exclamation (enthusiasm)
    r'[:;]-?[)D]',  # Smileys
]

NEGATIVE_INDICATORS = [
    r'\b(frustrated|annoyed|angry|upset|disappointed|confused|stuck)\b',
    r'\b(wrong|broken|failed|error|problem|issue|bug)\b',
    r'\b(don\'t understand|doesn\'t work|not working)\b',
    r'[?]{2,}',  # Multiple questions (confusion/frustration)
]

# Style detection patterns
FORMALITY_PATTERNS = {
    Formality.FORMAL: [r'\b(please|kindly|would you|could you|I would appreciate)\b'],
    Formality.CASUAL: [r'\b(hey|yo|gonna|wanna|kinda|yeah|nope|lol|haha)\b'],
    Formality.INTIMATE: [r'\b(bro|dude|mate|fam|bestie)\b'],
}


class RelationalGraphSkill(BaseSkill):
    """
    Tracks relational dynamics, not just content.

    Capabilities:
    - analyze_sentiment_velocity: Track mood during session
    - extract_style_preferences: Detect implicit rules
    - link_episodic_context: Connect by emotional state
    - retrieve_shared_narrative: Recall rapport history
    - update_relational_state: Update relationship model
    """

    SKILL_ID = "memory/relational-graph"
    SKILL_NAME = "Relational Graph Memory"
    SKILL_DESCRIPTION = "Tracks relational dynamics like sentiment and interaction style."
    SKILL_CATEGORY = SkillCategory.SYSTEM
    SKILL_LEVEL = SkillLevel.BASIC
    SKILL_TAGS = ["memory", "relationships", "sentiment", "rapport", "human-dynamics"]

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).parents[3] / "data" / "relational_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize relational memory database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relational_states (
                user_id TEXT PRIMARY KEY,
                state_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment_score REAL,
                emotional_state TEXT,
                message_sample TEXT,
                style_markers TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_narratives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                narrative_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_referenced TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute relational graph operation."""
        capability = params.get("capability", "analyze_sentiment_velocity")

        try:
            if capability == "analyze_sentiment_velocity":
                return self._analyze_sentiment_velocity(params)
            elif capability == "extract_style_preferences":
                return self._extract_style_preferences(params)
            elif capability == "link_episodic_context":
                return self._link_episodic_context(params)
            elif capability == "retrieve_shared_narrative":
                return self._retrieve_shared_narrative(params)
            elif capability == "update_relational_state":
                return self._update_relational_state(params)
            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    error=f"Unknown capability: {capability}"
                )
        except Exception as e:
            logger.exception(f"Relational graph error: {e}")
            return SkillResult(success=False, output={"error": str(e)}, error=str(e))

    def _analyze_sentiment_velocity(self, params: Dict) -> SkillResult:
        """
        Track mood trajectory during session.
        Velocity = rate of sentiment change.
        """
        session_history = params.get("session_history", [])
        current_message = params.get("message", "")

        if not session_history and not current_message:
            return SkillResult(
                success=True,
                output={
                    "current_sentiment": 0.0,
                    "trend": SentimentTrend.STABLE.value,
                    "velocity": 0.0,
                    "confidence": 0.0,
                    "analysis": "No messages to analyze",
                }
            )

        # Calculate sentiment for each message
        sentiments = []
        for msg in session_history:
            text = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            score = self._calculate_sentiment(text)
            sentiments.append(score)

        # Add current message
        if current_message:
            sentiments.append(self._calculate_sentiment(current_message))

        if len(sentiments) < 2:
            trend = SentimentTrend.STABLE
            velocity = 0.0
        else:
            # Calculate velocity (rate of change)
            changes = [sentiments[i] - sentiments[i-1] for i in range(1, len(sentiments))]
            velocity = sum(changes) / len(changes)

            # Determine trend
            if abs(velocity) < 0.1:
                trend = SentimentTrend.STABLE
            elif velocity > 0.1:
                trend = SentimentTrend.IMPROVING
            elif velocity < -0.1:
                trend = SentimentTrend.DECLINING
            else:
                # Check for volatility
                if max(changes) - min(changes) > 0.5:
                    trend = SentimentTrend.VOLATILE
                else:
                    trend = SentimentTrend.STABLE

        current = sentiments[-1] if sentiments else 0.0
        emotional_keywords = self._extract_emotional_keywords(current_message)

        return SkillResult(
            success=True,
            output={
                "current_sentiment": current,
                "trend": trend.value,
                "velocity": velocity,
                "confidence": min(1.0, len(sentiments) / 5.0),
                "sentiment_history": sentiments[-10:],
                "emotional_keywords": emotional_keywords,
                "interpretation": self._interpret_sentiment_state(current, trend),
            }
        )

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text (-1.0 to 1.0)."""
        if not text:
            return 0.0

        text_lower = text.lower()
        positive_count = sum(
            len(re.findall(p, text_lower, re.IGNORECASE))
            for p in POSITIVE_INDICATORS
        )
        negative_count = sum(
            len(re.findall(p, text_lower, re.IGNORECASE))
            for p in NEGATIVE_INDICATORS
        )

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        # Normalize to -1 to 1
        score = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, score))

    def _extract_emotional_keywords(self, text: str) -> List[str]:
        """Extract emotional keywords from text."""
        keywords = []
        text_lower = text.lower()

        for pattern in POSITIVE_INDICATORS + NEGATIVE_INDICATORS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)

        return list(set(keywords))[:10]

    def _interpret_sentiment_state(self, current: float, trend: SentimentTrend) -> str:
        """Human-readable sentiment interpretation."""
        sentiment_desc = (
            "positive" if current > 0.3 else
            "negative" if current < -0.3 else
            "neutral"
        )

        if trend == SentimentTrend.IMPROVING:
            return f"User mood is {sentiment_desc} and improving"
        elif trend == SentimentTrend.DECLINING:
            return f"User mood is {sentiment_desc} and declining - consider adjusting approach"
        elif trend == SentimentTrend.VOLATILE:
            return f"User mood is {sentiment_desc} but volatile - tread carefully"
        else:
            return f"User mood is {sentiment_desc} and stable"

    def _extract_style_preferences(self, params: Dict) -> SkillResult:
        """
        Detect implicit communication rules.
        "User uses short sentences" -> constraint
        "User never says thank you" -> expectation
        """
        session_history = params.get("session_history", [])
        user_id = params.get("user_id", "default")

        if not session_history:
            return SkillResult(
                success=True,
                output={
                    "style_profile": {
                        "formality": Formality.NEUTRAL.value,
                        "verbosity": Verbosity.MODERATE.value,
                        "emoji_usage": False,
                        "detected_rules": [],
                    },
                    "confidence": 0.0,
                }
            )

        # Analyze messages
        user_messages = [
            msg.get("content", "") if isinstance(msg, dict) else str(msg)
            for msg in session_history
            if (isinstance(msg, dict) and msg.get("role") == "user") or not isinstance(msg, dict)
        ]

        if not user_messages:
            user_messages = [str(msg) for msg in session_history[:5]]

        # Calculate metrics
        avg_length = sum(len(m) for m in user_messages) / max(1, len(user_messages))
        has_emoji = any(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', m) for m in user_messages)
        has_punctuation = all(re.search(r'[.!?]$', m.strip()) for m in user_messages if m.strip())

        # Detect formality
        formality = Formality.NEUTRAL
        for level, patterns in FORMALITY_PATTERNS.items():
            if any(re.search(p, ' '.join(user_messages), re.IGNORECASE) for p in patterns):
                formality = level
                break

        # Detect verbosity
        if avg_length < 30:
            verbosity = Verbosity.TERSE
        elif avg_length > 100:
            verbosity = Verbosity.VERBOSE
        else:
            verbosity = Verbosity.MODERATE

        # Extract implicit rules
        detected_rules = []
        pet_peeves = []
        preferences = []

        if verbosity == Verbosity.TERSE:
            detected_rules.append("User prefers short, direct responses")
            preferences.append("brevity")

        if not has_emoji:
            detected_rules.append("User doesn't use emojis - avoid them in responses")
            pet_peeves.append("emoji overuse")

        if formality == Formality.CASUAL:
            detected_rules.append("User is casual - match their tone")
            preferences.append("casual language")
        elif formality == Formality.FORMAL:
            detected_rules.append("User is formal - maintain professionalism")
            preferences.append("professional tone")

        # Check for question patterns
        question_ratio = sum(1 for m in user_messages if '?' in m) / max(1, len(user_messages))
        if question_ratio > 0.7:
            detected_rules.append("User asks many questions - be thorough in answers")

        profile = StyleProfile(
            formality=formality,
            verbosity=verbosity,
            emoji_usage=has_emoji,
            uses_punctuation=has_punctuation,
            average_message_length=int(avg_length),
            detected_rules=detected_rules,
            pet_peeves=pet_peeves,
            preferences=preferences,
        )

        return SkillResult(
            success=True,
            output={
                "style_profile": {
                    "formality": profile.formality.value,
                    "verbosity": profile.verbosity.value,
                    "emoji_usage": profile.emoji_usage,
                    "uses_punctuation": profile.uses_punctuation,
                    "average_message_length": profile.average_message_length,
                    "detected_rules": profile.detected_rules,
                    "pet_peeves": profile.pet_peeves,
                    "preferences": profile.preferences,
                },
                "confidence": min(1.0, len(user_messages) / 10.0),
                "messages_analyzed": len(user_messages),
            }
        )

    def _link_episodic_context(self, params: Dict) -> SkillResult:
        """
        Connect conversations by emotional state, not keywords.
        "User is stressed again, similar to last Tuesday"
        """
        user_id = params.get("user_id", "default")
        emotional_query = params.get("emotional_query", "")
        current_sentiment = params.get("current_sentiment", 0.0)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Find similar emotional episodes
        cursor.execute("""
            SELECT session_id, timestamp, sentiment_score, emotional_state, message_sample
            FROM interaction_episodes
            WHERE user_id = ?
            ORDER BY ABS(sentiment_score - ?) ASC
            LIMIT 5
        """, (user_id, current_sentiment))

        episodes = cursor.fetchall()
        conn.close()

        linked_episodes = []
        for ep in episodes:
            session_id, timestamp, score, state, sample = ep
            similarity = 1.0 - abs(score - current_sentiment)
            linked_episodes.append({
                "session_id": session_id,
                "timestamp": timestamp,
                "sentiment_score": score,
                "emotional_state": state,
                "message_sample": sample[:100] if sample else "",
                "similarity": similarity,
            })

        return SkillResult(
            success=True,
            output={
                "linked_episodes": linked_episodes,
                "current_sentiment": current_sentiment,
                "pattern_detected": self._detect_pattern(linked_episodes, current_sentiment),
            }
        )

    def _detect_pattern(self, episodes: List[Dict], current: float) -> Optional[str]:
        """Detect emotional patterns across episodes."""
        if len(episodes) < 2:
            return None

        # Check if user is often in similar state
        similar_count = sum(1 for ep in episodes if ep.get("similarity", 0) > 0.7)

        if similar_count >= 2 and current < -0.3:
            return "User frequently experiences frustration - may need extra patience"
        elif similar_count >= 2 and current > 0.3:
            return "User is often positive - maintain encouraging tone"

        return None

    def _retrieve_shared_narrative(self, params: Dict) -> SkillResult:
        """
        Recall "inside jokes" or shared history for rapport.
        Things that don't have factual utility but build relationship.
        """
        user_id = params.get("user_id", "default")
        narrative_type = params.get("narrative_type", None)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        if narrative_type:
            cursor.execute("""
                SELECT id, narrative_type, content, created_at, last_referenced
                FROM shared_narratives
                WHERE user_id = ? AND narrative_type = ?
                ORDER BY last_referenced DESC
                LIMIT 10
            """, (user_id, narrative_type))
        else:
            cursor.execute("""
                SELECT id, narrative_type, content, created_at, last_referenced
                FROM shared_narratives
                WHERE user_id = ?
                ORDER BY last_referenced DESC
                LIMIT 10
            """, (user_id,))

        narratives = cursor.fetchall()
        conn.close()

        shared_narratives = []
        for n in narratives:
            id_, type_, content, created, referenced = n
            shared_narratives.append({
                "id": id_,
                "type": type_,
                "content": content,
                "created_at": created,
                "last_referenced": referenced,
            })

        return SkillResult(
            success=True,
            output={
                "shared_narratives": shared_narratives,
                "narrative_count": len(shared_narratives),
                "types_found": list(set(n["type"] for n in shared_narratives)),
            }
        )

    def _update_relational_state(self, params: Dict) -> SkillResult:
        """
        Update the full relational model for a user.
        """
        user_id = params.get("user_id", "default")
        session_history = params.get("session_history", [])
        session_id = params.get("session_id", datetime.now().isoformat())

        # Get current state
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT state_json FROM relational_states WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            state = json.loads(row[0])
        else:
            state = {
                "user_id": user_id,
                "session_count": 0,
                "total_messages": 0,
                "relationship_quality": 0.5,
            }

        # Update with new session data
        state["session_count"] = state.get("session_count", 0) + 1
        state["total_messages"] = state.get("total_messages", 0) + len(session_history)
        state["last_interaction"] = datetime.now().isoformat()

        # Analyze current session
        sentiment_result = self._analyze_sentiment_velocity({
            "session_history": session_history,
        })
        style_result = self._extract_style_preferences({
            "session_history": session_history,
            "user_id": user_id,
        })

        # Update relationship quality based on sentiment
        current_sentiment = sentiment_result.output.get("current_sentiment", 0.0)
        old_quality = state.get("relationship_quality", 0.5)
        new_quality = old_quality * 0.8 + (current_sentiment + 1) / 2 * 0.2
        state["relationship_quality"] = max(0.0, min(1.0, new_quality))

        # Store updated state
        cursor.execute("""
            INSERT OR REPLACE INTO relational_states (user_id, state_json, updated_at)
            VALUES (?, ?, ?)
        """, (user_id, json.dumps(state), datetime.now().isoformat()))

        # Store episode
        cursor.execute("""
            INSERT INTO interaction_episodes
            (user_id, session_id, sentiment_score, emotional_state, message_sample, style_markers)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            session_id,
            current_sentiment,
            sentiment_result.output.get("trend", "stable"),
            session_history[-1].get("content", "")[:200] if session_history else "",
            json.dumps(style_result.output.get("style_profile", {})),
        ))

        conn.commit()
        conn.close()

        return SkillResult(
            success=True,
            output={
                "relational_state": state,
                "sentiment_analysis": sentiment_result.output,
                "style_profile": style_result.output.get("style_profile"),
                "relationship_quality": state["relationship_quality"],
            }
        )


# Convenience functions
def analyze_mood(session_history: List[Dict]) -> Dict:
    """Quick mood analysis for a session."""
    skill = RelationalGraphSkill()
    result = skill.execute({
        "capability": "analyze_sentiment_velocity",
        "session_history": session_history,
    }, SkillContext())
    return result.output


def get_style_profile(session_history: List[Dict]) -> Dict:
    """Get user's communication style."""
    skill = RelationalGraphSkill()
    result = skill.execute({
        "capability": "extract_style_preferences",
        "session_history": session_history,
    }, SkillContext())
    return result.output
