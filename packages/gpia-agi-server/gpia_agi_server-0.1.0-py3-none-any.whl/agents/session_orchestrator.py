"""
Learning Session Orchestrator

Coordinates autonomous learning sessions between Professor and Alpha agents.
Monitors progress, manages timing, and generates session reports.
"""

import os
import time
import json
import signal
from datetime import datetime, timedelta
from pathlib import Path

from agent_utils import (
    AgentMemory, log_event,
    query_deepseek, query_qwen
)

# Configuration
SESSION_DURATION = int(os.getenv("SESSION_DURATION", 300))  # 5 minutes
CYCLE_INTERVAL = int(os.getenv("CYCLE_INTERVAL", 30))
REPORT_INTERVAL = 60  # Report every minute


class SessionOrchestrator:
    """Orchestrates learning sessions between agents."""

    def __init__(self):
        self.name = "orchestrator"
        self.professor_memory = AgentMemory("/app/professor-memories/professor.db")
        self.alpha_memory = AgentMemory("/app/alpha-memories/alpha.db")
        self.lessons_dir = Path("/app/lessons")
        self.logs_dir = Path("/app/logs")
        self.session_start = None
        self.running = True

        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        log_event(self.name, "initialized", {
            "session_duration": SESSION_DURATION
        })

    def _shutdown(self, signum, frame):
        log_event(self.name, "shutdown_requested")
        self.running = False

    def get_lesson_stats(self) -> dict:
        """Get lesson statistics."""
        self.lessons_dir.mkdir(parents=True, exist_ok=True)

        total_lessons = 0
        completed = 0
        pending = 0
        homework_submitted = 0
        homework_graded = 0
        total_score = 0
        graded_count = 0

        for file in self.lessons_dir.glob("*.json"):
            if file.name.startswith("hw_"):
                homework_submitted += 1
                hw = json.loads(file.read_text())
                if hw.get("graded"):
                    homework_graded += 1
                    total_score += hw.get("score", 0)
                    graded_count += 1
            else:
                total_lessons += 1
                lesson = json.loads(file.read_text())
                if lesson.get("status") == "completed":
                    completed += 1
                else:
                    pending += 1

        avg_score = total_score / graded_count if graded_count > 0 else 0

        return {
            "total_lessons": total_lessons,
            "completed": completed,
            "pending": pending,
            "homework_submitted": homework_submitted,
            "homework_graded": homework_graded,
            "average_score": avg_score
        }

    def generate_progress_report(self) -> str:
        """Generate a progress report using LLM."""
        prof_stats = self.professor_memory.get_stats()
        alpha_stats = self.alpha_memory.get_stats()
        lesson_stats = self.get_lesson_stats()

        elapsed = (datetime.now() - self.session_start).total_seconds() if self.session_start else 0

        report_data = {
            "elapsed_seconds": elapsed,
            "professor_memories": prof_stats["total_memories"],
            "alpha_memories": alpha_stats["total_memories"],
            "lessons": lesson_stats
        }

        report_prompt = f"""
Generate a brief learning session progress report:

Data:
{json.dumps(report_data, indent=2)}

Include:
1. Session progress (time elapsed vs total)
2. Teaching effectiveness (lessons completed, avg score)
3. Memory growth (both agents)
4. One recommendation

Keep it under 200 words.
"""

        report = query_qwen(report_prompt, max_tokens=300)
        return report

    def monitor_session(self):
        """Monitor the learning session."""
        self.session_start = datetime.now()
        session_end = self.session_start + timedelta(seconds=SESSION_DURATION)
        last_report = self.session_start

        print("\n" + "="*70)
        print("LEARNING SESSION ORCHESTRATOR")
        print(f"Duration: {SESSION_DURATION} seconds")
        print(f"Started: {self.session_start.strftime('%H:%M:%S')}")
        print("="*70 + "\n")

        log_event(self.name, "session_monitoring_started", {
            "duration": SESSION_DURATION
        })

        while self.running and datetime.now() < session_end:
            # Get current stats
            prof_stats = self.professor_memory.get_stats()
            alpha_stats = self.alpha_memory.get_stats()
            lesson_stats = self.get_lesson_stats()

            elapsed = (datetime.now() - self.session_start).total_seconds()
            remaining = SESSION_DURATION - elapsed

            # Print status
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] STATUS UPDATE")
            print(f"  Elapsed: {int(elapsed)}s / {SESSION_DURATION}s ({int(elapsed/SESSION_DURATION*100)}%)")
            print(f"  Professor memories: {prof_stats['total_memories']}")
            print(f"  Alpha memories: {alpha_stats['total_memories']}")
            print(f"  Lessons: {lesson_stats['completed']} completed, {lesson_stats['pending']} pending")
            print(f"  Homework: {lesson_stats['homework_graded']}/{lesson_stats['homework_submitted']} graded")
            if lesson_stats['average_score'] > 0:
                print(f"  Avg score: {lesson_stats['average_score']:.1f}/10")

            # Generate report every minute
            if (datetime.now() - last_report).total_seconds() >= REPORT_INTERVAL:
                print("\n--- PROGRESS REPORT ---")
                report = self.generate_progress_report()
                print(report[:500])
                print("--- END REPORT ---\n")

                # Save report
                report_file = self.logs_dir / f"report_{datetime.now().strftime('%H%M%S')}.txt"
                report_file.parent.mkdir(parents=True, exist_ok=True)
                report_file.write_text(report)

                last_report = datetime.now()

            # Wait before next check
            time.sleep(CYCLE_INTERVAL)

        # Final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate final session report."""
        duration = (datetime.now() - self.session_start).total_seconds()
        prof_stats = self.professor_memory.get_stats()
        alpha_stats = self.alpha_memory.get_stats()
        lesson_stats = self.get_lesson_stats()

        # Get recent memories from both agents
        prof_recent = self.professor_memory.get_recent(5)
        alpha_recent = self.alpha_memory.get_recent(5)

        final_prompt = f"""
Generate a comprehensive final report for this autonomous learning session:

SESSION DATA:
- Duration: {duration:.1f} seconds
- Professor memories: {prof_stats}
- Alpha memories: {alpha_stats}
- Lesson stats: {lesson_stats}

PROFESSOR'S RECENT ACTIVITIES:
{chr(10).join([m['content'][:100] for m in prof_recent])}

ALPHA'S RECENT LEARNINGS:
{chr(10).join([m['content'][:100] for m in alpha_recent])}

Create a report with:
1. Executive Summary
2. Teaching Effectiveness
3. Learning Progress
4. Key Achievements
5. Recommendations for Next Session

Be analytical and constructive.
"""

        final_report = query_deepseek(final_prompt, max_tokens=800)

        print("\n" + "="*70)
        print("FINAL SESSION REPORT")
        print("="*70)
        print(final_report)
        print("="*70 + "\n")

        # Save final report
        report_file = self.logs_dir / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        full_report = f"""
AUTONOMOUS LEARNING SESSION - FINAL REPORT
============================================
Date: {datetime.now().isoformat()}
Duration: {duration:.1f} seconds

STATISTICS:
-----------
Professor Memories: {prof_stats['total_memories']}
Alpha Memories: {alpha_stats['total_memories']}
Lessons Completed: {lesson_stats['completed']}
Average Score: {lesson_stats['average_score']:.1f}/10

LLM ANALYSIS:
-------------
{final_report}

============================================
End of Report
"""

        report_file.write_text(full_report)
        print(f"Report saved: {report_file}")

        log_event(self.name, "session_complete", {
            "duration": duration,
            "professor_memories": prof_stats["total_memories"],
            "alpha_memories": alpha_stats["total_memories"],
            "lessons_completed": lesson_stats["completed"]
        })


def main():
    print("Starting Learning Session Orchestrator...")
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST', 'localhost:11434')}")

    # Wait for agents to initialize
    print("Waiting for agents to initialize...")
    time.sleep(10)

    orchestrator = SessionOrchestrator()
    orchestrator.monitor_session()

    print("Orchestrator session ended.")


if __name__ == "__main__":
    main()
