#!/usr/bin/env python3
"""
Autonomous Skill Selector Agent - Meta-learning skill selection (like LL.model).

NOT a static router - this is an autonomous agent running continuously that:

1. LEARNS: Observes which skills work for which models/tasks
2. RECOMMENDS: Makes increasingly intelligent skill selections
3. ADAPTS: Updates internal models based on real outcomes
4. EXPLORES: Tries new skills to discover better combinations
5. EVOLVES: Continuously improves its decision-making

Works like an internal "LL.model" that trains on skill outcome data.

Key insight: Instead of hardcoded rules, the agent learns patterns like:
  "For GPIA-core + reasoning tasks → riemann_deep_analysis works best"
  "For GPIA-core + synthesis → synergy with zeta_function_synthesis"
  "For Student models → quick_summary is reliable"

And updates these associations as it observes outcomes.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import json
import sqlite3
from datetime import datetime
import time
import logging

# Import the core registry
try:
    from skills.core_registry import get_core_skill_registry
    CORE_REGISTRY_AVAILABLE = True
except ImportError:
    CORE_REGISTRY_AVAILABLE = False


class SkillSelectorMemory:
    """Persistent memory system for the agent (SQLite backend)."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Record of skill recommendations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    model TEXT,
                    task TEXT,
                    task_pattern TEXT,
                    skill_selected TEXT,
                    success BOOLEAN,
                    quality_score FLOAT,
                    selection_method TEXT
                )
            """)

            # Learned associations (what the agent learns)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY,
                    model TEXT,
                    task_pattern TEXT,
                    skill_name TEXT,
                    success_rate REAL,
                    avg_quality REAL,
                    confidence REAL,
                    observations INTEGER,
                    last_updated REAL,
                    UNIQUE(model, task_pattern, skill_name)
                )
            """)

            # Exploration attempts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exploration (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    model TEXT,
                    task_pattern TEXT,
                    skill_tried TEXT,
                    outcome_success BOOLEAN,
                    outcome_quality REAL
                )
            """)

            conn.commit()

    def record_recommendation(self, model: str, task: str, task_pattern: str,
                             skill: str, success: bool, quality: float,
                             method: str):
        """Record a skill recommendation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO recommendations
                (timestamp, model, task, task_pattern, skill_selected, success, quality_score, selection_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (time.time(), model, task, task_pattern, skill, success, quality, method))
            conn.commit()

    def update_pattern(self, model: str, task_pattern: str, skill: str,
                       success_rate: float, avg_quality: float, confidence: float,
                       observations: int):
        """Update or create a learned pattern."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO learned_patterns
                (model, task_pattern, skill_name, success_rate, avg_quality, confidence, observations, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(model, task_pattern, skill_name) DO UPDATE SET
                    success_rate=excluded.success_rate,
                    avg_quality=excluded.avg_quality,
                    confidence=excluded.confidence,
                    observations=excluded.observations,
                    last_updated=excluded.last_updated
            """, (model, task_pattern, skill, success_rate, avg_quality, confidence, observations, time.time()))
            conn.commit()

    def get_learned_patterns(self, model: str, task_pattern: str) -> List[Dict]:
        """Get all learned patterns for a model-task combo."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT skill_name, success_rate, avg_quality, confidence, observations
                FROM learned_patterns
                WHERE model = ? AND task_pattern = ?
                ORDER BY confidence DESC, avg_quality DESC
            """, (model, task_pattern))

            results = []
            for skill, sr, aq, conf, obs in cursor.fetchall():
                results.append({
                    "skill": skill,
                    "success_rate": sr,
                    "avg_quality": aq,
                    "confidence": conf,
                    "observations": obs
                })
            return results

    def get_all_patterns(self) -> List[Dict]:
        """Get all learned patterns."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT model, task_pattern, skill_name, success_rate, avg_quality, confidence, observations
                FROM learned_patterns
                ORDER BY confidence DESC, avg_quality DESC
            """)

            results = []
            for model, pattern, skill, sr, aq, conf, obs in cursor.fetchall():
                results.append({
                    "model": model,
                    "pattern": pattern,
                    "skill": skill,
                    "success_rate": sr,
                    "avg_quality": aq,
                    "confidence": conf,
                    "observations": obs
                })
            return results


