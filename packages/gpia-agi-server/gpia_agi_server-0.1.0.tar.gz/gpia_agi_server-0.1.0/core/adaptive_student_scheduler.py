"""
Adaptive Student Scheduler - Dynamic resource-aware orchestration.

Tracks actual resource consumption per student and adapts the next student
selection based on real hardware state.

Architecture:
1. Start with highest-priority student
2. Track resource consumption (VRAM, time, tokens)
3. After completion, measure actual hardware state
4. Select next student that:
   - Fits within remaining VRAM safely
   - Has highest priority among available options
   - Matches current resource availability patterns
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3


class StudentPriority(Enum):
    """Student priority levels."""
    CRITICAL = 1     # Must run
    HIGH = 2         # Important
    MEDIUM = 3       # Standard
    LOW = 4          # Optional


@dataclass
class StudentResourceProfile:
    """Measured resource consumption for a student."""
    student_name: str
    model_name: str
    vram_used_mb: float
    time_seconds: float
    tokens_generated: int
    tokens_per_second: float
    success: bool
    timestamp: float


@dataclass
class HardwareSnapshot:
    """Hardware state measurement."""
    vram_used_mb: float
    vram_total_mb: float
    vram_free_mb: float
    ram_used_mb: float
    ram_total_mb: float
    ram_free_mb: float
    cpu_percent: float
    timestamp: float

    @property
    def vram_util_percent(self) -> float:
        """VRAM utilization percentage."""
        if self.vram_total_mb == 0:
            return 0
        return (self.vram_used_mb / self.vram_total_mb) * 100

    @property
    def can_fit_4gb_model(self) -> bool:
        """Can a 4GB model fit safely (with 1GB reserve)?"""
        return self.vram_free_mb >= 5120  # 4GB + 1GB reserve


class AdaptiveStudentScheduler:
    """Dynamically schedules students based on resource availability."""

    STUDENTS = {
        "alpha": {"priority": StudentPriority.HIGH, "expected_vram_mb": 3800, "expected_time_s": 30},
        "beta": {"priority": StudentPriority.HIGH, "expected_vram_mb": 4400, "expected_time_s": 35},
        "gamma": {"priority": StudentPriority.MEDIUM, "expected_vram_mb": 4400, "expected_time_s": 25},
        "delta": {"priority": StudentPriority.HIGH, "expected_vram_mb": 3800, "expected_time_s": 30},
        "epsilon": {"priority": StudentPriority.MEDIUM, "expected_vram_mb": 4100, "expected_time_s": 35},
        "zeta": {"priority": StudentPriority.HIGH, "expected_vram_mb": 5000, "expected_time_s": 40},
    }

    def __init__(self, session_dir: Path):
        """Initialize scheduler with session directory."""
        self.session_dir = Path(session_dir)
        self.history_dir = self.session_dir / "scheduler_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # SQLite database for tracking
        self.db_path = self.history_dir / "student_profiles.db"
        self._init_database()

        # Current cycle tracking
        self.current_cycle = 0
        self.completed_students = set()
        self.student_order = []

    def _init_database(self):
        """Initialize SQLite database for resource tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_runs (
                    id INTEGER PRIMARY KEY,
                    cycle INTEGER,
                    student TEXT,
                    vram_mb REAL,
                    time_seconds REAL,
                    tokens INTEGER,
                    tokens_per_sec REAL,
                    success INTEGER,
                    timestamp REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hardware_snapshots (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    vram_used REAL,
                    vram_total REAL,
                    ram_used REAL,
                    ram_total REAL,
                    cpu_percent REAL
                )
            """)
            conn.commit()

    def record_completion(
        self,
        student: str,
        vram_used_mb: float,
        time_seconds: float,
        tokens_generated: int,
    ):
        """Record student completion metrics."""
        # Generate model name from student (e.g., "alpha" -> "rh-alpha:latest")
        model_name = f"rh-{student}:latest"

        profile = StudentResourceProfile(
            student_name=student,
            model_name=model_name,
            vram_used_mb=vram_used_mb,
            time_seconds=time_seconds,
            tokens_generated=tokens_generated,
            tokens_per_second=tokens_generated / max(time_seconds, 1),
            success=True,
            timestamp=time.time(),
        )

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO student_runs
                (cycle, student, vram_mb, time_seconds, tokens, tokens_per_sec, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_cycle,
                student,
                vram_used_mb,
                time_seconds,
                tokens_generated,
                profile.tokens_per_second,
                1,
                time.time()
            ))
            conn.commit()

        # Save JSON backup
        profile_file = self.history_dir / f"cycle_{self.current_cycle}_{student}.json"
        profile_file.write_text(json.dumps(asdict(profile), indent=2))

        self.completed_students.add(student)

    def record_hardware_snapshot(self, snapshot: HardwareSnapshot):
        """Record hardware state."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO hardware_snapshots
                (timestamp, vram_used, vram_total, ram_used, ram_total, cpu_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot.timestamp,
                snapshot.vram_used_mb,
                snapshot.vram_total_mb,
                snapshot.ram_used_mb,
                snapshot.ram_total_mb,
                snapshot.cpu_percent,
            ))
            conn.commit()

    def get_next_student(self, hardware: HardwareSnapshot) -> Optional[str]:
        """
        Determine next student to run based on:
        1. Available VRAM
        2. Priority
        3. Previous consumption patterns
        """
        # Get students not yet run this cycle
        remaining = [s for s in self.STUDENTS.keys() if s not in self.completed_students]
        if not remaining:
            return None

        # Filter by hardware constraints
        candidates = [
            s for s in remaining
            if self._can_fit_student(s, hardware)
        ]

        if not candidates:
            # No student fits - return None
            return None

        # Sort by priority (lower number = higher priority)
        candidates.sort(
            key=lambda s: self.STUDENTS[s]["priority"].value
        )

        return candidates[0]

    def _can_fit_student(self, student: str, hardware: HardwareSnapshot) -> bool:
        """Check if student model fits in available VRAM."""
        expected_vram_mb = self.STUDENTS[student]["expected_vram_mb"]
        vram_needed_mb = expected_vram_mb + 1024  # 1GB safety margin

        # Check if enough free VRAM
        return hardware.vram_free_mb >= vram_needed_mb

    def get_average_consumption(self, student: str) -> Dict:
        """Get average resource consumption for student."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT AVG(vram_mb), AVG(time_seconds), AVG(tokens), AVG(tokens_per_sec)
                FROM student_runs
                WHERE student = ? AND success = 1
            """, (student,))
            row = cursor.fetchone()

        if not row or row[0] is None:
            return {
                "vram_mb": self.STUDENTS[student]["expected_vram_mb"],
                "time_seconds": self.STUDENTS[student]["expected_time_s"],
                "tokens": 3000,
                "tokens_per_sec": 85,
            }

        return {
            "vram_mb": row[0],
            "time_seconds": row[1],
            "tokens": int(row[2]),
            "tokens_per_sec": row[3],
        }

    def estimate_remaining_cycle_time(self, remaining_students: List[str]) -> float:
        """Estimate time to complete remaining students."""
        total_time = 0
        for student in remaining_students:
            avg = self.get_average_consumption(student)
            total_time += avg["time_seconds"]

        # Add validation overhead (30s per 6 students)
        total_time += 30 * (len(remaining_students) / 6)

        return total_time

    def start_cycle(self, cycle: int):
        """Initialize new cycle."""
        self.current_cycle = cycle
        self.completed_students = set()

    def get_cycle_summary(self) -> Dict:
        """Get summary of current cycle."""
        total_vram_used = 0
        total_time = 0
        total_tokens = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(vram_mb), SUM(time_seconds), SUM(tokens)
                FROM student_runs
                WHERE cycle = ? AND success = 1
            """, (self.current_cycle,))
            row = cursor.fetchone()

        if row and row[0]:
            total_vram_used = row[0]
            total_time = row[1]
            total_tokens = row[2]

        return {
            "cycle": self.current_cycle,
            "students_completed": len(self.completed_students),
            "total_vram_used_mb": total_vram_used,
            "total_time_seconds": total_time,
            "total_tokens": int(total_tokens) if total_tokens else 0,
            "completed_students": sorted(self.completed_students),
        }


# Singleton
_SCHEDULER = None


def get_adaptive_scheduler(session_dir: Path = None) -> AdaptiveStudentScheduler:
    """Get or create scheduler."""
    global _SCHEDULER
    if _SCHEDULER is None:
        if session_dir is None:
            session_dir = Path("/app/agents/sessions/default")
        _SCHEDULER = AdaptiveStudentScheduler(session_dir)
    return _SCHEDULER
