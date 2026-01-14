"""
Adaptive Operation - Intelligent Continuous Execution
======================================================

This skill enables Alpha Agent to run continuously with adaptive timing
based on learned patterns from memory and activity analysis.

Moves from mechanical (fixed intervals) to intelligent (pattern-based)
autonomous operation.

Capabilities:
- analyze_activity: Analyze recent activity patterns
- calculate_interval: Determine optimal next interval
- adjust_timing: Update operation timing based on patterns
- learn_patterns: Extract timing patterns from memory

This is the meta-skill that makes "running continuously" an
intelligent, learned capability rather than a mechanical loop.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

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


class AdaptiveOperationSkill(Skill):
    """
    Intelligent continuous operation with adaptive timing.

    Instead of fixed intervals (e.g., every 300 seconds), this skill
    learns from patterns to optimize when Alpha should run.

    Factors considered:
    - Recent activity levels (messages, changes, events)
    - Memory growth patterns
    - Time of day patterns
    - Resource availability
    - Goal urgency
    """

    def __init__(self):
        self._memory = None
        self._baseline_interval = 300  # Default 5 minutes
        self._min_interval = 30  # Minimum 30 seconds
        self._max_interval = 3600  # Maximum 1 hour

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
            id="alpha/adaptive-operation",
            name="Adaptive Operation",
            description="Intelligent continuous operation with pattern-based adaptive timing",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.EXPERT,
            tags=["alpha", "adaptive", "timing", "autonomous", "meta-cognitive"],
            dependencies=[
                SkillDependency(skill_id="conscience/memory", optional=False),
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["analyze_activity", "calculate_interval", "adjust_timing", "learn_patterns"],
                },
                "time_window": {
                    "type": "number",
                    "description": "Time window in seconds for activity analysis",
                    "default": 3600,
                },
                "current_interval": {
                    "type": "number",
                    "description": "Current operation interval",
                },
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "activity_level": {"type": "number"},
                "recommended_interval": {"type": "number"},
                "patterns": {"type": "object"},
                "reasoning": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "analyze_activity": self._analyze_activity,
            "calculate_interval": self._calculate_interval,
            "adjust_timing": self._adjust_timing,
            "learn_patterns": self._learn_patterns,
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
            logger.error(f"AdaptiveOperation {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _analyze_activity(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Analyze recent activity to determine system load.

        Activity indicators:
        - New memories created
        - Memory access frequency
        - Messages received
        - Skills executed
        - Cycles completed

        Returns activity level: 0.0 (idle) to 1.0 (very busy)
        """
        time_window = input_data.get("time_window", 3600)  # Default 1 hour

        if not self.memory:
            # Fallback: moderate activity assumption
            return SkillResult(
                success=True,
                output={
                    "activity_level": 0.5,
                    "reasoning": "Memory not available, assuming moderate activity",
                },
                skill_id=self.metadata().id,
            )

        # Get memory stats
        stats = self.memory.store.get_stats()
        total_memories = stats.get("total_memories", 0)

        # Get recent memories (last time_window)
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=time_window)

        recent_memories = self.memory.store.recall_by_time(
            start=start_time,
            end=end_time,
            limit=1000
        )

        # Calculate activity metrics
        recent_count = len(recent_memories)
        activity_rate = recent_count / (time_window / 60)  # Memories per minute

        # Classify activity level
        if activity_rate > 10:
            activity_level = 1.0  # Very busy
            reasoning = f"High activity: {activity_rate:.1f} memories/min"
        elif activity_rate > 5:
            activity_level = 0.8  # Busy
            reasoning = f"Busy: {activity_rate:.1f} memories/min"
        elif activity_rate > 2:
            activity_level = 0.5  # Moderate
            reasoning = f"Moderate: {activity_rate:.1f} memories/min"
        elif activity_rate > 0.5:
            activity_level = 0.3  # Low
            reasoning = f"Low activity: {activity_rate:.1f} memories/min"
        else:
            activity_level = 0.1  # Idle
            reasoning = f"Idle: {activity_rate:.1f} memories/min"

        return SkillResult(
            success=True,
            output={
                "activity_level": activity_level,
                "recent_memories": recent_count,
                "activity_rate": activity_rate,
                "reasoning": reasoning,
                "time_window": time_window,
            },
            skill_id=self.metadata().id,
        )

    def _calculate_interval(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Calculate optimal next interval based on activity analysis.

        Logic:
        - High activity (>0.8): Short interval (30-60s)
        - Medium activity (0.3-0.8): Moderate interval (2-5min)
        - Low activity (<0.3): Long interval (10-30min)
        - Idle (<0.1): Maximum interval (up to 1hr)
        """
        # First analyze current activity
        activity_result = self._analyze_activity(input_data, context)

        if not activity_result.success:
            # Fallback to baseline
            return SkillResult(
                success=True,
                output={
                    "recommended_interval": self._baseline_interval,
                    "reasoning": "Activity analysis failed, using baseline",
                },
                skill_id=self.metadata().id,
            )

        activity_level = activity_result.output.get("activity_level", 0.5)

        # Calculate interval based on activity
        if activity_level >= 0.9:
            interval = self._min_interval  # 30s
            reasoning = "Very high activity - checking every 30s"
        elif activity_level >= 0.7:
            interval = 60  # 1min
            reasoning = "High activity - checking every minute"
        elif activity_level >= 0.5:
            interval = 180  # 3min
            reasoning = "Moderate activity - checking every 3 minutes"
        elif activity_level >= 0.3:
            interval = 300  # 5min (baseline)
            reasoning = "Normal activity - baseline interval"
        elif activity_level >= 0.15:
            interval = 600  # 10min
            reasoning = "Low activity - checking every 10 minutes"
        elif activity_level >= 0.05:
            interval = 1800  # 30min
            reasoning = "Very low activity - checking every 30 minutes"
        else:
            interval = self._max_interval  # 1hr
            reasoning = "Idle - maximum interval"

        # Ensure within bounds
        interval = max(self._min_interval, min(interval, self._max_interval))

        return SkillResult(
            success=True,
            output={
                "recommended_interval": interval,
                "activity_level": activity_level,
                "reasoning": reasoning,
                "activity_analysis": activity_result.output,
            },
            skill_id=self.metadata().id,
        )

    def _adjust_timing(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Adjust timing based on learned patterns and current state.

        This combines:
        1. Current activity analysis
        2. Historical patterns
        3. Time of day factors
        4. Goal urgency

        Returns: Complete timing adjustment recommendation
        """
        current_interval = input_data.get("current_interval", self._baseline_interval)

        # Get interval recommendation
        interval_result = self._calculate_interval(input_data, context)

        if not interval_result.success:
            return SkillResult(
                success=False,
                output=None,
                error="Interval calculation failed",
                skill_id=self.metadata().id,
            )

        recommended_interval = interval_result.output.get("recommended_interval")
        activity_level = interval_result.output.get("activity_level", 0.5)

        # Calculate adjustment percentage
        if current_interval > 0:
            change_percent = ((recommended_interval - current_interval) / current_interval) * 100
        else:
            change_percent = 0

        # Determine adjustment action
        if abs(change_percent) < 10:
            action = "MAINTAIN"
            adjustment = "Current timing is optimal"
        elif change_percent > 0:
            action = "INCREASE"
            adjustment = f"Increase interval by {change_percent:.0f}% ({current_interval}s → {recommended_interval}s)"
        else:
            action = "DECREASE"
            adjustment = f"Decrease interval by {abs(change_percent):.0f}% ({current_interval}s → {recommended_interval}s)"

        # Store timing decision in memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Timing adjustment: {action} - {adjustment}",
                "memory_type": "procedural",
                "importance": 0.6,
                "context": {
                    "type": "timing_decision",
                    "action": action,
                    "old_interval": current_interval,
                    "new_interval": recommended_interval,
                    "activity_level": activity_level,
                    "timestamp": datetime.now().isoformat(),
                }
            }, context)

        return SkillResult(
            success=True,
            output={
                "action": action,
                "current_interval": current_interval,
                "recommended_interval": recommended_interval,
                "change_percent": change_percent,
                "adjustment": adjustment,
                "reasoning": interval_result.output.get("reasoning"),
            },
            skill_id=self.metadata().id,
        )

    def _learn_patterns(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Extract timing patterns from historical memory.

        Analyzes:
        - Activity patterns by time of day
        - Typical interval adjustments
        - Successful vs. unsuccessful timing decisions
        - Correlation between activity and outcomes
        """
        if not self.memory:
            return SkillResult(
                success=False,
                output=None,
                error="Memory required for pattern learning",
                skill_id=self.metadata().id,
            )

        # Recall timing decisions from memory
        timing_memories = self.memory.execute({
            "capability": "recall",
            "query": "timing decision adjustment interval",
            "memory_type": "procedural",
            "limit": 50,
        }, context)

        if not timing_memories.success:
            return SkillResult(
                success=False,
                output=None,
                error="Failed to recall timing memories",
                skill_id=self.metadata().id,
            )

        memories = timing_memories.output.get("memories", [])

        # Analyze patterns
        patterns = {
            "total_decisions": len(memories),
            "increases": 0,
            "decreases": 0,
            "maintains": 0,
            "avg_activity": 0.0,
        }

        activity_sum = 0.0
        for mem in memories:
            ctx = mem.get("context", {})
            if isinstance(ctx, str):
                import json
                try:
                    ctx = json.loads(ctx)
                except:
                    continue

            action = ctx.get("action", "")
            if action == "INCREASE":
                patterns["increases"] += 1
            elif action == "DECREASE":
                patterns["decreases"] += 1
            elif action == "MAINTAIN":
                patterns["maintains"] += 1

            activity_sum += ctx.get("activity_level", 0.5)

        if len(memories) > 0:
            patterns["avg_activity"] = activity_sum / len(memories)

        # Generate pattern summary
        if patterns["total_decisions"] == 0:
            summary = "No timing patterns learned yet - building baseline"
        else:
            dominant_action = max(
                [("INCREASE", patterns["increases"]),
                 ("DECREASE", patterns["decreases"]),
                 ("MAINTAIN", patterns["maintains"])],
                key=lambda x: x[1]
            )[0]
            summary = f"Learned {patterns['total_decisions']} timing decisions. "
            summary += f"Dominant pattern: {dominant_action}. "
            summary += f"Average activity: {patterns['avg_activity']:.2f}"

        return SkillResult(
            success=True,
            output={
                "patterns": patterns,
                "summary": summary,
                "learned_at": datetime.now().isoformat(),
            },
            skill_id=self.metadata().id,
        )
