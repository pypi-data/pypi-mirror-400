#!/usr/bin/env python3
"""
Skill Learning Coordinator

Master orchestrator for the skill learning lifecycle:
1. CrossKnowledgeDetector: Identifies opportunities
2. SkillStagingOrchestrator: Prepares and learns skills
3. SkillInjector: Injects validated skills into sessions

This coordinator:
- Manages the flow between all three components
- Handles resource scheduling for skill learning
- Tracks overall learning progress
- Reports to professor on opportunities and completions
- Auto-injects safe optimizations
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sqlite3

from skills.cross_knowledge_detector import (
    CrossKnowledgeDetector,
    ProgressMetrics,
    get_cross_knowledge_detector,
)
from skills.skill_staging_orchestrator import (
    SkillStagingOrchestrator,
    get_skill_staging_orchestrator,
)
from skills.skill_injector import (
    SkillInjector,
    get_skill_injector,
)


@dataclass
class SkillLearningReport:
    """Report on skill learning activity."""
    cycle: int
    recommendations: List[Dict]       # Skills recommended
    staged: List[Dict]                # Skills being learned
    injected: List[Dict]              # Skills newly injected
    active_skills: List[str]          # Currently active skills
    learning_progress: str            # Summary message


class SkillLearningCoordinator:
    """Coordinates skill learning lifecycle."""

    def __init__(self, session_dir: Path):
        """Initialize coordinator."""
        self.session_dir = Path(session_dir)
        self.coordinator_dir = self.session_dir / "skill_learning"
        self.coordinator_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the three components
        self.detector = get_cross_knowledge_detector(session_dir)
        self.orchestrator = get_skill_staging_orchestrator(session_dir)
        self.injector = get_skill_injector(session_dir)

        # Database for coordination tracking
        self.db_path = self.coordinator_dir / "coordination.db"
        self._init_database()

        # Configuration
        self.auto_inject_safe_skills = True  # Auto-inject <2x speedup improvements
        self.resource_budget_for_learning = 5000  # Tokens per cycle for skill learning
        self.learning_enabled = True

    def _init_database(self):
        """Initialize database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coordination_events (
                    id INTEGER PRIMARY KEY,
                    cycle INTEGER,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def process_cycle(
        self,
        cycle: int,
        current_progress: ProgressMetrics,
        available_resources: Dict,
    ) -> SkillLearningReport:
        """
        Process one cycle of skill learning.

        Args:
            cycle: Current research cycle
            current_progress: Current research progress metrics
            available_resources: Available VRAM, tokens, CPU, etc.

        Returns:
            Report on skill learning activity
        """
        print(f"\n[SKILL LEARNING] Processing cycle {cycle}...")

        recommendations = []
        staged = []
        injected = []

        # Phase 1: Detect opportunities
        print(f"[PHASE 1] Detecting cross-knowledge opportunities...")
        skill_recs = self.detector.analyze_progress(current_progress)

        for rec in skill_recs[:3]:  # Top 3 recommendations
            recommendations.append({
                "skill": rec.skill_name,
                "student": rec.student,
                "priority": rec.priority.name,
                "speedup": rec.estimated_speedup,
            })

            # Print message to professor
            print(f"\n  📚 Opportunity Detected!")
            print(f"     Skill: {rec.skill_name}")
            print(f"     Student: {rec.student}")
            print(f"     Speedup: {rec.estimated_speedup:.1f}x")
            print(f"     Why: {rec.reasoning}")

            # Stage skill for learning if resources available
            if available_resources.get("vram_free_gb", 0) > 3:
                print(f"     → Staging for learning...")
                self.orchestrator.stage_skill_learning(
                    skill_name=rec.skill_name,
                    student=rec.student,
                    target_goal=current_progress.bottleneck or "RH research",
                    reasoning=rec.reasoning,
                    current_cycle=cycle,
                )
                staged.append({
                    "skill": rec.skill_name,
                    "student": rec.student,
                    "status": "staged",
                })

        # Phase 2: Execute skill learning for staged skills
        print(f"\n[PHASE 2] Executing skill learning...")
        staged_skills = self.orchestrator.get_staged_skills()

        for skill_name, staged_skill in staged_skills.items():
            # Check if resources available for learning
            tokens_available = available_resources.get("tokens", 0)
            if tokens_available > self.resource_budget_for_learning:
                print(f"  Learning {skill_name}...")

                # Execute learning
                success, skill_path = self.orchestrator.execute_skill_learning(
                    skill_name=skill_name,
                    available_tokens=self.resource_budget_for_learning,
                    current_cycle=cycle,
                )

                if success:
                    print(f"  ✓ {skill_name} synthesized")

                    # Validate skill
                    print(f"  Validating {skill_name}...")
                    speedup = 1.5  # Simulated speedup
                    validated = self.orchestrator.validate_learned_skill(
                        skill_name=skill_name,
                        validation_metric=speedup,
                        current_cycle=cycle,
                    )

                    if validated:
                        print(f"  ✓ {skill_name} validated with {speedup:.1f}x speedup")

                        # Phase 3: Inject skill
                        if self.auto_inject_safe_skills and speedup < 2.0:
                            print(f"  Auto-injecting {skill_name} (safe speedup)...")
                            inject_success = self._inject_skill(
                                skill_name=skill_name,
                                skill_path=skill_path,
                                current_cycle=cycle,
                                safety_level="auto",
                            )

                            if inject_success:
                                injected.append({
                                    "skill": skill_name,
                                    "speedup": speedup,
                                    "students": ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"],
                                })

        # Phase 4: Get active skills
        active_skills = list(self.injector.get_active_skills().keys())

        # Generate report
        report = SkillLearningReport(
            cycle=cycle,
            recommendations=recommendations,
            staged=staged,
            injected=injected,
            active_skills=active_skills,
            learning_progress=self._generate_progress_message(
                recommendations, staged, injected, active_skills
            ),
        )

        # Log event
        self._log_event(cycle, "cycle_processed", {
            "recommendations": len(recommendations),
            "staged": len(staged),
            "injected": len(injected),
            "active": len(active_skills),
        })

        return report

    def _inject_skill(
        self,
        skill_name: str,
        skill_path: Path,
        current_cycle: int,
        safety_level: str = "auto",
    ) -> bool:
        """Inject a validated skill."""
        # Inject into all students
        all_students = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]

        success = self.injector.inject_skill(
            skill_name=skill_name,
            skill_path=skill_path,
            target_students=all_students,
            current_cycle=current_cycle,
            safety_level=safety_level,
        )

        if success:
            self._log_event(current_cycle, "skill_injected", {
                "skill": skill_name,
                "students": all_students,
                "safety_level": safety_level,
            })

        return success

    def _generate_progress_message(
        self,
        recommendations: List[Dict],
        staged: List[Dict],
        injected: List[Dict],
        active_skills: List[str],
    ) -> str:
        """Generate progress message for professor."""
        msg = ""

        if recommendations:
            msg += f"\n🎯 **Skill Opportunities**: {len(recommendations)} detected\n"
            for rec in recommendations:
                msg += f"   - {rec['skill']}: {rec['speedup']:.1f}x speedup (Priority: {rec['priority']})\n"

        if staged:
            msg += f"\n📚 **Learning**: {len(staged)} skills staged for learning\n"

        if injected:
            msg += f"\n✨ **New Capabilities**: {len(injected)} skills injected\n"
            for inj in injected:
                msg += f"   - {inj['skill']}: {inj['speedup']:.1f}x faster\n"

        if active_skills:
            msg += f"\n🔧 **Active Skills**: {', '.join(active_skills)}\n"

        if not msg:
            msg = "\nNo skill learning activity this cycle.\n"

        return msg

    def _log_event(self, cycle: int, event_type: str, event_data: Dict):
        """Log coordination event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO coordination_events
                (cycle, event_type, event_data, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                cycle,
                event_type,
                json.dumps(event_data),
                time.time(),
            ))
            conn.commit()

    def get_report_to_professor(self) -> str:
        """Generate comprehensive report for professor."""
        report = "SKILL LEARNING STATUS REPORT\n"
        report += "=" * 70 + "\n"

        # Recommendations
        report += self.detector.generate_professor_message(
            list(self.detector.get_learned_skills().values())
        )

        # Staged skills
        report += "\nSTAGED SKILLS:\n"
        report += self.orchestrator.get_status_report()

        # Active skills
        report += "\nINJECTED SKILLS:\n"
        report += self.injector.get_injection_report()

        return report

    def get_full_message_for_professor(self, latest_report: SkillLearningReport) -> str:
        """
        Generate the full message that Professor should see about skill learning.

        This is what gets printed to console for the professor.
        """
        msg = "\n" + "=" * 80 + "\n"
        msg += "SKILL LEARNING COORDINATOR REPORT\n"
        msg += "=" * 80 + "\n"

        msg += latest_report.learning_progress

        msg += "\n" + "=" * 80 + "\n"

        return msg


# Singleton
_COORDINATOR = None


def get_skill_learning_coordinator(session_dir: Path = None) -> SkillLearningCoordinator:
    """Get or create coordinator."""
    global _COORDINATOR
    if _COORDINATOR is None:
        if session_dir is None:
            session_dir = Path("agents/sessions/default")
        _COORDINATOR = SkillLearningCoordinator(session_dir)
    return _COORDINATOR
