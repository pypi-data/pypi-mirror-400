#!/usr/bin/env python3
"""
Cross-Knowledge Detector Skill

Analyzes student performance and research progress to identify which skills
would most accelerate progress toward the goal (solving RH).

Example detection:
  "Hello Professor, I detected: If student learns 'spectral-analysis' skill,
   we can solve eigenvalue-alignment 3x faster. Preparing student profile.
   As soon as resources available, tackle the skill. Once valid, I'll inject
   it into the next student session."

Architecture:
1. Monitor student proposals and success rates
2. Identify bottlenecks in current approach
3. Query skill library for relevant cross-domain knowledge
4. Estimate time savings from learning new skill
5. Recommend skill learning to professor
6. Stage student for learning when resources available
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3


class SkillPriority(Enum):
    """Priority levels for skill learning."""
    CRITICAL = 1      # Blocks progress, must learn immediately
    HIGH = 2          # Significant speedup (>2x faster)
    MEDIUM = 3        # Moderate speedup (1.5x - 2x faster)
    LOW = 4           # Minor improvement (<1.5x faster)


@dataclass
class SkillRecommendation:
    """Recommendation to learn a new skill."""
    skill_name: str                    # e.g., "spectral-analysis"
    student: str                       # Which student should learn (e.g., "gamma")
    priority: SkillPriority            # CRITICAL, HIGH, MEDIUM, LOW
    estimated_speedup: float           # e.g., 3.2 (3.2x faster)
    reasoning: str                     # Why this skill helps
    estimated_learning_time: float     # Seconds to learn skill
    estimated_time_saved: float        # Seconds saved per use after learning
    cycles_to_breakeven: int          # How many cycles before time saved > time spent
    confidence: float                  # 0.0-1.0, how confident in recommendation


@dataclass
class ProgressMetrics:
    """Current research progress."""
    cycle: int
    students_completed: int
    total_proposals: int
    total_tokens: int
    avg_proposal_quality: float        # 0.0-1.0
    convergence_rate: float            # 0.0-1.0 (how fast approaching goal)
    bottleneck: Optional[str]          # What's slowing progress (e.g., "eigenvalue-analysis")
    identified_gaps: List[str]         # Skills that would help
    timestamp: float


class CrossKnowledgeDetector:
    """Detects opportunities for skill learning to accelerate research."""

    # Known cross-domain skill opportunities for RH research
    SKILL_OPPORTUNITIES = {
        "spectral-analysis": {
            "domains": ["eigenvalue", "hamiltonian", "quantum"],
            "estimated_speedup": 3.2,
            "reasoning": "Spectral methods directly apply to eigenvalue-based RH approaches",
            "learning_time": 120,  # seconds
        },
        "number-theoretic-lattice": {
            "domains": ["distribution", "lattice-points", "symmetry"],
            "estimated_speedup": 2.8,
            "reasoning": "Lattice theory explains zero spacing patterns",
            "learning_time": 150,
        },
        "functional-equations": {
            "domains": ["zeta-function", "analytic-continuation", "functional"],
            "estimated_speedup": 2.5,
            "reasoning": "Functional equations are central to zeta function analysis",
            "learning_time": 140,
        },
        "computational-verification": {
            "domains": ["numerical", "verification", "algorithm"],
            "estimated_speedup": 2.2,
            "reasoning": "Numerical verification tests theoretical predictions",
            "learning_time": 100,
        },
        "algebraic-geometry": {
            "domains": ["algebraic", "geometry", "variety"],
            "estimated_speedup": 2.0,
            "reasoning": "Algebraic geometry provides structure for RH proofs",
            "learning_time": 180,
        },
        "information-theory": {
            "domains": ["entropy", "information", "complexity"],
            "estimated_speedup": 1.8,
            "reasoning": "Information-theoretic bounds relate to zero distribution",
            "learning_time": 110,
        },
    }

    def __init__(self, session_dir: Path):
        """Initialize detector with session directory."""
        self.session_dir = Path(session_dir)
        self.history_dir = self.session_dir / "skill_detector_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Database for tracking recommendations and learning
        self.db_path = self.history_dir / "skill_recommendations.db"
        self._init_database()

        # Cache of learned skills (don't recommend learning twice)
        self.learned_skills = set()
        self._load_learned_skills()

    def _init_database(self):
        """Initialize SQLite database for skill tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY,
                    cycle INTEGER,
                    skill_name TEXT,
                    student TEXT,
                    priority TEXT,
                    estimated_speedup REAL,
                    reasoning TEXT,
                    timestamp REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_skills (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT UNIQUE,
                    learned_cycle INTEGER,
                    learned_by_student TEXT,
                    validation_status TEXT,
                    speedup_measured REAL,
                    timestamp REAL
                )
            """)
            conn.commit()

    def _load_learned_skills(self):
        """Load skills already learned in this session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT skill_name FROM learned_skills
                WHERE validation_status = 'valid'
            """)
            self.learned_skills = {row[0] for row in cursor.fetchall()}

    def analyze_progress(self, progress_metrics: ProgressMetrics) -> List[SkillRecommendation]:
        """
        Analyze current progress and identify skill learning opportunities.

        Args:
            progress_metrics: Current research metrics

        Returns:
            List of skill recommendations ranked by priority
        """
        recommendations = []

        # Analyze convergence rate
        if progress_metrics.convergence_rate < 0.3:
            # Very slow progress - need significant acceleration
            priority_boost = SkillPriority.CRITICAL
        elif progress_metrics.convergence_rate < 0.5:
            # Slow progress - need good speedup
            priority_boost = SkillPriority.HIGH
        else:
            # Moderate progress
            priority_boost = SkillPriority.MEDIUM

        # Identify relevant skills based on identified gaps
        for gap in progress_metrics.identified_gaps:
            for skill_name, skill_info in self.SKILL_OPPORTUNITIES.items():
                # Skip if already learned
                if skill_name in self.learned_skills:
                    continue

                # Check if skill relevant to this gap
                if any(domain in gap.lower() for domain in skill_info["domains"]):
                    recommendation = SkillRecommendation(
                        skill_name=skill_name,
                        student=self._select_student_for_skill(skill_name),
                        priority=priority_boost,
                        estimated_speedup=skill_info["estimated_speedup"],
                        reasoning=skill_info["reasoning"],
                        estimated_learning_time=skill_info["learning_time"],
                        estimated_time_saved=skill_info["learning_time"] * (
                            skill_info["estimated_speedup"] - 1
                        ),
                        cycles_to_breakeven=self._calculate_breakeven(
                            skill_info["learning_time"],
                            skill_info["estimated_speedup"]
                        ),
                        confidence=self._calculate_confidence(gap, skill_name),
                    )
                    recommendations.append(recommendation)

        # Sort by priority
        recommendations.sort(key=lambda r: (r.priority.value, -r.estimated_speedup))

        # Save recommendations
        for rec in recommendations:
            self._record_recommendation(progress_metrics.cycle, rec)

        return recommendations

    def _select_student_for_skill(self, skill_name: str) -> str:
        """Select which student should learn this skill."""
        # Map skills to students based on specialization
        student_specializations = {
            "alpha": ["spectral-analysis", "functional-equations"],
            "beta": ["algebraic-geometry", "number-theoretic-lattice"],
            "gamma": ["computational-verification", "information-theory"],
            "delta": ["functional-equations", "algebraic-geometry"],
            "epsilon": ["cross-knowledge-synthesis"],
            "zeta": ["computational-verification", "algorithm"],
        }

        # Find best match
        for student, skills in student_specializations.items():
            if skill_name in skills:
                return student

        # Default to epsilon (meta-learner)
        return "epsilon"

    def _calculate_breakeven(self, learning_time: float, speedup: float) -> int:
        """Calculate how many cycles needed to break even on learning time."""
        # Assuming ~30s per cycle baseline
        baseline_cycle_time = 30
        time_saved_per_cycle = baseline_cycle_time * (speedup - 1) / speedup

        if time_saved_per_cycle <= 0:
            return float('inf')

        return int(learning_time / time_saved_per_cycle) + 1

    def _calculate_confidence(self, gap: str, skill_name: str) -> float:
        """Calculate confidence that this skill will help."""
        # Simple heuristic: how many domain keywords match
        skill_info = self.SKILL_OPPORTUNITIES[skill_name]
        matching_domains = sum(
            1 for domain in skill_info["domains"]
            if domain.lower() in gap.lower()
        )

        base_confidence = min(1.0, matching_domains / 2)  # Normalize to 0-1
        return max(0.5, base_confidence)  # Never less than 50% confident

    def _record_recommendation(self, cycle: int, recommendation: SkillRecommendation):
        """Record skill recommendation in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO recommendations
                (cycle, skill_name, student, priority, estimated_speedup, reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cycle,
                recommendation.skill_name,
                recommendation.student,
                recommendation.priority.name,
                recommendation.estimated_speedup,
                recommendation.reasoning,
                time.time(),
            ))
            conn.commit()

    def record_skill_learned(
        self,
        skill_name: str,
        learned_by_student: str,
        cycle: int,
        validation_status: str = "pending"
    ):
        """Record that a skill was learned."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learned_skills
                (skill_name, learned_cycle, learned_by_student, validation_status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                skill_name,
                cycle,
                learned_by_student,
                validation_status,
                time.time(),
            ))
            conn.commit()

        if validation_status == "valid":
            self.learned_skills.add(skill_name)

    def validate_skill(self, skill_name: str, speedup_measured: float):
        """Mark skill as validated with measured speedup."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE learned_skills
                SET validation_status = 'valid', speedup_measured = ?
                WHERE skill_name = ?
            """, (speedup_measured, skill_name))
            conn.commit()

        self.learned_skills.add(skill_name)

    def get_learned_skills(self) -> Dict[str, Dict]:
        """Get all validated skills that can be injected."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT skill_name, speedup_measured, learned_by_student
                FROM learned_skills
                WHERE validation_status = 'valid'
            """)
            return {
                row[0]: {
                    "speedup": row[1],
                    "learned_by": row[2],
                }
                for row in cursor.fetchall()
            }

    def generate_professor_message(self, recommendations: List[SkillRecommendation]) -> str:
        """Generate natural language message for professor."""
        if not recommendations:
            return "No cross-knowledge opportunities detected at this time."

        # Get highest priority recommendation
        top_rec = recommendations[0]

        message = f"""
