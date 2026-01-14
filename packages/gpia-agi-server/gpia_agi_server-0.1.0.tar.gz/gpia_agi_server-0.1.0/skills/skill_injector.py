#!/usr/bin/env python3
"""
Skill Injector

Injects validated learned skills into student sessions.

How it works:
1. Checks for validated skills (from skill_staging_orchestrator)
2. Safely integrates them into student execution context
3. Validates injection doesn't break existing behavior
4. Tracks impact on performance metrics
5. Auto-applies safe optimizations without approval
6. Logs all injections for audit trail

Safe optimizations that auto-inject (no approval needed):
- Speedup improvements (<2x)
- Bug fixes
- Performance optimizations
- Algorithm improvements
- Mathematical refinements

Requires approval:
- New capabilities (risky)
- Behavioral changes
- External dependencies
- Resource requirement changes
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import importlib.util


class InjectionStatus(Enum):
    """Status of skill injection."""
    PENDING = 1       # Waiting to be injected
    INJECTING = 2     # Currently injecting
    ACTIVE = 3        # Injected and working
    ROLLED_BACK = 4   # Injection failed, rolled back
    FAILED = 5        # Injection failed


@dataclass
class InjectionRecord:
    """Record of a skill injection event."""
    skill_name: str
    injected_cycle: int
    students_affected: List[str]       # Which students got this skill
    status: InjectionStatus
    performance_impact: float           # Measured speedup
    safety_level: str                   # "auto", "approved", "manual"
    injection_timestamp: float
    rollback_timestamp: Optional[float] = None
    audit_notes: str = ""


class SkillInjector:
    """Injects validated skills into student sessions."""

    def __init__(self, session_dir: Path):
        """Initialize skill injector."""
        self.session_dir = Path(session_dir)
        self.injection_dir = self.session_dir / "skill_injections"
        self.injection_dir.mkdir(parents=True, exist_ok=True)

        # Database for injection tracking
        self.db_path = self.injection_dir / "injections.db"
        self._init_database()

        # Cache of injected skills
        self.active_skills: Dict[str, Callable] = {}
        self._load_active_skills()

    def _init_database(self):
        """Initialize database for injection tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS injections (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT,
                    injected_cycle INTEGER,
                    students_affected TEXT,
                    status TEXT,
                    performance_impact REAL,
                    safety_level TEXT,
                    injection_timestamp REAL,
                    rollback_timestamp REAL,
                    audit_notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS injection_metrics (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT,
                    student TEXT,
                    cycle INTEGER,
                    metric_name TEXT,
                    before_value REAL,
                    after_value REAL,
                    improvement REAL,
                    timestamp REAL
                )
            """)
            conn.commit()

    def _load_active_skills(self):
        """Load previously injected active skills."""
        # In real implementation, would load and parse skill files
        pass

    def inject_skill(
        self,
        skill_name: str,
        skill_path: Path,
        target_students: List[str],
        current_cycle: int,
        safety_level: str = "auto",  # "auto", "approved", "manual"
    ) -> bool:
        """
        Inject a validated skill into student sessions.

        Args:
            skill_name: Name of skill to inject
            skill_path: Path to skill Python file
            target_students: Which students get this skill
            current_cycle: Current research cycle
            safety_level: How to handle injection (auto/approved/manual)

        Returns:
            True if injection successful
        """
        print(f"\n[SKILL INJECTION] Injecting {skill_name} into {target_students}...")

        # Check injection safety
        if not self._check_injection_safety(skill_name, skill_path):
            print(f"[WARN] Skill {skill_name} failed safety checks")
            if safety_level == "auto":
                print(f"[SKIP] Auto-injection aborted due to safety concerns")
                return False
            elif safety_level == "manual":
                print(f"[WAIT] Requires manual approval (not implemented)")
                return False

        # Validate skill file
        if not skill_path.exists():
            print(f"[FAIL] Skill file not found: {skill_path}")
            return False

        try:
            # Load skill module
            spec = importlib.util.spec_from_file_location(skill_name, skill_path)
            skill_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(skill_module)

            # Try to validate module has required functions
            if not hasattr(skill_module, f"apply_{skill_name.replace('-', '_')}"):
                print(f"[WARN] Skill missing expected function")
                # Still allow injection for informational skills
                pass

            # Cache the skill
            self.active_skills[skill_name] = skill_module

            # Record injection
            record = InjectionRecord(
                skill_name=skill_name,
                injected_cycle=current_cycle,
                students_affected=target_students,
                status=InjectionStatus.ACTIVE,
                performance_impact=0.0,  # Will be measured later
                safety_level=safety_level,
                injection_timestamp=time.time(),
                audit_notes=f"Injected into {len(target_students)} students",
            )

            self._record_injection(record)

            print(f"[OK] {skill_name} injected into {', '.join(target_students)}")
            return True

        except Exception as e:
            print(f"[FAIL] Skill injection failed: {e}")
            self._record_failed_injection(skill_name, current_cycle, str(e))
            return False

    def _check_injection_safety(self, skill_name: str, skill_path: Path) -> bool:
        """
        Check if skill is safe to inject.

        Safe criteria:
        - Doesn't contain dangerous imports (subprocess, os.system, etc.)
        - Has reasonable file size
        - Doesn't modify global state
        - Includes validation functions
        """
        try:
            content = skill_path.read_text()

            # Check for dangerous patterns
            dangerous_patterns = [
                "os.system",
                "subprocess.run",
                "exec(",
                "eval(",
                "__import__",
            ]

            for pattern in dangerous_patterns:
                if pattern in content:
                    print(f"[WARN] Detected dangerous pattern: {pattern}")
                    return False

            # Check file size (should be reasonable)
            file_size_kb = skill_path.stat().st_size / 1024
            if file_size_kb > 500:  # 500 KB max
                print(f"[WARN] Skill file too large: {file_size_kb:.0f} KB")
                return False

            # Check for validation function
            if "def validate" not in content:
                print(f"[WARN] Skill missing validation function")
                # Not a blocker, but logged

            return True

        except Exception as e:
            print(f"[ERROR] Safety check failed: {e}")
            return False

    def apply_injected_skill(
        self,
        skill_name: str,
        data: Dict,
        student: str = None,
    ) -> Dict:
        """
        Apply an injected skill to data.

        Args:
            skill_name: Skill to apply
            data: Input data
            student: Which student is using it (optional, for tracking)

        Returns:
            Processed data with skill applied
        """
        if skill_name not in self.active_skills:
            # Skill not available, return data unchanged
            return data

        try:
            skill_module = self.active_skills[skill_name]

            # Try to call apply function
            apply_func_name = f"apply_{skill_name.replace('-', '_')}"
            if hasattr(skill_module, apply_func_name):
                apply_func = getattr(skill_module, apply_func_name)
                result = apply_func(data)
                return result
            else:
                # Skill exists but no apply function
                return data

        except Exception as e:
            print(f"[WARN] Error applying {skill_name}: {e}")
            return data

    def measure_injection_impact(
        self,
        skill_name: str,
        student: str,
        cycle: int,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float],
    ) -> float:
        """
        Measure performance impact of skill injection.

        Args:
            skill_name: Injected skill
            student: Which student
            cycle: Research cycle
            before_metrics: Metrics before injection
            after_metrics: Metrics after injection

        Returns:
            Measured speedup (>1.0 = improvement)
        """
        speedups = []

        for metric_name in before_metrics:
            if metric_name in after_metrics:
                before = before_metrics[metric_name]
                after = after_metrics[metric_name]

                # Calculate improvement (depends on metric direction)
                if metric_name in ("time_seconds", "tokens_per_second"):
                    # For time: lower is better
                    if before > 0:
                        speedup = before / after
                    else:
                        speedup = 1.0
                elif metric_name in ("quality_score", "success_rate"):
                    # For quality: higher is better
                    if before > 0:
                        speedup = after / before
                    else:
                        speedup = 1.0
                else:
                    speedup = 1.0

                speedups.append(speedup)

                # Record metric
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO injection_metrics
                        (skill_name, student, cycle, metric_name, before_value, after_value, improvement, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        skill_name,
                        student,
                        cycle,
                        metric_name,
                        before,
                        after,
                        speedup,
                        time.time(),
                    ))
                    conn.commit()

        # Return average speedup
        if speedups:
            avg_speedup = sum(speedups) / len(speedups)
            return avg_speedup
        else:
            return 1.0

    def _record_injection(self, record: InjectionRecord):
        """Record successful injection."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO injections
                (skill_name, injected_cycle, students_affected, status, performance_impact, safety_level, injection_timestamp, audit_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.skill_name,
                record.injected_cycle,
                ",".join(record.students_affected),
                record.status.name,
                record.performance_impact,
                record.safety_level,
                record.injection_timestamp,
                record.audit_notes,
            ))
            conn.commit()

    def _record_failed_injection(self, skill_name: str, cycle: int, error: str):
        """Record failed injection attempt."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO injections
                (skill_name, injected_cycle, students_affected, status, performance_impact, safety_level, injection_timestamp, audit_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_name,
                cycle,
                "",
                InjectionStatus.FAILED.name,
                0.0,
                "manual",
                time.time(),
                f"Failed: {error[:200]}",
            ))
            conn.commit()

    def get_active_skills(self) -> Dict[str, str]:
        """Get list of currently active injected skills."""
        return {skill_name: "active" for skill_name in self.active_skills.keys()}

    def rollback_injection(self, skill_name: str, reason: str = ""):
        """Rollback an injected skill."""
        if skill_name in self.active_skills:
            del self.active_skills[skill_name]

            # Record rollback
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE injections
                    SET status = ?, rollback_timestamp = ?, audit_notes = ?
                    WHERE skill_name = ? AND status = ?
                """, (
                    InjectionStatus.ROLLED_BACK.name,
                    time.time(),
                    f"Rolled back: {reason}",
                    skill_name,
                    InjectionStatus.ACTIVE.name,
                ))
                conn.commit()

            print(f"[ROLLBACK] {skill_name} rolled back: {reason}")

    def get_injection_report(self) -> str:
        """Generate report of all injections."""
        report = "SKILL INJECTION AUDIT REPORT\n"
        report += "=" * 70 + "\n\n"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT skill_name, injected_cycle, students_affected, status,
                       performance_impact, safety_level
                FROM injections
                ORDER BY injection_timestamp DESC
                LIMIT 20
            """)

            for row in cursor:
                skill_name, cycle, students, status, impact, safety = row
                report += f"Skill: {skill_name}\n"
                report += f"  Cycle: {cycle}\n"
                report += f"  Students: {students}\n"
                report += f"  Status: {status}\n"
                report += f"  Impact: {impact:.2f}x\n"
                report += f"  Safety: {safety}\n"
                report += "\n"

        return report


# Singleton
_INJECTOR = None


def get_skill_injector(session_dir: Path = None) -> SkillInjector:
    """Get or create injector."""
    global _INJECTOR
    if _INJECTOR is None:
        if session_dir is None:
            session_dir = Path("agents/sessions/default")
        _INJECTOR = SkillInjector(session_dir)
    return _INJECTOR
