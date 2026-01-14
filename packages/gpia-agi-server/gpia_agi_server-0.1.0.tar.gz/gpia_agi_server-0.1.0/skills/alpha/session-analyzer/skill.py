"""
Session Analyzer - Autonomous Learning from Conversations
==========================================================

This skill enables Alpha Agent to analyze conversations, extract learnings,
identify patterns, and recognize skill needs for continuous self-improvement.

Capabilities:
- analyze: Analyze a conversation session for insights
- extract_patterns: Identify recurring themes and patterns
- identify_needs: Recognize capability gaps from conversation
- store_learnings: Persist insights to memory

Uses MindsetSkill with multi-model reasoning for deep analysis.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillDependency,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)


class SessionAnalyzerSkill(Skill):
    """
    Analyzes conversation sessions to extract learnings and skill needs.

    This is how Alpha learns from interactions - by reflecting on
    conversations to identify what worked, what didn't, and what
    capabilities are needed.
    """

    def __init__(self):
        self._mindset = None
        self._memory = None

    @property
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="alpha/session-analyzer",
            name="Session Analyzer",
            description="Analyzes conversations to extract learnings and identify skill needs",
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["alpha", "analysis", "learning", "meta-cognitive", "autonomous"],
            dependencies=[
                SkillDependency(skill_id="conscience/mindset", optional=False),
                SkillDependency(skill_id="conscience/memory", optional=False),
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["analyze", "extract_patterns", "identify_needs", "store_learnings"],
                },
                "conversation": {
                    "type": "string",
                    "description": "Conversation text or summary to analyze",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context about the session",
                },
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "analysis": {"type": "object"},
                "patterns": {"type": "array"},
                "needs": {"type": "array"},
                "learnings": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "analyze": self._analyze,
            "extract_patterns": self._extract_patterns,
            "identify_needs": self._identify_needs,
            "store_learnings": self._store_learnings,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"SessionAnalyzer {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _analyze(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Comprehensive analysis of a conversation session.

        Uses multi-model reasoning (DeepSeek -> Qwen -> DeepSeek) to:
        1. Identify topics discussed
        2. Extract key insights
        3. Recognize patterns
        4. Identify learning opportunities
        5. Suggest skill needs
        """
        conversation = input_data.get("conversation", "")
        session_context = input_data.get("context", {})

        if not conversation:
            return SkillResult(
                success=False,
                output=None,
                error="No conversation provided",
                skill_id=self.metadata().id,
            )

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required but not available",
                skill_id=self.metadata().id,
            )

        # Use MindsetSkill for deep analysis
        analysis_result = self.mindset.execute({
            "capability": "analyze",
            "problem": f"""
Analyze this conversation session:

{conversation}

Context: {session_context}

Provide structured analysis of:
1. Main topics discussed
2. Key insights and discoveries
3. Skills that were used/mentioned
4. Capability gaps identified
5. Learning opportunities
6. Patterns or themes
7. Recommendations for improvement
            """,
            "pattern": "balanced",  # DeepSeek -> Qwen -> DeepSeek
        }, context)

        if not analysis_result.success:
            return SkillResult(
                success=False,
                output=None,
                error=f"Analysis failed: {analysis_result.error}",
                skill_id=self.metadata().id,
            )

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "conversation_length": len(conversation),
            "context": session_context,
            "llm_analysis": analysis_result.output,
            "summary": analysis_result.output.get("conclusion", "")[:500],
        }

        return SkillResult(
            success=True,
            output={"analysis": analysis},
            skill_id=self.metadata().id,
        )

    def _extract_patterns(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Extract recurring patterns from conversation analysis.

        Looks for:
        - User preferences and interests
        - Question types and complexity
        - Technical topics discussed
        - Learning styles
        - Interaction patterns
        """
        conversation = input_data.get("conversation", "")

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        pattern_result = self.mindset.execute({
            "capability": "analyze",
            "problem": f"""
Extract patterns from this conversation:

{conversation}

Identify:
1. User's primary interests and focus areas
2. Technical depth and complexity preferences
3. Interaction style (questions, requests, explorations)
4. Learning patterns (theoretical vs. practical)
5. Recurring themes or topics
6. Problem-solving approaches

Provide structured list of patterns observed.
            """,
            "pattern": "deep_analysis",
        }, context)

        if pattern_result.success:
            patterns = {
                "identified_at": datetime.now().isoformat(),
                "patterns": pattern_result.output.get("conclusion", ""),
                "confidence": pattern_result.output.get("confidence", 0.5),
            }

            return SkillResult(
                success=True,
                output={"patterns": [patterns]},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="Pattern extraction failed",
            skill_id=self.metadata().id,
        )

    def _identify_needs(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Identify capability gaps and skill needs from conversation.

        Recognizes:
        - Skills mentioned but not available
        - Workflows attempted but incomplete
        - User requests that couldn't be fully satisfied
        - Missing integrations or capabilities
        """
        conversation = input_data.get("conversation", "")

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        needs_result = self.mindset.execute({
            "capability": "analyze",
            "problem": f"""
Analyze this conversation to identify capability gaps and skill needs:

{conversation}

Identify:
1. Skills that were mentioned but not fully available
2. Capabilities the user wanted but system couldn't provide
3. Workflows that were incomplete or blocked
4. Integration points that are missing
5. Autonomous capabilities that would improve operation
6. Meta-cognitive skills that would enable self-improvement

For each need, specify:
- What capability is missing
- Why it's needed
- How it would be used
- Priority (critical/high/medium/low)
            """,
            "pattern": "balanced",
        }, context)

        if needs_result.success:
            needs = {
                "identified_at": datetime.now().isoformat(),
                "needs_analysis": needs_result.output.get("conclusion", ""),
                "reasoning": needs_result.output.get("reasoning_trace", []),
            }

            return SkillResult(
                success=True,
                output={"needs": [needs]},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="Needs identification failed",
            skill_id=self.metadata().id,
        )

    def _store_learnings(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Store conversation learnings in memory for future recall.

        Creates semantic memories of:
        - Key insights discovered
        - Patterns identified
        - Capability gaps recognized
        - User preferences learned
        """
        learnings = input_data.get("learnings", [])
        analysis = input_data.get("analysis", {})

        if not self.memory:
            return SkillResult(
                success=False,
                output=None,
                error="MemorySkill required",
                skill_id=self.metadata().id,
            )

        stored_count = 0

        # Store each learning as semantic memory
        if isinstance(learnings, list):
            for learning in learnings:
                if isinstance(learning, dict):
                    content = learning.get("content", "")
                    importance = learning.get("importance", 0.7)
                elif isinstance(learning, str):
                    content = learning
                    importance = 0.7
                else:
                    continue

                self.memory.execute({
                    "capability": "experience",
                    "content": f"Session learning: {content}",
                    "memory_type": "semantic",
                    "importance": importance,
                    "context": {
                        "type": "session_learning",
                        "source": "session_analyzer",
                        "timestamp": datetime.now().isoformat(),
                    }
                }, context)
                stored_count += 1

        # Store overall analysis summary
        if analysis:
            summary = analysis.get("summary", "")
            if summary:
                self.memory.execute({
                    "capability": "experience",
                    "content": f"Session analysis: {summary}",
                    "memory_type": "episodic",
                    "importance": 0.8,
                    "context": {
                        "type": "session_analysis",
                        "timestamp": datetime.now().isoformat(),
                    }
                }, context)
                stored_count += 1

        return SkillResult(
            success=True,
            output={
                "learnings": learnings,
                "stored_count": stored_count,
                "summary": f"Stored {stored_count} learnings in memory",
            },
            skill_id=self.metadata().id,
        )