Hello Professor, I detected a cross-knowledge opportunity:

**Skill**: {top_rec.skill_name}
**Target Student**: {top_rec.student}
**Priority**: {top_rec.priority.name}
**Estimated Speedup**: {top_rec.estimated_speedup:.1f}x faster

**Why This Matters**:
{top_rec.reasoning}

**Learning Plan**:
- Learning time: {top_rec.estimated_learning_time:.0f} seconds
- Break-even point: {top_rec.cycles_to_breakeven} cycles
- Time saved per use: {top_rec.estimated_time_saved:.0f} seconds
- Confidence: {top_rec.confidence*100:.0f}%

**Proposed Action**:
1. Stage {top_rec.student} for skill learning
2. When resources available, execute learning cycle
3. Once validated, inject skill into all student sessions
4. All future research benefiting from {top_rec.estimated_speedup:.1f}x speedup

Proceeding with skill staging...
"""
        return message


# Singleton
_DETECTOR = None


def get_cross_knowledge_detector(session_dir: Path = None) -> CrossKnowledgeDetector:
    """Get or create detector."""
    global _DETECTOR
    if _DETECTOR is None:
        if session_dir is None:
            session_dir = Path("agents/sessions/default")
        _DETECTOR = CrossKnowledgeDetector(session_dir)
    return _DETECTOR