class AutonomousSkillSelectorAgent:
    """
    Autonomous agent that learns to select the best skills autonomously.

    This is not a static router but a learning system that:
    - Observes outcomes of skill usage
    - Extracts patterns (model, task_type → best_skill)
    - Builds confidence scores based on observations
    - Makes intelligent recommendations
    - Explores new skills vs. exploiting known good ones
    """

    def __init__(self, repo_root: Path = None):
        """Initialize the autonomous skill selector agent."""
        if repo_root is None:
            repo_root = Path(__file__).resolve().parent.parent

        self.repo_root = repo_root
        self.skills_dir = repo_root / "skills"

        # Memory system
        memory_db = self.skills_dir / "core" / "selector_memory.db"
        self.memory = SkillSelectorMemory(memory_db)
        
        # Connect to official Registry
        self.registry = None
        if CORE_REGISTRY_AVAILABLE:
            self.registry = get_core_skill_registry(repo_root)

        # Learning parameters
        self.exploration_rate = 0.15  # 15% of decisions try new skills
        self.confidence_threshold = 0.70  # Use skill if confidence >= this
        self.min_observations_for_confidence = 5  # Need 5+ runs
        
        # Memory Safeguards
        self.max_skills_per_pattern = 5  # Max 5 different skills per pattern
        self._skill_cache = {}
        self.max_cache_size = 1000

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _manage_cache(self):
        """Prevent cache from growing unbounded."""
        if len(self._skill_cache) > self.max_cache_size:
            # Clear oldest 50%
            items_to_remove = self.max_cache_size // 2
            keys = list(self._skill_cache.keys())
            for key in keys[:items_to_remove]:
                del self._skill_cache[key]
            self.logger.info(f"[SAFEGUARD] Cleared {items_to_remove} items from skill cache")

    def abstract_task_pattern(self, task: str, state_metadata: Optional[Dict] = None) -> str:
        """
        Abstract a task to a pattern, now considering mathematical state data.
        """
        # If the mathematical state is "Hot" (high energy), prioritize reasoning
        if state_metadata and state_metadata.get("energy_level", 0) > 0.8:
            return "reasoning"

        task_lower = task.lower()
        patterns = {
            "reasoning": ["analyze", "derive", "explain", "understand", "reason", "complex"],
            "synthesis": ["combine", "synthesize", "integrate", "merge"],
            "validation": ["validate", "check", "verify", "prove"],
            "optimization": ["optimize", "improve", "enhance", "speed up"],
            "decomposition": ["break", "decompose", "split", "divide"],
            "pattern_recognition": ["pattern", "recognize", "detect", "identify"],
        }

        for pattern, keywords in patterns.items():
            if any(kw in task_lower for kw in keywords):
                return pattern

        return "general"

    def select_skill(self, model: str, task: str,
                    available_skills: Optional[List[str]] = None,
                    state_metadata: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Select best skill, now aware of the Dense-State environment.
        """
        # Periodic cache cleanup
        import random
        if random.random() < 0.05:  # 5% of calls
            self._manage_cache()

        pattern = self.abstract_task_pattern(task, state_metadata)
        
        # If no available_skills provided, fetch from official registry
        if not available_skills and self.registry:
            skills_by_cat = self.registry.list_core_skills()
            available_skills = skills_by_cat.get(pattern, [])
            # Fallback to all skills if category is empty
            if not available_skills:
                available_skills = [s for sublist in skills_by_cat.values() for s in sublist]

        # Get learned patterns for this model-task
        learned = self.memory.get_learned_patterns(model, pattern)
        
        # SAFEGUARD: Limit number of skills we consider per pattern
        if len(learned) > self.max_skills_per_pattern:
            learned = learned[:self.max_skills_per_pattern]

        reasoning = {
            "model": model,
            "task": task,
            "pattern": pattern,
            "learned_options": len(learned),
            "selection_method": "unknown",
            "selected_skill": None,
            "confidence": 0.0,
            "reasoning_explanation": ""
        }

        if learned and learned[0]["confidence"] >= self.confidence_threshold:
            # EXPLOIT: High confidence in top option
            skill = learned[0]["skill"]
            reasoning["selection_method"] = "exploitation"
            reasoning["confidence"] = learned[0]["confidence"]
            reasoning["selected_skill"] = skill
            reasoning["reasoning_explanation"] = (
                f"High confidence ({learned[0]['confidence']:.1%}) "
                f"with {learned[0]['observations']} observations"
            )
            return skill, reasoning

        elif available_skills:
            # EXPLORE: Try new skill or low-confidence option
            import random
            
            # SAFEGUARD: Ensure we don't choose from an empty list
            if not available_skills:
                skill = None
            else:
                if learned:
                    filtered_skills = [s for s in available_skills if s != learned[0]["skill"]]
                    skill = random.choice(filtered_skills) if filtered_skills else available_skills[0]
                else:
                    skill = random.choice(available_skills)

            if skill:
                reasoning["selection_method"] = "exploration"
                reasoning["confidence"] = 0.5
                reasoning["selected_skill"] = skill
                reasoning["reasoning_explanation"] = "Exploring new skill combination"
                return skill, reasoning
            else:
                reasoning["selection_method"] = "no_data"
                reasoning["selected_skill"] = None
                return None, reasoning

        elif learned:
            # FALLBACK: Use best learned even if low confidence
            skill = learned[0]["skill"]
            reasoning["selection_method"] = "fallback"
            reasoning["confidence"] = learned[0]["confidence"]
            reasoning["selected_skill"] = skill
            reasoning["reasoning_explanation"] = f"Fallback to best learned"
            return skill, reasoning

        else:
            # NO DATA: Return None or default
            reasoning["selection_method"] = "no_data"
            reasoning["selected_skill"] = None
            reasoning["reasoning_explanation"] = "No learned patterns yet"
            return None, reasoning

    def record_outcome(self, model: str, task: str, skill: str,
                      success: bool, quality: float, selection_method: str = ""):
        """
        Record the outcome of a skill selection and update learning.

        The agent learns from outcomes:
        - If skill worked well → increase confidence
        - If skill failed → decrease confidence
        - Track success rates per skill per model-task pair
        """
        pattern = self.abstract_task_pattern(task)

        # Record the recommendation
        self.memory.record_recommendation(model, task, pattern, skill, success, quality, selection_method)

        # Learn from it: update the pattern for this model-task-skill combo
        with sqlite3.connect(self.memory.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*), SUM(success), AVG(quality_score)
                FROM recommendations
                WHERE model = ? AND task_pattern = ? AND skill_selected = ?
            """, (model, pattern, skill))

            total, successes, avg_quality = cursor.fetchone()

            if total:
                success_rate = (successes or 0) / total
                # Confidence grows with observations
                confidence = min(1.0, total / (self.min_observations_for_confidence * 3))

                # Update the pattern
                self.memory.update_pattern(
                    model=model,
                    task_pattern=pattern,
                    skill=skill,
                    success_rate=success_rate,
                    avg_quality=avg_quality or 0.0,
                    confidence=confidence,
                    observations=total
                )

                self.logger.info(
                    f"[LEARNING] {model}/{pattern}/{skill}: "
                    f"SR={success_rate:.1%} Q={avg_quality:.2f} Conf={confidence:.2f} (n={total})"
                )

    def print_learned_knowledge(self):
        """Print what the agent has learned so far."""
        patterns = self.memory.get_all_patterns()

        print("\n" + "=" * 80)
        print("AUTONOMOUS SKILL SELECTOR - LEARNED KNOWLEDGE")
        print("=" * 80)

        if not patterns:
            print("\nNo patterns learned yet. Agent still exploring...\n")
            return

        # Group by model
        by_model = {}
        for p in patterns:
            model = p["model"]
            if model not in by_model:
                by_model[model] = {}
            pattern_name = p["pattern"]
            if pattern_name not in by_model[model]:
                by_model[model][pattern_name] = []
            by_model[model][pattern_name].append(p)

        for model in sorted(by_model.keys()):
            print(f"\nModel: {model}")
            print("-" * 80)
            for pattern in sorted(by_model[model].keys()):
                skills = by_model[model][pattern]
                print(f"  {pattern:20}")
                for s in skills:
                    print(f"    {s['skill']:30} SR={s['success_rate']:5.1%} "
                          f"Q={s['avg_quality']:.2f} C={s['confidence']:.2f} n={s['observations']}")

        print("\n" + "=" * 80 + "\n")

    def print_agent_status(self):
        """Print overall agent status."""
        patterns = self.memory.get_all_patterns()
        total_patterns = len(patterns)
        avg_confidence = sum(p["confidence"] for p in patterns) / len(patterns) if patterns else 0
        avg_sr = sum(p["success_rate"] for p in patterns) / len(patterns) if patterns else 0

        print("\n" + "=" * 80)
        print("AUTONOMOUS SKILL SELECTOR AGENT - STATUS")
        print("=" * 80)

        print(f"\nLearning Progress:")
        print(f"  Learned patterns: {total_patterns}")
        print(f"  Average confidence: {avg_confidence:.2f}/1.00")
        print(f"  Average success rate: {avg_sr:.1%}")
        print(f"  Exploration rate: {self.exploration_rate:.0%}")
        print(f"  Min observations for confidence: {self.min_observations_for_confidence}")
        print(f"  Confidence threshold: {self.confidence_threshold:.0%}")

        print(f"\nAgent Mode:")
        print(f"  Exploitation: Use learned skill when confidence >= {self.confidence_threshold:.0%}")
        print(f"  Exploration: Try new skills {self.exploration_rate:.0%} of time")
        print(f"  Learning: Update patterns from every outcome")

        print(f"\nMemory:")
        print(f"  Database: {self.memory.db_path}")

        print("=" * 80 + "\n")


