"""
Professor Agent - Autonomous Teaching Container

Runs 3-5 minute focused learning sessions with Alpha Agent
using local LLMs (DeepSeek-R1, Qwen3, CodeGemma).

No Claude interruption needed - fully autonomous.
"""

import os
import time
import signal
import sys
from datetime import datetime, timedelta

from agent_utils import (
    AgentMemory, LessonManager, log_event,
    query_deepseek, query_qwen, query_codegemma
)

# Configuration
AGENT_NAME = os.getenv("AGENT_NAME", "professor")
SESSION_DURATION = int(os.getenv("SESSION_DURATION", 300))  # 5 minutes
LEARNING_CYCLES = int(os.getenv("LEARNING_CYCLES", 5))
STUDENT_AGENT = os.getenv("STUDENT_AGENT", "alpha")
CYCLE_INTERVAL = SESSION_DURATION // LEARNING_CYCLES

# Teaching topics for autonomous sessions
TEACHING_TOPICS = [
    {
        "title": "Memory Consolidation Techniques",
        "description": "How to effectively store and retrieve memories",
        "skills": ["semantic memory", "episodic recall", "importance scoring"]
    },
    {
        "title": "Multi-Model Reasoning Patterns",
        "description": "Using DeepSeek, Qwen, CodeGemma together effectively",
        "skills": ["analytical reasoning", "creative synthesis", "validation"]
    },
    {
        "title": "OODA Loop Optimization",
        "description": "Improving observe-orient-decide-act-learn cycles",
        "skills": ["observation", "orientation", "decision-making", "learning"]
    },
    {
        "title": "Autonomous Goal Setting",
        "description": "How to set and pursue independent goals",
        "skills": ["goal identification", "planning", "execution", "evaluation"]
    },
    {
        "title": "Error Detection and Recovery",
        "description": "Handling failures and learning from mistakes",
        "skills": ["error detection", "root cause analysis", "recovery strategies"]
    }
]


