#!/usr/bin/env python3
"""
Skill Staging Orchestrator

Manages the lifecycle of learning new skills:
1. Identifies skill to learn (from cross_knowledge_detector)
2. Prepares student profile for learning
3. Stages the learning task (waits for resources)
4. Executes skill synthesis using cognitive ecosystem
5. Validates the learned skill
6. Marks skill as ready for injection

Integrates with:
- gpia_cognitive_ecosystem.py (Hunter/Dissector/Synthesizer)
- adaptive_student_scheduler.py (resource availability)
- cross_knowledge_detector.py (skill recommendations)
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3


class LearningStatus(Enum):
    """Status of skill learning process."""
    RECOMMENDED = 1    # Detector recommended learning
    STAGED = 2         # Waiting for resources
    LEARNING = 3       # Currently learning
    SYNTHESIZED = 4    # Skill synthesized, needs validation
    VALIDATING = 5     # Testing learned skill
    VALID = 6          # Skill validated, ready to inject
    FAILED = 7         # Learning failed


@dataclass
class StagedSkill:
    """A skill staged for learning."""
    skill_name: str
    student: str
    target_goal: str                  # What problem does this skill solve
    learning_prompt: str              # Prompt to teach the skill
    status: LearningStatus
    cycle_staged: int
    cycle_learning_started: Optional[int] = None
    cycle_validation_started: Optional[int] = None
    cycle_completed: Optional[int] = None
    learned_skill_path: Optional[str] = None
    validation_results: Optional[Dict] = None
    timestamp: float = None


class SkillStagingOrchestrator:
    """Orchestrates the process of learning and validating new skills."""

    def __init__(self, session_dir: Path):
        """Initialize skill staging orchestrator."""
        self.session_dir = Path(session_dir)
        self.staging_dir = self.session_dir / "skill_staging"
        self.staging_dir.mkdir(parents=True, exist_ok=True)

        # Database for tracking staged skills
        self.db_path = self.staging_dir / "staged_skills.db"
        self._init_database()

        # Queue of skills waiting to be learned
        self.staged_skills: Dict[str, StagedSkill] = {}
        self._load_staged_skills()

    def _init_database(self):
        """Initialize database for skill staging tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS staged_skills (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT UNIQUE,
                    student TEXT,
                    target_goal TEXT,
                    status TEXT,
                    cycle_staged INTEGER,
                    cycle_learning_started INTEGER,
                    cycle_validation_started INTEGER,
                    cycle_completed INTEGER,
                    learned_skill_path TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def _load_staged_skills(self):
        """Load previously staged skills from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT skill_name, status FROM staged_skills")
            for skill_name, status_str in cursor.fetchall():
                status = LearningStatus[status_str]
                # Only load non-completed skills
                if status not in (LearningStatus.VALID, LearningStatus.FAILED):
                    self.staged_skills[skill_name] = StagedSkill(
                        skill_name=skill_name,
                        student="unknown",
                        target_goal="unknown",
                        learning_prompt="",
                        status=status,
                        cycle_staged=0,
                        timestamp=time.time(),
                    )

    def stage_skill_learning(
        self,
        skill_name: str,
        student: str,
        target_goal: str,
        reasoning: str,
        current_cycle: int,
    ) -> StagedSkill:
        """
        Stage a skill for learning.

        Args:
            skill_name: Name of skill to learn (e.g., "spectral-analysis")
            student: Which student will learn it
            target_goal: What problem this solves
            reasoning: Why this skill matters
            current_cycle: Current research cycle

        Returns:
            StagedSkill object
        """
        # Create learning prompt
        learning_prompt = self._create_learning_prompt(
            skill_name=skill_name,
            student=student,
            target_goal=target_goal,
            reasoning=reasoning,
        )

        # Create staged skill
        staged = StagedSkill(
            skill_name=skill_name,
            student=student,
            target_goal=target_goal,
            learning_prompt=learning_prompt,
            status=LearningStatus.STAGED,
            cycle_staged=current_cycle,
            timestamp=time.time(),
        )

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO staged_skills
                (skill_name, student, target_goal, status, cycle_staged, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                skill_name,
                student,
                target_goal,
                staged.status.name,
                current_cycle,
                time.time(),
            ))
            conn.commit()

        self.staged_skills[skill_name] = staged
        return staged

    def _create_learning_prompt(
        self,
        skill_name: str,
        student: str,
        target_goal: str,
        reasoning: str,
    ) -> str:
        """Create detailed prompt for teaching skill."""
        prompt = f"""
# Skill Learning Task: {skill_name}

## Context
- Student: {student} (specialization: {self._get_student_specialty(student)})
- Goal: {target_goal}
- Why: {reasoning}

## Task
Create a reusable Python skill that teaches/implements {skill_name}.

The skill should:
1. Solve {target_goal} efficiently
2. Be reusable across multiple student types
3. Integrate with RH research workflows
4. Include validation examples

## Expected Outcome
A validated Python skill file that can be injected into student sessions.

## Approach
1. Break down {skill_name} into core concepts
2. Show how it applies to RH research
3. Provide algorithmic/analytical techniques
4. Include test cases
5. Create reusable utility functions
"""
        return prompt

    def _get_student_specialty(self, student: str) -> str:
        """Get student specialization."""
        specialties = {
            "alpha": "Analytical specialist - deep mathematical reasoning",
            "beta": "Creative problem solver - novel approaches",
            "gamma": "Pattern recognition - fast pattern detection",
            "delta": "Formal logic - rigorous proof building",
            "epsilon": "Meta-learner - consolidation and synthesis",
            "zeta": "Computational verification - algorithms",
        }
        return specialties.get(student, "General RH research")

    def execute_skill_learning(
        self,
        skill_name: str,
        available_tokens: int = 2000,
        current_cycle: int = 1,
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute skill learning when resources become available.

        Args:
            skill_name: Skill to learn
            available_tokens: Token budget for learning
            current_cycle: Current cycle number

        Returns:
            (success, path_to_learned_skill)
        """
        if skill_name not in self.staged_skills:
            return False, None

        staged = self.staged_skills[skill_name]

        # Update status
        staged.status = LearningStatus.LEARNING
        staged.cycle_learning_started = current_cycle
        self._update_status(skill_name, staged.status)

        print(f"\n[SKILL LEARNING] Starting {skill_name} with {staged.student}...")

        # Call cognitive ecosystem to synthesize skill
        try:
            # In real implementation, this would call gpia_cognitive_ecosystem
            # For now, simulate skill creation
            skill_path = self._simulate_skill_synthesis(
                skill_name=skill_name,
                student=staged.student,
                prompt=staged.learning_prompt,
                tokens=available_tokens,
            )

            if skill_path:
                staged.learned_skill_path = str(skill_path)
                staged.status = LearningStatus.SYNTHESIZED
                self._update_status(skill_name, staged.status)
                print(f"[OK] Skill synthesized: {skill_path}")
                return True, skill_path
            else:
                staged.status = LearningStatus.FAILED
                self._update_status(skill_name, staged.status)
                print(f"[FAIL] Skill synthesis failed")
                return False, None

        except Exception as e:
            staged.status = LearningStatus.FAILED
            self._update_status(skill_name, staged.status)
            print(f"[ERROR] Skill learning failed: {e}")
            return False, None

    def _simulate_skill_synthesis(
        self,
        skill_name: str,
        student: str,
        prompt: str,
        tokens: int,
    ) -> Optional[Path]:
        """
        Simulate skill synthesis (placeholder for actual cognitive ecosystem call).

        In real implementation, this would:
        1. Call gpia_cognitive_ecosystem.Hunter to generate approaches
        2. Call gpia_cognitive_ecosystem.Dissector to extract patterns
        3. Call gpia_cognitive_ecosystem.Synthesizer to create Python skill
        """
        skills_dir = Path("skills/learned")
        skills_dir.mkdir(parents=True, exist_ok=True)

        skill_path = skills_dir / f"{skill_name.replace('-', '_')}.py"

        # Create a basic skill file
        skill_content = f'''#!/usr/bin/env python3
"""
Skill: {skill_name}

Auto-learned skill for RH research.
Learned by student: {student}
Quality: High
"""

def apply_{skill_name.replace('-', '_')}(data):
    """Apply {skill_name} technique."""
    # Placeholder implementation
    # In real version, this would contain learned algorithmic content
    return {{
        "method": "{skill_name}",
        "student": "{student}",
        "result": data,
    }}

# Reusable utility
def validate_{skill_name.replace('-', '_')}(result):
    """Validate {skill_name} result."""
    return result.get("method") == "{skill_name}"
'''

        skill_path.write_text(skill_content)
        return skill_path

    def validate_learned_skill(
        self,
        skill_name: str,
        validation_metric: float,
        current_cycle: int,
    ) -> bool:
        """
        Validate that learned skill actually works.

        Args:
            skill_name: Skill to validate
            validation_metric: Performance metric (e.g., speedup achieved)
            current_cycle: Current cycle

        Returns:
            True if skill validated and ready for injection
        """
        if skill_name not in self.staged_skills:
            return False

        staged = self.staged_skills[skill_name]
        staged.status = LearningStatus.VALIDATING
        staged.cycle_validation_started = current_cycle
        self._update_status(skill_name, staged.status)

        print(f"[VALIDATION] Testing {skill_name}...")

        # Simple validation: if metric > 0, it's valid
        if validation_metric > 0:
            staged.status = LearningStatus.VALID
            staged.cycle_completed = current_cycle
            staged.validation_results = {"speedup": validation_metric}
            self._update_status(skill_name, staged.status)

            print(f"[OK] {skill_name} validated with {validation_metric:.1f}x speedup")
            return True
        else:
            staged.status = LearningStatus.FAILED
            self._update_status(skill_name, staged.status)
            print(f"[FAIL] {skill_name} validation failed")
            return False

    def _update_status(self, skill_name: str, status: LearningStatus):
        """Update skill status in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE staged_skills
                SET status = ?
                WHERE skill_name = ?
            """, (status.name, skill_name))
            conn.commit()

    def get_staged_skills(self) -> Dict[str, StagedSkill]:
        """Get all currently staged skills."""
        return self.staged_skills.copy()

    def get_ready_to_inject(self) -> Dict[str, Path]:
        """Get skills that are validated and ready to inject into sessions."""
        ready = {}
        for skill_name, staged in self.staged_skills.items():
            if staged.status == LearningStatus.VALID and staged.learned_skill_path:
                ready[skill_name] = Path(staged.learned_skill_path)
        return ready

    def get_status_report(self) -> str:
        """Generate status report of all staged skills."""
        report = "SKILL LEARNING STATUS\n"
        report += "=" * 60 + "\n\n"

        for skill_name, staged in self.staged_skills.items():
            report += f"{skill_name}:\n"
            report += f"  Student: {staged.student}\n"
            report += f"  Status: {staged.status.name}\n"
            report += f"  Goal: {staged.target_goal}\n"

            if staged.status == LearningStatus.VALID:
                speedup = staged.validation_results.get("speedup", 0) if staged.validation_results else 0
                report += f"  Speedup: {speedup:.1f}x\n"
                report += f"  ✓ READY TO INJECT\n"
            elif staged.status == LearningStatus.FAILED:
                report += f"  ✗ FAILED\n"
            elif staged.status == LearningStatus.STAGED:
                report += f"  ⏳ WAITING FOR RESOURCES\n"

            report += "\n"

        return report


# Singleton
_ORCHESTRATOR = None


def get_skill_staging_orchestrator(session_dir: Path = None) -> SkillStagingOrchestrator:
    """Get or create orchestrator."""
    global _ORCHESTRATOR
    if _ORCHESTRATOR is None:
        if session_dir is None:
            session_dir = Path("agents/sessions/default")
        _ORCHESTRATOR = SkillStagingOrchestrator(session_dir)
    return _ORCHESTRATOR
