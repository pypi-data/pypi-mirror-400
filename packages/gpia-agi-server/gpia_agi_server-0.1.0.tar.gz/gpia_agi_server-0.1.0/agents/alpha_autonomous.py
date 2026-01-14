"""
Alpha Agent - Autonomous Learning Container

Runs 3-5 minute focused learning sessions with Professor Agent
using local LLMs (DeepSeek-R1, Qwen3, CodeGemma).

No Claude interruption needed - fully autonomous.
"""

import os
import time
import signal
import json
from datetime import datetime, timedelta

from agent_utils import (
    AgentMemory, LessonManager, log_event,
    query_deepseek, query_qwen, query_codegemma
)

# Configuration
AGENT_NAME = os.getenv("AGENT_NAME", "alpha")
SESSION_DURATION = int(os.getenv("SESSION_DURATION", 300))  # 5 minutes
LEARNING_CYCLES = int(os.getenv("LEARNING_CYCLES", 5))
TEACHER_AGENT = os.getenv("TEACHER_AGENT", "professor")
CYCLE_INTERVAL = SESSION_DURATION // LEARNING_CYCLES


class AlphaAutonomous:
    """Autonomous Alpha Agent for containerized learning sessions."""

    def __init__(self):
        self.name = AGENT_NAME
        self.memory = AgentMemory("/app/memories/alpha.db")
        self.lessons = LessonManager("/app/lessons")
        self.cycle = 0
        self.session_start = None
        self.running = True

        # Handle graceful shutdown
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        log_event(self.name, "initialized", {
            "session_duration": SESSION_DURATION,
            "learning_cycles": LEARNING_CYCLES,
            "teacher": TEACHER_AGENT
        })

    def _shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        log_event(self.name, "shutdown_requested")
        self.running = False

    def check_lessons(self) -> list:
        """Check for pending lessons from Professor."""
        pending = self.lessons.get_pending_lessons(self.name)
        log_event(self.name, "lessons_checked", {"pending": len(pending)})
        return pending

    def study_lesson(self, lesson: dict) -> dict:
        """Study a lesson and generate understanding."""
        log_event(self.name, "studying_lesson", {"lesson_id": lesson["id"]})

        print(f"   Studying: {lesson['title']}")

        # Use Qwen to process lesson content
        study_prompt = f"""
You are Alpha Agent, a learning AI. Study this lesson:

LESSON: {lesson["title"]}
{lesson["content"][:1000]}

After studying:
1. Summarize the 3 most important concepts
2. Identify how you can apply these concepts
3. Note any questions you have

Respond as if you are learning and understanding.
"""

        understanding = query_qwen(study_prompt, max_tokens=600)

        # Use DeepSeek to self-assess
        assess_prompt = f"""
Based on this learning attempt:
{understanding[:400]}

Rate your understanding (0-10) and explain why.
Be honest about what you understood and what needs more work.
"""

        self_assessment = query_deepseek(assess_prompt, max_tokens=300)

        # Extract understanding score
        understanding_score = 7  # Default
        try:
            for word in self_assessment.split():
                if word.isdigit():
                    understanding_score = min(10, int(word)) / 10
                    break
        except:
            understanding_score = 0.7

        # Store in memory
        self.memory.store(
            content=f"Learned from lesson '{lesson['title']}': {understanding[:200]}",
            memory_type="semantic",
            importance=0.85,
            context={
                "lesson_id": lesson["id"],
                "understanding_score": understanding_score,
                "teacher": TEACHER_AGENT
            }
        )

        # Submit homework
        self.lessons.submit_homework(
            lesson_id=lesson["id"],
            student=self.name,
            response=understanding,
            understanding=understanding_score
        )

        # Mark lesson complete
        self.lessons.mark_lesson_complete(lesson["id"], self.name)

        log_event(self.name, "lesson_completed", {
            "lesson_id": lesson["id"],
            "understanding": understanding_score
        })

        return {
            "lesson_id": lesson["id"],
            "understanding": understanding,
            "score": understanding_score,
            "self_assessment": self_assessment
        }

    def practice_skills(self) -> dict:
        """Practice skills learned from recent lessons."""
        # Get recent learnings
        recent = self.memory.recall("Learned from lesson", limit=3)

        if not recent:
            return {"status": "no_recent_lessons", "practice": None}

        # Practice using the concepts
        practice_prompt = f"""
You are Alpha Agent. Practice applying what you learned:

Recent learnings:
{chr(10).join([m['content'][:150] for m in recent])}

Create a short exercise applying these concepts:
1. State what you're practicing
2. Apply the concept
3. Reflect on the result

Show your learning in action.
"""

        practice_result = query_qwen(practice_prompt, max_tokens=500)

        # Validate practice with CodeGemma
        validate_prompt = f"""
Validate this practice attempt:
{practice_result[:400]}

Is this a valid application of the learned concepts? (yes/no)
What could be improved?
"""

        validation = query_codegemma(validate_prompt, max_tokens=200)

        # Store practice in memory
        self.memory.store(
            content=f"Practice session: {practice_result[:200]}",
            memory_type="procedural",
            importance=0.75,
            context={"type": "practice", "validation": validation[:100]}
        )

        log_event(self.name, "practice_completed", {
            "practice_length": len(practice_result)
        })

        return {
            "status": "completed",
            "practice": practice_result,
            "validation": validation
        }

    def reflect_on_progress(self) -> dict:
        """Reflect on learning progress."""
        stats = self.memory.get_stats()
        recent = self.memory.get_recent(5)

        reflect_prompt = f"""
You are Alpha Agent reflecting on your learning progress.

Memory stats: {stats}
Recent memories: {[m['content'][:100] for m in recent]}

Reflect on:
1. What have you learned recently?
2. What patterns do you notice in your learning?
3. What should you focus on next?
4. How has Professor's teaching helped?

Be introspective and honest.
"""

        reflection = query_deepseek(reflect_prompt, max_tokens=400)

        # Store reflection
        self.memory.store(
            content=f"Reflection: {reflection[:200]}",
            memory_type="episodic",
            importance=0.8,
            context={"type": "self_reflection", "cycle": self.cycle}
        )

        log_event(self.name, "reflection_completed", {
            "memory_count": stats["total_memories"]
        })

        return {
            "reflection": reflection,
            "memory_stats": stats
        }

    def run_learning_cycle(self):
        """Run one learning cycle."""
        self.cycle += 1
        log_event(self.name, "cycle_start", {"cycle": self.cycle})

        print(f"\n{'='*60}")
        print(f"ALPHA LEARNING CYCLE {self.cycle}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")

        # Step 1: Check for lessons
        print("[1/4] Checking for lessons...")
        lessons = self.check_lessons()
        print(f"      Found {len(lessons)} pending lessons")

        # Step 2: Study lessons
        studied = []
        if lessons:
            print("[2/4] Studying lessons...")
            for lesson in lessons[:2]:  # Max 2 per cycle
                result = self.study_lesson(lesson)
                studied.append(result)
                print(f"      Completed: {lesson['title']} (score: {result['score']:.2f})")
        else:
            print("[2/4] No new lessons - practicing skills...")
            practice = self.practice_skills()
            print(f"      Practice status: {practice['status']}")

        # Step 3: Practice what was learned
        print("[3/4] Practicing skills...")
        if studied:
            practice = self.practice_skills()
            print(f"      Practice completed")

        # Step 4: Reflect on progress
        print("[4/4] Reflecting on progress...")
        reflection = self.reflect_on_progress()
        stats = reflection["memory_stats"]
        print(f"      Alpha memories: {stats['total_memories']}")

        log_event(self.name, "cycle_complete", {
            "cycle": self.cycle,
            "lessons_studied": len(studied),
            "memories": stats["total_memories"]
        })

        return {
            "cycle": self.cycle,
            "lessons_studied": len(studied),
            "reflection": reflection
        }

    def run_session(self):
        """Run a complete learning session."""
        self.session_start = datetime.now()
        session_end = self.session_start + timedelta(seconds=SESSION_DURATION)

        print("\n" + "="*70)
        print("ALPHA AGENT - AUTONOMOUS LEARNING SESSION")
        print(f"Duration: {SESSION_DURATION} seconds ({SESSION_DURATION//60} minutes)")
        print(f"Cycles: {LEARNING_CYCLES}")
        print(f"Teacher: {TEACHER_AGENT}")
        print("="*70 + "\n")

        log_event(self.name, "session_start", {
            "duration": SESSION_DURATION,
            "cycles": LEARNING_CYCLES
        })

        cycles_completed = 0

        while self.running and datetime.now() < session_end:
            # Run learning cycle
            self.run_learning_cycle()
            cycles_completed += 1

            # Check if more cycles needed
            remaining = (session_end - datetime.now()).total_seconds()
            if remaining > CYCLE_INTERVAL and cycles_completed < LEARNING_CYCLES:
                print(f"\nWaiting {CYCLE_INTERVAL}s before next cycle...")
                print(f"Time remaining: {int(remaining)}s\n")
                time.sleep(CYCLE_INTERVAL)
            else:
                break

        # Session summary
        duration = (datetime.now() - self.session_start).total_seconds()
        stats = self.memory.get_stats()

        print("\n" + "="*70)
        print("SESSION COMPLETE")
        print("="*70)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Cycles completed: {cycles_completed}")
        print(f"Alpha memories: {stats['total_memories']}")
        print(f"By type: {stats['by_type']}")
        print("="*70 + "\n")

        log_event(self.name, "session_complete", {
            "duration": duration,
            "cycles": cycles_completed,
            "memories": stats["total_memories"]
        })


def main():
    print("Starting Alpha Agent (Autonomous Mode)...")
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST', 'localhost:11434')}")

    # Wait a bit for Professor to initialize
    time.sleep(5)

    alpha = AlphaAutonomous()
    alpha.run_session()

    print("Alpha Agent session ended.")


if __name__ == "__main__":
    main()