def get_skill_selector_agent(repo_root: Path = None) -> AutonomousSkillSelectorAgent:
    """Get or create the autonomous skill selector agent (singleton)."""
    global _AGENT
    if _AGENT is None:
        _AGENT = AutonomousSkillSelectorAgent(repo_root)
    return _AGENT


_AGENT = None


if __name__ == "__main__":
    # Demo: Show agent learning
    agent = get_skill_selector_agent()

    print("\n" + "=" * 80)
    print("AUTONOMOUS SKILL SELECTOR AGENT - LEARNING DEMO")
    print("=" * 80)

    # Simulate skill recommendations and outcomes
    demo_data = [
        ("gpia-core", "Analyze the mathematical structure", "riemann_deep_analysis", True, 0.92),
        ("gpia-core", "Analyze the proof carefully", "riemann_deep_analysis", True, 0.91),
        ("gpia-core", "Analyze the hypothesis", "riemann_deep_analysis", True, 0.89),
        ("gpia-core", "Synthesize insights", "zeta_function_synthesis", True, 0.88),
        ("gpia-core", "Synthesize findings", "zeta_function_synthesis", True, 0.85),
        ("alpha", "Quick summary", "quick_summary", True, 0.78),
        ("alpha", "Brief explanation", "quick_summary", True, 0.81),
        ("beta", "Combine perspectives", "synthesis", True, 0.82),
    ]

    print("\nProcessing outcomes and learning patterns...")
    for model, task, skill, success, quality in demo_data:
        agent.record_outcome(model, task, skill, success, quality, "demo")
        print(f"  {model:10} + {task[:35]:35} -> {skill:30} Q={quality:.2f}")

    # Show what was learned
    agent.print_learned_knowledge()
    agent.print_agent_status()
