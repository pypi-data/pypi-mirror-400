"""
Agent Utilities - Shared functions for autonomous agents

Provides:
- LLM communication with Ollama
- Memory management (SQLite)
- Lesson file handling
- Logging utilities
"""

import os
import json
import sqlite3
import requests
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.dynamic_budget_orchestrator import apply_dynamic_budget
# Configuration from environment
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost:11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}/api/generate"


class AgentMemory:
    """SQLite-based memory for agents running in containers."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        """Initialize memory tables."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'episodic',
                importance REAL DEFAULT 0.5,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC);
            CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at DESC);
        """)
        self.conn.commit()

    def store(self, content: str, memory_type: str = "episodic",
              importance: float = 0.5, context: Dict = None) -> str:
        """Store a memory."""
        memory_id = hashlib.sha256(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        self.conn.execute("""
            INSERT INTO memories (id, content, memory_type, importance, context)
            VALUES (?, ?, ?, ?, ?)
        """, (
            memory_id,
            content,
            memory_type,
            importance,
            json.dumps(context) if context else None
        ))
        self.conn.commit()
        return memory_id

    def recall(self, query: str = None, memory_type: str = None,
               limit: int = 10) -> List[Dict]:
        """Recall memories."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []

        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)

        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total,
                memory_type,
                AVG(importance) as avg_importance
            FROM memories
            GROUP BY memory_type
        """)

        by_type = {}
        total = 0
        for row in cursor.fetchall():
            by_type[row[1]] = row[0]
            total += row[0]

        return {"total_memories": total, "by_type": by_type}

    def get_recent(self, limit: int = 5) -> List[Dict]:
        """Get most recent memories."""
        cursor = self.conn.execute("""
            SELECT * FROM memories
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query_llm(model: str, prompt: str, max_tokens: int = 1500,
              temperature: float = 0.7) -> str:
    """Query local Ollama LLM."""
    try:
        effective_max = apply_dynamic_budget(prompt, max_tokens, model_id=model)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": effective_max,
            },
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            result = (data.get("response") or "").strip()
            if not result and data.get("thinking"):
                retry_payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
                }
                retry = requests.post(OLLAMA_URL, json=retry_payload, timeout=120)
                if retry.status_code == 200:
                    result = (retry.json().get("response") or "").strip()
            return result
        return f"[Error: {response.status_code}]"
    except Exception as e:
        return f"[Error: {e}]"


def query_deepseek(prompt: str, max_tokens: int = 1500) -> str:
    """Query DeepSeek-R1 for analytical reasoning."""
    return query_llm("gpia-deepseek-r1:latest", prompt, max_tokens, temperature=0.5)


def query_qwen(prompt: str, max_tokens: int = 1500) -> str:
    """Query Qwen3 for creative synthesis."""
    return query_llm("gpia-qwen3:latest", prompt, max_tokens, temperature=0.7)


def query_codegemma(prompt: str, max_tokens: int = 1000) -> str:
    """Query CodeGemma for quick validation."""
    return query_llm("gpia-codegemma:latest", prompt, max_tokens, temperature=0.3)


class LessonManager:
    """Manage lessons shared between agents via volume."""

    def __init__(self, lessons_dir: str = "/app/lessons"):
        self.lessons_dir = Path(lessons_dir)
        self.lessons_dir.mkdir(parents=True, exist_ok=True)

    def create_lesson(self, title: str, content: str,
                      teacher: str, student: str) -> str:
        """Create a lesson file."""
        lesson_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        lesson = {
            "id": lesson_id,
            "title": title,
            "content": content,
            "teacher": teacher,
            "student": student,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        lesson_file = self.lessons_dir / f"{lesson_id}_{teacher}_to_{student}.json"
        lesson_file.write_text(json.dumps(lesson, indent=2))
        return lesson_id

    def get_pending_lessons(self, student: str) -> List[Dict]:
        """Get pending lessons for a student."""
        lessons = []
        for file in self.lessons_dir.glob(f"*_to_{student}.json"):
            lesson = json.loads(file.read_text())
            if lesson.get("status") == "pending":
                lessons.append(lesson)
        return sorted(lessons, key=lambda x: x["created_at"])

    def mark_lesson_complete(self, lesson_id: str, student: str):
        """Mark a lesson as completed."""
        for file in self.lessons_dir.glob(f"{lesson_id}_*_to_{student}.json"):
            lesson = json.loads(file.read_text())
            lesson["status"] = "completed"
            lesson["completed_at"] = datetime.now().isoformat()
            file.write_text(json.dumps(lesson, indent=2))

    def submit_homework(self, lesson_id: str, student: str,
                        response: str, understanding: float):
        """Student submits homework for a lesson."""
        homework = {
            "lesson_id": lesson_id,
            "student": student,
            "response": response,
            "understanding": understanding,
            "submitted_at": datetime.now().isoformat()
        }

        hw_file = self.lessons_dir / f"hw_{lesson_id}_{student}.json"
        hw_file.write_text(json.dumps(homework, indent=2))

    def get_homework(self, lesson_id: str, student: str) -> Optional[Dict]:
        """Get homework submission for a lesson."""
        hw_file = self.lessons_dir / f"hw_{lesson_id}_{student}.json"
        if hw_file.exists():
            return json.loads(hw_file.read_text())
        return None


def log_event(agent: str, event: str, details: Dict = None):
    """Log agent events."""
    log_dir = Path("/app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "event": event,
        "details": details or {}
    }

    log_file = log_dir / f"{agent}_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[{agent}] {event}: {details}")
