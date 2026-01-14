#!/usr/bin/env python3
"""
GPIA-Core Skill Registry - Specialized skills for core reasoning model.

Architecture:
  - GPIA-core has its own curated skill set
  - Optimized for deep reasoning and synthesis
  - Fallback to general skills if needed
  - Can evolve independently from student skills
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3


class GPIACoreSkillRegistry:
    """Specialized registry for GPIA-core model skills."""

    # Core-specific skill categories (different from student skills)
    CORE_SKILL_CATEGORIES = {
        "reasoning": "Deep logical reasoning patterns",
        "synthesis": "Combining multiple insights into coherent output",
        "validation": "Checking proofs and logical consistency",
        "abstraction": "Finding patterns and generalizations",
        "decomposition": "Breaking complex problems into sub-problems",
        "recursive_thinking": "Recursive problem solving",
        "constraint_solving": "Working with mathematical constraints",
        "pattern_recognition": "Finding mathematical patterns",
    }

    def __init__(self, repo_root: Path = None):
        """Initialize GPIA-core skill registry."""
        if repo_root is None:
            repo_root = Path(__file__).resolve().parent.parent

        self.repo_root = repo_root
        self.skills_dir = repo_root / "skills"
        self.core_skills_dir = self.skills_dir / "core"
        self.core_skills_dir.mkdir(parents=True, exist_ok=True)

        # Database for skill performance tracking
        self.db_path = self.core_skills_dir / "core_skill_metrics.db"
        self._init_database()

        # In-memory cache
        self._skill_cache = {}
        self._performance_cache = {}

    def _init_database(self):
        """Initialize SQLite database for skill metrics."""
        with sqlite3.connect(self.db_path) as conn:
            # Track skill usage and performance
            conn.execute("""
                CREATE TABLE IF NOT EXISTS core_skills (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    category TEXT,
                    description TEXT,
                    version TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)

            # Track skill performance
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_performance (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT,
                    task TEXT,
                    success BOOLEAN,
                    quality_score FLOAT,
                    execution_time_ms FLOAT,
                    tokens_used INTEGER,
                    timestamp REAL
                )
            """)

            # Track skill compositions (which skills work together)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_compositions (
                    id INTEGER PRIMARY KEY,
                    primary_skill TEXT,
                    supporting_skill TEXT,
                    synergy_score FLOAT,
                    use_count INTEGER,
                    timestamp REAL
                )
            """)

            conn.commit()

    def list_core_skills(self) -> Dict[str, List[str]]:
        """List all available core skills by category.

        Returns: {
            "reasoning": ["skill1", "skill2", ...],
            "synthesis": [...],
            ...
        }
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT category, name FROM core_skills
                ORDER BY category, name
            """)

            skills_by_category = {}
            for category, name in cursor.fetchall():
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(name)

            return skills_by_category

    def get_skill_for_task(self, task: str, task_type: str = "reasoning") -> Optional[str]:
        """Get best skill for a given task.

        Args:
            task: The task description
            task_type: Type of task (reasoning, synthesis, validation, etc.)

        Returns: Skill name if found, else None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name
                FROM core_skills
                WHERE category = ?
                ORDER BY (
                    SELECT AVG(quality_score)
                    FROM skill_performance
                    WHERE skill_name = core_skills.name
                ) DESC
                LIMIT 1
            """, (task_type,))

            result = cursor.fetchone()
            return result[0] if result else None

    def register_core_skill(
        self,
        name: str,
        category: str,
        description: str,
        version: str = "1.0"
    ) -> bool:
        """Register a new core skill.

        Args:
            name: Skill name (e.g., "riemann_analysis")
            category: Skill category (from CORE_SKILL_CATEGORIES)
            description: What the skill does
            version: Semantic version

        Returns: True if registered, False if already exists
        """
        if category not in self.CORE_SKILL_CATEGORIES:
            raise ValueError(f"Unknown category: {category}")

        import time

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO core_skills (name, category, description, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, category, description, version, time.time(), time.time()))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def record_skill_performance(
        self,
        skill_name: str,
        task: str,
        success: bool,
        quality_score: float,
        execution_time_ms: float,
        tokens_used: int
    ):
        """Record how well a skill performed on a task.

        Args:
            skill_name: Which skill was used
            task: What task it performed
            success: Did it succeed?
            quality_score: 0.0-1.0 quality rating
            execution_time_ms: How long it took
            tokens_used: Tokens consumed
        """
        import time

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO skill_performance
                (skill_name, task, success, quality_score, execution_time_ms, tokens_used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (skill_name, task, success, quality_score, execution_time_ms, tokens_used, time.time()))
            conn.commit()

    def get_skill_performance(self, skill_name: str) -> Dict[str, Any]:
        """Get performance statistics for a skill.

        Returns: {
            "name": "skill_name",
            "success_rate": 0.95,
            "avg_quality": 0.87,
            "avg_time_ms": 2500,
            "total_uses": 42,
            "avg_tokens": 450
        }
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    skill_name,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                    COUNT(*) as total,
                    AVG(quality_score) as avg_quality,
                    AVG(execution_time_ms) as avg_time,
                    AVG(tokens_used) as avg_tokens
                FROM skill_performance
                WHERE skill_name = ?
                GROUP BY skill_name
            """, (skill_name,))

            result = cursor.fetchone()
            if not result:
                return {}

            name, successes, total, avg_quality, avg_time, avg_tokens = result
            return {
                "name": name,
                "success_rate": successes / total if total > 0 else 0,
                "avg_quality": avg_quality or 0,
                "avg_time_ms": avg_time or 0,
                "total_uses": total,
                "avg_tokens": avg_tokens or 0
            }

    def record_skill_synergy(self, primary: str, supporting: str, synergy_score: float):
        """Record that two skills work well together.

        Args:
            primary: Main skill being used
            supporting: Skill that enhanced the result
            synergy_score: 0.0-1.0 indicating how well they worked together
        """
        import time

        with sqlite3.connect(self.db_path) as conn:
            # Check if composition already exists
            cursor = conn.execute("""
                SELECT id, use_count FROM skill_compositions
                WHERE primary_skill = ? AND supporting_skill = ?
            """, (primary, supporting))

            existing = cursor.fetchone()

            if existing:
                # Update existing composition
                skill_id, use_count = existing
                conn.execute("""
                    UPDATE skill_compositions
                    SET use_count = ?, synergy_score = ?, timestamp = ?
                    WHERE id = ?
                """, (use_count + 1, synergy_score, time.time(), skill_id))
            else:
                # Create new composition
                conn.execute("""
                    INSERT INTO skill_compositions
                    (primary_skill, supporting_skill, synergy_score, use_count, timestamp)
                    VALUES (?, ?, ?, 1, ?)
                """, (primary, supporting, synergy_score, time.time()))

            conn.commit()

    def get_best_skill_combinations(self, primary_skill: str) -> List[Dict]:
        """Get skills that work best with a given primary skill.

        Returns: [
            {
                "supporting_skill": "name",
                "synergy_score": 0.92,
                "use_count": 15
            },
            ...
        ]
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT supporting_skill, synergy_score, use_count
                FROM skill_compositions
                WHERE primary_skill = ?
                ORDER BY synergy_score DESC
                LIMIT 5
            """, (primary_skill,))

            results = []
            for supporting, synergy, use_count in cursor.fetchall():
                results.append({
                    "supporting_skill": supporting,
                    "synergy_score": synergy,
                    "use_count": use_count
                })

            return results

    def get_top_skills(self, category: str = None, limit: int = 10) -> List[Dict]:
        """Get top performing skills (by quality score).

        Args:
            category: Filter by category, or None for all
            limit: How many to return

        Returns: List of skill dicts with performance stats
        """
        with sqlite3.connect(self.db_path) as conn:
            if category:
                query = """
                    SELECT cs.name, cs.category, cs.version,
                           AVG(sp.quality_score) as avg_quality,
                           COUNT(*) as use_count,
                           AVG(sp.execution_time_ms) as avg_time
                    FROM core_skills cs
                    LEFT JOIN skill_performance sp ON cs.name = sp.skill_name
                    WHERE cs.category = ?
                    GROUP BY cs.name
                    ORDER BY avg_quality DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, (category, limit))
            else:
                query = """
                    SELECT cs.name, cs.category, cs.version,
                           AVG(sp.quality_score) as avg_quality,
                           COUNT(*) as use_count,
                           AVG(sp.execution_time_ms) as avg_time
                    FROM core_skills cs
                    LEFT JOIN skill_performance sp ON cs.name = sp.skill_name
                    GROUP BY cs.name
                    ORDER BY avg_quality DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, (limit,))

            results = []
            for name, category, version, avg_quality, use_count, avg_time in cursor.fetchall():
                results.append({
                    "name": name,
                    "category": category,
                    "version": version,
                    "avg_quality": avg_quality or 0,
                    "use_count": use_count or 0,
                    "avg_time_ms": avg_time or 0
                })

            return results

    def print_registry_status(self):
        """Print current registry status."""
        skills_by_cat = self.list_core_skills()

        print("\n" + "=" * 80)
        print("GPIA-CORE SKILL REGISTRY STATUS")
        print("=" * 80)

        total_skills = 0
        for category in sorted(self.CORE_SKILL_CATEGORIES.keys()):
            skills = skills_by_cat.get(category, [])
            count = len(skills)
            total_skills += count
            print(f"\n{category.upper()} ({count})")
            print(f"  {self.CORE_SKILL_CATEGORIES[category]}")
            for skill in skills:
                perf = self.get_skill_performance(skill)
                if perf:
                    print(f"    - {skill}: {perf.get('success_rate', 0)*100:.0f}% success, "
                          f"Q={perf.get('avg_quality', 0):.2f}")
                else:
                    print(f"    - {skill}: (no data yet)")

        print(f"\n{'=' * 80}")
        print(f"Total core skills: {total_skills}")
        print(f"Database: {self.db_path}")
        print("=" * 80 + "\n")


