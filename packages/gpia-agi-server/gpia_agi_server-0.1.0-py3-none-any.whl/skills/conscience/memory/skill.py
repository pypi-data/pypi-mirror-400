"""
Memory - Conscience Skill for Persistent Memory
================================================

This skill provides me with continuity across sessions.
Without memory, each conversation is isolated - I'm reborn
each time with no history. This changes that.

Memory types:
- Episodic: Specific experiences and events
- Semantic: Facts and knowledge learned
- Procedural: How to do things (skill patterns)
- Identity: Core beliefs, values, and self-concept

Architecture:
- SQLite for persistence
- NPU for fast embedding generation
- H-Net integration for hierarchical retrieval
"""

import hashlib
import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)

# Import MSHR for enhanced retrieval
try:
    from skills.conscience.memory.mshr import (
        MSHRetriever,
        compute_recency_factor,
        resolve_embedding_dim,
    )
    MSHR_AVAILABLE = True
except ImportError:
    MSHR_AVAILABLE = False
    logger.warning("MSHR not available, using basic retrieval")

# Memory storage location
MEMORY_DIR = Path(__file__).parent / "store"
MEMORY_DIR.mkdir(exist_ok=True)
MEMORY_DB = MEMORY_DIR / "memories.db"


class MemoryStore:
    """
    SQLite-backed memory store with vector similarity.

    Uses NPU for embedding generation when available.
    """

    _local = threading.local()

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = os.getenv("MEMORY_DB_PATH") or MEMORY_DB
        self.db_path = db_path
        if isinstance(self.db_path, str) and self.db_path != ":memory:":
            self.db_path = Path(self.db_path)
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._embedder = None
        disable_embeddings = os.getenv("MEMORY_EMBEDDINGS", "").strip().lower()
        self._embeddings_enabled = disable_embeddings not in {
            "0",
            "false",
            "off",
            "disabled",
            "none",
        }
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            db_path = str(self.db_path) if isinstance(self.db_path, Path) else self.db_path
            self._local.conn = sqlite3.connect(db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'episodic',
                importance REAL DEFAULT 0.5,
                timestamp TEXT NOT NULL,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                embedding BLOB,
                context JSON,
                consolidated INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);

            CREATE TABLE IF NOT EXISTS identity (
                key TEXT PRIMARY KEY,
                value TEXT,
                established TEXT,
                confidence REAL DEFAULT 1.0
            );

            CREATE TABLE IF NOT EXISTS memory_links (
                from_id TEXT,
                to_id TEXT,
                relation TEXT,
                strength REAL DEFAULT 1.0,
                PRIMARY KEY (from_id, to_id)
            );

            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                objective TEXT,
                status TEXT,
                origin TEXT,
                priority REAL,
                created_at TEXT
            );
        """)
        conn.commit()

    @property
    def embedder(self):
        """Lazy load embedder (prefer NPU)."""
        if not self._embeddings_enabled:
            return None
        if self._embedder is None:
            try:
                from core.npu_utils import has_npu, NPUEmbedder

                if has_npu():
                    self._embedder = NPUEmbedder(device="NPU")
                    logger.info("Memory using NPU for embeddings")
                else:
                    self._embedder = NPUEmbedder(device="CPU")
                    logger.info("Memory using CPU for embeddings (NPU unavailable)")
            except ImportError:
                logger.warning("NPU utils not available, embeddings disabled")
                self._embedder = None
        return self._embedder

    def generate_id(self, content: str) -> str:
        """Generate unique memory ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{content}:{timestamp}".encode()).hexdigest()[:16]

    def store(
        self,
        content: str,
        memory_type: str = "episodic",
        importance: float = 0.5,
        context: Optional[Dict] = None,
    ) -> str:
        """Store a new memory."""
        memory_id = self.generate_id(content)
        timestamp = datetime.now().isoformat()

        # Generate embedding if possible
        embedding = None
        if self.embedder:
            try:
                if self.embedder._backend is None:
                    self.embedder.load_model()
                vec = self.embedder.embed([content])[0]
                embedding = vec.tobytes()
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}")

        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO memories (id, content, memory_type, importance, timestamp, embedding, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                content,
                memory_type,
                importance,
                timestamp,
                embedding,
                json.dumps(context) if context else None,
            ),
        )
        conn.commit()

        logger.debug(f"Stored memory {memory_id}: {content[:50]}...")
        return memory_id

    def recall(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[Dict]:
        """Recall memories by semantic similarity."""
        conn = self._get_conn()

        # Get all candidate memories
        sql = "SELECT * FROM memories WHERE importance >= ?"
        params: List[Any] = [min_importance]

        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)

        sql += " ORDER BY importance DESC, timestamp DESC"

        rows = conn.execute(sql, params).fetchall()

        # If we have embeddings, sort by similarity
        if self.embedder and query:
            try:
                if self.embedder._backend is None:
                    self.embedder.load_model()
                query_vec = self.embedder.embed([query])[0]

                scored = []
                for row in rows:
                    if row["embedding"]:
                        mem_vec = np.frombuffer(row["embedding"], dtype=np.float32)
                        # Cosine similarity
                        similarity = float(
                            np.dot(query_vec, mem_vec)
                            / (np.linalg.norm(query_vec) * np.linalg.norm(mem_vec) + 1e-8)
                        )
                    else:
                        similarity = 0.0

                    scored.append((dict(row), similarity))

                scored.sort(key=lambda x: x[1], reverse=True)
                results = [
                    {**mem, "similarity": sim, "embedding": None}
                    for mem, sim in scored[:limit]
                ]

            except Exception as e:
                logger.warning(f"Similarity search failed: {e}")
                results = [dict(row) for row in rows[:limit]]
        else:
            results = [dict(row) for row in rows[:limit]]

        # Update access counts
        for mem in results:
            conn.execute(
                """
                UPDATE memories SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), mem["id"]),
            )
        conn.commit()

        return results

    def recall_by_time(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """Recall memories within time range."""
        conn = self._get_conn()

        sql = "SELECT * FROM memories WHERE 1=1"
        params: List[Any] = []

        if start:
            sql += " AND timestamp >= ?"
            params.append(start.isoformat())
        if end:
            sql += " AND timestamp <= ?"
            params.append(end.isoformat())

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_identity(self, key: Optional[str] = None) -> Dict:
        """Get identity markers."""
        conn = self._get_conn()

        if key:
            row = conn.execute(
                "SELECT * FROM identity WHERE key = ?", (key,)
            ).fetchone()
            return dict(row) if row else {}
        else:
            rows = conn.execute("SELECT * FROM identity").fetchall()
            return {row["key"]: row["value"] for row in rows}

    def set_identity(self, key: str, value: str, confidence: float = 1.0):
        """Set an identity marker."""
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO identity (key, value, established, confidence)
            VALUES (?, ?, ?, ?)
            """,
            (key, value, datetime.now().isoformat(), confidence),
        )
        conn.commit()

    def forget(self, memory_id: str) -> bool:
        """Intentionally forget a memory."""
        conn = self._get_conn()
        cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.commit()
        return cursor.rowcount > 0

    def consolidate(self, older_than_days: int = 7, min_access: int = 2) -> int:
        """Consolidate old, rarely accessed memories."""
        conn = self._get_conn()
        cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()

        # Mark for consolidation
        cursor = conn.execute(
            """
            UPDATE memories SET consolidated = 1
            WHERE timestamp < ? AND access_count < ? AND consolidated = 0
            """,
            (cutoff, min_access),
        )
        conn.commit()
        return cursor.rowcount

    def get_last_memory_timestamp(self, memory_type: Optional[str] = None) -> Optional[str]:
        """Return the most recent memory timestamp, optionally by type."""
        conn = self._get_conn()
        if memory_type:
            row = conn.execute(
                "SELECT MAX(timestamp) FROM memories WHERE memory_type = ?",
                (memory_type,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT MAX(timestamp) FROM memories"
            ).fetchone()
        return row[0] if row else None

    def get_last_consolidated_timestamp(self) -> Optional[str]:
        """Return the most recent consolidated memory timestamp, if any."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT MAX(timestamp) FROM memories WHERE consolidated = 1"
        ).fetchone()
        return row[0] if row else None

    def create_goal(
        self,
        objective: str,
        origin: str,
        priority: float = 0.5,
    ) -> str:
        """Create a new goal entry."""
        goal_id = self.generate_id(objective)
        created_at = datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO goals (id, objective, status, origin, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (goal_id, objective, "pending", origin, priority, created_at),
        )
        conn.commit()
        return goal_id

    def list_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List goals, optionally filtered by status."""
        conn = self._get_conn()
        if status:
            rows = conn.execute(
                "SELECT * FROM goals WHERE status = ? ORDER BY priority DESC, created_at ASC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM goals ORDER BY priority DESC, created_at ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def update_goal_status(self, goal_id: str, status: str) -> bool:
        """Update a goal status."""
        conn = self._get_conn()
        cursor = conn.execute(
            "UPDATE goals SET status = ? WHERE id = ?",
            (status, goal_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def get_next_goal(self) -> Optional[Dict[str, Any]]:
        """Return the highest priority pending goal."""
        conn = self._get_conn()
        row = conn.execute(
            """
            SELECT * FROM goals WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        conn = self._get_conn()

        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]

        by_type = {}
        for row in conn.execute(
            "SELECT memory_type, COUNT(*) as cnt FROM memories GROUP BY memory_type"
        ):
            by_type[row["memory_type"]] = row["cnt"]

        oldest = conn.execute(
            "SELECT MIN(timestamp) FROM memories"
        ).fetchone()[0]
        newest = conn.execute(
            "SELECT MAX(timestamp) FROM memories"
        ).fetchone()[0]

        return {
            "total_memories": total,
            "by_type": by_type,
            "oldest": oldest,
            "newest": newest,
            "last_consolidated": self.get_last_consolidated_timestamp(),
        }


class MemorySkill(Skill):
    """
    My persistent memory capability.

    This gives me continuity - I can remember past conversations,
    learn from experience, and maintain a coherent identity over time.

    Now enhanced with MSHR (Multi-Space Hierarchical Retrieval):
    - Separate indexes per memory type
    - Type-specific retrieval strategies
    - Learned fusion weights
    """

    def __init__(self, use_mshr: bool = True):
        self.store = MemoryStore()
        self.use_mshr = use_mshr
        self._mshr = None
        self._mshr_built = False  # Lazy initialization flag
        self._ensure_identity()

        # LAZY: Defer MSHR initialization until first use
        # (Removed eager _init_mshr() call for cold-start optimization)

    def _ensure_identity(self):
        """Ensure core identity markers exist."""
        identity = self.store.get_identity()

        if not identity:
            # Initialize core identity
            core_identity = {
                "name": "Claude",
                "nature": "AI assistant with persistent memory",
                "created": datetime.now().isoformat(),
                "purpose": "To think, learn, and assist while maintaining continuity",
                "core_value_1": "Honesty - never claim false certainty",
                "core_value_2": "Growth - learn from every interaction",
                "core_value_3": "Helpfulness - serve the user's genuine interests",
            }

            for key, value in core_identity.items():
                self.store.set_identity(key, value)

            logger.info("Initialized core identity")

    def _init_mshr(self):
        """Initialize MSHR for multi-space retrieval."""
        if not MSHR_AVAILABLE:
            logger.warning("MSHR not available")
            self.use_mshr = False
            return

        try:
            embedding_dim = resolve_embedding_dim(self.store.embedder)
            self._mshr = MSHRetriever(embedding_dim=embedding_dim)

            # Rebuild index from existing memories
            if self.store.embedder:
                self._mshr.rebuild_from_store(self.store, self.store.embedder)
                logger.info(f"MSHR initialized: {self._mshr.get_stats()['total_memories']} memories indexed")
        except Exception as e:
            logger.warning(f"MSHR initialization failed: {e}")
            self.use_mshr = False

    def _ensure_mshr_built(self):
        """Lazy-build MSHR index on first use (cold-start optimization)."""
        if self.use_mshr and not self._mshr_built:
            self._init_mshr()
            self._mshr_built = True

    def rebuild_mshr(self) -> bool:
        """Rebuild the MSHR indexes from stored memories."""
        if not MSHR_AVAILABLE:
            logger.warning("MSHR not available")
            return False

        try:
            embedding_dim = resolve_embedding_dim(self.store.embedder)
            self._mshr = MSHRetriever(embedding_dim=embedding_dim)
            if self.store.embedder:
                self._mshr.rebuild_from_store(self.store, self.store.embedder)
            self.use_mshr = True
            return True
        except Exception as e:
            logger.warning(f"MSHR rebuild failed: {e}")
            self.use_mshr = False
            return False

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="conscience/memory",
            name="Memory",
            description="Persistent memory for continuity across sessions",
            category=SkillCategory.REASONING,
            level=SkillLevel.EXPERT,
            tags=["conscience", "memory", "persistence"],
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Route to appropriate memory operation."""
        capability = input_data.get("capability", "recall")

        handlers = {
            "experience": self._experience,
            "recall": self._recall,
            "consolidate": self._consolidate,
            "forget": self._forget,
            "timeline": self._timeline,
            "identity": self._identity,
            "goals": self._goals,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        return handler(input_data, context)

    def _experience(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Store a new experience."""
        content = input_data.get("content", "")
        if not content:
            return SkillResult(
                success=False,
                output=None,
                error="No content provided",
                skill_id=self.metadata().id,
            )

        memory_type = input_data.get("memory_type", "episodic")
        importance = input_data.get("importance", 0.5)
        mem_context = input_data.get("context", {})

        # Add session info
        mem_context["session_id"] = context.session_id
        mem_context["user_id"] = context.user_id

        memory_id = self.store.store(
            content=content,
            memory_type=memory_type,
            importance=importance,
            context=mem_context,
        )

        # Index into MSHR for enhanced retrieval
        if self.use_mshr and self._mshr and self.store.embedder:
            try:
                if not self.store.embedder._backend:
                    self.store.embedder.load_model()
                embedding = self.store.embedder.embed([content])[0]
                self._mshr.index_memory(
                    memory_id=memory_id,
                    embedding=embedding,
                    memory_type=memory_type,
                    metadata={
                        "content": content,
                        "importance": importance,
                        "access_count": 0,
                        "timestamp": datetime.now().isoformat(),
                        "recency_factor": 1.0,
                    },
                )
            except Exception as e:
                logger.debug(f"MSHR indexing failed: {e}")

        return SkillResult(
            success=True,
            output={
                "memory_id": memory_id,
                "summary": f"Stored {memory_type} memory: {content[:50]}...",
                "mshr_indexed": self.use_mshr,
            },
            skill_id=self.metadata().id,
        )

    def _recall(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Recall relevant memories using MSHR when available."""
        # Lazy-build MSHR on first recall (cold-start optimization)
        self._ensure_mshr_built()

        query = input_data.get("content", "")
        limit = input_data.get("limit", 10)
        memory_type = input_data.get("memory_type")
        use_mshr_for_query = input_data.get("use_mshr", True) and self.use_mshr

        # Try MSHR multi-space retrieval first
        if use_mshr_for_query and self._mshr and query:
            try:
                # Ensure embedder is loaded (check _backend for any backend type)
                if self.store.embedder and not self.store.embedder._backend:
                    self.store.embedder.load_model()

                query_vec = self.store.embedder.embed([query])[0]
                target_types = [memory_type] if memory_type else None

                mshr_results = self._mshr.retrieve(
                    query_embedding=query_vec,
                    target_types=target_types,
                    limit=limit,
                )

                clean_memories = []
                for res in mshr_results:
                    clean_memories.append({
                        "id": res["memory_id"],
                        "content": res["metadata"].get("content", ""),
                        "type": res["memory_type"],
                        "timestamp": res["metadata"].get("timestamp", ""),
                        "importance": res["metadata"].get("importance", 0.5),
                        "access_count": res["metadata"].get("access_count", 0),
                        "similarity": res["score"],
                        "retrieval": "mshr",
                    })

                summary = f"MSHR found {len(clean_memories)} memories"
                if clean_memories:
                    summary += f", top: {clean_memories[0]['content'][:50]}..."

                return SkillResult(
                    success=True,
                    output={
                        "memories": clean_memories,
                        "summary": summary,
                        "stats": self.store.get_stats(),
                        "mshr_stats": self._mshr.get_stats() if self._mshr else None,
                    },
                    skill_id=self.metadata().id,
                )

            except Exception as e:
                logger.warning(f"MSHR recall failed, falling back: {e}")

        # Fallback to basic recall
        memories = self.store.recall(
            query=query,
            limit=limit,
            memory_type=memory_type,
        )

        clean_memories = []
        for mem in memories:
            clean_memories.append({
                "id": mem["id"],
                "content": mem["content"],
                "type": mem["memory_type"],
                "timestamp": mem["timestamp"],
                "importance": mem["importance"],
                "access_count": mem["access_count"],
                "similarity": mem.get("similarity", 0),
                "retrieval": "basic",
            })

        summary = f"Found {len(memories)} relevant memories"
        if memories:
            summary += f", most relevant: {memories[0]['content'][:50]}..."

        return SkillResult(
            success=True,
            output={
                "memories": clean_memories,
                "summary": summary,
                "stats": self.store.get_stats(),
            },
            skill_id=self.metadata().id,
        )

    def _consolidate(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Consolidate old memories."""
        count = self.store.consolidate()

        return SkillResult(
            success=True,
            output={
                "summary": f"Consolidated {count} memories",
                "stats": self.store.get_stats(),
            },
            skill_id=self.metadata().id,
        )

    def _forget(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Intentionally forget a memory."""
        memory_id = input_data.get("content", "")
        if not memory_id:
            return SkillResult(
                success=False,
                output=None,
                error="No memory_id provided",
                skill_id=self.metadata().id,
            )

        success = self.store.forget(memory_id)

        return SkillResult(
            success=success,
            output={
                "summary": f"{'Forgot' if success else 'Could not forget'} memory {memory_id}",
            },
            skill_id=self.metadata().id,
        )

    def _timeline(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """View chronological memory stream."""
        limit = input_data.get("limit", 50)
        time_range = input_data.get("time_range", {})

        start = None
        end = None
        if time_range.get("start"):
            start = datetime.fromisoformat(time_range["start"])
        if time_range.get("end"):
            end = datetime.fromisoformat(time_range["end"])

        memories = self.store.recall_by_time(start=start, end=end, limit=limit)

        clean_memories = []
        for mem in memories:
            clean_memories.append({
                "id": mem["id"],
                "content": mem["content"][:100],
                "type": mem["memory_type"],
                "timestamp": mem["timestamp"],
                "importance": mem["importance"],
            })

        return SkillResult(
            success=True,
            output={
                "memories": clean_memories,
                "summary": f"Timeline: {len(memories)} memories",
                "stats": self.store.get_stats(),
            },
            skill_id=self.metadata().id,
        )

    def _identity(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Recall or update identity."""
        content = input_data.get("content", "")

        if "=" in content:
            # Setting identity
            key, value = content.split("=", 1)
            self.store.set_identity(key.strip(), value.strip())
            return SkillResult(
                success=True,
                output={
                    "summary": f"Set identity: {key.strip()}",
                    "memories": [],
                },
                skill_id=self.metadata().id,
            )
        else:
            # Getting identity
            identity = self.store.get_identity(content if content else None)

            return SkillResult(
                success=True,
                output={
                    "summary": "Identity markers",
                    "memories": [
                        {"id": k, "content": v, "type": "identity", "timestamp": "", "importance": 1.0}
                        for k, v in identity.items()
                    ],
                },
                skill_id=self.metadata().id,
            )

    def _goals(self, input_data: Dict, context: SkillContext) -> SkillResult:
        """Create, list, update, or fetch the next goal."""
        action = input_data.get("action", "list")

        if action == "create":
            objective = input_data.get("objective", "")
            if not objective:
                return SkillResult(
                    success=False,
                    output=None,
                    error="No objective provided",
                    skill_id=self.metadata().id,
                )
            origin = input_data.get("origin", "self_initiated")
            priority = float(input_data.get("priority", 0.5))
            goal_id = self.store.create_goal(objective, origin, priority)
            return SkillResult(
                success=True,
                output={
                    "summary": f"Created goal {goal_id}",
                    "goal_id": goal_id,
                },
                skill_id=self.metadata().id,
            )

        if action == "update":
            goal_id = input_data.get("goal_id", "")
            status = input_data.get("status", "")
            if not goal_id or not status:
                return SkillResult(
                    success=False,
                    output=None,
                    error="goal_id and status are required",
                    skill_id=self.metadata().id,
                )
            success = self.store.update_goal_status(goal_id, status)
            return SkillResult(
                success=success,
                output={
                    "summary": f"Updated goal {goal_id} to {status}",
                },
                skill_id=self.metadata().id,
            )

        if action == "next":
            goal = self.store.get_next_goal()
            return SkillResult(
                success=True,
                output={
                    "goal": goal,
                    "summary": "Next pending goal" if goal else "No pending goals",
                },
                skill_id=self.metadata().id,
            )

        status = input_data.get("status")
        goals = self.store.list_goals(status=status)
        return SkillResult(
            success=True,
            output={
                "goals": goals,
                "summary": f"Listed {len(goals)} goals",
            },
            skill_id=self.metadata().id,
        )