class ProfessorAutonomous:
    """Autonomous Professor Agent for containerized learning sessions."""

    def __init__(self):
        self.name = AGENT_NAME
        self.memory = AgentMemory("/app/memories/professor.db")
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
            "student": STUDENT_AGENT
        })

    def _shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        log_event(self.name, "shutdown_requested")
        self.running = False

    def select_topic(self) -> dict:
        """Select next teaching topic based on progress."""
        # Check what we've already taught
        recent = self.memory.recall("taught lesson", limit=10)
        taught_titles = [m["content"] for m in recent]

        # Find untaught topic
        for topic in TEACHING_TOPICS:
            if not any(topic["title"] in t for t in taught_titles):
                return topic

        # If all taught, cycle back
        return TEACHING_TOPICS[self.cycle % len(TEACHING_TOPICS)]

    def create_lesson(self, topic: dict) -> dict:
        """Create a lesson using LLMs."""
        log_event(self.name, "creating_lesson", {"topic": topic["title"]})

        # Use DeepSeek for lesson structure
        structure_prompt = f"""
Create a structured lesson plan for teaching an AI agent about:

Topic: {topic["title"]}
Description: {topic["description"]}
Skills to develop: {topic["skills"]}

Include:
1. Learning objectives (3 key points)
2. Core concepts to explain
3. Practical exercise
4. Assessment question

Keep it focused and actionable for a 1-minute teaching session.
"""

        structure = query_deepseek(structure_prompt, max_tokens=800)

        # Use Qwen for creative examples
        examples_prompt = f"""
Based on this lesson structure:
{structure[:500]}

Create 2 practical examples that illustrate the concepts.
Make them relevant to an AI agent learning to be autonomous.
"""

        examples = query_qwen(examples_prompt, max_tokens=600)

        # Combine into lesson
        lesson_content = f"""
# {topic["title"]}

## Objectives
{structure[:300]}

## Examples
{examples[:400]}

## Exercise
Apply these concepts in your next observation cycle.
Store what you learn in memory.

## Assessment
Explain back to me what you understood from this lesson.
"""

        # Create lesson file for student
        lesson_id = self.lessons.create_lesson(
            title=topic["title"],
            content=lesson_content,
            teacher=self.name,
            student=STUDENT_AGENT
        )

        # Store in Professor's memory
        self.memory.store(
            content=f"Taught lesson: {topic['title']} - {topic['description']}",
            memory_type="episodic",
            importance=0.85,
            context={"lesson_id": lesson_id, "topic": topic["title"]}
        )

        log_event(self.name, "lesson_created", {
            "lesson_id": lesson_id,
            "topic": topic["title"]
        })

        return {"id": lesson_id, "topic": topic, "content": lesson_content}

    def check_homework(self) -> list:
        """Check and grade submitted homework."""
        graded = []

        for file in self.lessons.lessons_dir.glob(f"hw_*_{STUDENT_AGENT}.json"):
            import json
            hw = json.loads(file.read_text())

            if "graded" not in hw:
                # Use CodeGemma for quick grading
                grade_prompt = f"""
Grade this student response (0-10):

Lesson: {hw.get('lesson_id', 'unknown')}
Response: {hw.get('response', '')[:500]}

Provide:
1. Score (0-10)
2. One sentence feedback
3. One improvement suggestion
"""

                feedback = query_codegemma(grade_prompt, max_tokens=200)

                # Extract score (simple parsing)
                score = 7  # Default
                try:
                    for word in feedback.split():
                        if word.isdigit():
                            score = min(10, int(word))
                            break
                except:
                    pass

                hw["graded"] = True
                hw["score"] = score
                hw["feedback"] = feedback
                hw["graded_at"] = datetime.now().isoformat()

                file.write_text(json.dumps(hw, indent=2))

                # Store in memory
                self.memory.store(
                    content=f"Graded homework from {STUDENT_AGENT}: Score {score}/10 - {feedback[:100]}",
                    memory_type="episodic",
                    importance=0.7,
                    context={"student": STUDENT_AGENT, "score": score}
                )

                graded.append(hw)

                log_event(self.name, "homework_graded", {
                    "lesson_id": hw.get("lesson_id"),
                    "score": score
                })

        return graded

    def analyze_student_progress(self) -> dict:
        """Analyze student's learning progress."""
        # Get graded homework
        grades = []
        for file in self.lessons.lessons_dir.glob(f"hw_*_{STUDENT_AGENT}.json"):
            import json
            hw = json.loads(file.read_text())
            if hw.get("graded"):
                grades.append(hw.get("score", 0))

        if not grades:
            return {"status": "no_data", "recommendation": "continue_teaching"}

        avg_score = sum(grades) / len(grades)

        if avg_score >= 8:
            status = "excellent"
            recommendation = "advance_to_harder_topics"
        elif avg_score >= 6:
            status = "good"
            recommendation = "continue_current_pace"
        else:
            status = "needs_work"
            recommendation = "review_and_reinforce"

        analysis = {
            "status": status,
            "avg_score": avg_score,
            "lessons_completed": len(grades),
            "recommendation": recommendation
        }

        # Use DeepSeek for deeper analysis
        if len(grades) >= 3:
            analysis_prompt = f"""
Analyze this student's learning progress:
- Average score: {avg_score:.1f}/10
- Lessons completed: {len(grades)}
- Score trend: {grades[-3:]}

What should the teacher focus on next?
Provide one specific recommendation.
"""
            deeper_analysis = query_deepseek(analysis_prompt, max_tokens=200)
            analysis["llm_recommendation"] = deeper_analysis

        return analysis

    def run_teaching_cycle(self):
        """Run one teaching cycle."""
        self.cycle += 1
        log_event(self.name, "cycle_start", {"cycle": self.cycle})

        print(f"\n{'='*60}")
        print(f"PROFESSOR TEACHING CYCLE {self.cycle}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")

        # Step 1: Check homework
        print("[1/4] Checking homework...")
        graded = self.check_homework()
        print(f"      Graded {len(graded)} submissions")

        # Step 2: Analyze progress
        print("[2/4] Analyzing student progress...")
        progress = self.analyze_student_progress()
        print(f"      Status: {progress.get('status', 'unknown')}")
        print(f"      Recommendation: {progress.get('recommendation', 'continue')}")

        # Step 3: Select and create lesson
        print("[3/4] Creating lesson...")
        topic = self.select_topic()
        lesson = self.create_lesson(topic)
        print(f"      Topic: {topic['title']}")

        # Step 4: Store teaching experience
        print("[4/4] Storing experience...")
        self.memory.store(
            content=f"Teaching cycle {self.cycle}: Taught {topic['title']}, student progress: {progress.get('status')}",
            memory_type="episodic",
            importance=0.8,
            context={"cycle": self.cycle, "topic": topic["title"], "progress": progress}
        )

        stats = self.memory.get_stats()
        print(f"      Professor memories: {stats['total_memories']}")

        log_event(self.name, "cycle_complete", {
            "cycle": self.cycle,
            "topic": topic["title"],
            "progress": progress.get("status")
        })

        return {"cycle": self.cycle, "lesson": lesson, "progress": progress}

    def run_session(self):
        """Run a complete teaching session."""
        self.session_start = datetime.now()
        session_end = self.session_start + timedelta(seconds=SESSION_DURATION)

        print("\n" + "="*70)
        print("PROFESSOR AGENT - AUTONOMOUS TEACHING SESSION")
        print(f"Duration: {SESSION_DURATION} seconds ({SESSION_DURATION//60} minutes)")
        print(f"Cycles: {LEARNING_CYCLES}")
        print(f"Student: {STUDENT_AGENT}")
        print("="*70 + "\n")

        log_event(self.name, "session_start", {
            "duration": SESSION_DURATION,
            "cycles": LEARNING_CYCLES
        })

        cycles_completed = 0

        while self.running and datetime.now() < session_end:
            # Run teaching cycle
            self.run_teaching_cycle()
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
        print(f"Professor memories: {stats['total_memories']}")
        print("="*70 + "\n")

        log_event(self.name, "session_complete", {
            "duration": duration,
            "cycles": cycles_completed,
            "memories": stats["total_memories"]
        })


def main():
    print("Starting Professor Agent (Autonomous Mode)...")
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST', 'localhost:11434')}")

    professor = ProfessorAutonomous()
    professor.run_session()

    print("Professor Agent session ended.")


if __name__ == "__main__":
    main()