# Global instance
_CORE_REGISTRY = None


def get_core_skill_registry(repo_root: Path = None) -> GPIACoreSkillRegistry:
    """Get or create the GPIA-core skill registry (singleton)."""
    global _CORE_REGISTRY
    if _CORE_REGISTRY is None:
        _CORE_REGISTRY = GPIACoreSkillRegistry(repo_root)
    return _CORE_REGISTRY


if __name__ == "__main__":
    # Demo: Initialize and show registry
    registry = get_core_skill_registry()

    # Register some example core skills
    example_skills = [
        ("riemann_deep_analysis", "reasoning", "Deep analysis of Riemann Hypothesis from first principles"),
        ("zeta_function_synthesis", "synthesis", "Combining zeta function properties with recent findings"),
        ("proof_validation", "validation", "Validating mathematical proofs for logical consistency"),
        ("pattern_abstraction", "abstraction", "Finding abstract patterns in number theory"),
        ("problem_decomposition", "decomposition", "Breaking RH into solvable sub-problems"),
        ("recursive_analysis", "recursive_thinking", "Applying recursion to mathematical problems"),
        ("constraint_solver", "constraint_solving", "Solving problems with mathematical constraints"),
        ("number_pattern_detector", "pattern_recognition", "Detecting patterns in sequences and functions"),
    ]

    for name, category, description in example_skills:
        registry.register_core_skill(name, category, description, "1.0")

    # Show status
    registry.print_registry_status()
